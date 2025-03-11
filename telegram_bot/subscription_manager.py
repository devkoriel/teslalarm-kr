import threading

from config import DATABASE_URL

# This module uses PostgreSQL to store subscription data.
# Table: subscriptions(user_id TEXT, keyword TEXT)
# (Table creation is handled on first subscription)

subscriptions_lock = threading.Lock()


def get_db_connection():
    import psycopg2

    return psycopg2.connect(DATABASE_URL)


def add_subscription(user_id, keyword):
    with subscriptions_lock:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS subscriptions (
                user_id TEXT,
                keyword TEXT,
                PRIMARY KEY (user_id, keyword)
            )
        """
        )
        cur.execute(
            """
            INSERT INTO subscriptions (user_id, keyword)
            VALUES (%s, %s)
            ON CONFLICT (user_id, keyword) DO NOTHING
        """,
            (str(user_id), keyword.lower()),
        )
        conn.commit()
        cur.close()
        conn.close()


def remove_subscription(user_id, keyword):
    with subscriptions_lock:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM subscriptions WHERE user_id = %s AND keyword = %s",
            (str(user_id), keyword.lower()),
        )
        conn.commit()
        cur.close()
        conn.close()


def list_subscriptions(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT keyword FROM subscriptions WHERE user_id = %s", (str(user_id),))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [row[0] for row in rows]
