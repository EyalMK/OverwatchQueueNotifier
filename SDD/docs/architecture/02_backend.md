# Backend Architecture Deep Dive
## Overwatch AI Queue Detection & Notification App

**Version**: 1.0  
**Owner**: Backend Lead  
**Last Updated**: February 6, 2026

---

## 1. Backend Technology Stack

### Dependency Management with uv

Dependencies are managed via `pyproject.toml` with [uv](https://github.com/astral-sh/uv) for fast resolution and installation:

```toml
# pyproject.toml
[project]
name = "ow-queue-notifier-backend"
version = "1.0.0"
description = "AI-powered Overwatch queue detection backend"
requires-python = ">=3.11"

dependencies = [
    "onnxruntime>=1.16.0",      # AI inference (CPU-only, Intel-optimized)
    "onnx>=1.14.0",              # Model format
    "opencv-python>=4.8.0",      # Image processing (captures, regions)
    "pydantic>=2.0",              # Config validation, API contracts
    "sqlalchemy>=2.0",            # ORM (SQLite database)
    "alembic>=1.12.0",            # Schema migrations
    "pydantic-settings>=2.0",     # Environment configuration
    "python-dotenv>=1.0",         # .env file support
    "pywin32>=305",               # Windows API (DCE screen capture)
    "discord-webhook>=1.3",       # Discord notifications
    "strands-agents>=0.1.0",      # Agent orchestration & MCP client/server
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",                # Testing framework
    "pytest-cov>=4.0",            # Coverage reporting
    "pytest-asyncio>=0.20.0",    # Async test support
    "black>=23.0",                # Code formatter
    "pylint>=2.17.0",             # Linter
    "mypy>=1.0",                  # Type checker
]
```

### Installation & Usage

```bash
# Install uv (one-time)
pip install uv

# Install all dependencies + dev (creates .venv automatically)
uv sync --all-extras --dev

# Run tests
uv run pytest tests/

# Type check
uv run mypy src/

# Format and lint
uv run black src/
uv run pylint src/

# Run application
uv run python -m src.main

# Update lock file (uv.lock)
uv lock

# Freeze to lock file (for CI/CD reproducibility)
uv sync --frozen
```

---

## 2. Package Structure

```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py                      # Entry point, daemon loop
│   ├── config.py                    # Pydantic settings loader
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py              # SQLAlchemy ORM models
│   │   │   ├── CalibrationProfile
│   │   │   ├── DetectionHistory
│   │   │   ├── NotificationLog
│   │   │   └── Settings
│   │   └── schemas.py               # Pydantic schemas (API contracts)
│   │       ├── PerceiveStateRequest
│   │       ├── PerceiveStateResponse
│   │       ├── StateTransition
│   │       └── NotificationPayload
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── gate.py                  # Heuristics (brightness check)
│   │   ├── classifier.py            # ONNX Int8 model inference
│   │   ├── escalation.py            # FP32 fallback model
│   │   ├── models/
│   │   │   ├── classifier.onnx      # Downloaded pre-trained
│   │   │   └── escalation.onnx      # Downloaded pre-trained
│   │   └── utils.py                 # Preprocessing, confidence scoring
│   ├── perception/
│   │   ├── __init__.py
│   │   ├── engine.py                # Orchestrates gate+classifier+escalation
│   │   ├── screen.py                # Screen capture via MCP
│   │   └── state_machine.py         # State transitions (idle→queue→match)
│   ├── notifications/
│   │   ├── __init__.py
│   │   ├── desktop.py               # Windows toast notifications
│   │   ├── discord.py               # Discord webhook integration
│   │   └── deduplication.py         # Prevents burst alerts
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py            # SQLite session factory
│   │   ├── migrations/              # Alembic versions
│   │   │   └── versions/
│   │   │       ├── 001_initial_schema.py
│   │   │       └── 002_add_indexes.py
│   │   └── repositories/            # Data access objects (DAO)
│   │       ├── calibration_repo.py
│   │       ├── detection_repo.py
│   │       ├── notification_repo.py
│   │       └── settings_repo.py
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── server.py                # MCP server registration
│   │   ├── tools/
│   │   │   ├── screen_perceive.py   # Tool: perceive_state
│   │   │   ├── screen_capture.py    # Tool: capture_regions
│   │   │   ├── notify_desktop.py    # Tool: desktop notifications
│   │   │   └── notify_discord.py    # Tool: discord notifications
│   │   └── handlers.py              # Tool invocation handlers
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py                # Structured JSON logging
│   │   ├── errors.py                # Custom exception classes
│   │   ├── decorators.py            # @async_timer, @retry_with_backoff
│   │   └── validators.py            # Pydantic custom validators
│   └── cli/
│       ├── __init__.py
│       └── dev_cli.py               # Manual commands for testing
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # Pytest fixtures
│   ├── unit/
│   │   ├── test_gate.py
│   │   ├── test_classifier.py
│   │   ├── test_state_machine.py
│   │   ├── test_deduplication.py
│   │   └── test_discord.py
│   ├── integration/
│   │   ├── test_perception_pipeline.py
│   │   ├── test_database.py
│   │   ├── test_mcp_tools.py
│   │   └── test_notification_dispatch.py
│   └── fixtures/
│       ├── __init__.py
│       ├── screenshots/             # Mock screenshots
│       └── models.py                # Fake ONNX models for testing
├── requirements.txt
├── pyproject.toml
├── pytest.ini
├── .env.example
└── README.md
```

---

## 3. Core Service Layer

### 3.1 Perception Engine (Main Loop)

```python
# src/perception/engine.py

class PerceptionEngine:
    """Orchestrates AI perception: gate + classifier + escalation."""
    
    def __init__(self, db_session, config: Config):
        self.db = db_session
        self.config = config
        self.gate = GateHeuristics()
        self.classifier = ClassifierModel()
        self.escalation = EscalationModel()
        self.state_machine = StateMachine()
        self.deduplicator = NotificationDeduplicator()
        self.metrics = PerformanceMetrics()
    
    async def perceive_state(self) -> PerceiveStateResponse:
        """Main perception loop (called every 100ms)."""
        # Step 1: Capture regions
        start = time.time()
        regions = await self.capture_regions()
        
        # Step 2: Gate heuristics (always-on, <5ms)
        gate_conf = self.gate.evaluate(regions['queue_status'])
        
        # Step 3: Classifier if gate uncertain
        if gate_conf < 0.60:
            clf_conf = await self.classifier.infer(regions)
        else:
            clf_conf = gate_conf
        
        # Step 4: Escalation if classifier uncertain
        if clf_conf < 0.85:
            final_conf = await self.escalation.infer(regions)
        else:
            final_conf = clf_conf
        
        # Step 5: State machine
        state = self.state_machine.evaluate(final_conf)
        elapsed_ms = (time.time() - start) * 1000
        
        # Step 6: Log to database
        await self.db_insert_detection(
            state=state,
            confidence=final_conf,
            evidence={
                'gate_score': gate_conf,
                'classifier_score': clf_conf,
                'escalation_score': final_conf
            },
            latency_ms=elapsed_ms
        )
        
        # Step 7: Handle notifications
        await self.maybe_notify(state)
        
        # Step 8: Update metrics
        self.metrics.record(elapsed_ms)
        
        return PerceiveStateResponse(
            state=state,
            confidence=final_conf,
            latency_ms=elapsed_ms
        )
    
    async def maybe_notify(self, state: str):
        """Dispatch notifications on state transition."""
        previous_state = self.state_machine.current_state
        
        if previous_state == "idle" and state == "queue":
            # Dedup check
            if not self.deduplicator.should_suppress():
                await self.notify_manager.send_all([
                    NotificationPayload(
                        channel="desktop",
                        title="Queue Detected",
                        body="Your team has found a queue!"
                    ),
                    NotificationPayload(
                        channel="discord",
                        message="🎮 Queue detected!"
                    )
                ])
        
        self.state_machine.current_state = state
```

---

### 3.2 Agent Orchestration with Strands

The backend uses [Strands Agents](https://github.com/strands-ai/agents) for coordinating multi-agent perception and notification workflows:

```python
# src/agents/perception_agent.py

from strands import Agent, tool
from strands_mcp import MCPClient

class QueuePerceptionAgent(Agent):
    """Multi-agent orchestration for queue detection."""
    
    def __init__(self, config: Config):
        super().__init__("queue-perception-agent")
        self.config = config
        self.perception_engine = PerceptionEngine(config)
        self.notification_agent = NotificationAgent(config)
        self.mcp_client = MCPClient()
    
    @tool
    async def perceive_and_notify(self) -> dict:
        """
        Main agent task: perceive state and trigger notifications.
        Called by scheduler every 100ms.
        """
        # Run perception pipeline
        response = await self.perception_engine.perceive_state()
        
        # If state changed, delegate to notification agent
        if response.state_changed:
            notification_result = await self.notification_agent.handle_state_change(
                previous_state=response.previous_state,
                current_state=response.state,
                confidence=response.confidence
            )
            return {
                "perception": {
                    "state": response.state,
                    "confidence": response.confidence,
                    "latency_ms": response.latency_ms
                },
                "notification": notification_result
            }
        
        return {
            "perception": {
                "state": response.state,
                "confidence": response.confidence,
                "latency_ms": response.latency_ms
            },
            "notification": None
        }
    
    @tool
    async def get_calibration(self, resolution: str) -> dict:
        """Retrieve calibration profile for given resolution."""
        return await self.perception_engine.load_calibration(resolution)


class NotificationAgent(Agent):
    """Multi-channel notification coordination."""
    
    def __init__(self, config: Config):
        super().__init__("notification-agent")
        self.config = config
        self.desktop_notifier = DesktopNotifier()
        self.discord_notifier = DiscordNotifier(config.discord_webhook)
        self.deduplicator = NotificationDeduplicator()
    
    @tool
    async def handle_state_change(
        self,
        previous_state: str,
        current_state: str,
        confidence: float
    ) -> dict:
        """Coordinate notifications across desktop and Discord."""
        
        # Check deduplication
        if self.deduplicator.should_suppress():
            return {"suppressed": True}
        
        results = {}
        
        # Desktop notification
        if current_state == "queue":
            results["desktop"] = await self.desktop_notifier.notify(
                title="Queue Detected",
                body=f"Confidence: {confidence:.1%}"
            )
        
        # Discord notification
        if current_state in ["queue", "match_found"]:
            results["discord"] = await self.discord_notifier.notify(
                message=f"🎮 Queue detected! (confidence: {confidence:.1%})"
            )
        
        return results


# Bootstrap agents in main.py
# src/main.py

async def main():
    """Agent bootstrap and event loop."""
    config = load_config()
    
    # Create agents
    perception_agent = QueuePerceptionAgent(config)
    
    # Register MCP tools (Strands introspection)
    await perception_agent.register_mcp_tools()
    
    # Start periodic task via Strands scheduler
    from strands.scheduler import IntervalScheduler
    
    scheduler = IntervalScheduler()
    scheduler.add_task(
        perception_agent.perceive_and_notify,
        interval_ms=100,  # Every 100ms
        name="perception-loop"
    )
    
    # Run indefinitely
    await scheduler.start()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

**Key Benefits of Strands Agents:**

| Benefit | Details |
|---------|---------|
| **MCP Native** | Built-in support for MCP client/server patterns—perception & notification agents expose tools |
| **Async Orchestration** | Natural async/await coordination between perception→deduplication→notification |
| **Tool Registry** | Agent tools auto-discoverable by MCP clients (e.g., Node.js frontend) |
| **Scheduler** | Built-in interval scheduling (100ms loop) without background threads |
| **Error Handling** | Agent-level error recovery and retry logic |

---

### 3.3 AI Models Layer

```python
# src/ai/classifier.py

class ClassifierModel:
    """Int8 quantized ONNX model for queue state classification."""
    
    def __init__(self, path="src/ai/models/classifier.onnx"):
        self.session = ort.InferenceSession(
            path,
            providers=["CPUExecutionProvider"],
            sess_options=self._get_session_options()
        )
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
    
    async def infer(self, regions: Dict[str, np.ndarray]) -> float:
        """Runs inference on captured regions."""
        # Preprocess
        queue_region = regions['queue_status']
        processed = self._preprocess(queue_region)
        
        # Quantize to Int8
        quantized = self._quantize_int8(processed)
        
        # Infer (30–40ms)
        outputs = self.session.run(
            [self.output_name],
            {self.input_name: quantized}
        )
        
        # Postprocess
        confidence = self._postprocess(outputs[0])
        
        return confidence
    
    def _preprocess(self, image: np.ndarray) -> np.ndarray:
        """Normalize to [0,1], resize to model input size."""
        # Resize to 224×224 (standard ImageNet)
        resized = cv2.resize(image, (224, 224))
        # Normalize
        normalized = resized.astype(np.float32) / 255.0
        # HWC → NCHW
        batched = np.expand_dims(normalized, 0)
        transposed = np.transpose(batched, (0, 3, 1, 2))
        return transposed
    
    def _quantize_int8(self, data: np.ndarray) -> np.ndarray:
        """Convert FP32 to Int8 for faster inference."""
        # Scale to [-128, 127]
        return np.clip(data * 127, -128, 127).astype(np.int8)
    
    def _postprocess(self, output: np.ndarray) -> float:
        """Convert model output to confidence [0, 1]."""
        # Softmax over queue/idle classes
        softmax = np.exp(output) / np.sum(np.exp(output))
        confidence = float(softmax[0, 1])  # Queue class
        return confidence
```

---

### 3.4 State Machine

```python
# src/perception/state_machine.py

class StateMachine:
    """Manages state transitions and prevents spurious alerts."""
    
    STATES = ["idle", "queue", "match_found", "hero_select", "loading", "in_game"]
    CONFIDENCE_THRESHOLD = 0.80
    STABILITY_WINDOW_MS = 500  # Wait 500ms before transitioning
    
    def __init__(self):
        self.current_state = "idle"
        self.confidence_history = collections.deque(maxlen=10)
        self.last_transition = time.time()
    
    def evaluate(self, confidence: float) -> str:
        """Determine next state from confidence score."""
        # Record confidence
        self.confidence_history.append(confidence)
        
        # Compute moving average
        avg_confidence = np.mean(self.confidence_history)
        
        # State decision logic
        if avg_confidence > self.CONFIDENCE_THRESHOLD:
            new_state = "queue"
        else:
            new_state = "idle"
        
        # Check stability (require 500ms of consistent signal)
        if new_state != self.current_state:
            elapsed_since_last = time.time() - self.last_transition
            if elapsed_since_last < self.STABILITY_WINDOW_MS / 1000.0:
                # Not stable yet, keep current state
                return self.current_state
            else:
                # Stable, transition allowed
                self.last_transition = time.time()
                self.current_state = new_state
        
        return self.current_state
```

---

### 3.5 Database Repository Layer

```python
# src/database/repositories/detection_repo.py

class DetectionRepository:
    """Data access for detection_history table."""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def insert(self, detection: Detection) -> int:
        """Insert detection record."""
        record = DetectionHistoryModel(
            state=detection.state,
            confidence=detection.confidence,
            evidence=json.dumps(detection.evidence),
            timestamp=datetime.now(timezone.utc)
        )
        self.session.add(record)
        self.session.commit()
        return record.id
    
    async def get_recent(self, limit: int = 100) -> List[Detection]:
        """Get recent N detections, ordered by timestamp DESC."""
        records = self.session.query(DetectionHistoryModel)\
            .order_by(DetectionHistoryModel.timestamp.desc())\
            .limit(limit)\
            .all()
        
        return [Detection.from_orm(r) for r in records]
    
    async def cleanup_old(self, older_than_hours: int = 24):
        """Delete detections older than N hours."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=older_than_hours)
        self.session.query(DetectionHistoryModel)\
            .filter(DetectionHistoryModel.timestamp < cutoff)\
            .delete()
        self.session.commit()
```

---

## 4. MCP Tool Implementations

### Tool 1: screen.perceive_state

```python
# src/mcp/tools/screen_perceive.py

@mcp_tool(name="screen.perceive_state")
async def perceive_state(
    request: PerceiveStateRequest = Body(...)
) -> PerceiveStateResponse:
    """
    Detects current Overwatch queue state via AI perception.
    
    **Request**:
    ```json
    {
      "resolution": {"width": 1920, "height": 1080},
      "use_escalation": true
    }
    ```
    
    **Response**:
    ```json
    {
      "state": "queue",
      "confidence": 0.87,
      "latency_ms": 52,
      "evidence": {
        "gate_score": 0.89,
        "classifier_score": 0.87,
        "escalation_score": null
      }
    }
    ```
    
    **Errors**:
    - 400 Bad Request: Invalid resolution
    - 503 Service Unavailable: Models not loaded
    """
    engine = get_perception_engine()
    response = await engine.perceive_state()
    return response
```

---

## 5. Error Handling & Logging

### Custom Exceptions

```python
# src/utils/errors.py

class OWQueueNotifierError(Exception):
    """Base exception."""
    pass

class ModelLoadError(OWQueueNotifierError):
    """ONNX model failed to load."""
    pass

class ScreenCaptureError(OWQueueNotifierError):
    """Windows screen capture failed."""
    pass

class NotificationError(OWQueueNotifierError):
    """Discord or desktop notification failed."""
    pass

class DatabaseError(OWQueueNotifierError):
    """SQLite operation failed."""
    pass

class CalibrationError(OWQueueNotifierError):
    """Calibration profile invalid or missing."""
    pass
```

### Structured Logging

```python
# src/utils/logger.py

import logging
import json

class JSONFormatter(logging.Formatter):
    """Outputs structured JSON logs."""
    
    def format(self, record):
        log_dict = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'module': record.module,
            'function': record.funcName,
            'message': record.getMessage(),
            'latency_ms': getattr(record, 'latency_ms', None),
            'state': getattr(record, 'state', None),
            'confidence': getattr(record, 'confidence', None),
        }
        return json.dumps(log_dict)

# Usage
logger.info("Queue detected", extra={
    'state': 'queue',
    'confidence': 0.87,
    'latency_ms': 52
})
```

---

## 6. Testing Strategy

### Unit Test Example: Gate Heuristics

```python
# tests/unit/test_gate.py

@pytest.fixture
def gate():
    return GateHeuristics(brightness_threshold=100)

def test_bright_image_passes_gate(gate):
    """Bright image (high brightness) should pass gate."""
    # Create mock image: all white (brightness 255)
    bright_image = np.ones((100, 100, 3), dtype=np.uint8) * 255
    
    confidence = gate.evaluate(bright_image)
    
    assert confidence > 0.8, "Bright queue region should pass gate"

def test_dark_image_fails_gate(gate):
    """Dark image (low brightness) should fail gate."""
    dark_image = np.ones((100, 100, 3), dtype=np.uint8) * 50
    
    confidence = gate.evaluate(dark_image)
    
    assert confidence < 0.6, "Dark queue region should fail gate"
```

---

## 7. Performance Profiling

### Latency Targets

```python
# Profile on every sprint

def profile_perception_latency():
    """Measure e2e latency: capture → state."""
    latencies = []
    for _ in range(100):
        start = time.perf_counter()
        state = perceive_state()
        elapsed_ms = (time.perf_counter() - start) * 1000
        latencies.append(elapsed_ms)
    
    print(f"P50:  {np.percentile(latencies, 50):.1f}ms")
    print(f"P95:  {np.percentile(latencies, 95):.1f}ms")
    print(f"P99:  {np.percentile(latencies, 99):.1f}ms")
    print(f"Max:  {max(latencies):.1f}ms")
    
    assert np.percentile(latencies, 95) < 100, "P95 must be <100ms"
```

---

## 8. Deployment Checklist

- [ ] ONNX models downloaded and quantized to Int8
- [ ] SQLite schema migrated (alembic upgrade head)
- [ ] Discord webhook URL configured in .env
- [ ] First-run calibration workflow tested
- [ ] Performance profiling complete (latency <100ms p95)
- [ ] All unit tests pass (pytest -v)
- [ ] Integration tests pass
- [ ] E2E test: Queue detection → notification working
- [ ] Logs validated (JSON format, no sensitive data)
- [ ] Database vacuum scheduled (nightly)

---

**Owner**: Backend Lead  
**Last Updated**: February 6, 2026
