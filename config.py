import os
import sys

from dotenv import load_dotenv

load_dotenv()


def get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name)
    if value:
        return value
    if default is not None:
        return default
    print(f"переменная {name} не задана, проверь файл .env")
    sys.exit(1)


OLLAMA_BASE_URL = get_env(name='OLLAMA_BASE_URL', default="http://localhost:11434")
MODEL_NAME = get_env(name='MODEL_NAME')
OLLAMA_CHAT_URL = f"{OLLAMA_BASE_URL}/v1/chat/completions"
PG_HOST = get_env(name='PG_HOST', default="localhost")
PG_PORT = get_env(name='PG_PORT', default="5432")
PG_DB_NAME = get_env(name='PG_DB_NAME')
PG_USER = get_env(name='PG_USER')
PG_PASSWORD = get_env(name='PG_PASSWORD')
print(f"Конфигурация: модель {MODEL_NAME}, Ollama {OLLAMA_BASE_URL}, база {PG_DB_NAME} на {PG_HOST}:{PG_PORT}")

TEMP_QUESTION = 0.7
TEMP_GRADING = 0.1

QUESTIONS_PER_SESSION = 2