SCHEMA = """
CREATE TABLE IF NOT EXISTS user_settings (
    user_id BIGINT PRIMARY KEY,
    preferred_lang VARCHAR(5)
);

CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    source TEXT,
    title TEXT,
    content TEXT,
    url TEXT UNIQUE,
    published TEXT,
    hash TEXT UNIQUE
);

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


def create_tables(conn):
    with conn.cursor() as cur:
        cur.execute(SCHEMA)
    conn.commit()
