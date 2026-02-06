from __future__ import annotations

import sqlite3
from pathlib import Path


def run_migrations(db_path: str) -> None:
    migrations_dir = Path(__file__).parent / "migrations"
    migrations_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations ("
        "version TEXT PRIMARY KEY,"
        "executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ")"
    )

    migrations = sorted(migrations_dir.glob("*.sql"))
    for migration_file in migrations:
        version = migration_file.stem
        cursor.execute("SELECT 1 FROM schema_migrations WHERE version = ?", (version,))
        if cursor.fetchone():
            continue

        sql = migration_file.read_text(encoding="utf-8")
        try:
            cursor.executescript(sql)
            cursor.execute("INSERT INTO schema_migrations (version) VALUES (?)", (version,))
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    conn.close()


if __name__ == "__main__":
    default_db_path = Path(__file__).resolve().parents[2] / "local.db"
    run_migrations(str(default_db_path))
    print(f"Migrations applied to {default_db_path}")
