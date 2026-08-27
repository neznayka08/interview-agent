import json
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
- пиши на русском языке
- не пиши двойные кавычки внутри текста вопроса
Уровень. Вопрос должен соответствовать уровню middle+: не определение термина, а вопрос на понимание и применение.
Формат ответа. Верни СТРОГО JSON такой структуры:
{
  "question": "текст вопроса",
  "key_points": ["первый пункт", "второй пункт", "третий пункт"]
}
question - сам вопрос
key_points - верни список 3-5 ключевых пунктов, которые должен затронуть хороший ответ. Конкретные технические аспекты, а не «преимущества» и «основные компоненты»
Не оборачивай в markdown, не пиши ничего до и после."""

GRADER_PROMPT = """Роль. Ты технический эксперт, проверяешь ответ кандидата на позицию middle+ по NLP и LLM.
Задача. Оценить фактическую корректность и полноту ответа. Вместе с вопросом даётся список ключевых пунктов, которые должен затронуть полный ответ, и оценивать надо именно покрытие этих пунктов.
Как засчитывать пункт. Смысл: пункт считается покрытым, если кандидат передал его суть — своими словами, другими терминами, в свёрнутом виде. Дословное совпадение не требуется. Отдельно: если кандидат сказал что-то верное, чего в списке нет, — это не ошибка, а плюс.
Шкала оценивания:
0 — не покрыт ни один, или ответ не по теме
1 — покрыт один пункт из списка
2 — покрыто два пункта, но меньше половины
3 — покрыта примерно половина
4 — покрыты все существенные, упущено второстепенное
5 — покрыты все пункты
Фактическая ошибка снижает балл независимо от покрытия.
Фактическая ошибка — это неверное утверждение в ответе; отсутствие информации ошибкой не считается и учитывается только в покрытии.
Ограничения:
- Не хвалить авансом.
- Называть конкретные пробелы, а не общие слова.
- Оценивать существо, а не грамотность и объём.
- Писать по-русски.
- Не снижать балл за краткость, если суть передана — это устный ответ, а не статья.
- Не снижать балл за формулировку, отличную от твоей.
- Не выдумывать требований, которых нет в списке ключевых пунктов.
Формат ответа. Верни СТРОГО JSON такой структуры:
{
  "covered_points": ["первый пункт которые покрыл", "второй пункт которые покрыл", "третий пункт которые покрыл"],
  "missed_points": ["первый пункт которые упустил", "второй пункт которые упустил", "третий пункт которые упустил"],
  "comment": "текст комментария",
  "score": 0
}
covered_points - пункты которые кандидат покрыл
missed_points - пункты которые кандидат упустил
comment - краткий комментарий, одно-два предложения а счет ответа
score - целое число от 0 до 5, без кавычек, без диапазона.
Не оборачивай в markdown, не пиши ничего до и после."""

TOPICS = ["эмбеддинги", "RAG", "метрики классификации", "system design", "pyspark", "CV", "NLP", "Classic ML"]
TEMP_QUESTION = 0.7
TEMP_GRADING = 0.1

topic = random.choice(TOPICS)


messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": f"Тема: {topic}"}
]


def ask_model(messages_list, temperature=0.7, json_mode=False):
    payload = {
        "model": MODEL_NAME,
        "messages": messages_list,
        "temperature": temperature
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

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

raw = ask_model(messages, TEMP_QUESTION, json_mode=True)
start = raw.find("{")
end = raw.rfind("}")

if start == -1 or end == -1:
    print("JSON в ответе нет")
    print(f'{raw}')
    sys.exit(1)

cleaned = raw[start:end + 1]

try:
    parsed = json.loads(cleaned)
except json.JSONDecodeError as j:
    print(f"{cleaned}")
    print(f"{j}")
    sys.exit(1)

question = parsed.get("question")
if not question:
    print("Нет вопроса")
    print(f'{parsed}')
    sys.exit(1)

key_points_raw = parsed.get("key_points", [])
if not isinstance(key_points_raw, list):
    print("Ключевые пункты пришли в неверном формате")
    key_points = ""
else:
    key_points = ", ".join(key_points_raw)

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

Ключевые пункты по теме: {key_points}

Ответ кандидата: {user_answer}
"""
}
]
grade = ask_model(grade_messages, TEMP_GRADING, json_mode=True)
print(grade)