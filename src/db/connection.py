import sqlite3
from contextlib import contextmanager
from typing import Generator

from src.exceptions import DatabaseConnectionError

_db_path: str = ""


def configure(db_path: str) -> None:
    global _db_path
    _db_path = db_path


def _get_connection() -> sqlite3.Connection:
    if not _db_path:
        raise DatabaseConnectionError("DB 경로가 설정되지 않았습니다")
    try:
        conn = sqlite3.connect(_db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        raise DatabaseConnectionError(str(e))


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = _get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
