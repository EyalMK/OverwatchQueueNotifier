from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest


@pytest.fixture()
def temp_db(tmp_path: Path) -> str:
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    conn.close()
    return str(db_path)
