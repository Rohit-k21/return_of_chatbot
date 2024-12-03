import os
import config
import pdf_reader
import prompt_model
import chroma_vector_store
import chroma_vector_query
import get_collect
from flask_cors import CORS
from flask import Flask, request, jsonify
 
app = Flask(__name__)
CORS(app)

existing_collection= ''

@app.route('/test')
def test():
    print("Test connection successful")
    return "Test connection successful"

@app.route('/pdf_upload', methods=['POST'])
def upload_and_store():
    global existing_collection
    if 'pdf' not in request.files:
        return jsonify(status=400, message="No file part in the request")

    file = request.files['pdf']
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

@app.route('/set_collection', methods=['POST'])
def set_collection_name():
    global existing_collection
    existing_collection = request.json.get('collection_name')
    print(existing_collection)
    return jsonify(existing_collection)

@app.route('/get_collection', methods=['GET'])
def get_collection_name():
    res = get_collect.list_collections()
    return jsonify(res)

@app.route('/prompt_query', methods=['POST'])
def prompt_vectors_query():
    query = request.json.get("query")
    if not query:
        return jsonify(status=404, message="Query is not available")
    
    try:
        matched_result, page_numbers = chroma_vector_query.query_similar_content(existing_collection, query)
        print("FROM APP.PY...", matched_result, "page", page_numbers)
        response = prompt_model.prompt_model_for_response(matched_result, query)
        return jsonify(collection=existing_collection, page_numbers=page_numbers, model_response=response)
    except Exception as e:
        return jsonify(status=500, message='Error while querying the vectors and prompting the model', error=str(e))

if __name__ == '__main__':
    app.run()
    # app.run(host="0.0.0.0", port=int("1999"), debug=False)
