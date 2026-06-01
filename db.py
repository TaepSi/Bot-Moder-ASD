import os
import psycopg2

DATABASE_URL = os.environ["DATABASE_URL"]

conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True


def get_bad_words():
    with conn.cursor() as cur:
        cur.execute("SELECT word FROM bad_words")
        return [row[0] for row in cur.fetchall()]


def add_report(chat_id, reporter_id, text, reason):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO reports (chat_id, reporter_id, message_text, reason)
            VALUES (%s, %s, %s, %s)
        """, (chat_id, reporter_id, text, reason))
