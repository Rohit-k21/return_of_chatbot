import shortuuid
import re
import fitz
import json

def process_pdf_to_json(pdf_bytes):
    def extract_text_from_pdf(pdf_bytes):
        # Open the PDF from bytes
        pdf_document = fitz.open("pdf", pdf_bytes)
        extracted_text = {}

        # Iterate through each page and extract text
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text = page.get_text()
            extracted_text[f"page_{page_num + 1}"] = text

        return extracted_text

    def clean_text(text):
        # Remove extra spaces and line breaks
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        # cleaned_text = re.sub(r'\b[a-zA-Z]\b', '', cleaned_text)
        cleaned_text = re.sub(r'[^a-zA-Z0-9.,-]', ' ', cleaned_text)
        cleaned_text = re.sub(r'\s[a-zA-Z]\s', ' ', cleaned_text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        return cleaned_text

    def create_upload_file(pdf_content):
        # Save the uploaded file to the server or process it directly
        pdf_chat_id = str(shortuuid.uuid())
        contents = pdf_content
        extracted_text = extract_text_from_pdf(contents)
        
        clean_text_content = {"pdf-content":{}}
        
        # Store each page's text as a key-value pair
        for page_key, text in extracted_text.items():
            cleaned_text = clean_text(text)
            clean_text_content[page_key] = cleaned_text
        
        # Save the file to a specific location
        with open(f"../json_data/pdf_chat_id_{pdf_chat_id}.json", "w", encoding="utf-8") as f:
            json.dump(clean_text_content, f, ensure_ascii=False, indent=4)

        return {
            "chat_id": pdf_chat_id,
            "message": "PDF content processed and stored successfully."
        }

    return create_upload_file(pdf_bytes)

# Example usage
if __name__ == "__main__":
    # Read the PDF file as bytes
    with open("../pdfs_folder/file.pdf", "rb") as pdf_file:
        pdf_bytes = pdf_file.read()

    # Process the PDF and get the JSON content
    result = process_pdf_to_json(pdf_bytes)
    print(result)
