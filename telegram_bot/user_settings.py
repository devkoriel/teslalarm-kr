import json

import psycopg2

from config import DATABASE_URL
from utils.logger import setup_logger

logger = setup_logger()


def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


def initialize_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id BIGINT PRIMARY KEY,
            preferred_lang VARCHAR(5) DEFAULT 'ko',
            keywords JSON DEFAULT '[]',
            notify_times JSON DEFAULT '[]',
            notify_frequency INTEGER DEFAULT 1
        );
        """
    )
    conn.commit()
    cur.close()
    conn.close()


def set_user_language(user_id, lang_code):
    initialize_table()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO user_settings (user_id, preferred_lang)
        VALUES (%s, %s)
        ON CONFLICT (user_id) DO UPDATE SET preferred_lang = %s;
        """,
        (user_id, lang_code, lang_code),
    )
    conn.commit()
    cur.close()
    conn.close()
    return True


def get_user_language(user_id):
    initialize_table()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT preferred_lang FROM user_settings WHERE user_id = %s;", (user_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] if result else "ko"


def set_user_keywords(user_id, keywords: list):
    initialize_table()
    conn = get_db_connection()
    cur = conn.cursor()
    keywords_json = json.dumps(keywords)
    cur.execute(
        """
        INSERT INTO user_settings (user_id, keywords)
        VALUES (%s, %s)
        ON CONFLICT (user_id) DO UPDATE SET keywords = %s;
        """,
        (user_id, keywords_json, keywords_json),
    )
    conn.commit()
    cur.close()
    conn.close()
    return True


def get_user_keywords(user_id):
    initialize_table()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT keywords FROM user_settings WHERE user_id = %s;", (user_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    try:
        return json.loads(result[0]) if result and result[0] else []
    except Exception as e:
        logger.error(f"키워드 파싱 오류: {e}")
        return []


def get_all_user_settings():
    """모든 사용자 설정을 가져오는 함수 (user_id, preferred_lang, keywords)."""
    initialize_table()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id, preferred_lang, keywords FROM user_settings;")
    results = cur.fetchall()
    cur.close()
    conn.close()
    users = []
    for user_id, preferred_lang, keywords_json in results:
        try:
            keywords = json.loads(keywords_json) if keywords_json else []
        except Exception as e:
            logger.error(f"키워드 파싱 오류: {e}")
            keywords = []
        users.append({"user_id": user_id, "language": preferred_lang, "keywords": keywords})
    return users
