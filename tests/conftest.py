import os
import tempfile
import pytest

from src.db import connection as db_conn
from src.db.schema import init_db


@pytest.fixture
def db(tmp_path):
    db_file = str(tmp_path / "test.db")
    db_conn.configure(db_file)
    init_db()
    yield db_file
    db_conn.configure("")
