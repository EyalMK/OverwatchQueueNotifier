# Backend

Quickstart:

```bash
cd backend
# Create and sync env (uv must be installed)
uv sync --all-extras --dev

# Run migrations
uv run python -m src.db.migrations

# Run tests
uv run pytest
```
