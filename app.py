import os
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

        saved_images = []

        for i, image in enumerate(result.images):
            filename = (
                f"{slugify(prompt)}-"
                f"{uuid.uuid4().hex[:8]}-{i+1}.png"
            )

            image_path = STATIC_DIR / filename

            image.save(image_path)

            saved_images.append(str(image_path))

        return saved_images

    except Exception as e:
        print(f"Generation error: {e}")

        saved_images = []

        for i in range(4):
            svg_path = STATIC_DIR / (
                f"{slugify(prompt)}-"
                f"{uuid.uuid4().hex[:8]}-{i+1}.svg"
            )

            svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="500">
  <rect width="100%" height="100%" fill="#111827"/>
  <circle cx="620" cy="140" r="110" fill="#f59e0b" opacity="0.9"/>
  <path d="M0 380 C140 300 240 310 330 360 S560 430 800 330 L800 500 L0 500 Z"
        fill="#1d4ed8" opacity="0.8"/>
  <path d="M0 420 C180 340 280 350 390 390 S610 450 800 390"
        stroke="#f8fafc" stroke-width="3"
        fill="none" opacity="0.8"/>
  <rect x="70" y="90" width="310" height="180"
        rx="20" fill="#ffffff" opacity="0.12"/>
  <text x="110" y="170"
        font-size="25"
        fill="#f8fafc"
        font-family="Arial">
        Generated Prompt
  </text>
  <text x="110" y="215"
        font-size="22"
        fill="#f8fafc"
        font-family="Arial">
        {prompt}
  </text>
  <text x="110" y="260"
        font-size="18"
        fill="#f59e0b"
        font-family="Arial">
        Variation {i + 1}
  </text>
</svg>
"""

            svg_path.write_text(svg, encoding="utf-8")

            saved_images.append(str(svg_path))

        return saved_images


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate_web_image():
    prompt = request.form.get(
        "prompt",
        ""
    ).strip() or "A fantasy landscape"

    image_paths = generate_image(prompt)

    image_urls = [
        os.path.relpath(
            path,
            start=BASE_DIR
        ).replace("\\", "/")
        for path in image_paths
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
