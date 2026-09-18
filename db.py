import json

import psycopg2

import config

INSERT_SQL = """INSERT INTO attempts (
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

STATS_SQL = """
SELECT topic, AVG(score) AS avg_score, COUNT(*) AS cnt
FROM attempts
GROUP BY topic
ORDER BY avg_score
"""

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
                cur.execute(INSERT_SQL, values)
        return True
    except psycopg2.Error as err:
        print('запись в базу не удалась, оценка при этом получена', err)
        return False


def get_topic_stats():
    try:
        with psycopg2.connect(host=config.PG_HOST,
                              port=config.PG_PORT,
                              user=config.PG_USER,
                              password=config.PG_PASSWORD,
                              dbname=config.PG_DB_NAME) as conn:
            with conn.cursor() as cur:
                cur.execute(STATS_SQL)
                rows = cur.fetchall()
            stats = {}
            for topic, avg_score, cnt in rows:
                stats[topic] = float(avg_score)
        return stats
    except psycopg2.Error as err:
        print('чтение в базы не удалась', err)
        return {}


if __name__ == "__main__":
    stats = get_topic_stats()
    print(stats)