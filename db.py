import json

import psycopg2

import config

sql = """INSERT INTO attempts (
topic,
question,
user_answer,
score,
grader_comment,
key_points,
covered_points,
missed_points
) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""


def save_attempt(topic,
                 question,
                 user_answer,
                 score,
                 grader_comment,
                 key_points,
                 covered_points,
                 missed_points):
    values = [topic,
              question,
              user_answer,
              score,
              grader_comment,
              json.dumps(key_points),
              json.dumps(covered_points),
              json.dumps(missed_points)]
    try:
        with psycopg2.connect(host=config.PG_HOST,
                              port=config.PG_PORT,
                              user=config.PG_USER,
                              password=config.PG_PASSWORD,
                              dbname=config.PG_DB_NAME) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, values)
        return True
    except psycopg2.Error as err:
        print('запись в базу не удалась, оценка при этом получена', err)
        return False
