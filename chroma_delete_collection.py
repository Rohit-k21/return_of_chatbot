import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings

chroma_client = chromadb.PersistentClient(
    path="chroma_store",
    settings=Settings(),
    tenant=DEFAULT_TENANT,
    database=DEFAULT_DATABASE,
)

def delete_collection(collection_name):
    """Delete a collection from ChromaDB."""
    try:
        chroma_client.delete_collection(name=collection_name)
        print(f"Collection '{collection_name}' deleted successfully.")
    except Exception as e:
        print(f"Error deleting collection '{collection_name}': {e}")

delete_collection("disclosure_guide")
