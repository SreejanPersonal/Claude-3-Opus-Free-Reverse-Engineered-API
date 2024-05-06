# Claude-3-Opus-Free-Reverse-Engineered-API
# ======================================
# Author: Devs Do Code (Sree)
# Description: Free and unlimited API interface to Claude 3 Opus and other AI models.
# Features: Free and unlimited, Reverse-engineered, 10+ AI models available, including Claude 3 Opus
# License: MIT License
# Contributing: Fork and submit a pull request to contribute.

import json
import random
import re
import requests
import json

def load_api_info():
    with open("Theb_API.json", "r") as file:
        return json.load(file)
    
def remove_apis():
    with open("Theb_API.json", "r") as file:
        data = json.load(file)
    if data: data.pop(0)
    with open("Theb_API.json", "w") as file:
        json.dump(data, file, indent=4)

def initiate_api_conversation(input_text: str, model_identifier: str = 'Claude-3-Opus', organization_id: str = load_api_info()[0]['ORGANIZATION_ID'], access_token: str = load_api_info()[0]['API_KEY']) -> str:
    """
    Initiates an API conversation request and retrieves the response content.

    Parameters:
    - organization_id (str): The unique identifier for the API organization.
    - model_identifier (str): The identifier for the desired conversation model.
    - input_text (str): The textual input for initiating the conversation.

    Returns:
    - str: The textual content of the API response.

    Note:
    - The model_identifier should correspond to one of the predefined model keys.
    """

    # Mapping of model identifiers to their respective keys
    model_key_mapping = {
        'Claude-3-Opus' : 'ade084104e614c31ada6892744fcd3c5',
        'Claude-3-Haiku' : "d2c2b37c042d4b248af62a033eccd1b2",
        'Claude-3-Sonnet' : "8b851ff081d54ba7b46a42a5099fcc64",
        'Claude 2': 'a248a40fe3c4493598064c9ba725e8c9',

        'llama-3-70b': '5da08fc7ac704d0d9bee545cbbb91793',
        'llama-3-8b': 'c60d009ce85f47f087952f17eead4eab',
        'cod-llama-70b': 'bccdb1b4dee94dc59d6e15e2a73ac2ba',

        'mistral 8x22b': '70b3f32d71a34b97af9d660e1245fe15',
        'WizardLM 2 8x22B' : 'ebf8820be60f40a38a3cae32795f8bd2',

        'chatgpt-3-5-turbo': '58f5e7e50fee4779a1e5fe16c3aa302b',
        'dbrx': '20ea474d42dd44eaa618971cdb16bfa7',
        'Theb-ai': '7e682da4dde7ee214baa0efc0cf6d7a4',
        
    }

    # API endpoint construction
    api_endpoint = f"https://beta.theb.ai/api/conversation?org_id={organization_id}&req_rand={random.random()}"

    # HTTP request headers
    request_headers = {
        "Authorization": f"Bearer {access_token}",
    }

    # HTTP request payload
    request_payload = {
        "text": input_text,
        "model": model_key_mapping[model_identifier],
        "functions": None,
        "attachments": [],
        "model_params": {
            "system_prompt": "Be Helpful and Friendly",
            "temperature": "1",
            "top_p": "1",
            "frequency_penalty": "0",
            "presence_penalty": "0",
            "long_term_memory": "ltm"
        },
    }

    # Execution of the API request
    payload_as_json = json.dumps(request_payload)
    response = requests.post(api_endpoint, headers=request_headers, data=payload_as_json, stream=True)
    if response.status_code == 200:
        accumulated_response_text = ""
        for line in response.iter_lines(decode_unicode=True, chunk_size=1, delimiter="\n"):
            if line and "event: " not in line:
                line_content = re.sub("data:", "", line)
                try:
                    response_data = json.loads(line_content)
                    if 'tid' in response_data: continue
                    print(response_data['args']['content'].replace(accumulated_response_text, ''), end="")
                    accumulated_response_text = response_data['args']['content']
                except json.JSONDecodeError:
                    continue

        
        if accumulated_response_text != "": return accumulated_response_text
        else : 
            resp_lines = response.text.split("\r")
            for line in reversed(resp_lines):
                if "event: " not in line and line.strip():
                    try:
                        data_value = re.sub("data:", "", line)
                        json_data = json.loads(data_value)
                        return json_data['args']['content']
                    except Exception as e:
                        continue
            
    elif response.status_code == 400:
        print("\033[91m" + f"Switching to Next API " + "\033[0m")
        remove_apis()
        return initiate_api_conversation(input_text=input_text, model_identifier=model_identifier, organization_id= load_api_info()[0]['ORGANIZATION_ID'], access_token = load_api_info()[0]['API_KEY'])


if __name__ == "__main__":
    print(f"\033[91mIt is worth noting that, when running in a Jupyter notebook environment, the code output may appear to be faster compared to a regular Python script. This discrepancy in performance has not been fully understood, but it is possible that contributing to resolving this issue could be beneficial. Additionally, the website that has been reverse engineered for this API interaction has been observed to be slow in terms of response time. Therefore, it is to be expected that the API responses will also be slower in comparison. It is suggested to use smaller models, such as 'llama-3-8b', to improve the responsiveness of the API interaction. Furthermore, it should be noted that the underlying website does not support fast API inference, resulting in slower responses\n\n\033[92m1This will be printed on every command. It is recommended that you remove this print statement for not getting irritated\033[0m")
    response_content = initiate_api_conversation(input_text="Write 30 Lines about India ")
    # response_content = initiate_api_conversation(input_text="Can you please provide information about your development team, including the company or organization that created you, the names of your creators or lead developers, the programming languages and frameworks used to build you, and any notable features or technologies that enable your conversational capabilities?", model_identifier="Claude-3-Sonnet")
    # print("\n\n\n" + response_content)