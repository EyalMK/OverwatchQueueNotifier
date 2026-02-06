# Cloud Architecture
## Overwatch AI Queue Detection & Notification App

**Generated**: February 6, 2026  
**Version**: 1.0

---

## Deployment Model: Local-First (No Cloud Required)

This application is **inherently local-first**. All computation happens on the user's machine:

```
User's Windows PC (Local)
└── Electron App + Python Backend
    ├── AI Inference (ONNX on device)
    ├── Screen Capture (DCE API local)
    ├── SQLite Database (local file)
    └── Notifications (local + optional external webhooks)

External Services (Optional, User-Configured):
└── Discord (if user provides webhook URL)
    └── One-way HTTP POST (user owns the integration)
```

**No cloud backend required for MVP functionality.**

---

## Optional Cloud Expansion (v2+)

If future versions add cloud features (e.g., multi-device sync, stats aggregation), here's the architecture:

### Architecture Diagram (Hypothetical v2)

```
┌─────────────────────────────────────┐
│   User's Windows PC (Desktop App)   │
│  ┌─────────────────────────────────┐│
│  │ Local Processing (as base model)││
│  │ + Analytics Upload (optional)   ││
│  └──────────────┬──────────────────┘│
└─────────────────┼────────────────────┘
                  │ HTTPS (optional analytics)
                  │ Minimal data: state, confidence, timestamp (no screenshots)
                  ▼
        ┌─────────────────────────┐
        │  Cloud API Gateway      │
        │  (API.example.com)      │
        └──────────┬──────────────┘
                   │
        ┌──────────┴──────────────┬────────────┐
        │                         │            │
        ▼                         ▼            ▼
    ┌────────┐         ┌──────────────────┐  ┌─────────┐
    │Analytics│ ┌─────▶ │ Time-Series DB  │  │ Secrets │
    │Service  │         │ (InfluxDB/Mongo)│  │ Manager │
    └────────┘         └──────────────────┘  │ (Vault) │
                                             └─────────┘
```

---

## Local-First Advantages

| Aspect | Benefit |
|--------|---------|
| **Privacy** | No screenshot data leaves device; user data remains on disk |
| **Latency** | <1s MATCH_FOUND detection vs. cloud round-trip |
| **Reliability** | Works offline; no server dependency; always available |
| **Simplicity** | No backend operations, no scaling concerns, no auth complexity |
| **Cost** | Zero server cost; zero compliance audits needed |

---

## If Cloud Becomes Necessary

### Service Mapping (AWS Example)

| Feature | Current (Local) | Cloud Alternative |
|---------|-----------------|-------------------|
| **Screen Capture** | Windows DCE API | Remote desktop streaming (unreliable) |
| **AI Inference** | ONNX on device | EC2 GPU (latency cost) |
| **SQLite Storage** | Local file | RDS (adds latency + cost) |
| **Discord Webhooks** | Direct HTTP | API Gateway + Lambda (adds latency) |
| **Auto-Update** | GitHub Releases | S3 + CloudFront (not necessary) |
| **Analytics** | None (v1) | CloudWatch Logs + Athena |
| **Error Reporting** | File logs | Sentry / Rollbar (optional) |

### Why Cloud is NOT Required

1. **AI Inference**: Tiny model (200 KB) + ONNX Runtime (5 MB) is entirely self-contained
2. **Storage**: SQLite is a single file; no database server needed
3. **Notifications**: Discord webhooks are user-provided (no server intermediary)
4. **Scaling**: Single-user app; no horizontal scaling needed

---

## Auto-Update Mechanism (GitHub-Based)

The application updates itself **without cloud infrastructure**:

```
User's App (v1.0.0)
  │
  ├─ Weekly check: GET https://api.github.com/repos/user/ow-notifier/releases/latest
  │
  └─ Response: {"tag_name": "v1.0.1", "assets": [{"name": "app-1.0.1.msi", "url": ...}]}
       │
       ├─ Download .msi from GitHub CDN
       ├─ Verify SHA256 signature (RELEASES file)
       ├─ Install on next app restart
       └─ Update to v1.0.1
```

**No dedicated update server needed.**

---

## Monitoring & Observability (Local)

### Local Logging

```json
{
  "timestamp": "2026-02-06T14:30:45.500Z",
  "level": "INFO",
  "service": "perception_agent",
  "event": "detection_complete",
  "state": "MATCH_FOUND",
  "confidence": 0.94,
  "latency_ms": 42,
  "resolution": "1920x1080"
}
```

Logs written to:
- `%APPDATA%\OverwatchQueueNotifier\logs\app.log` (local file)
- Console (optional debug mode)

### Optional: Cloud Error Reporting (v2+)

```python
# Optional integration with Sentry
import sentry_sdk

if config.SENTRY_DSN:  # Only if user opts in
    sentry_sdk.init(config.SENTRY_DSN, environment="production")
    logger.info("Sentry error reporting enabled")
else:
    logger.info("Sentry disabled (local logging only)")
```

**Philosophy**: Default local-only; cloud opt-in (never mandatory).

---

## Backup & Disaster Recovery

### User Data Backup

```
SQLite Database: %LOCALAPPDATA%\OverwatchQueueNotifier\local.db
├── Calibration profiles (reproducible; can be regenerated)
├── Detection history (archive-able; can be exported/deleted)
├── Notification log (appendable; can be cleared)
└── Settings (small; easily re-entered)
```

### Recommended Backup Strategy

```
User can manually:
1. Settings → Logs → Export JSON (backup history + settings)
2. Copy local.db to external drive (full database backup)
3. Settings are also stored in Zustand localStorage (browser DevTools)
```

### Disaster Recovery Plan (RTO/RPO)

| Scenario | RTO | RPO | Action |
|----------|-----|-----|--------|
| **App crashes** | <5 min | <1 min | User restarts app; database is persistent |
| **Local.db corrupted** | <1 hour | <1 day | User re-runs calibration; history lost but app functional |
| **Machine fails** | <1 day | <1 month | User installs app on new machine; history not recovered (cloud backup optional) |

**No SLA required** (consumer app, user owns their data).

---

## Cost Analysis (If Cloud Were Used)

### Hypothetical AWS Cost (Never Used, For Reference)

```
Component          | Cost/Month | Notes
─────────────────────────────────────────────────────
EC2 (API gateway)  | $20–50     | t3.small, single instance
RDS (analytics)    | $20–50     | db.t3.micro, minimal
S3 (logs + updates)| $5–10      | < 10 GB/month
CloudFront (CDN)   | $5–10      | Minimal traffic
Total              | $50–120    | Per month for 100s of users

With local-first: $0 cloud cost per user
```

**Verdict**: Local-first is **dramatically cheaper** for small user base.

---

## Security Implications of Local-First

| Aspect | Local | Cloud |
|--------|-------|-------|
| **Data Leakage Risk** | User controls (personal machine) | Server compromise |
| **Privacy** | Never leaves device | Multi-tenant exposure |
| **Compliance** | N/A (personal use) | GDPR, SOC2 required |
| **Availability** | User's ISP / hardware | 99.9% SLA cost |

**Local is inherently more private and secure.**

---

## Future: Optional Cloud Features

If we decide to add cloud features in v2+, here's the opt-in model:

```python
# config.py
class CloudConfig:
    CLOUD_API_URL = os.getenv("CLOUD_API_URL", None)  # None = disabled
    ANALYTICS_ENABLED = os.getenv("ANALYTICS_ENABLED", "false") == "true"
    ERROR_REPORTING_ENABLED = os.getenv("ERROR_REPORTING", "false") == "true"

# main.py
if config.CLOUD_API_URL:
    logger.info("Cloud features enabled")
    controller = CloudPerceptionController(config.CLOUD_API_URL)
else:
    logger.info("Cloud disabled; using local-only mode")
    controller = LocalPerceptionController()
```

All cloud features are **behind environment flags** and **never mandatory**.

---

## Compliance & Regulations

### GDPR (If User Data Goes to Cloud)

- ✓ Currently: Not applicable (local-only, no personal data collection)
- ⚠ Future: If cloud analytics, need privacy policy, consent mechanism

### HIPAA / PCI

- ✗ Not applicable (gaming app, no health/financial data)

### Windows Secure Boot / Code Signing

- TODO: MSI installer code-signing (with EV certificate, future release)
- Currently: Unsigned (safe for unsigned publication; user accepts)

---

## Summary

**Overwatch Queue Notifier** is **fundamentally local-first**:
- No cloud backend required
- All AI inference on device
- All data stays on user's PC
- GitHub webhooks for updates (no update server)
- Optional: User-configured Discord webhooks
- Future: Cloud features behind opt-in flags

**This design prioritizes privacy, latency, and simplicity.**
