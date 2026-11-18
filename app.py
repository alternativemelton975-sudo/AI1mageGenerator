import re
import uuid
from pathlib import Path

from flask import Flask, render_template, request

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-")
    return value or "image"


def generate_image(prompt: str):
    prompt = (prompt or "A fantasy landscape").strip()

    try:
        import torch
        from diffusers import StableDiffusionPipeline

        model_id = "runwayml/stable-diffusion-v1-5"

        device = "cuda" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if device == "cuda" else torch.float32

        pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch_dtype
        )

        pipe = pipe.to(device)

        result = pipe(
            prompt,
            num_images_per_prompt=4,
            num_inference_steps=20
        )

        image_paths = []

        for i, image in enumerate(result.images):
            filename = (
                f"{slugify(prompt)}-"
                f"{uuid.uuid4().hex[:8]}-"
                f"{i + 1}.png"
            )

            image_path = STATIC_DIR / filename

            image.save(image_path)

            image_paths.append(filename)

        return image_paths

    except Exception as e:
        print(f"Image Generation Error: {e}")

        image_paths = []

        for i in range(4):
            filename = (
                f"{slugify(prompt)}-"
                f"{uuid.uuid4().hex[:8]}-"
                f"{i + 1}.svg"
            )

            svg_path = STATIC_DIR / filename

            svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="500">
  <rect width="100%" height="100%" fill="#111827"/>
  <circle cx="620" cy="140" r="110" fill="#f59e0b" opacity="0.9"/>
  <path d="M0 380 C140 300 240 310 330 360
           S560 430 800 330
           L800 500 L0 500 Z"
        fill="#1d4ed8"
        opacity="0.8"/>
  <text x="100"
        y="200"
        fill="white"
        font-size="24"
        font-family="Arial">
        {prompt}
  </text>
  <text x="100"
        y="250"
        fill="#f59e0b"
        font-size="20"
        font-family="Arial">
        Variation {i + 1}
  </text>
</svg>
"""

            svg_path.write_text(svg, encoding="utf-8")

            image_paths.append(filename)

        return image_paths


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate_web_image():
    prompt = request.form.get(
        "prompt",
        ""
    ).strip() or "A fantasy landscape"

    image_files = generate_image(prompt)

    image_urls = [
        f"/static/{filename}"
        for filename in image_files
    ]

    return render_template(
        "result.html",
        prompt=prompt,
        image_urls=image_urls
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
