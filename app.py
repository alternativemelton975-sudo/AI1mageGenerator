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


def generate_image(prompt: str, output_path: str | None = None) -> str:
    prompt = (prompt or "A fantasy landscape").strip()

    if output_path is None:
        output_path = STATIC_DIR / f"{slugify(prompt)}-{uuid.uuid4().hex[:8]}.svg"
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        import torch
        from diffusers import StableDiffusionPipeline

        model_id = "runwayml/stable-diffusion-v1-5"
        device = "cuda" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if device == "cuda" else torch.float32

        pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch_dtype)
        pipe = pipe.to(device)
        image = pipe(prompt, num_inference_steps=4 if device == "cuda" else 1).images[0]

        image_path = output_path
        if image_path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            image_path = image_path.with_suffix(".png")

        image.save(image_path)
        return str(image_path)
    except Exception:
        svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='800' height='500'>
  <rect width='100%' height='100%' fill='#111827' />
  <circle cx='620' cy='140' r='110' fill='#f59e0b' opacity='0.9' />
  <path d='M0 380 C140 300 240 310 330 360 S560 430 800 330 L800 500 L0 500 Z' fill='#1d4ed8' opacity='0.8' />
  <path d='M0 420 C180 340 280 350 390 390 S610 450 800 390' stroke='#f8fafc' stroke-width='3' fill='none' opacity='0.8' />
  <rect x='70' y='90' width='310' height='180' rx='20' fill='#ffffff' opacity='0.12' />
  <text x='110' y='170' font-size='25' fill='#f8fafc' font-family='Arial, sans-serif'>Generated prompt</text>
  <text x='110' y='215' font-size='22' fill='#f8fafc' font-family='Arial, sans-serif'>{prompt}</text>
</svg>"""
        output_path.write_text(svg, encoding="utf-8")
        return str(output_path)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate_web_image():
    prompt = request.form.get("prompt", "").strip() or "A fantasy landscape"
    output_path = generate_image(prompt)
    image_url = os.path.relpath(output_path, start=BASE_DIR).replace("\\", "/")
    return render_template("result.html", prompt=prompt, image_url=image_url)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
