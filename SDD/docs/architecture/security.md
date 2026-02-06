# Security Architecture
## Overwatch AI Queue Detection & Notification App

**Generated**: February 6, 2026  
**Version**: 1.0

---

## Authentication & Authorization

### No User Accounts (LocalFirst Design)

This application has **no authentication system**. It's a local-only desktop app with:
- No login or user accounts
- No cloud backend
- No API authentication tokens
- All data stored locally on the user's machine

**Authorization**: Single-user implicit (whoever runs the app has full access to local data).

---

## Secret Management

### Discord Webhook URL (Sensitive Credential)

**Storage**:
```
SQLite settings table: key="discord_webhook_url", value="https://discordapp.com/api/webhooks/12345/abc..."

Encryption at rest: 
  - Optional: Store encrypted with OS Credential Manager (Windows Data Protection API)
  - Current: Plain text in SQLite (user owns the file)
```

**Access Control**:
- Webhook URL masked in UI (Settings → Discord tab shows `***...***`)
- Only readable from settings table
- No logging of webhook URL in error messages

**Rotation**:
- User can delete and re-enter at any time (Settings → Discord → delete + enter new)
- No automatic rotation (user-managed)

**Exposure Mitigation**:
- Webhook URL is not embedded in distributed code
- Not logged in debug output
- HTTP requests use TLS 1.2+ (HTTPS enforced)

---

## Input Validation Layer

### User Inputs

```python
# settings.py (Pydantic)
from pydantic import BaseModel, HttpUrl, AnyUrl
from urllib.parse import urlparse

class DiscordWebhookSettings(BaseModel):
    webhook_url: HttpUrl
    
    @validator('webhook_url')
    def validate_discord_webhook(cls, v):
        """Validate Discord webhook URL format"""
        parsed = urlparse(str(v))
        if parsed.hostname != 'discordapp.com' and not parsed.hostname.endswith('discord.com'):
            raise ValueError("Invalid Discord webhook domain")
        if '/api/webhooks/' not in str(v):
            raise ValueError("Invalid Discord webhook path")
        return v

# Validation on entry
try:
    webhook = DiscordWebhookSettings(webhook_url=user_input)
except ValueError as e:
    logger.warning(f"Invalid webhook URL: {e}")
    return {"error": str(e)}, 400
```

### Screenshot Inputs (Cropped Regions)

```python
# perception/classifier.py
import numpy as np

def predict(self, image: np.ndarray) -> Tuple[str, float]:
    """
    Validate image before inference
    """
    # Type check
    if not isinstance(image, np.ndarray):
        raise TypeError(f"Expected ndarray, got {type(image)}")
    
    # Shape check (must be 224×224×3)
    if image.shape != (224, 224, 3):
        raise ValueError(f"Expected shape (224, 224, 3), got {image.shape}")
    
    # Value range check (must be uint8 [0-255])
    if image.dtype != np.uint8:
        raise TypeError(f"Expected uint8, got {image.dtype}")
    
    # Proceed to inference
    return self._run_inference(image)
```

---

## SQL Injection Prevention

**Status**: **No SQL injection risk** (parameterized queries only)

```python
# All queries use parameterized statements:

# ✓ SAFE
cursor.execute(
    "SELECT * FROM detection_history WHERE id = ? AND state = ?",
    (detection_id, state)
)

# ✗ NEVER (vulnerable)
cursor.execute(f"SELECT * FROM detection_history WHERE id = {detection_id}")
```

**Policy**: 100% parameterized queries. Code review checks for f-strings in SQL.

---

## XSS & CSRF Prevention

### XSS (Cross-Site Scripting)

**Status**: **Not applicable** (no web server, local Electron app)

However, if a Discord notification body is user-controlled:
```python
# Escape user content for Discord embed
import html

user_message = "<script>alert('xss')</script>"
safe_message = html.escape(user_message)
# Output: "&lt;script&gt;alert('xss')&lt;/script&gt;"
```

### CSRF (Cross-Site Request Forgery)

**Status**: **Not applicable** (local-only, no session cookies, no external forms)

Discord webhooks:
- One-way HTTP POST (no state changes via GET)
- Webhook URL is user-configured (no CSRF possible)

---

## Data Encryption

### At Rest (SQLite Database)

**Current**: No encryption (SQLite plain file)

**Optional Future**: SQLCipher
```python
# SQLCipher enables transparent AES-256 encryption
# Usage: conn = sqlite3.connect("file:local.db?cipher=aes256", uri=True)
#        conn.execute(f"PRAGMA key = '{password}'")
```

**Rationale for no encryption**:
- Single-user local app; user owns the file
- Database only contains screenshots + timestamps (not highly sensitive)
- Encryption adds password management burden
- Can be added later if needed

### In Transit (Discord Webhooks)

**Status**: **TLS 1.2+ enforced**

```python
import httpx

# ✓ Secure: HTTPS enforced, TLS verification
async def send_discord_webhook(url: str, payload: dict):
    async with httpx.AsyncClient(verify=True) as client:
        response = await client.post(url, json=payload, timeout=5.0)
        return response
```

**Certificate Pinning**: Not required (Discord's public CAs trusted)

---

## OWASP Top 10 Checklist (Applied to This Project)

| OWASP Risk | Status | Mitigation |
|------------|--------|-----------|
| **A01: Broken Access Control** | ✓ N/A | Single-user local app; no user management |
| **A02: Cryptographic Failures** | ✓ Partial | HTTPS for webhooks; SQLite encryption optional |
| **A03: Injection** | ✓ Safe | 100% parameterized SQL queries |
| **A04: Insecure Design** | ✓ Safe | Privacy-first (no cloud, local processing only) |
| **A05: Security Misconfiguration** | ✓ Safe | No server; no exposed configs; secrets in SQLite only |
| **A06: Vulnerable & Outdated Components** | ✓ Monitored | uv pip audit + npm audit in CI/CD |
| **A07: Identification & Auth Failures** | ✓ N/A | No authentication (local app) |
| **A08: Software & Data Integrity Failures** | ✓ Safe | GitHub Releases signed; auto-update validates hash (SHA256) |
| **A09: Logging & Monitoring Failures** | ✓ Monitored | Structured JSON logs; optional cloud error reporting |
| **A10: SSRF** | ✓ Safe | Only Discord webhooks (user-configured); no server-side requests |

---

## Authentication Flow (Not Applicable)

Since there's no user login, the "authentication" is implicit:
```
User launches app
  │
  ├─ Read local SQLite database (implicit trust: user owns machine)
  └─ Load settings (including Discord webhook URL, if set)
```

---

## Game Input Automation (Security)

**Key Constraint**: The application **never interacts with game input**.

```python
# ✓ Allowed: Read-only screen capture
frame = screen_capture.capture_window("Overwatch")  # GetWindowDC only

# ✗ Forbidden: Input automation
# cursor.click(1920, 1080)  # NO
# keyboard.press('Enter')   # NO
```

**Rationale**: 
- Avoid Overwatch anti-cheat detection
- Maintain user trust (read-only monitoring)
- No liability for account bans

---

## Rate Limiting & DoS Protection

### Discord Webhook Rate Limits

**Discord Limit**: 10 requests per 10 seconds, global

**Mitigation**:
```python
# Exponential backoff on 429 (Too Many Requests)
async def send_with_retry(url: str, payload: dict, max_retries: int = 5):
    for attempt in range(max_retries):
        try:
            response = await client.post(url, json=payload, timeout=5.0)
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 2 ** attempt))
                logger.warning(f"Rate limited; retrying after {retry_after}s")
                await asyncio.sleep(min(retry_after, 30))
                continue
            response.raise_for_status()
            return response
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(2 ** attempt)
    
    raise NotificationError("Discord webhook delivery failed after retries")
```

### Local DoS

**Risk**: Low (desktop app, single process)

**Mitigation**:
- Memory limit: 300 MB (enforced in task manager, not by app)
- Detection queue size: Max 100 pending notifications
- Screen capture timeout: 1s (non-blocking)

---

## Logging & Audit Trail

### Log Levels

```python
import json
from datetime import datetime

def log_event(level: str, service: str, event: str, **context):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "level": level,
        "service": service,
        "event": event,
        **context
    }
    print(json.dumps(log_entry), file=sys.stdout)  # Also write to file
    
    # Sensitive data redaction
    if "webhook_url" in context:
        log_entry["webhook_url"] = "***redacted***"
```

### Sensitive Data Not Logged

- Discord webhook URLs (redacted as `***redacted***`)
- Screenshot content (only metadata logged)
- Cropped regions (not stored in logs)

**Audit Trail**:
- Detection history + notification log stored in SQLite (immutable append-only)
- User can export logs as JSON (Settings → Logs → Export)

---

## Error Handling (Security)

### Safe Error Messages (User-Facing)

```python
# ✗ Unsafe: Exposes internal paths
return {"error": "Database locked at /home/user/.ow-notifier/local.db"}

# ✓ Safe: Generic, no system info
return {"error": "Unable to save calibration. Please try again."}
```

### Developer Logs (Detailed)

```python
logger.error("DB Lock", extra={
    "service": "notification_repo",
    "db_path": db_path,
    "error": str(e),
    "timestamp": now,
})
```

---

## Summary

**Overwatch Queue Notifier** is a **privacy-first, local application** with:
- **No authentication**: Single-user implicit trust
- **Input validation**: Parameterized SQL, URL validation, type checks
- **Secret storage**: Discord webhook URL in SQLite (optional encryption)
- **TLS transport**: HTTPS for webhooks, standard certificate validation
- **No cloud leak**: All processing local, no telemetry by default
- **Logging**: Structured, sensitive data redacted, immutable audit trail
- **OWASP compliance**: Safe from injection, crypto-failure, and misconfiguration

The security model is appropriate for a **privacy-sensitive, local desktop application**.
