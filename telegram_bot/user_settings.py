import psycopg2

from config import DATABASE_URL


def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


def set_user_language(user_id, lang_code):
    """
    사용자의 언어 설정('ko' 또는 'en')을 데이터베이스에 저장.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id BIGINT PRIMARY KEY,
            preferred_lang VARCHAR(5)
        );
    """
    )
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
    """
    사용자의 선호 언어를 조회. 기본값은 'ko'.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT preferred_lang FROM user_settings WHERE user_id = %s;", (user_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] if result else "ko"
