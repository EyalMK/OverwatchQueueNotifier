from __future__ import annotations

from .config import load_config
from .db.migrations import run_migrations


def main() -> None:
    config = load_config()
    run_migrations(config.db_path)
    print("Backend initialized")


if __name__ == "__main__":
    main()
