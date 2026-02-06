# DevOps Lead Specification  
## Overwatch AI Queue Detection & Notification App

**Generated**: February 6, 2026  
**Version**: 1.0  
**Status**: Draft → Infrastructure Foundation

---

## 1. Infrastructure Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│           Windows 10/11 User Machine                      │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐ │
│  │     System Tray Application                         │ │
│  │  (Electron: Main + Renderer)                        │ │
│  │                                                     │ │
│  │  ┌──────────────┐   ┌──────────────────┐          │ │
│  │  │  Tray Window │───│ Settings Modal   │          │ │
│  │  │  StateDisplay│   │ Calibration Wiz  │          │ │
│  │  └──────────────┘   └──────────────────┘          │ │
│  └────────────┬────────────────────────────────────────┘ │
│               │ (IPC)                                      │
│               ▼                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │      Backend Services (Python)                       │ │
│  │  Strands Agent + MCP Servers                         │ │
│  │                                                      │ │
│  │  ┌──────────────────────────────────────────────┐  │ │
│  │  │ Perception Loop (Main Agent)                 │  │ │
│  │  │ - Screen Capture (Windows DCE API)           │  │ │
│  │  │ - Gate Service (heuristics)                  │  │ │
│  │  │ - AI Classifier (ONNX Runtime)               │  │ │
│  │  └──────────────────────────────────────────────┘  │ │
│  │                                                      │ │
│  │  ┌──────────────────────────────────────────────┐  │ │
│  │  │ Notification Service                         │  │ │
│  │  │ - Deduplication Queue                        │  │ │
│  │  │ - Desktop Notif (Windows Toast API)          │  │ │
│  │  │ - Discord Webhook (HTTP Retry)               │  │ │
│  │  └──────────────────────────────────────────────┘  │ │
│  │                                                      │ │
│  │  ┌──────────────────────────────────────────────┐  │ │
│  │  │ MCP Tools (HTTP Server: 127.0.0.1:5000)     │  │ │
│  │  │ - screen.perceive_state                      │  │ │
│  │  │ - screen.capture_regions                     │  │ │
│  │  │ - notify.* tools                             │  │ │
│  │  └──────────────────────────────────────────────┘  │ │
│  └──────────────┬───────────────────────────────────────┘ │
│                 │                                         │
│  ┌──────────────▼────────────────────────────────────┐  │
│  │  SQLite Database (local.db)                       │  │
│  │  - calibration_profiles                          │  │
│  │  - detection_history                             │  │
│  │  - notification_log                              │  │
│  │  - settings                                      │  │
│  └────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Auto-Update Mechanism                           │   │
│  │  - Check GitHub Releases weekly                  │   │
│  │  - Download MSI delta                            │   │
│  │  - Verify signature                              │   │
│  │  - Install on next restart                       │   │
│  └──────────────────────────────────────────────────┘   │
│                                                            │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Logging & Monitoring                            │   │
│  │  - JSON structured logs (file + stdout)          │   │
│  │  - Error reporting (optional cloud)              │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘

        ┌─────────────────────────┐
        │  GitHub (Cloud)         │
        │  - Releases (MSI + SHA) │
        │  - Issue tracking       │
        │  - CI/CD (Actions)      │
        └─────────────────────────┘

        ┌─────────────────────────┐
        │  Discord (External)     │
        │  - Webhook notifications│
        │  (if configured by user)│
        └─────────────────────────┘
```

---

## 2. CI/CD Pipeline Architecture

```
Code Push
  │
  ▼
GitHub Actions Workflow: test.yml
  │
  ├─→ [Lint]  ──→ eslint + black + pylint
  │            ──→ ✓ Pass / ❌ Fail (block merge)
  │
  ├─→ [Type Check] ──→ TypeScript strict mode
  │                  ──→ Python mypy
  │                  ──→ ✓ Pass / ❌ Fail (block merge)
  │
  ├─→ [Unit Tests] ──→ pytest (backend)
  │                  ──→ vitest (frontend)
  │                  ──→ Coverage report (lcov)
  │                  ──→ ✓ >75% / ❌ Below threshold (fail)
  │
  ├─→ [Security] ──→ npm audit + uv pip compile --audit
  │               ──→ SAST scan (GitHub CodeQL)
  │               ──→ ✓ No critical / ❌ Found (fail)
  │
  ├─→ [Build] ──→ Electron: npm run build
  │            ──→ .asar bundle created
  │            ──→ ✓ Success / ❌ Fail (show logs)
  │
  └─→ [Artifacts]
       │
       ├─→ Store build cache (node_modules, .venv)
       ├─→ Upload coverage report to Coveralls
       └─→ Create draft release (on git tag)

Build Artifact: dist/electron-app.asar

On Release Tag (v1.0.0):
  │
  ├─→ [Package] ──→ windows-installer task
  │             ──→ Sign code (optional)
  │             ──→ Create: Overwatch-Queue-Notifier-1.0.0.msi
  │
  ├─→ [Generate] ──→ Create SHA256 checksums
  │              ──→ RELEASES manifest for auto-update
  │
  └─→ [Publish] ──→ Upload to GitHub Releases
                ──→ Attach: .msi + .exe + RELEASES file
                ──→ Notify via Discord webhook
```

---

## 3. Docker Setup (Development Only)

### docker-compose.yml

```yaml
version: "3.9"

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    ports:
      - "5000:5000"  # MCP HTTP server
    volumes:
      - ./backend/src:/app/src
      - ./backend/models:/app/models
    environment:
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=DEBUG
      - MCP_PORT=5000
    command: python -m main --dev
    profiles: ["dev"]

  tests:
    build:
      context: ./backend
      dockerfile: Dockerfile.test
    volumes:
      - ./backend:/app
    environment:
      - PYTHONUNBUFFERED=1
    command: pytest tests/ --cov=src --cov-report=term-color
    profiles: ["test"]
```

### Dockerfile.dev (Backend Development)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

COPY pyproject.toml uv.lock .
RUN uv sync --all-extras --dev

COPY src ./src
COPY models ./models

EXPOSE 5000

CMD ["uv", "run", "python", "-m", "src.main"]
```

### Dockerfile (Production - Multi-Stage)

```dockerfile
# Stage 1: Build
FROM python:3.11-slim as builder

WORKDIR /build

# Install uv
RUN pip install uv

COPY pyproject.toml uv.lock .
RUN uv sync --all-extras --no-dev --frozen

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install uv in runtime
RUN pip install uv

# Copy virtual environment from builder
COPY --from=builder /build/.venv ./.venv

# Copy application code
COPY src ./src
COPY models ./models

# Non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000
CMD ["uv", "run", "python", "-m", "src.main"]
```

---

## 4. Environment Matrix: Dev vs Staging vs Production

| Factor | Development | Staging | Production |
|--------|-------------|---------|-----------|
| **OS** | Windows 10/11 (local) | Clean Windows 11 VM | User machines (Windows 10/11) |
| **Python Version** | 3.11 (pinned) | 3.11 (pinned) | 3.11 (bundled in .msi) |
| **AI Models** | DEBUG models (small) | Full models (INT8) | Full models (INT8) |
| **Log Level** | DEBUG | INFO | WARN |
| **Screen Caps** | Saved for debugging | No saving | No saving (privacy) |
| **Discord Webhook** | Test webhook | Staging webhook | User-configured |
| **Update Check** | Disabled (dev build) | Every 24h | Every 24h |
| **Code Signing** | None | Debug signature | Production cert |
| **Database** | SQLite (in-memory for tests) | SQLite (persistent) | SQLite (persistent) |
| **Monitoring** | Local logs only | Logs + optional Sentry | Local logs + optional error reporting |

---

## 5. Deployment Strategy: Windows MSI + Auto-Update

### Deployment Flow

```
Developer Tags Release (v1.0.0)
  │
  ▼
GitHub Actions: Build + Package
  ├─→ Electron build: npm run build
  ├─→ Create installer: electron-builder --win msi
  ├─→ Sign code (Production cert)
  ├─→ Generate: Overwatch-Queue-Notifier-1.0.0.msi
  ├─→ Generate: RELEASES manifest (for auto-update)
  └─→ Upload to GitHub Releases + Create draft release
       │
       ▼
  User Downloads: .msi file
       │
       ▼
  Windows Installer (built-in)
       ├─→ Extracts files to Program Files\OverwatchQueueNotifier
       ├─→ Registers in Add/Remove Programs
       ├─→ Adds Start Menu shortcut
       ├─→ Sets up auto-start (if user selects)
       └─→ Launches app on completion
       │
       ▼
  First Run
       ├─→ Initialize SQLite database
       ├─→ Detect screen resolution
       ├─→ Download initial calibration profile (if new)
       └─→ Show tray icon + welcome
       │
       ▼
  Weekly Auto-Update Check
       ├─→ Query GitHub Releases API for latest version
       ├─→ Compare: local vs remote version
       ├─→ If newer exists:
       │   ├─→ Download delta MSI (new version only)
       │   ├─→ Verify SHA256 checksum
       │   ├─→ If valid: Stage for installation on next restart
       │   └─→ Notify user ("Update available, will install on restart")
       ├─→ If user restarts:
       │   ├─→ MSI installer runs (transparent)
       │   ├─→ Old version files backed up
       │   ├─→ Database preserved (migration if needed)
       │   └─→ App relaunches
       └─→ If user ignores:
           └─→ Try again next week
```

### RELEASES Manifest (for electron-updater)

```
RELEASES
SHA256 checksum_of_v1.0.0.msi
|OverwatchQueueNotifier|1.0.0|v1.0.0.msi|65536|SHA256_CHECKSUM|
|OverwatchQueueNotifier|0.9.9|v0.9.9.msi|62400|SHA256_CHECKSUM|

(Tracks available versions + checksums)
```

---

## 6. Monitoring & Alerting

### What to Monitor

| Metric | Source | Target | Alert Threshold |
|--------|--------|--------|-----------------|
| **App Crashes** | Windows Event Log | Sentry (optional) | 5+ crashes/day |
| **Detection Latency** | App logs | Local dashboard | p95 > 200ms |
| **CPU Usage (30-min avg)** | `psutil` | Local system tray | > 15% sustained |
| **GPU Usage** | GPU monitor | Local logs | > 10% (if GPU enabled) |
| **Memory Usage** | `psutil` | Local system tray | > 300 MB |
| **Discord Webhook Failures** | notification_log DB | Email / Discord DM | 10+ failures in 1h |
| **AI Inference Errors** | App logs | App logger | 5+ errors/hour |
| **False Positives** | User reports + logs | Analytics (optional) | >1 per 4h queue |

### Monitoring Output

```python
# backend/src/monitoring/metrics.py
class AppMetrics:
    def __init__(self):
        self.cpu_history = deque(maxlen=180)  # last 30 min @ 10s intervals
        self.memory_history = deque(maxlen=180)
        self.inference_latencies = deque(maxlen=100)
        self.error_count = Counter()
    
    def record_metrics(self):
        """Capture every 10 seconds"""
        cpu = psutil.Process().cpu_percent(interval=0.1)
        mem = psutil.Process().memory_info().rss / 1024**2  # MB
        
        self.cpu_history.append(cpu)
        self.memory_history.append(mem)
        
        # Alert if CPU sustained >15% for 5 min
        avg_cpu_5min = mean(list(self.cpu_history)[-30:])
        if avg_cpu_5min > 15.0:
            logger.warning(f"High CPU usage: {avg_cpu_5min:.1f}% (5-min avg)")
```

---

## 7. Logging Strategy

### Structured JSON Logging

```python
# backend/src/logger.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "service": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra context from record.__dict__
        if hasattr(record, "extra_context"):
            log_entry.update(record.extra_context)
        
        return json.dumps(log_entry)

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())  # stdout for Docker
logger.addHandler(logging.FileHandler("app.log"))  # File for persistence
```

### Log Levels & Retention

- **DEBUG**: Frame-by-frame gate signals, model inputs (disabled in production)
- **INFO**: State transitions, calibration loaded, notification sent, auto-update checked
- **WARN**: Low confidence detections, Discord rate limit, model fallback used
- **ERROR**: Window not found, AI crash, notification delivery failure
- **FATAL**: Database corruption, unrecoverable error

**Retention**: 
- 7 days of logs kept locally
- Automatic rotation daily
- Old logs compressed (gzip)
- No PII in logs (never log cropped images or Discord URLs in plain form)

---

## 8. Backup & Recovery

### Database Backup Schedule

```python
# backend/src/db/backup.py
import schedule

def daily_backup():
    """Backup database every day at 2 AM"""
    timestamp = datetime.now().strftime("%Y%m%d")
    backup_path = f"backups/local_{timestamp}.db"
    shutil.copy2("local.db", backup_path)
    
    # Keep only last 7 backups
    backups = sorted(glob.glob("backups/local_*.db"))
    for old in backups[:-7]:
        os.remove(old)

schedule.every().day.at("02:00").do(daily_backup)
```

### Restore Procedure

**User Action**: Settings → Backup & Recovery → "Restore from Backup"
1. List available backups (date, size)
2. User selects backup
3. Verify backup is valid (quick query test)
4. Swap: `local.db.backup` ← `local.db`, `local.db` ← selected backup
5. Restart app
6. Verify detection history restored

**RTO**: <2 minutes (backup + restart)  
**RPO**: <24 hours (daily automated backups)

---

## 9. Security: Code Signing & Updates

### Code Signing Setup

```powershell
# Windows Code Signing Certificate (Production)
# Acquire EV cert from DigiCert / GlobalSign

# Sign MSI before release
signtool.exe sign /f cert.pfx /p PASSWORD /t http://timestamp.server.com Overwatch-Queue-Notifier-1.0.0.msi

# Verify signature
signtool.exe verify /pa Overwatch-Queue-Notifier-1.0.0.msi
```

### Update Verification

```python
# backend/src/updater.py
import hashlib
import requests

def verify_update(msi_path: str, expected_sha256: str) -> bool:
    """Verify MSI checksum before installation"""
    with open(msi_path, "rb") as f:
        actual_sha256 = hashlib.sha256(f.read()).hexdigest()
    
    if actual_sha256 != expected_sha256:
        logger.error(f"Update checksum mismatch: {actual_sha256} != {expected_sha256}")
        return False
    
    logger.info(f"Update checksum verified: {actual_sha256}")
    return True
```

---

## 10. Development Workflow

### Local Development Setup

```bash
# Clone repo
git clone https://github.com/emalada/overwatch-queue-notifier.git
cd overwatch-queue-notifier

# Install uv (one-time)
pip install uv

# Setup backend (uv handles venv automatically)
cd backend
uv sync --all-extras --dev
uv run pytest tests/

# Setup frontend
cd ../frontend
npm install
npm run dev  # Starts Electron dev with hot reload

# From project root, run together
npm run dev  # Runs: backend server + electron dev
```

### GitHub Actions Workflow Triggers

| Event | Workflow | Steps |
|-------|----------|-------|
| **Push to `main`** | `test.yml` | lint → typecheck → test → build |
| **Push to `develop`** | `test.yml` + nightly `e2e.yml` | all tests + E2E suite |
| **PR created** | `test.yml` | block merge if any step fails |
| **Tag push (v\*)** | `release.yml` | build → sign → package → upload to GitHub Releases |
| **Weekly** | `dependency-check.yml` | npm audit + uv pip compile --audit |

---

## 11. Deployment Checklist (Pre-Release)

- [ ] All tests passing (unit, integration, E2E)
- [ ] Code coverage ≥75%
- [ ] No security vulnerabilities (npm audit, uv pip compile --audit clean)
- [ ] No new TypeScript errors (strict mode)
- [ ] Performance targets met (CPU <10%, latency <100ms p95)
- [ ] Database migrations tested (schema migration script works)
- [ ] Auto-update mechanism tested (manually download + install)
- [ ] Documentation updated (CHANGELOG, README)
- [ ] Code signed (if production release)
- [ ] Release notes written in GitHub

---

## 12. Troubleshooting & Rollback

### If Installer Fails

```powershell
# User-facing troubleshooting
msiexec /x {ProductCode} /l*v "uninstall_log.txt"  # Full uninstall
# Then download and run latest .msi

# DevOps: Debug installer issues
msiexec /i *.msi /l*v "install_log.txt"  # Verbose install log
# Review install_log.txt for specific error
```

### If Update Fails

1. App detects update download failed → no install staged
2. User can manually download from GitHub Releases
3. Or: Settings → "Check for Updates Now" (retry)

### Rollback Procedure (if release has critical bug)

1. Remove release tag: `git tag -d v1.0.1 && git push origin :v1.0.1`
2. Delete from GitHub Releases
3. Mark previous release as latest
4. Users with auto-update will NOT download broken version (version check fails)
5. Users with broken version: manual downgrade via GitHub Releases

---

## 13. Next Steps

1. ✅ **DevOps spec approved** → Setup GitHub Actions workflows
2. ⏭️ **CI/CD implementation** → test.yml, release.yml (Sprint 0)
3. ⏭️ **Installer build** → WiX toolset integration (Sprint 1)
4. ⏭️ **Auto-update mechanism** → electron-updater config (Sprint 1)
5. ⏭️ **First release** → v0.1.0-alpha to GitHub Releases (Sprint 2)

**Owner**: DevOps Lead  
**Stakeholders**: Backend Lead, Frontend Lead, QA Lead, Release Manager
