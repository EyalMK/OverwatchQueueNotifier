# Development Environment Setup
## Overwatch AI Queue Detection & Notification App

**Generated**: February 6, 2026  
**Version**: 1.0

---

## Prerequisites

- **OS**: Windows 10 / 11 (development can target Windows specifically)
- **Git**: Latest (`git --version`)
- **Node.js**: 18+ LTS (`node --version`, `npm --version`)
- **Python**: 3.11+ (`python --version`)
- **Visual C++ Build Tools**: For native modules (node-gyp, opencv)

---

## Step 1: Clone Repository

```bash
git clone https://github.com/EyalMK/OverwatchQueueNotifier.git
cd OverwatchQueueNotifier
git checkout develop
```

---

## Step 2: Install Dependencies

### Frontend

```bash
cd frontend
npm install
npm run typecheck  # Verify TypeScript
npm run lint
```

### Backend

```bash
cd backend

# Install uv package manager
pip install uv

# Install dependencies
uv sync --all-extras --dev
```

### Global Tools

```bash
# ESLint, prettier, black (global, optional)
npm install -g eslint prettier
pip install black pylint mypy
```

---

## Step 3: Environment Variables

### Backend (`.env` in `/backend`)

```bash
# Logging
LOG_LEVEL=DEBUG
LOG_FILE=logs/app.log

# MCP Server
MCP_PORT=5000
MCP_HOST=127.0.0.1

# AI Models
MODEL_TINY_PATH=models/tiny_classifier.onnx
MODEL_ESCALATION_PATH=models/escalation_model.onnx

# Gate Configuration
GATE_PIXEL_DIFF_THRESHOLD=15.0
GATE_HISTOGRAM_THRESHOLD=0.3

# Perception
PERCEPTION_CYCLE_MS=500
CONFIDENCE_THRESHOLD_ESCALATION=0.85

# Discord (auto-loaded from SQLite settings; set here for testing)
DISCORD_WEBHOOK_URL=<optional-test-url>

# Testing
TEST_MODE=false
FIXTURES_PATH=tests/fixtures
```

### Frontend (`.env` in `/frontend`)

```bash
# API
VITE_MCP_SERVER_URL=http://127.0.0.1:5000

# Logging
VITE_LOG_LEVEL=debug

# Feature flags
VITE_ENABLE_DASHBOARD=false
VITE_ENABLE_ANALYTICS=false
```

---

## Step 4: Start Development Servers

### Terminal 1: Backend

```bash
cd backend
uv run python -m src.main --dev
# Output: MCP server listening on http://127.0.0.1:5000
```

### Terminal 2: Frontend (with watch mode)

```bash
cd frontend
npm run dev
# Output: Electron dev server listening on http://localhost:3000
```

### Terminal 3: Tests (optional)

```bash
# Backend tests in watch mode
cd backend && pytest --watch tests/unit

# OR Frontend tests
cd frontend && npm run test:watch
```

---

## Step 5: Verify Setup

### Backend Health Check

```bash
curl -X POST http://127.0.0.1:5000/mcp/tools/screen.perceive_state \
  -H "Content-Type: application/json" \
  -d '{"resolution": "1920x1080"}'

# Expected response:
# {
#   "state": "IDLE",
#   "confidence": 0.92,
#   "timestamp": "2026-02-06T14:30:45.500Z"
# }
```

### Frontend Health Check

- Tray window should appear in system tray
- Click tray icon → Tray window should open
- Settings → Discord tab → Field should be empty (first run)

### Database Health Check

```bash
sqlite3 backend/local.db "SELECT COUNT(*) FROM sqlite_master WHERE type='table';"
# Expected: 4 (calibration_profiles, detection_history, notification_log, settings)
```

---

## Database Setup

SQLite is auto-initialized on first run. To reset:

```bash
cd backend
rm local.db
# Restart backend; migrations will run on startup
```

---

## Working with Docker (Optional)

```bash
# Start dev environment in Docker
docker-compose -f docker-compose.yml up -d backend

# Run tests in isolation
docker-compose -f docker-compose.yml --profile test up tests

# Stop
docker-compose down
```

---

## IDE Setup

### VS Code (Recommended)

**Extensions**:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- ESLint (dbaeumer.vscode-eslint)
- Prettier (esbenp.prettier-vscode)
- SQLite (alexcvzz.sqlite3)

**Settings** (`.vscode/settings.json`):
```json
{
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true
  },
  "[typescript]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

---

## Common Commands

```bash
# Backend
cd backend
uv run pytest tests/             # Run all tests
uv run pytest --cov tests/       # Coverage report
uv run black src/               # Format code
uv run pylint src/              # Lint check

# Frontend
cd frontend
npm run build                   # Production bundle
npm test                        # Run tests
npm run lint                    # ESLint
npm run typecheck               # TypeScript strict check

# Both
npm run dev                     # Start both (requires concurrently)
npm run build:all               # Build both
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'onnxruntime'` | `uv sync` in backend/ directory |
| `npm ERR! ERESOLVE unable to resolve dependency tree` | `npm install --legacy-peer-deps` |
| Port 5000 in use | `lsof -i :5000` (kill process) or change `MCP_PORT` |
| TypeScript errors in IDE | Restart "TypeScript Language Server" (VS Code) |
| SQLite "database is locked" | Close any open connections; restart backend |
| Electron white screen | Clear cache: `rm -rf ~/.ow-notifier/Cache` |

---

## Summary

Development setup is **straightforward**:
1. Clone repo
2. Install Node + Python deps
3. Set env vars
4. Start backend + frontend servers
5. Verify with health checks
6. Begin development!

**Total time**: ~15 minutes with good internet.
