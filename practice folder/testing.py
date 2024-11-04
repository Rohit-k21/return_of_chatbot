import os
import chromadb
from dotenv import load_dotenv
from openai import AzureOpenAI
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings

def query_similar_content(existing_collection, query):
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

    # Get the existing collection
    try:
        collection = chroma_client.get_collection(name=existing_collection)
    except Exception as e:
        print(f"Error retrieving collection: {e}")
        return None, []

    # Query embeddings
    def query_embedding(query_text):
        # Get embedding for the query text
        response = openai_client.embeddings.create(
            input=query_text,
            model=AZURE_OPENAI_EMBEDDING_MODEL
        )
        query_vector = response.data[0].embedding

        # Query the collection for similar embeddings
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=1  # Adjust number of results as needed
        )

        return results

    # Perform the query
    query_results = query_embedding(query)

    # Check if there are any results
    if not query_results['documents']:
        print("No matching documents found.")
        return None, []

    # Extract results and page numbers
    matched_result = query_results['documents'][0]
    # page_numbers = [meta['page'] for meta in query_results['metadatas'][0]]

    # print(matched_result, "page", page_numbers)
    print(matched_result)
    return matched_result, #page_numbers

# Example call
# documents, page_numbers = query_similar_content('file', 'What is the Total comprehensive income?')
query_similar_content("disclosure_embeddings", "What is the max len of L-001?")
# print(documents, page_numbers)
