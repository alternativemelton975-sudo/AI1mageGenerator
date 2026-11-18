import os
import uuid
from pathlib import Path

from flask import Flask, render_template, request

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

pipe = None


def get_pipeline():
    global pipe

    if pipe is None:
        import torch
        from diffusers import StableDiffusionPipeline

        pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float32
        )

        pipe = pipe.to(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

    return pipe


from PIL import Image

def generate_image(prompt):
    image = Image.new("RGB", (512, 512), color="blue")

    filename = "test.png"
    image.save(f"static/{filename}")

    return f"/static/{filename}"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    prompt = request.form.get(
        "prompt",
        "A fantasy landscape"
    )

    image_url = generate_image(prompt)

    return render_template(
        "result.html",
        prompt=prompt,
        image_url=image_url
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
