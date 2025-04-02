from database.db_manager import get_connection


class FakeConnection:
    pass


def fake_connect(db_url):
    # Verify that the DATABASE_URL environment variable is set correctly.
    assert db_url == "postgresql://dummy_user:dummy_password@db:5432/test_database"
    return FakeConnection()


def test_get_connection(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "test_database")
    monkeypatch.setattr("database.db_manager.psycopg2.connect", fake_connect)
    conn = get_connection()
    assert isinstance(conn, FakeConnection)
