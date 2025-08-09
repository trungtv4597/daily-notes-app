import types
import pytest

from src.components.database import DatabaseManager


class DummyCursor:
    def __init__(self, responses=None):
        self.queries = []
        self.params = []
        self._responses = responses or {}
        self.rowcount = 1
        self._fetchone_value = [42]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=None):
        self.queries.append(sql.strip())
        if params is not None:
            self.params.append(params)

    def fetchone(self):
        return self._fetchone_value


class DummyConn:
    def __init__(self):
        self.commits = 0
        self.rollbacks = 0
        self.closed = False
        self.cursor_obj = DummyCursor()

    def cursor(self, *args, **kwargs):
        return self.cursor_obj

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closed = True


@pytest.fixture
def dbm(monkeypatch):
    dbm = DatabaseManager
    # monkeypatch connection params with minimal dummy values to avoid ValueError in __init__
    class DM(DatabaseManager):
        def __init__(self):
            self.connection_params = {
                'host': 'h', 'database': 'd', 'user': 'u', 'password': 'p', 'port': 5432
            }
    dm = DM()

    dummy_conn = DummyConn()
    monkeypatch.setattr(dm, 'get_connection', lambda: dummy_conn)
    return dm, dummy_conn


def test_save_sent_email_inserts_and_returns_id(dbm):
    dm, dummy_conn = dbm
    email_id = dm.save_sent_email(1, 'to@test', 'sub', 'body', status='queued')
    assert email_id == 42
    # Check the query executed
    assert any('INSERT INTO sent_emails' in q for q in dummy_conn.cursor_obj.queries)
    assert dummy_conn.commits == 1


def test_update_sent_email_status_updates_and_commits(dbm):
    dm, dummy_conn = dbm
    ok = dm.update_sent_email_status(42, 'sent', None)
    assert ok is True
    assert any('UPDATE sent_emails' in q for q in dummy_conn.cursor_obj.queries)
    assert dummy_conn.commits == 1

