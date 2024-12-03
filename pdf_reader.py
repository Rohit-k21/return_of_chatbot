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

def process_pdf_to_json(pdf_bytes, pdf_path):
    def extract_text_from_pdf(pdf_bytes):
        pdf_document = fitz.open("pdf", pdf_bytes)
        extracted_text = {}
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text = page.get_text()
            extracted_text[f"page_{page_num + 1}"] = text
        return extracted_text

    def clean_text(text):
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        cleaned_text = re.sub(r'[^a-zA-Z0-9.,-]', ' ', cleaned_text)
        cleaned_text = re.sub(r'\s[a-zA-Z]\s', ' ', cleaned_text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        return cleaned_text

    def create_upload_file(pdf_content, pdf_path):
        pdf_name = os.path.basename(pdf_path).split(".")[0]
        json_file_path = os.path.join(config.JSON_FILEPATH, f"{pdf_name}.json")
        if os.path.exists(json_file_path):
            return pdf_name+".json already exists"
        extracted_text = extract_text_from_pdf(pdf_content)
        clean_text_content = {}
        for page_key, text in extracted_text.items():
            cleaned_text = clean_text(text)
            clean_text_content[page_key] = cleaned_text
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(clean_text_content, f, ensure_ascii=False, indent=4)
        return "Pdf data extracted to "+pdf_name+".json Successfully"

    return create_upload_file(pdf_bytes, pdf_path)

# Example usage of the functions
# pdf_path = "./pdfs_folder/file.pdf"
# pdf_bytes = read_pdf_as_bytes(pdf_path)
# result = process_pdf_to_json(pdf_bytes, pdf_path)
# print(result)