import random
import sys

import db
import prompts
import config
import llm
import utils


def run_question(topic):
    messages = [
        {"role": "system", "content": prompts.SYSTEM_PROMPT},
        {"role": "user", "content": f"Тема: {topic}"}
    ]

    raw = llm.ask_model(messages, config.TEMP_QUESTION, json_mode=True)
    parsed = llm.extract_json(raw)

    if parsed is None:
        print("JSON с ошибками")
        return None

    question = parsed.get("question")
    if not question:
        print("Нет вопроса")
        print(f'{parsed}')
        return None

    key_points = llm.join_list_field(parsed, field_name="key_points")

    print(f'Тема: {topic}')
    print(question)
    print("Жду ответ, если уже не нужно напиши 'выход'")

    utils.clear_input_buffer()

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
        {"role": "system", "content": prompts.GRADER_PROMPT},
        {"role": "user", "content": f"""Тема: {topic}
      
Вопрос: {question}

Ключевые пункты по теме: {key_points}

Ответ кандидата: {user_answer}
"""
         }
    ]
    grade = llm.ask_model(grade_messages, config.TEMP_GRADING, json_mode=True)
    parsed_grade = llm.extract_json(grade)

    if parsed_grade is None:
        print("JSON с ошибками")
        return None

    covered_points = llm.join_list_field(parsed_grade, field_name="covered_points")
    missed_points = llm.join_list_field(parsed_grade, field_name="missed_points")
    grader_comment = parsed_grade.get("grader_comment")
    score_raw = parsed_grade.get("score")
    if isinstance(score_raw, int):
        score = score_raw
    else:
        try:
            score = int(score_raw)
        except (ValueError, TypeError):
            print("Неверный формат оценки")
            print(score_raw)
            return None
    if not 0 <= score <= 5:
        print("Неверный формат оценки")
        return None

    print(f'Покрытые ответы: {covered_points}')
    print(f'Пропущенные ответы: {missed_points}')
    print(f'Комментарий: {grader_comment}')
    print(f'Оценка: {score}')

    saved_db = db.save_attempt(topic,
                               question,
                               user_answer,
                               score,
                               grader_comment,
                               parsed.get("key_points"),
                               parsed_grade.get("covered_points"),
                               parsed_grade.get("missed_points")
                               )
    if not saved_db:
        print('Запись в базу не удалась, оценка при этом получена')

    return score


def main():
    topics = random.sample(prompts.TOPICS, config.QUESTIONS_PER_SESSION)
    scores = []
    for number, topic in enumerate(topics, start=1):
        print(f"Вопрос {number} из {config.QUESTIONS_PER_SESSION}")
        score = run_question(topic)
        if score is not None:
            scores.append(score)
        else:
            print("Некорректный результат")
    if not scores:
        print('Ни один вопрос не удалось провести')
    else:
        avg_score = sum(scores) / len(scores)
        print(f"Вопросов пройдено {len(scores)} из {config.QUESTIONS_PER_SESSION}")
        print(f"Средний балл: {round(avg_score, 1)}")


if __name__ == "__main__":
    main()
