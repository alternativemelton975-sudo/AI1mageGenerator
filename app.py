import os

import requests
from flask import Flask, render_template, request

app = Flask(__name__)

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")


def search_images(query):
    if not PIXABAY_API_KEY:
        return []

    url = "https://pixabay.com/api/"

    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "image_type": "photo",
        "safesearch": "true",
        "per_page": 12
    }

    response = requests.get(url, params=params, timeout=10)

    if response.status_code != 200:
        return []

    data = response.json()

    return [
        image["webformatURL"]
        for image in data.get("hits", [])
    ]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate_web_image():

    prompt = request.form.get(
        "prompt",
        ""
    ).strip()

    if not prompt:
        prompt = "nature"

    image_urls = search_images(prompt)

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
