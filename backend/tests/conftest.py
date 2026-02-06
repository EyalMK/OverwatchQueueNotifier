from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture()
def temp_db(tmp_path: Path) -> str:
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    conn.close()
    return str(db_path)
