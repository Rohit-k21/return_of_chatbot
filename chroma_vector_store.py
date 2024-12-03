import os
import json
import chromadb
from dotenv import load_dotenv
from openai import AzureOpenAI
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings

def store_vectors_to_chroma(json_path, collection_name):
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

    try:
        collection = chroma_client.get_collection(name=collection_name)
        print(collection, "already exists.")
        return "Collection "+collection_name+" already exists"
    except Exception:
        collection = chroma_client.get_or_create_collection(name=collection_name)

    with open(json_path, 'r') as file:
        data = json.load(file)

    text_chunks = []
    for page, content in data.items():
        text_chunks.append((page, content))

    def get_embeddings(text_chunks):
        embeddings = []
        for page, chunk in text_chunks:
            response = openai_client.embeddings.create(
                input=chunk.strip(),
                model=AZURE_OPENAI_EMBEDDING_MODEL
            )
            embeddings.append({
                "text": chunk.strip(),
                "embedding": response.data[0].embedding,
                "page": page
            })
        return embeddings

    def store_embeddings_in_chroma(embeddings):
        for item in embeddings:
            collection.upsert(
                documents=[item['text']],
                embeddings=[item['embedding']],
                ids=[str(hash(item['text']))],
                metadatas=[{"page": item['page']}]
            )

    embeddings = get_embeddings(text_chunks)
    store_embeddings_in_chroma(embeddings)

    print("Embeddings stored in ChromaDB successfully.")
    return "Collection "+collection_name+" Created Successfully"
