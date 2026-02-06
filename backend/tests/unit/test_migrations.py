from __future__ import annotations

import sqlite3

from src.db.migrations import run_migrations


def _list_tables(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    return {row[0] for row in rows}


def test_run_migrations_creates_schema(temp_db: str) -> None:
    run_migrations(temp_db)

    conn = sqlite3.connect(temp_db)
    tables = _list_tables(conn)
    conn.close()

    assert "schema_migrations" in tables
    assert "calibration_profiles" in tables
    assert "detection_history" in tables
    assert "notification_log" in tables
    assert "settings" in tables
