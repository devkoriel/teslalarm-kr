import hashlib
import json

import psycopg2
import redis

from config import DATABASE_URL, REDIS_URL
from utils.logger import setup_logger

logger = setup_logger()


def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


def get_redis_client():
    return redis.Redis.from_url(REDIS_URL)


def save_article(article: dict):
    """
    Saves an article to the 'articles' table in PostgreSQL.
    Table schema: id, source, title, content, date, url, hash.
    Duplicate articles (by URL or hash) are ignored.
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
            date TEXT,
            url TEXT UNIQUE,
            hash TEXT UNIQUE
        )
    """
    )
    content_hash = hashlib.sha1(article.get("content", "").encode("utf-8")).hexdigest()
    cur.execute(
        """
        INSERT INTO articles (source, title, content, date, url, hash)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (url) DO NOTHING
    """,
        (
            article.get("source"),
            article.get("title"),
            article.get("content"),
            article.get("date"),
            article.get("url"),
            content_hash,
        ),
    )
    conn.commit()
    cur.close()
    conn.close()


def save_event(event: dict):
    """
    Saves an event to the 'events' table in PostgreSQL.
    Table schema: id, type, model, details, source, url, confidence, detected_at.
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
        )
    """
    )
    cur.execute(
        """
        INSERT INTO events (type, model, details, source, url, confidence)
        VALUES (%s, %s, %s, %s, %s, %s)
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


def publish_event(event: dict):
    """
    Publishes an event to the Redis queue 'events_queue'.
    """
    client = get_redis_client()
    client.rpush("events_queue", json.dumps(event))
    logger.info("Event published to Redis queue.")
