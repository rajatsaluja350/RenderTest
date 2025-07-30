from flask import Flask, render_template, request
import requests
from PIL import Image
import io

app = Flask(__name__)

OCR_API_KEY = "helloworld"  # Replace with your OCR.Space API key

def extract_receipt_data(image_bytes):
    response = requests.post(
        "https://api.ocr.space/parse/image",
        files={"filename": image_bytes},
        data={"apikey": OCR_API_KEY, "language": "eng"},
    )
    result = response.json()
    parsed_text = result.get("ParsedResults", [{}])[0].get("ParsedText", "")
    return parsed_text

@app.route("/", methods=["GET", "POST"])
def index():
    extracted_data = []
    if request.method == "POST":
        files = request.files.getlist("receipts")
        for file in files:
            image_bytes = file.read()
            text = extract_receipt_data(image_bytes)
            extracted_data.append({"filename": file.filename, "text": text})
    return render_template("index.html", extracted_data=extracted_data)

if __name__ == "__main__":
    app.run(debug=True)
