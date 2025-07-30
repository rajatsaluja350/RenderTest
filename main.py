from flask import Flask, render_template, request
import requests
from PIL import Image
import io
import base64

app = Flask(__name__)

OCR_API_KEY = "helloworld"  # Replace with your OCR.Space API key

def extract_text_from_image(image_bytes):
    response = requests.post(
        "https://api.ocr.space/parse/image",
        files={"filename": image_bytes},
        data={"apikey": OCR_API_KEY, "language": "eng"},
    )
    result = response.json()
    if result.get("IsErroredOnProcessing"):
        return ""
    return result["ParsedResults"][0]["ParsedText"]

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    if request.method == "POST":
        files = request.files.getlist("receipts")
        for file in files:
            image_bytes = file.read()
            text = extract_text_from_image(image_bytes)
            results.append({
                "filename": file.filename,
                "text": text
            })
    return render_template("index.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)
