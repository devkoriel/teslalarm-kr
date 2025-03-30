from database.db_manager import get_connection


class FakeConnection:
    pass


def fake_connect(db_url):
    # 환경변수로 설정된 DATABASE_URL가 올바른지 확인합니다.
    assert db_url == "test_database"
    return FakeConnection()


def test_get_connection(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "test_database")
    monkeypatch.setattr("database.db_manager.psycopg2.connect", fake_connect)
    conn = get_connection()
    assert isinstance(conn, FakeConnection)
