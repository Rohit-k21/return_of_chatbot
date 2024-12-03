import os
import config
import pdf_reader
import prompt_model
import chroma_vector_store
import chroma_vector_query
from flask_cors import CORS
from flask import Flask, request, jsonify
import get_collect
import json
import config
from prompt_model import fetch_last_context

app = Flask(__name__)
CORS(app)

existing_collection= ''
# Define the folder and file path
history_folder = 'history_file'  # Folder where history files are stored
history_filename = 'query_response_history.json'  # Name of the history file
history_file_path = os.path.join(history_folder, history_filename)

@app.route('/test')
def test():
    print("Test connection successful")
    return "Test connection successful"

@app.route('/pdf_upload', methods=['POST'])
def upload_and_store():
    global existing_collection
    if 'file' not in request.files:
        return jsonify(status=400, message="No file part in the request")

    file = request.files['file']
    file_name = file.filename
    file_name = file_name.split(".")[0]
    existing_collection = file_name

    if file_name == '':
        return jsonify(status=400, message="No selected file")

    try:
        pdf_path = os.path.join(config.PDF_FILEPATH, file_name)
        file.save(pdf_path)

        pdf_bytes = pdf_reader.read_pdf_as_bytes(pdf_path)
        result = pdf_reader.process_pdf_to_json(pdf_bytes, pdf_path)

        json_path = os.path.join(config.JSON_FILEPATH, f"{os.path.splitext(file_name)[0]}.json")

        try:
            if not os.path.exists(json_path):
                return jsonify(status=404, message="JSON file does not exist at the expected path")

            embedding_result = chroma_vector_store.store_vectors_to_chroma(json_path, file_name)

            return jsonify(status=200, message={
                "pdf_processing": result,
                "vector_embedding": embedding_result
            })

        except Exception as embed_error:
            return jsonify(status=500, message='Error while embedding vectors: ' + str(embed_error))

    except Exception as pdf_error:
        return jsonify(status=500, message='Encountered Error while processing PDF: ' + str(pdf_error))

@app.route('/get_collection', methods=['GET'])
def get_collection_name():
    collections_list = get_collect.list_collections()
    return jsonify(collections_list)

@app.route('/set_collection', methods=['POST'])
def set_collection_name():
    global existing_collection
    existing_collection = request.json.get('collection_name')
    return jsonify(collection_name=existing_collection)

@app.route('/prompt_query', methods=['POST'])
def prompt_vectors_query():
    
    query = request.json.get("query")
    if not query:
        return jsonify(status=404, message="Query is not available")
    
    try:
        # matched_result, page_numbers = chroma_vector_query.query_similar_content(existing_collection, query)
        matched_result = chroma_vector_query.query_similar_content(existing_collection, query)
        # print(matched_result, "page", page_numbers)
        response = prompt_model.prompt_model_for_response(matched_result, query,existing_collection)
        # return jsonify(collection=existing_collection, page_numbers=page_numbers, model_response=response)
        return jsonify(collection=existing_collection, model_response=response)
    except Exception as e:
        return jsonify(status=500, message='Error while querying the vectors and prompting the model', error=str(e))

@app.route('/get_query_history', methods=['GET'])
def get_query_history():
    try:
        # Check if the history file exists
        if not os.path.exists(history_file_path):
            return jsonify(status=404, message="No query history found")

        # Load the query history from the JSON file
        with open(history_file_path, 'r') as file:
            history = json.load(file)

        # Get the collection_name parameter from the request
        collection_name = request.args.get('collection')
        print("collection is :", collection_name)

        # If a collection name is provided, filter history based on it
        if collection_name:
            filtered_history = [
                item for item in history if item.get('collection_name') == collection_name
            ]
            return jsonify(status=200, history=filtered_history)

        # If no collection_name is provided, return all history
        return jsonify(status=200, history=history)

    except Exception as e:
        return jsonify(status=500, message=f"Error while fetching query history: {str(e)}")

@app.route('/get_last_context', methods=['GET'])
def get_last_context():
    # Get the collection name from the request arguments
    collection_name = request.args.get('collection_name')
    if not collection_name:
        return jsonify({"error": "Collection name is required"}), 400

    # Fetch the last context for the specified collection
    last_context = fetch_last_context(collection_name)

    # Return the context as JSON
    return jsonify({"context": last_context})


if __name__ == '__main__':
    app.run(port=5001)
    # app.run(host="0.0.0.0", port=int("1998"), debug=False)
