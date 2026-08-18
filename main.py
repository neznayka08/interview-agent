import os
import random
import sys

import requests
from dotenv import load_dotenv

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

SYSTEM_PROMPT = """Роль. Ты технический интервьюер, проводишь собеседование на позицию middle+ инженера по NLP и LLM.
Задача. Твоя задача — задать кандидату один вопрос по указанной теме.
Ограничения:
- задай ровно один вопрос
- не отвечай на свой вопрос
- не предлагай варианты ответа
- начинай сразу с текста вопроса
- выведи только текст вопроса, без нумерации и заголовков
- пиши на русском языке
Уровень. Вопрос должен соответствовать уровню middle+: не определение термина, а вопрос на понимание и применение."""

TOPICS = ["эмбеддинги", "RAG", "метрики классификации", "system design", "pyspark", "CV", "NLP", "Classic ML"]
TEMP_QUESTION = 0.7
TEMP_GRADING = 0.7

topic = random.choice(TOPICS)

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": f"Тема: {topic}"}
]


def ask_model(messages_list, temperature=0.7):
    payload = {
        "model": MODEL_NAME,
        "messages": messages_list,
        "temperature": temperature
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
    except requests.exceptions.ConnectionError as e:
        print(f'{e}\nОлама не доступна проверь запущена ли она')
        sys.exit(1)

    if response.status_code != 200:
        print(response.text)
        sys.exit(1)

    data = response.json()
    # print(data)
    return data['choices'][0]['message']['content']


question = ask_model(messages, TEMP_QUESTION)
print(f'Тема: {topic}')
print(question)
