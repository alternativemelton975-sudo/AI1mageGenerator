import os
import uuid
import requests
from pathlib import Path
from flask import Flask, render_template, request

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}"
}


def generate_image(prompt):
    print("Using URL:", API_URL)
    print("Token exists:", bool(HF_TOKEN))

    response = requests.post(
        API_URL,
        headers=HEADERS,
        json={"inputs": prompt},
        timeout=120
    )

    print("Status Code:", response.status_code)

    if response.status_code != 200:
        raise Exception(
            f"API Error: {response.status_code} - {response.text}"
        )

    if response.headers.get(
        "content-type",
        ""
    ).startswith("application/json"):
        raise Exception(response.text)

    filename = f"{uuid.uuid4().hex}.png"

    image_path = STATIC_DIR / filename

    with open(image_path, "wb") as image_file:
        image_file.write(response.content)

    return f"/static/{filename}"


@app.route("/")
def index():
    return render_template("index.html")
    
@app.route("/test")
def test():
    try:
        response = requests.get(
            "https://www.google.com",
            timeout=10
        )

        return f"Success: {response.status_code}"

    except Exception as e:
        return str(e)

@app.route("/generate", methods=["POST"])
def generate():
    prompt = request.form.get(
        "prompt",
        ""
    ).strip()

    if not prompt:
        prompt = "A fantasy landscape"

    try:
        image_url = generate_image(prompt)

        return render_template(
            "result.html",
            prompt=prompt,
            image_url=image_url,
            error=None
        )

    except Exception as e:
        print("Generation Error:", str(e))

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
