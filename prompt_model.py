import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import openpyxl
import config
from datetime import datetime
import json
import get_collect
from flask import jsonify,request

def prompt_model_for_response(matched_result, query,existing_collection): 
    load_dotenv()
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_4o_MODEL = os.getenv("AZURE_OPENAI_4o_MODEL")
 
    client = AzureOpenAI(api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version=AZURE_OPENAI_API_VERSION)
    
    last_context = fetch_last_context(existing_collection)

    system_message = (
    "You are a PDF querying AI. Your task is to answer the queries."
    f"Previous context:\n{last_context}\n\n"
    " If the user asks about specific terms, such as 'Property Type,' respond with relevant content directly from the 'PDF content' without inferring unrelated information."
    " If the query involves an ID, focus on extracting the information associated with that ID."
)

    if "list" in query.lower() or "types" in query.lower():
        system_message += " Provide a detailed list where applicable."
        
    if "id" in query.lower():
        system_message += " If the user is asking for an 'ID', ensure you extract the details tied to that ID, and not just the name."

    try:
        response = client.chat.completions.create(
            model=AZURE_OPENAI_4o_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"{query}\nPDF content: {matched_result}"},
            ],
            temperature=0.8,  
            max_tokens=256,
            top_p=0.7,
            frequency_penalty=0.5
        )

        # Extracting the response content
        result = response.choices[0].message.content.strip() if response.choices else "No response generated."

        tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else "Token usage information not available."
        print(f"Tokens used for response: {tokens_used}")
        
        save_query_response_to_history(query, result,existing_collection)


    except Exception as e:
        print(f"Error in prompt_model_for_response: {e}")
        result = "Sorry, an error occurred while processing your request."

    return result

def save_query_response_to_history(query, response,existing_collection):
    history_file = os.path.join(config.HISTORY_FILEPATH, "query_response_history.json")

    if not os.path.exists(config.HISTORY_FILEPATH):
        os.makedirs(config.HISTORY_FILEPATH)
    
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            history_data = json.load(f)
    else:
        history_data = []
        
    for entry in history_data:
        if entry.get("query") == query and entry.get("collection_name") == existing_collection:
            print("Duplicate entry detected. Not adding to history.")
            return 
        
    collection_history = [entry for entry in history_data if entry.get("collection_name") == existing_collection]
    last_context = collection_history[-1].get("context", "") if collection_history else ""
    updated_context = f"{last_context}\nUser: {query}\nBot: {response}"

    query_response_entry = {
        "id": str(len(history_data) + 1),
        "collection_name": existing_collection,  
        "query": query,
        "response": response,
        "context" : updated_context,
        "timestamp": datetime.now().isoformat()
    }
    print("collection is : ", existing_collection)

    history_data.append(query_response_entry)

    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history_data, f, indent=4)

    print(f"Query and response saved to {history_file}")

def fetch_last_context(collection_name):
    history_file = os.path.join(config.HISTORY_FILEPATH, "query_response_history.json")
    
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            history_data = json.load(f)
        
        collection_history = [entry for entry in history_data if entry.get("collection_name") == collection_name]
        if collection_history:
            return collection_history[-1].get("context", "")
    
    return "No previous context available."


 
 