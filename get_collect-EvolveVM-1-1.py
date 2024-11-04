import os
from dotenv import load_dotenv
import chromadb
from openai import AzureOpenAI
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings

def list_collections():
    # Load environment variables
    load_dotenv()
    AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_EMBEDDING_MODEL = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL")
 
    # Initialize Azure OpenAI client
    openai_client = AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT
    )
    # Initialize ChromaDB client
    chroma_client = chromadb.PersistentClient(
        path="chroma_store",
        settings=Settings(),
        tenant=DEFAULT_TENANT,
        database=DEFAULT_DATABASE,
    )

    # Retrieve and print the list of collections
    collections = chroma_client.list_collections()
    print(collections)
    formatted_collections = [{'id': col.id, 'name': col.name} for col in collections]  # Adjust as needed
    return formatted_collections

# Example call to list collections
collections = list_collections()
print("Available Collections:")
for collection in collections:
    print(collection)
