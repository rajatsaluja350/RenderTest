import os
import requests
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from PIL import Image
import io
import fitz  # PyMuPDF

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

OCR_SPACE_API_KEY = 'helloworld'  # Free demo key from OCR.Space

def extract_text_from_image(image_bytes):
    response = requests.post(
        'https://api.ocr.space/parse/image',
        files={'filename': image_bytes},
        data={'apikey': OCR_SPACE_API_KEY, 'language': 'eng'}
    )
    result = response.json()
    if result.get('IsErroredOnProcessing'):
        return ''
    return result['ParsedResults'][0]['ParsedText']

def extract_text_from_pdf(pdf_path):
    text = ''
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def parse_receipt_text(text):
    import re
    date_match = re.search(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b', text)
    amount_match = re.search(r'\b(?:Total|Amount|Paid)[^\d]*(\d+[.,]?\d*)\b', text, re.IGNORECASE)
    place_match = re.search(r'\b(?:Store|Merchant|Place|Location)[^\n]*\n([^\n]+)', text, re.IGNORECASE)

    return {
        'date': date_match.group(1) if date_match else 'N/A',
        'amount': amount_match.group(1) if amount_match else 'N/A',
        'place': place_match.group(1).strip() if place_match else 'N/A'
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    if request.method == 'POST':
        files = request.files.getlist('receipts')
        for file in files:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            if filename.lower().endswith('.pdf'):
                text = extract_text_from_pdf(filepath)
            else:
                image_bytes = file.read()
                text = extract_text_from_image(image_bytes)

            parsed = parse_receipt_text(text)
            parsed['filename'] = filename
            results.append(parsed)

    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
