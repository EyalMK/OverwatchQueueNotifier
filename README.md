# Overwatch Queue Notifier

Local-first Windows desktop app that detects Overwatch 2 queue states and sends notifications.

## Prerequisites
- Windows 10/11
- Python 3.11
- Node.js 18+

## Quick Start
```bash
# Backend
cd backend
pip install uv
uv sync --all-extras --dev
uv run python -m src.main --dev

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Environment
Backend defaults to `backend/local.db`. Override with `.env` in `backend/`:
```bash
MCP_PORT=5000
LOG_LEVEL=INFO
DB_PATH=local.db
OVERWATCH_WINDOW_TITLE=Overwatch 2
```

Frontend uses `VITE_MCP_SERVER_URL`:
```bash
VITE_MCP_SERVER_URL=http://127.0.0.1:5000
```

## Tests
```bash
cd backend
pytest

cd frontend
npm run test
```
