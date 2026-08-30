import json
import sys

import requests

import config


def ask_model(messages_list, temperature=0.7, json_mode=False):
    payload = {
        "model": config.MODEL_NAME,
        "messages": messages_list,
        "temperature": temperature
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    try:
        response = requests.post(config.OLLAMA_CHAT_URL, json=payload, timeout=120)
    except requests.exceptions.ConnectionError as e:
        print(f'{e}\nОлама не доступна проверь запущена ли она')
        sys.exit(1)

    if response.status_code != 200:
        print(response.text)
        sys.exit(1)

    data = response.json()
    # print(data)
    return data['choices'][0]['message']['content']


def extract_json(text: str):
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        print("JSON в ответе нет")
        print(f'{text}')
        return None

    cleaned = text[start:end + 1]

    try:
        pars = json.loads(cleaned)
    except json.JSONDecodeError as j:
        print(f"{cleaned}")
        print(f"{j}")
        return None
    return pars


def join_list_field(data, field_name):
    field_name_raw = data.get(field_name, [])
    if not isinstance(field_name_raw, list):
        print(f"поле {field_name} пришло в неверном формате")
        print(field_name_raw)
        factor = ""
    else:
        factor = ", ".join(field_name_raw)
    return factor
