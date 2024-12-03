import re
import os
import json
import fitz
import config

def read_pdf_as_bytes(pdf_path):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File not found at: {pdf_path}")
    with open(pdf_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
    return pdf_bytes

def process_pdf_to_text_file(pdf_bytes, pdf_path):
    def extract_text_from_pdf(pdf_bytes):
        pdf_document = fitz.open("pdf", pdf_bytes)
        extracted_text = []
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text = page.get_text()
            extracted_text.append(text)
        return extracted_text

    def clean_text(text):
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        cleaned_text = re.sub(r'[^a-zA-Z0-9.,-]', ' ', cleaned_text)
        cleaned_text = re.sub(r'\s[a-zA-Z]\s', ' ', cleaned_text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        return cleaned_text

    def create_text_file(pdf_content, pdf_path):
        pdf_name = os.path.basename(pdf_path).split(".")[0]
        txt_file_path = os.path.join(config.TXT_FILEPATH, f"{pdf_name}.txt")
        if os.path.exists(txt_file_path):
            return pdf_name + ".txt already exists"
        
        extracted_text = extract_text_from_pdf(pdf_content)
        cleaned_texts = [clean_text(text) for text in extracted_text]
        full_cleaned_text = "\n".join(cleaned_texts)
        
        with open(txt_file_path, "w", encoding="utf-8") as f:
            f.write(full_cleaned_text)
        return "Pdf data extracted to " + pdf_name + ".txt Successfully"

    return create_text_file(pdf_bytes, pdf_path)
