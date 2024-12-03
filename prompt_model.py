import os
from dotenv import load_dotenv
from openai import AzureOpenAI

def prompt_model_for_response(matched_result, query): 
    load_dotenv()
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_4o_MODEL = os.getenv("AZURE_OPENAI_4o_MODEL")
 
    client = AzureOpenAI(api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version=AZURE_OPENAI_API_VERSION)

 
    
    response = client.chat.completions.create(
        model=AZURE_OPENAI_4o_MODEL,
        messages=[
            {"role": "system", "content": "You are a pdf querying AI. Based on the user prompt and the most related content of the pdf attached, you should be able to answer the user's questions."},
            {"role": "user", "content": f"{query}\n pdf content: {matched_result}"},
        ],
        temperature=0.7,
        max_tokens=256,
        top_p=0.6,
        frequency_penalty=0.7
    )

    result = response.choices[0].message.content.strip()
    return result
 
 