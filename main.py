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

GRADER_PROMPT = """Роль. Ты Технический эксперт, проверяешь ответ кандидата на позицию middle+ по NLP и LLM.
Задача. Оценить фактическую корректность и полноту ответа.
Шкала оценивания:
0 — неверно или не по теме
1–2 — есть верные элементы, но принципиальные пробелы
3 — базово верно, поверхностно
4 — верно и полно
5 — верно, полно, с пониманием нюансов и ограничений
Порядок вывода. Разберись, что верно и что упущено, и только потом выставляй балл.
Ограничения:
- Не хвалить авансом.
- Называть конкретные пробелы, а не общие слова.
- Оценивать существо, а не грамотность и объём.
- Писать по-русски."""

TOPICS = ["эмбеддинги", "RAG", "метрики классификации", "system design", "pyspark", "CV", "NLP", "Classic ML"]

TEMP_QUESTION = 0.7
TEMP_GRADING = 0.1

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

print("Жду ответ, если уже не нужно напиши 'выход'")
while True:
    user_answer = input("Ответ: ").strip()
    if user_answer.lower() in ["exit", "quit", "выход"]:
        print('пока')
        sys.exit(0)
    if not user_answer:
        print('Ответ не может быть пустым')
    else:
        break

grade_messages = [
    {"role": "system", "content": GRADER_PROMPT},
    {"role": "user", "content": f"""Тема: {topic}
  
Вопрос: {question}

Ответ кандидата: {user_answer}
"""
}
]
grade = ask_model(grade_messages, TEMP_GRADING)
print(grade)