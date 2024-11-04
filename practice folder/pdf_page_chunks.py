import re
import os
import json
import fitz


def read_pdf_as_bytes(pdf_path):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File not found at: {pdf_path}")
    with open(pdf_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
    return pdf_bytes

def process_pdf_to_json(pdf_bytes, pdf_path, max_words_per_chunk=50):
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
        cleaned_text = re.sub(r'[^a-zA-Z0-9.,-]', ' ', cleaned_text)
        cleaned_text = re.sub(r'\s[a-zA-Z]\s', ' ', cleaned_text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        return cleaned_text

    def chunk_text(text, max_words):
        """Chunk the text into smaller segments based on word count."""
        words = text.split()
        chunks = []
        current_chunk = []

        for word in words:
            current_chunk.append(word)
            # If current chunk exceeds max words, finalize it
            if len(current_chunk) >= max_words:
                chunks.append(' '.join(current_chunk))
                current_chunk = []

        # Add any remaining words as a final chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def create_upload_file(pdf_content, pdf_path):
        # Create a unique ID for the PDF file
        pdf_name = os.path.basename(pdf_path).split(".")[0]
       
        # Extract text from the PDF
        extracted_text = extract_text_from_pdf(pdf_content)
        clean_text_content = {"pdf_content": {}}

        # Store each page's cleaned text as a key-value pair
        for page_key, text in extracted_text.items():
            cleaned_text = clean_text(text)
            chunks = chunk_text(cleaned_text, max_words_per_chunk)
            for idx, chunk in enumerate(chunks):
                clean_text_content["pdf_content"][f"{page_key}.{idx + 1}"] = chunk

        # Save the cleaned text as a JSON file
        with open(f"{pdf_name}.json", "w", encoding="utf-8") as f:
            json.dump(clean_text_content, f, ensure_ascii=False, indent=4)

        return {
            "chat_id": pdf_name,
            "message": "PDF content processed and stored successfully."
        }
   
    # Process the PDF file
    return create_upload_file(pdf_bytes, pdf_path)

 
# Example usage of the functions
pdf_path = "Filed.pdf"
pdf_bytes = read_pdf_as_bytes(pdf_path)
result = process_pdf_to_json(pdf_bytes, pdf_path)
print("result")