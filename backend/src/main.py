from __future__ import annotations

import argparse

from .config import load_config
from .db.migrations import run_migrations
from .mcp.server import main as run_mcp_server


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Overwatch Queue Notifier backend")
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Run MCP HTTP server after initializing the database",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    config = load_config()
    run_migrations(config.db_path)
    if args.dev:
        run_mcp_server()
        return
    print("Backend initialized")


if __name__ == "__main__":
    main()
