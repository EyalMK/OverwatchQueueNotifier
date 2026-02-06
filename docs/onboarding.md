# Developer Onboarding (5-Min Bootstrap)
## Overwatch Queue Notifier

This guide gets a fresh dev machine running in ~5 minutes.

## Prerequisites
- Windows 10/11, macOS, or Linux
- Git
- Python 3.11
- Node.js 18+

## Repo Setup
```bash
git clone <repo-url>
cd OverwatchQueueNotifier
```

## Environment Variables
Copy the example env file and update values as needed.
```bash
copy .env.example .env  # Windows PowerShell
```
```bash
cp .env.example .env    # macOS/Linux
```

## Backend (Python)
```bash
cd backend
python -m pip install --upgrade pip
python -m pip install -e .[dev]

# Run migrations
python -m src.db.migrations

# Run tests
pytest
```

## Frontend (Vite + React)
```bash
cd frontend
npm ci
npm run dev
```

## Recommended Local Checks (Match CI)
```bash
# Backend lint (ruff)
python -m pip install ruff
ruff check backend/src

# Frontend type check
cd frontend && npm run type-check
```

## Notes
- CI runs on `develop`, `main`, and `master` branches.
- Branch protection (2 approvals for `develop`) and repository secrets
  should be configured in GitHub settings.
- See `SDD/specs/backlog.md` for Sprint 0 ticket status.
