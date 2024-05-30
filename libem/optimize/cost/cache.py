import os
import json
import requests

URL = "https://raw.githubusercontent.com/BerriAI/" \
      "litellm/main/model_prices_and_context_window.json"
DIR_PATH = os.path.join(os.path.dirname(__file__))
PRICE_FILE_PATH = os.path.join(DIR_PATH, 'price.json')


def refresh_price_cache():
    fetch_price_info()
    cache_openai()


def fetch_price_info():
    try:
        response = requests.get(URL)
        response.raise_for_status()
        with open(PRICE_FILE_PATH, 'w') as f:
            f.write(response.text)
    except requests.RequestException as e:
        print(f"An error occurred: {e}")


def load_price_info():
    try:
        with open(PRICE_FILE_PATH, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"{PRICE_FILE_PATH} not found. Please check the filepath.")
    except json.JSONDecodeError:
        print(f"Error decoding {PRICE_FILE_PATH}. Please check the file content.")


"""OpenAI specific info"""
OPENAI_FILE_PATH = os.path.join(DIR_PATH, 'openai.json')


def cache_openai():
    price_info = load_price_info()
    prefixes = {'gpt', 'text-embedding', 'whisper'}
    openai_price_info = {name: details for name, details in price_info.items()
                         if any(name.startswith(prefix) for prefix in prefixes)}

    with open(OPENAI_FILE_PATH, 'w') as f:
        json.dump(openai_price_info, f, indent=4)

def load_openai():
    try:
        with open(OPENAI_FILE_PATH, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"{OPENAI_FILE_PATH} not found. Please check the filepath.")
    except json.JSONDecodeError:
        print(f"Error decoding {OPENAI_FILE_PATH}. Please check the file content.")
