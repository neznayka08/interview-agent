import os
import sys

from dotenv import load_dotenv
import requests

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
if not OLLAMA_BASE_URL:
    print("переменная OLLAMA_BASE_URL не задана, проверь файл .env")
    sys.exit(1)
print(f"Base URL: {OLLAMA_BASE_URL}")

MODEL_NAME = os.getenv("MODEL_NAME")
if not MODEL_NAME:
    print("переменная MODEL_NAME не задана, проверь файл .env")
    sys.exit(1)
print(f"Model Name: {MODEL_NAME}")

url = f"{OLLAMA_BASE_URL}/v1/chat/completions"

payload = {
    "model": MODEL_NAME,
    "messages": [
        {"role": "user", "content": "привет"}
    ]
}

try :
    response = requests.post(url, json=payload, timeout=120)
except requests.exceptions.ConnectionError:
    print('Олама не доступна проверь запущена ли она')
    sys.exit(1)

print(response.status_code)
if response.status_code != 200:
    print(response.text)
    sys.exit(1)

data = response.json()
#print(data)
print(data['choices'][0]['message']['content'])
