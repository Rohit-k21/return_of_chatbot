import os
import chromadb
from dotenv import load_dotenv
from openai import AzureOpenAI
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings
import openpyxl
from datetime import datetime
import tiktoken

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

def query_similar_content(existing_collection, query):
    
    print(existing_collection ,query)
    collection = chroma_client.get_collection(name=existing_collection)

    def query_embedding(query_text):
        try:
            response = openai_client.embeddings.create(
                input=query_text,
                model=AZURE_OPENAI_EMBEDDING_MODEL
            )
            query_vector = response.data[0].embedding

            results = collection.query(
                query_embeddings=[query_vector],
                n_results=3  
            )
        except Exception as e:            
            print(e)
        # print("----------------------/---------------------->",results)
        return results

    query_results = query_embedding(query)

    matched_result = query_results['documents'][0]
    matched_result = ''.join(matched_result)
    return matched_result

# Example call (make sure to provide an existing collection name)
# documents, page_numbers = query_similar_content('file', 'What is the Total comprehensive income?')
