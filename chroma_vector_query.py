import os
import chromadb
from dotenv import load_dotenv
from openai import AzureOpenAI
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings
import openpyxl
from datetime import datetime

def query_similar_content(existing_collection, query):
    load_dotenv()
    AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_EMBEDDING_MODEL = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL")
 
    openai_client = AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT
    )

    chroma_client = chromadb.PersistentClient(
        path="chroma_store",
        settings=Settings(),
        tenant=DEFAULT_TENANT,
        database=DEFAULT_DATABASE,
    )
    collection = chroma_client.get_collection(name=existing_collection)

    def query_embedding(query_text):
        response = openai_client.embeddings.create(
            input=query_text,
            model=AZURE_OPENAI_EMBEDDING_MODEL
        )
        query_vector = response.data[0].embedding

        results = collection.query(
            query_embeddings=[query_vector],
            n_results=1  
        )
    
        return results

    query_results = query_embedding(query)

    matched_result = query_results['documents'][0]
    page_numbers = [meta['page'] for meta in query_results['metadatas'][0]]
    matched_result = ''.join(matched_result)
    page_numbers = ', '.join(map(str, page_numbers))  

    print(f"Matched Result: {matched_result}, Page Numbers: {page_numbers}")

    store_responses_to_excel([
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "collection": existing_collection,
            "query": query,
            "model_response": matched_result,
            "page_numbers": page_numbers
        }
    ])

    return matched_result, page_numbers


def store_responses_to_excel(responses):
    excel_file_path = 'llm_responses.xlsx'

    if not os.path.exists(excel_file_path):
        wb = openpyxl.Workbook()
        sheet = wb.active
        sheet.title = "LLM Responses"
        sheet.append(["Timestamp", "Collection Name", "Query", "Model Response", "Page Numbers"])  
    else:
        wb = openpyxl.load_workbook(excel_file_path)
        sheet = wb.active

    for response in responses:
        timestamp = response["timestamp"]
        collection_name = response["collection"]
        query = response["query"]
        model_response = response["model_response"]
        page_numbers = response["page_numbers"]

        sheet.append([timestamp, collection_name, query, model_response, page_numbers])

    wb.save(excel_file_path)
    print(f"Responses successfully saved to {excel_file_path}")


# Example call (make sure to provide an existing collection name)
# documents, page_numbers = query_similar_content('file', 'What is the Total comprehensive income?')
