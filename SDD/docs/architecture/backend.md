# Backend Architecture
## Overwatch AI Queue Detection & Notification App

**Generated**: February 6, 2026  
**Version**: 1.0

---

## Layered Architecture

```
                      User/Tray UI (React)
                            │ IPC
                            ▼
        ┌─────────────────────────────────────┐
        │       HTTP API / MCP Handlers        │
        │  (screen.perceive_state, notify.*)  │
        └─────────────────┬───────────────────┘
                          │
        ┌─────────────────▼───────────────────┐
        │          Controllers/Tools           │
        │   (Request validation, routing)     │
        └─────────────────┬───────────────────┘
                          │
        ┌─────────────────▼───────────────────┐
        │          Services Layer             │
        │  ├─ PerceptionService               │
        │  ├─ NotificationService             │
        │  ├─ CalibrationService              │
        │  └─ StateManagementService          │
        └─────────────────┬───────────────────┘
                          │
        ┌─────────────────▼───────────────────┐
        │       Domain / Business Logic       │
        │  ├─ GateLogic (heuristics)          │
        │  ├─ Classifier (AI inference)       │
        │  ├─ StateTransitions (enum logic)   │
        │  └─ Deduplication (5s window)       │
        └─────────────────┬───────────────────┘
                          │
        ┌─────────────────▼───────────────────┐
        │      Data Access Layer / Repos      │
        │  ├─ CalibrationRepository           │
        │  ├─ DetectionRepository             │
        │  ├─ NotificationRepository          │
        │  └─ SettingsRepository              │
        └─────────────────┬───────────────────┘
                          │
        ┌─────────────────▼───────────────────┐
        │       External Dependencies         │
        │  ├─ SQLite Database                 │
        │  ├─ ONNX Runtime (AI models)        │
        │  ├─ Windows API (screen capture)    │
        │  ├─ Windows Toast Notifications     │
        │  └─ HTTP (Discord webhooks)         │
        └─────────────────────────────────────┘
```

---

## Directory Structure with Responsibilities

```
backend/
├── src/
│   ├── main.py
│   │   └─ Entry point: Bootstrap Strands agent, start perception loop
│   │
│   ├── perception/
│   │   ├── __init__.py
│   │   ├── screen_capture.py
│   │   │   └─ Windows DCE API wrapper
│   │   │      - GetWindowDC() → BitBlt → DIB → NumPy array
│   │   │      - Returns: RGB frame (1920×1080) in ~8ms
│   │   │
│   │   ├── gate.py
│   │   │   └─ Heuristic gate logic
│   │   │      - Pixel diff % check
│   │   │      - Histogram divergence (Bhattacharyya)
│   │   │      - Config-driven thresholds (env vars)
│   │   │
│   │   ├── classifier.py
│   │   │   └─ AI inference orchestration
│   │   │      - Load tiny + escalation models (ONNX Runtime)
│   │   │      - Crop regions from frame
│   │   │      - Normalize to model input size (224×224)
│   │   │      - Inference with confidence scores
│   │   │      - Escalation logic: if conf <0.85, run larger model
│   │   │
│   │   └── calibration.py
│   │       └─ Per-resolution calibration management
│   │          - Detect Overwatch window, compute screen regions
│   │          - Save crop coordinates + metadata to SQLite
│   │          - Load profile for detected resolution
│   │
│   ├── notification/
│   │   ├── __init__.py
│   │   ├── desktop_notif.py
│   │   │   └─ Windows Toast notification
│   │   │      - Title, body, sound, action URL
│   │   │      - Returns: notification_id + delivery status
│   │   │
│   │   ├── discord_notif.py
│   │   │   └─ Discord webhook HTTP POST
│   │   │      - Embed formatting (title, description, color, timestamp)
│   │   │      - Retry logic (429 rate-limit handling)
│   │   │      - Timeout 5s
│   │   │
│   │   ├── queue.py
│   │   │   └─ In-memory deduplication + dispatch
│   │   │      - 5-second window per state
│   │   │      - Enqueue MATCH_FOUND once, fire once
│   │   │      - Async dispatch to desktop + Discord
│   │   │
│   │   └── retry_policy.py
│   │       └─ Exponential backoff for transient failures
│   │          - Attempt 1: 1s, Attempt 2: 2s, Attempt 3: 4s
│   │          - Max 30s, then log + alert
│   │
│   ├── state/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   │   └─ TypedDicts + Enums
│   │   │      - GameState enum (IDLE, QUEUE, MATCH_FOUND, ...)
│   │   │      - Detection dataclass (state, confidence, timestamp, evidence)
│   │   │      - Evidence dataclass (gate_signals, classifier_info, crops)
│   │   │
│   │   └── repository.py
│   │       └─ Data access abstraction
│   │          - Save/load calibration profiles
│   │          - Log detections + notifications
│   │          - Query history (for dashboard/logs tab)
│   │          - Soft delete for settings
│   │
│   ├── mcp/
│   │   ├── server.py
│   │   │   └─ Node.js Express + HTTP handler
│   │   │      - Expose Python services via JSON HTTP
│   │   │
│   │   └── tools/
│   │       ├── perceive.py
│   │       │   └─ MCP tool: screen.perceive_state
│   │       │      - Request: timestamp, resolution, debug flag
│   │       │      - Response: state, confidence, evidence, latency
│   │       │
│   │       ├── capture.py
│   │       │   └─ MCP tool: screen.capture_regions
│   │       │      - Request: list of normalized crop regions
│   │       │      - Response: Base64-encoded JPG crops
│   │       │
│   │       └── notify.py
│   │           └─ MCP tools: notify.desktop, notify.discord
│   │              - Input: title, body, webhook_url, etc.
│   │              - Output: notification_id, status, timestamp
│   │
│   ├── config.py
│   │   └─ Configuration loader
│   │      - Load env vars (LOG_LEVEL, MCP_PORT, MODEL_PATHS, etc.)
│   │      - Merge with defaults
│   │      - Validate required settings
│   │
│   ├── logger.py
│   │   └─ Structured JSON logging
│   │      - Log to file + stdout
│   │      - Levels: DEBUG, INFO, WARN, ERROR
│   │      - Fields: timestamp, level, service, message, context
│   │
│   └── errors.py
│       └─ Custom exceptions
│          - WindowNotFoundError
│          - CalibrationError
│          - AIInferenceError
│          - NotificationError
│          - RateLimitError
│
├── models/
│   ├── tiny_classifier.onnx
│   │   └─ 200 KB, INT8 quantized
│   │      Input: 224×224×3 RGB normalized [0, 1]
│   │      Output: softmax logits (6 classes: IDLE, QUEUE, MATCH_FOUND, ...)
│   │      Latency: <50ms CPU inference
│   │
│   ├── escalation_model.onnx
│   │   └─ 5 MB, FP32
│   │      Input: 224×224×3 RGB normalized
│   │      Output: softmax logits (6 classes)
│   │      Latency: ~100ms (used only if tiny conf <0.85)
│   │
│   └── metadata.json
│       └─ Model versioning
│          - tiny: {version: "1.0", input_size: 224, classes: [...]}
│          - escalation: {version: "1.0", input_size: 224, classes: [...]}
│
├── tests/
│   ├── conftest.py
│   │   └─ Pytest fixtures (mock models, sample frames, DB)
│   │
│   ├── unit/
│   │   ├── test_gate.py          — Test heuristic logic
│   │   ├── test_classifier.py    — Test AI inference
│   │   ├── test_state_models.py  — Test GameState enum
│   │   ├── test_deduplication.py — Test 5s window dedup
│   │   └── test_retry_policy.py  — Test exponential backoff
│   │
│   ├── integration/
│   │   ├── test_perception_pipeline.py    — Full chain
│   │   ├── test_notification_flow.py      — Detect → Notify
│   │   ├── test_mcp_tools.py              — HTTP tool endpoints
│   │   └── test_database_transactions.py  — SQLite ops
│   │
│   ├── e2e/
│   │   ├── test_queue_to_match_detection_1920x1080.py
│   │   ├── test_false_positive_mitigation.py
│   │   └── test_calibration_per_resolution.py
│   │
│   └── fixtures/
│       ├── mock_screenshots/
│       │   ├── idle_1920x1080.png
│       │   ├── queue_1920x1080.png
│       │   ├── match_found_1920x1080.png
│       │   └── ... (3 resolutions × 6 states = 18 images)
│       │
│       └── test_data.json
│           └─ Seed data: calibration profiles, test settings
│
├── pyproject.toml
│   └─ UV project config
│      dependencies: onnxruntime, numpy, opencv-python, sqlite3, httpx, pydantic
│
├── uv.lock
│   └─ Pinned version lock file
│
├── .python-version
│   └─ Python 3.11
│
└── README.md
```

---

## Dependency Injection Approach

The backend uses **constructor-based dependency injection** via factory functions:

```python
# perception/gate.py
class GateService:
    def __init__(self, config: Config):
        self.config = config
        self.pixel_diff_threshold = config.gate_pixel_diff_threshold

# notification/queue.py
class NotificationQueue:
    def __init__(self, desktop_notif: DesktopNotifier, discord_notif: DiscordNotifier):
        self.desktop = desktop_notif
        self.discord = discord_notif

# main.py (bootstrap)
def create_app(config: Config):
    gate = GateService(config)
    classifier = ClassifierService(config)
    desktop_notif = DesktopNotifier()
    discord_notif = DiscordNotifier(config)
    notif_queue = NotificationQueue(desktop_notif, discord_notif)
    
    perception_agent = PerceptionAgent(gate, classifier, notif_queue)
    return perception_agent
```

**Benefits**:
- Testable: Mock dependencies in tests
- Configurable: Swap implementations without code changes
- Explicit: Clear dependencies in constructor

---

## Error Propagation Through Layers

### Perception Pipeline

```
ScreenCapture.capture()
  └─ Raises: WindowNotFoundError
     Caught by: controller
     Response: 400 error + "Overwatch window not found"

Gate.should_process()
  └─ Returns boolean (no error)

Classifier.predict()
  └─ Raises: AIInferenceError (model not loaded, bad input)
     Caught by: service
     Response: 503 error + retry logic

Notification.send()
  └─ Raises: NotificationError
     Caught by: queue (retry on transient)
     Response: log + alert on persistent failure
```

### Error Response Format (MCP)

```json
{
  "error": "AIInferenceError",
  "error_code": "ERR_AI_INFERENCE",
  "message": "ONNX model inference failed: invalid input shape",
  "timestamp": "2026-02-06T14:30:45.500Z",
  "details": {
    "model": "tiny_classifier.onnx",
    "input_shape": [1, 224, 224],
    "expected_shape": [1, 224, 224, 3]
  }
}
```

---

## Logging Strategy Per Layer

### Routes / MCP Tools Layer
```python
logger.info("screen.perceive_state called", {"resolution": "1920x1080", "debug": False})
```

### Controllers Layer
```python
logger.debug("Perceive request received", {"timestamp": ..., "resolution": ...})
logger.warning("Window not found; retrying", {"attempt": 2})
```

### Services Layer
```python
logger.info("Perception complete", {"state": "MATCH_FOUND", "confidence": 0.94, "latency_ms": 42})
logger.error("Notification send failed", {"notification_type": "discord", "error": ...})
```

### Domain Logic Layer
```python
logger.debug("Gate triggered", {"pixel_diff_pct": 15.3, "histogram_change": 0.78})
logger.debug("Classifier inference", {"model": "tiny_v1.0", "latency_ms": 38})
```

### Data Access Layer
```python
logger.debug("Detection history inserted", {"detection_id": 1234, "state": "MATCH_FOUND"})
```

---

## Summary

The backend follows a **clean layered architecture**:
- **Routes** handle HTTP requests and validation
- **Services** orchestrate business logic
- **Domain logic** encapsulates game state, AI, and decision rules
- **Repositories** abstract data persistence
- **Errors** propagate up with context, caught and formatted at routes

This separation ensures **testability**, **maintainability**, and **clear responsibility boundaries**.
