# Backend Lead Specification
## Overwatch AI Queue Detection & Notification App

**Generated**: February 6, 2026  
**Version**: 1.0  
**Status**: Draft → Technical Foundation

---

## 1. System Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                     Overwatch 2 Game Window                   │
│                      (Windows Screen)                         │
└──────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼ (Screen Capture)
┌──────────────────────────────────────────────────────────────┐
│                  Screen Capture Service                       │
│  (Windows DCE API: GetWindowDC → BitBlt → DIB)                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼ (Cropped Regions)
┌──────────────────────────────────────────────────────────────┐
│                   Gate Logic Service                          │
│  Cheap heuristics: pixel diff, histogram changes              │
│  Decision: Has screen changed significantly?                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                  [No Change]│[Change Detected]
                           │ │
                           │ ▼
                           │ ┌──────────────────────────────┐
                           │ │  AI Perception Pipeline      │
                           │ │  1. Tiny classifier (INT8)   │
                           │ │  2. Escalation if conf <0.85 │
                           │ │  3. Return: state + conf     │
                           │ └──────────────────┬───────────┘
                           │                   │
                           │    ┌──────────────┴──────┬────────┐
                           │    │                     │        │
                      [IDLE] [QUEUE] [MATCH_FOUND] [HERO_SELECT]
                           │    │         │            │
                           └────┴─────────┼────────────┘
                                         │
                                         ▼
                    ┌────────────────────────────────┐
                    │  Deduplication Service         │
                    │  (5s window, per state)        │
                    └────────────┬───────────────────┘
                                 │
                ┌────────────────┴─────────────────┐
                │                                  │
        ┌───────▼────────┐            ┌──────────▼──────┐
        │ Desktop Notif  │            │ Discord Webhook │
        │ (Windows API)  │            │ (HTTP POST)     │
        └────────────────┘            └─────────────────┘
                │                             │
                │         ┌───────────────────┘
                │         │
                ▼         ▼
        ┌──────────────────────────┐
        │  Notification Queue      │
        │  + Retry Logic (exp boff)│
        └──────────────────────────┘
```

---

## 2. Tech Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Screen Capture** | Windows DCE API (C/Python ctypes) | Direct, low-latency access to frame buffer |
| **Image Processing** | numpy + OpenCV (C++ backend) | Fast cropping, histogram analysis for gates |
| **AI Inference** | ONNX Runtime (INT8 quantized) | Platform-agnostic, hardware-accelerated, fast |
| **Tiny Classifier** | TinyMobileNetV3-based (200KB) | <50ms inference, CPU-only capable |
| **Escalation Model** | MobileNetV2-based (5MB) | ~100ms inference, optional GPU |
| **Local Server** | Node.js + Express (MCP servers) | Lightweight, event-driven, easy to orchestrate |
| **Process Orchestration** | Strands Agents SDK (Python) | Multi-agent perception + notification logic |
| **State Storage** | SQLite (local) | Zero-setup, no network, simple schema |
| **Notification Backend** | Windows Toasts (WinRT) + HTTP | Native desktop notifications + Discord webhooks |
| **Testing** | pytest + vitest | Python for backend, JS for Node services |

---

## 3. Project Directory Structure

```
OverwatchQueueNotifier/
├── backend/
│   ├── src/
│   │   ├── main.py                 # Entry point, Strands agent bootstrap
│   │   ├── perception/
│   │   │   ├── __init__.py
│   │   │   ├── screen_capture.py  # Windows DCE screen capture
│   │   │   ├── gate.py             # Heuristic gate logic (diff, histogram)
│   │   │   ├── classifier.py       # AI inference (ONNX Runtime)
│   │   │   └── calibration.py      # Per-resolution profile management
│   │   ├── notification/
│   │   │   ├── __init__.py
│   │   │   ├── desktop_notif.py   # Windows notification API
│   │   │   ├── discord_notif.py   # Webhook retry + rate limiting
│   │   │   ├── queue.py            # In-memory queue + deduplication
│   │   │   └── retry_policy.py     # Exponential backoff
│   │   ├── state/
│   │   │   ├── __init__.py
│   │   │   ├── models.py           # GameState enum, Evidence dataclass
│   │   │   └── repository.py       # SQLite access layer
│   │   ├── mcp/
│   │   │   ├── server.py           # MCP tool implementations
│   │   │   ├── tools/
│   │   │   │   ├── perceive.py     # screen.perceive_state tool
│   │   │   │   ├── capture.py      # screen.capture_regions tool
│   │   │   │   └── notify.py       # notify.* tools
│   │   ├── config.py               # Load env vars, models, profiles
│   │   ├── logger.py               # Structured logging (JSON)
│   │   └── errors.py               # Custom exception classes
│   │
│   ├── models/
│   │   ├── tiny_classifier.onnx    # INT8 quantized (200 KB)
│   │   ├── escalation_model.onnx   # Larger classifier (5 MB)
│   │   └── metadata.json           # Model versioning + input specs
│   │
│   ├── tests/
│   │   ├── test_screen_capture.py
│   │   ├── test_gate.py
│   │   ├── test_classifier.py
│   │   ├── test_notification.py
│   │   ├── test_deduplication.py
│   │   └── fixtures/
│   │       ├── sample_windows/     # Mock Overwatch screenshots per resolution
│   │       ├── calibration_profiles/
│   │       └── test_data.json
│   │
│   ├── pyproject.toml              # uv project configuration
│   ├── uv.lock                     # uv lock file (pinned versions)
│   ├── .python-version             # Python 3.11 version file
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── pages/
│   │   ├── components/
│   │   └── ...
│   └── ...
│
├── shared/
│   ├── types.ts                    # Shared type definitions (GameState, Evidence)
│   └── constants.ts
│
├── docs/                           # Generated by spec process
├── specs/                          # Generated by spec process
└── ...
```

---

## 4. Complete API Contracts (MCP Tools)

### Tool 1: screen.perceive_state

**Purpose**: Classify current game state from screen capture

**Request:**
```json
{
  "timestamp": "2026-02-06T14:30:45.123Z",
  "resolution": "1920x1080",
  "debug": false
}
```

**Response (Success 200):**
```json
{
  "state": "MATCH_FOUND",
  "confidence": 0.94,
  "timestamp": "2026-02-06T14:30:45.500Z",
  "inference_latency_ms": 42,
  "evidence": {
    "gate_triggered": true,
    "gate_signals": {
      "pixel_diff_pct": 15.3,
      "histogram_change": 0.78
    },
    "classifier_version": "tiny_v1.0",
    "model_name": "TinyMobileNetV3",
    "cropped_regions": [
      {
        "name": "match_found_button",
        "crop_coords": [960, 540, 1200, 600],
        "confidence_per_region": 0.96
      }
    ],
    "escalation_used": false
  }
}
```

**Response (Error 400):**
```json
{
  "error": "WindowNotFoundError",
  "error_code": "ERR_WIN_NOT_FOUND",
  "message": "Overwatch window not found. Is the game running?",
  "timestamp": "2026-02-06T14:30:45.500Z"
}
```

**Error Codes:**
- `200` — Success
- `400` — WindowNotFoundError, ResolutionMismatchError
- `503` — AIInferenceError (model initialization failed)
- `429` — RateLimitedError (too many requests)

---

### Tool 2: screen.capture_regions

**Purpose**: Capture cropped UI regions for inference

**Request:**
```json
{
  "resolution": "1920x1080",
  "regions": [
    {
      "name": "queue_icon",
      "crop_normalized": [0.45, 0.25, 0.55, 0.35]
    },
    {
      "name": "match_found_popup",
      "crop_normalized": [0.40, 0.40, 0.60, 0.60]
    }
  ],
  "format": "jpg"
}
```

**Response (Success 200):**
```json
{
  "timestamp": "2026-02-06T14:30:45.123Z",
  "resolution": "1920x1080",
  "regions": [
    {
      "name": "queue_icon",
      "data_base64": "iVBORw0KGgoAAAANSUhEUgAAAA...",
      "format": "jpg",
      "size_bytes": 1240
    }
  ],
  "total_capture_time_ms": 8
}
```

---

### Tool 3: notify.desktop

**Purpose**: Send Windows desktop notification

**Request:**
```json
{
  "title": "MATCH FOUND!",
  "body": "Your team has found a match! Confidence: 94%",
  "urgency": "high",
  "sound": true,
  "action_url": null
}
```

**Response (Success 200):**
```json
{
  "notification_id": "ow_notif_20260206_143045_123",
  "sent_at": "2026-02-06T14:30:45.600Z",
  "delivered": true
}
```

---

### Tool 4: notify.discord

**Purpose**: Send Discord webhook notification

**Request:**
```json
{
  "webhook_url": "https://discordapp.com/api/webhooks/12345/abcdef",
  "content": "MATCH FOUND! 🎮 Confidence: 94%",
  "embed": {
    "title": "Overwatch Match Detected",
    "description": "Your team has found a match!",
    "color": 3498db,
    "fields": [
      { "name": "Confidence", "value": "94%", "inline": true },
      { "name": "Detection Time", "value": "<50ms", "inline": true }
    ]
  }
}
```

**Response (Success 200):**
```json
{
  "discord_message_id": "123456789",
  "status": "delivered",
  "timestamp": "2026-02-06T14:30:45.700Z"
}
```

**Response (Error 429 — Rate Limited):**
```json
{
  "error": "RateLimitedError",
  "message": "Discord rate limit exceeded. Retry-After: 2s",
  "retry_after_ms": 2000,
  "timestamp": "2026-02-06T14:30:45.700Z"
}
```

---

## 5. Authentication & Security

### JWT (Not Used for v1)
- Single-user Windows app, no login
- Discord webhook auth via secret URL in env vars
- All credentials stored in `.env` file (not committed to git)

### Secret Management
- `DISCORD_WEBHOOK_URL` — environment variable, sourced from `.env`
- Never logged or exposed in error messages
- Loaded at startup, cached in memory, never written to disk temp files

### Rate Limiting
- Discord webhooks: max 2 requests/second (built-in)
- Screen capture: max 1 capture every 100ms (configurable, 500ms default)
- AI inference: single-threaded, serialized queue

---

## 6. Service Layer Architecture

### Layer 1: MCP Servers (Node.js + Express)
```typescript
// Thin HTTP wrapper around backend services
app.post('/screen/perceive-state', (req, res) => {
  // Delegate to Python backend via stdio or IPC
  pythonBackend.perceiveState(req.body).then(res.json);
});
```

**Responsibility**: HTTP routing, request validation, response serialization

### Layer 2: Orchestration Agent (Strands SDK, Python)
```python
# Main perception loop
while running:
  screenshot = screen_capture.grab()
  if gate.should_process(screenshot):
    state = classifier.predict(screenshot)
    if confidence < ESCALATION_THRESHOLD:
      state = escalation_model.predict(screenshot)
    
    if should_notify(state):
      notification_queue.enqueue(state)
```

**Responsibility**: Main event loop, agent state machine, decision making

### Layer 3: Service Logic (Python)
- `ScreenCapture` — Windows DCE API calls
- `Gate` — Heuristic evaluation (pixel diff, histogram)
- `Classifier` — ONNX Runtime inference
- `NotificationQueue` — Deduplication, retry logic
- `Repository` — SQLite access

**Responsibility**: Domain logic, error handling, logging

### Layer 4: Data Access (SQLite)
```sql
-- calibration_profiles table
CREATE TABLE calibration_profiles (
  id INTEGER PRIMARY KEY,
  resolution TEXT NOT NULL UNIQUE,
  profile_data BLOB NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- detection_history table
CREATE TABLE detection_history (
  id INTEGER PRIMARY KEY,
  state TEXT NOT NULL,
  confidence REAL NOT NULL,
  resolution TEXT NOT NULL,
  inference_latency_ms INTEGER,
  evidence_json TEXT,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- notification_log table
CREATE TABLE notification_log (
  id INTEGER PRIMARY KEY,
  notification_type TEXT NOT NULL, -- 'desktop' or 'discord'
  state TEXT NOT NULL,
  status TEXT NOT NULL, -- 'sent', 'failed', 'retry'
  retry_count INTEGER DEFAULT 0,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 7. Error Handling

### Custom Exception Classes

```python
# errors.py

class OverwatchQueueError(Exception):
    """Base exception for all domain errors"""
    pass

class WindowNotFoundError(OverwatchQueueError):
    """Overwatch window not found on screen"""
    http_status = 400
    error_code = "ERR_WIN_NOT_FOUND"

class ResolutionMismatchError(OverwatchQueueError):
    """Screen resolution changed unexpectedly"""
    http_status = 400
    error_code = "ERR_RES_MISMATCH"

class AIInferenceError(OverwatchQueueError):
    """AI model inference failed"""
    http_status = 503
    error_code = "ERR_AI_INFERENCE"

class NoCalibrationProfileError(OverwatchQueueError):
    """Calibration profile not found for resolution"""
    http_status = 400
    error_code = "ERR_NO_CALIBRATION"

class SelfNotificationError(OverwatchQueueError):
    """Attempted to notify while already in a match"""
    http_status = 400
    error_code = "ERR_SELF_NOTIF"

class RateLimitedError(OverwatchQueueError):
    """Rate limit exceeded (Discord or internal)"""
    http_status = 429
    error_code = "ERR_RATE_LIMITED"

class DiscordWebhookError(OverwatchQueueError):
    """Discord webhook delivery failed (retryable)"""
    http_status = 500
    error_code = "ERR_DISCORD_WEBHOOK"
    retryable = True
```

### Error Propagation

```
MCP Tool (perceive_state)
  │
  ├─→ ScreenCapture.grab()
  │     └─→ WindowNotFoundError → HTTP 400
  │
  ├─→ Gate.should_process()
  │     └─→ (no error)
  │
  ├─→ Classifier.predict()
  │     └─→ AIInferenceError → HTTP 503 (retry at agent level)
  │
  └─→ Response serialized, returned to caller
```

---

## 8. Rate Limiting Rules

| Endpoint / Service | Limit | Consequence |
|----------|-------|-------------|
| `perceive_state` | 1 req / 100ms (10 req/s max) | Queued internally, skipped if busy |
| `capture_regions` | 1 req / 100ms | Queued internally |
| `notify.discord` | 2 req / sec (Discord limit) | Exponential backoff + queue (1s, 2s, 4s, 8s) |
| `notify.desktop` | Unlimited (OS-buffered) | Windows handles queuing |
| Screenshot cycle | 500ms default (configurable) | Main event loop cadence |
| AI inference | Single-threaded (serialized) | Backpressure: skip frames if inference >400ms |

---

## 9. Middleware Chain Order

```
Request → Logger → ValidationMiddleware → ErrorHandlerMiddleware → Router
                                                                       │
        ┌────────────────────────────────────────────────────────────┘
        │
        ├─→ ScreenCaptureService
        ├─→ GateService
        ├─→ ClassifierService
        ├─→ DeduplicationService
        ├─→ NotificationQueueService
        │
        └─→ Response Serializer → Logger → Send

Error bubbles up:
   Domain Error → ErrorHandler → HTTP Response (400/429/503)
```

---

## 10. Dependency Injection

```python
# config.py
class ServiceContainer:
    def __init__(self):
        self.logger = Logger(LogLevel.INFO)
        self.screen_capture = ScreenCaptureService(self.logger)
        self.gate = GateService(self.logger)
        self.classifier = ClassifierService(
            model_path="models/tiny_classifier.onnx",
            logger=self.logger
        )
        self.notification_queue = NotificationQueueService(
            discord_webhook_url=os.getenv("DISCORD_WEBHOOK_URL"),
            logger=self.logger
        )
        self.repository = SQLiteRepository(
            db_path="local.db",
            logger=self.logger
        )

# main.py
container = ServiceContainer()
agent = PerceptionAgent(
    screen_capture=container.screen_capture,
    gate=container.gate,
    classifier=container.classifier,
    notification_queue=container.notification_queue,
    repository=container.repository,
    logger=container.logger
)
```

---

## 11. Logging Strategy

### Log Levels & Format

```json
{
  "timestamp": "2026-02-06T14:30:45.123Z",
  "level": "INFO",
  "service": "ScreenCaptureService",
  "message": "Screenshot captured",
  "resolution": "1920x1080",
  "size_bytes": 3145728,
  "elapsed_ms": 8
}
```

**Per-Service Log Output:**

| Service | Log Events |
|---------|-----------|
| **ScreenCaptureService** | Window found, capture start/end, resolution detected, errors |
| **GateService** | Gate triggered/not triggered, pixel_diff_pct, histogram_change |
| **ClassifierService** | Model loaded, inference start/end, confidence score, escalation decision |
| **NotificationQueue** | Enqueue, deduplicate (skipped), send start, retry attempt, success/failure |
| **Repository** | Query executed, result count, transaction commit/rollback |

**Log Levels:**
- `DEBUG` — Frame-by-frame gate signals (disabled in production)
- `INFO` — State transitions, notifications sent, calibration loaded
- `WARN` — Confidence <threshold, model fallback, Discord rate limit
- `ERROR` — Window not found, AI crash, notification delivery failure
- `FATAL` — Process crash, database corruption

**Retention Policy:**
- Logs rotated daily, kept for 7 days
- JSON formatted for `tail -f` friendly parsing
- No PII (screenshot content never logged, only metadata)

---

## 12. Classifier Confidence & Escalation Logic

```python
def perceive_state(screenshot):
    """
    Returns (state, confidence, evidence)
    
    Decision tree:
      conf >= 0.90 → return immediately (high confidence)
      0.70 <= conf < 0.90 → run escalation model if available
      conf < 0.70 → return UNKNOWN or prev state (too uncertain)
    """
    
    # Tiny classifier (always runs)
    state, tiny_conf = classifier.predict(screenshot, model="tiny")
    
    if tiny_conf >= 0.90:
        return (state, tiny_conf, evidence)
    
    if tiny_conf < 0.70:
        # Too uncertain, return previous state from repository
        prev_state = repository.get_last_state()
        return (prev_state or "IDLE", tiny_conf, evidence)
    
    # 0.70-0.90: escalate
    state_escalated, escalation_conf = classifier.predict(
        screenshot, model="escalation"
    )
    
    # Average the confidences
    final_conf = (tiny_conf + escalation_conf) / 2.0
    return (state_escalated, final_conf, evidence)
```

---

## 13. State Transitions & Validation

Allowed transitions:
```
IDLE
  ↓
QUEUE
  ↓
MATCH_FOUND
  ↓
HERO_SELECT
  ↓
LOADING
  ↓
IN_GAME
  ↓
↺ (repeats or → IDLE on disconnection)
```

**Hysteresis**: Prevent jitter by requiring 2 consecutive same-state detections (within 1s) before transitioning.

---

## 14. Performance Budget

| Component | Budget | Priority |
|-----------|--------|----------|
| Screen capture | <10ms | Critical |
| Gate heuristics | <5ms | Critical |
| Tiny classifier | <50ms (must, 95%ile) | Critical |
| Escalation classifier | <100ms (should) | High |
| Deduplication check | <1ms | Medium |
| Discord webhook | <500ms (non-blocking, async) | Low |
| Total perception cycle | <100ms (p95) | Critical |
| CPU usage idle | <10% sustained | Critical |
| Memory usage steady-state | <200 MB | High |

---

## 15. Testing Strategy

### Unit Tests (70% of coverage)

```python
# test_classifier.py
def test_classifier_tiny_model_loaded():
    classifier = ClassifierService("models/tiny_classifier.onnx")
    assert classifier.model is not None
    assert classifier.model.input_shape == (1, 224, 224, 3)

def test_perceive_state_match_found_confidence():
    classifier = ClassifierService(...)
    state, conf = classifier.predict(mock_match_found_image)
    assert state == "MATCH_FOUND"
    assert conf > 0.85
```

### Integration Tests (20% of coverage)

```python
# test_notification_queue_integration.py
def test_notification_sent_desktop_and_discord():
    queue = NotificationQueueService(webhook_url="https://...")
    queue.enqueue("MATCH_FOUND", confidence=0.94)
    
    # Wait for async delivery
    time.sleep(1)
    
    # Verify both notifications sent
    assert desktop_notif_received()
    assert discord_webhook_called()
```

### E2E Tests (10% of coverage)

```python
# test_e2e_queue_to_notification.py
def test_full_flow_queue_to_match_found():
    """Simulate user playing, queueing, match found"""
    
    # 1. Load calibration for 1920x1080
    assert calibration_loaded()
    
    # 2. Simulate idle → queue screen change
    agent.process_screenshot(idle_image)
    agent.process_screenshot(queue_image)
    assert agent.state == "QUEUE"
    
    # 3. Simulate match found
    agent.process_screenshot(match_found_image)
    time.sleep(1)
    
    # 4. Verify notification sent
    assert notification_received()
    assert repository.get_last_state() == "MATCH_FOUND"
```

---

## 16. Next Steps

1. ✅ **Backend spec approved** → Frontend lead reads this
2. ⏭️ **Implement MCP scaffolding** (Sprint 0.1) → Python + Node.js project structure
3. ⏭️ **Build screen capture** (Sprint 0.2) → Windows DCE proof-of-concept
4. ⏭️ **Integrate ONNX Runtime** (Sprint 0.3) → Tiny classifier loaded and tested
5. ⏭️ **Gate heuristic prototype** (Sprint 0.4) → Detect screen changes
6. ⏭️ **Notification service** (Sprint 1) → Desktop + Discord

**Owner**: Backend Lead  
**Stakeholders**: Arch Lead, DB Architect, QA Lead, DevOps Lead
