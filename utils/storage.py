import hashlib

import psycopg2

from config import DATABASE_URL


def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


def save_article(article):
    """
    기사를 PostgreSQL의 articles 테이블에 저장.
    article: dict {source, title, content, url, published}
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            source TEXT,
            title TEXT,
            content TEXT,
            url TEXT UNIQUE,
            published TEXT,
            hash TEXT UNIQUE
        );
    """
    )
    content_hash = hashlib.sha1(article.get("content", "").encode("utf-8")).hexdigest()
    cur.execute(
        """
        INSERT INTO articles (source, title, content, url, published, hash)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (url) DO NOTHING;
    """,
        (
            article.get("source"),
            article.get("title"),
            article.get("content"),
            article.get("url"),
            article.get("published", ""),
            content_hash,
        ),
    )
    conn.commit()
    cur.close()
    conn.close()


def save_event(event):
    """
    이벤트를 PostgreSQL의 events 테이블에 저장.
    event: dict {type, model, details, source, url, confidence}
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id SERIAL PRIMARY KEY,
            type TEXT,
            model TEXT,
            details TEXT,
            source TEXT,
            url TEXT,
            confidence REAL,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
    )
    cur.execute(
        """
        INSERT INTO events (type, model, details, source, url, confidence)
        VALUES (%s, %s, %s, %s, %s, %s);
    """,
        (
            event.get("type"),
            event.get("model"),
            event.get("details"),
            event.get("source"),
            event.get("url"),
            event.get("confidence"),
        ),
    )
    conn.commit()
    cur.close()
    conn.close()
