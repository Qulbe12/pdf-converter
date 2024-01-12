from flask import Flask, request, jsonify
from flask_cors import CORS
from pypdf import PdfReader, PdfFileReader
from io import BytesIO
import spacy

app = Flask(__name__)
CORS(app)

nlp = spacy.load("en_core_web_sm")

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route('/convert-pdf-to-text', methods=['POST'])
def convert_pdf_to_text():
    # Check if a file was sent in the request
    if 'pdf' not in request.files:
        print("error")
        return jsonify({'error': 'No file part'})

    pdf_file = request.files['pdf']
    if pdf_file.filename == '':
        return jsonify({'error': 'No selected file'})

    # Open the PDF file
    text = ""

    try:
        # Get the file's content as bytes
        pdf_bytes = pdf_file.read()

        # Create a file-like object using BytesIO
        pdf_file_like = BytesIO(pdf_bytes)

        # Initialize PdfReader
        pdf_reader = PdfReader(pdf_file_like)

        num_pages = len(pdf_reader.pages)

        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()

    except Exception as e:
        print(f"An error occurred: {e}")

        # Use SpaCy to process the text
        doc = nlp(text)

        paragraphs = []
        current_paragraph = ""

        # Iterate through sentences to identify paragraphs
        for sentence in doc.sents:
            if sentence.text.strip():  # Non-empty sentence
                current_paragraph += sentence.text
            else:  # Empty sentence indicates the end of a paragraph
                if current_paragraph.strip():  # Non-empty paragraph
                    paragraphs.append(current_paragraph.strip())
                    current_paragraph = ""

        # Add the last paragraph if any
        if current_paragraph.strip():
            paragraphs.append(current_paragraph.strip())

        return paragraphs


if __name__ == '__main__':
    app.run()
