import os
import uuid
import random

from flask import Flask, render_template, request
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

os.makedirs("static", exist_ok=True)


def generate_image(prompt):
    width = 768
    height = 768

    image = Image.new(
        "RGB",
        (width, height),
        (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )
    )

    draw = ImageDraw.Draw(image)

    for _ in range(100):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)

        draw.line(
            (x1, y1, x2, y2),
            fill=(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            ),
            width=random.randint(1, 8)
        )

    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except Exception:
        font = ImageFont.load_default()

    draw.text(
        (25, 25),
        prompt,
        fill=(255, 255, 255),
        font=font
    )

    filename = f"{uuid.uuid4().hex}.png"

    filepath = os.path.join(
        "static",
        filename
    )

    image.save(filepath)

    return f"/static/{filename}"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    prompt = request.form.get(
        "prompt",
        ""
    ).strip()

    if not prompt:
        prompt = "Random Artwork"

    try:
        image_url = generate_image(prompt)

        return render_template(
            "result.html",
            prompt=prompt,
            image_url=image_url,
            error=None
        )

    except Exception as e:
        return render_template(
            "result.html",
            prompt=prompt,
            image_url=None,
            error=str(e)
        )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
