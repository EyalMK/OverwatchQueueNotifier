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
[project]
name = "ow-queue-notifier-backend"
version = "1.0.0"
description = "AI-powered Overwatch queue detection backend"
requires-python = ">=3.11"

dependencies = [
    "onnxruntime>=1.16.0",      # AI inference
    "opencv-python>=4.8.0",     # Image processing
    "pydantic>=2.0",            # Config validation
    "sqlalchemy>=2.0",          # ORM (SQLite)
    "alembic>=1.12.0",          # Schema migrations
    "pywin32>=305",             # Windows API
    "discord-webhook>=1.3",     # Discord notifications
    "strands-agents>=0.1.0",    # Agent orchestration
]
```

### Installation & Usage

```bash
# Install uv (one-time)
pip install uv

# Install all dependencies + dev
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

# Update lock file
uv lock
```

---

## 2. Package Structure

```
backend/
├── src/
│   ├── main.py                   # Entry point, daemon loop
│   ├── config.py                 # Pydantic settings
│   ├── models/
│   │   ├── database.py           # SQLAlchemy ORM models
│   │   └── schemas.py            # Pydantic schemas
│   ├── ai/
│   │   ├── gate.py               # Heuristics gate
│   │   ├── classifier.py         # ONNX Int8 inference
│   │   ├── escalation.py         # FP32 fallback
│   │   └── models/               # ONNX model files
│   ├── perception/
│   │   ├── engine.py             # Main perception pipeline
│   │   ├── screen.py             # Screen capture
│   │   └── state_machine.py      # State transitions
│   ├── notifications/
│   │   ├── desktop.py            # Windows notifications
│   │   ├── discord.py            # Discord integration
│   │   └── deduplication.py      # Alert deduplication
│   ├── database/
│   │   ├── connection.py         # SQLite session factory
│   │   ├── migrations/           # Alembic versions
│   │   └── repositories/         # Data access objects
│   ├── mcp/
│   │   ├── server.py             # MCP server setup
│   │   ├── tools/                # Tool implementations
│   │   └── handlers.py           # Tool handlers
│   ├── agents/
│   │   ├── perception_agent.py   # Strands perception agent
│   │   └── notification_agent.py # Strands notification agent
│   └── utils/
│       ├── logger.py             # Structured logging
│       ├── errors.py             # Custom exceptions
│       └── decorators.py         # Async utilities
├── tests/
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── fixtures/                 # Test data
├── pyproject.toml                # Project config
├── uv.lock                       # Locked versions
├── .python-version               # Python 3.11
└── README.md
```

---

## 3. Core Service Layer

### 3.1 Perception Engine (Main Loop)

The perception engine orchestrates the AI pipeline: gate heuristics → classifier → escalation.

```python
class PerceptionEngine:
    """Orchestrates AI perception: gate + classifier + escalation."""
    
    async def perceive_state(self) -> PerceiveStateResponse:
        """Main perception loop (called every 100ms)."""
        # Step 1: Capture regions from screen
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
        
        # Step 5: State machine evaluation
        state = self.state_machine.evaluate(final_conf)
        
        # Step 6: Handle notifications
        await self.maybe_notify(state)
        
        return PerceiveStateResponse(
            state=state,
            confidence=final_conf,
            latency_ms=elapsed_ms
        )
```

---

### 3.2 Agent Orchestration with Strands

The backend uses Strands Agents for coordinating multi-agent perception and notification workflows:

```python
from strands import Agent, tool

class QueuePerceptionAgent(Agent):
    """Multi-agent orchestration for queue detection."""
    
    @tool
    async def perceive_and_notify(self) -> dict:
        """Main agent task: perceive state and trigger notifications."""
        response = await self.perception_engine.perceive_state()
        
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


class NotificationAgent(Agent):
    """Multi-channel notification coordination."""
    
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
```

**Key Benefits of Strands Agents:**

| Benefit | Details |
|---------|---------|
| **MCP Native** | Built-in MCP client/server support |
| **Async Orchestration** | Natural async/await coordination |
| **Tool Registry** | Auto-discoverable agent tools |
| **Scheduler** | Built-in interval scheduling (100ms loops) |
| **Error Handling** | Agent-level error recovery & retry |

---

### 3.3 AI Models Layer

```python
class ClassifierModel:
    """Int8 quantized ONNX model for queue state classification."""
    
    def __init__(self, path="src/ai/models/classifier.onnx"):
        self.session = ort.InferenceSession(
            path,
            providers=["CPUExecutionProvider"]
        )
    
    async def infer(self, regions: Dict[str, np.ndarray]) -> float:
        """Runs inference on captured regions."""
        queue_region = regions['queue_status']
        processed = self._preprocess(queue_region)
        quantized = self._quantize_int8(processed)
        
        outputs = self.session.run(
            [self.output_name],
            {self.input_name: quantized}
        )
        
        confidence = self._postprocess(outputs[0])
        return confidence
```

---

### 3.4 State Machine

The state machine manages transitions between game states:

```python
class StateMachine:
    """Manages state transitions and prevents spurious alerts."""
    
    STATES = ["idle", "queue", "match_found", "hero_select", "loading", "in_game"]
    CONFIDENCE_THRESHOLD = 0.80
    STABILITY_WINDOW_MS = 500
    
    def evaluate(self, confidence: float) -> str:
        """Determine next state from confidence score."""
        avg_confidence = np.mean(self.confidence_history)
        
        if avg_confidence > self.CONFIDENCE_THRESHOLD:
            new_state = "queue"
        else:
            new_state = "idle"
        
        return new_state
```

---

### 3.5 Database Repository Layer

```python
class DetectionRepository:
    """Data access for detection_history table."""
    
    async def insert(self, detection: Detection) -> int:
        """Insert detection record."""
        record = DetectionHistoryModel(
            state=detection.state,
            confidence=detection.confidence,
            timestamp=datetime.now(timezone.utc)
        )
        self.session.add(record)
        self.session.commit()
        return record.id
    
    async def get_recent(self, limit: int = 100) -> List[Detection]:
        """Get recent N detections."""
        records = self.session.query(DetectionHistoryModel)\
            .order_by(DetectionHistoryModel.timestamp.desc())\
            .limit(limit)\
            .all()
        return [Detection.from_orm(r) for r in records]
```

---

## 4. MCP Tool Implementations

### Tool 1: screen.perceive_state

```python
@mcp_tool(name="screen.perceive_state")
async def perceive_state(
    request: PerceiveStateRequest = Body(...)
) -> PerceiveStateResponse:
    """
    Detects current Overwatch queue state via AI perception.
    
    **Response**:
    {
      "state": "queue",
      "confidence": 0.87,
      "latency_ms": 52
    }
    
    **Errors**:
    - 400: Invalid resolution
    - 503: Models not loaded
    """
    engine = get_perception_engine()
    response = await engine.perceive_state()
    return response
```

---

## 5. Error Handling & Logging

### Custom Exceptions

```python
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
    """Notification delivery failed."""
    pass
```

### Structured Logging

```python
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
@pytest.fixture
def gate():
    return GateHeuristics(brightness_threshold=100)

def test_bright_image_passes_gate(gate):
    """Bright image should pass gate."""
    bright_image = np.ones((100, 100, 3), dtype=np.uint8) * 255
    confidence = gate.evaluate(bright_image)
    assert confidence > 0.8

def test_dark_image_fails_gate(gate):
    """Dark image should fail gate."""
    dark_image = np.ones((100, 100, 3), dtype=np.uint8) * 50
    confidence = gate.evaluate(dark_image)
    assert confidence < 0.6
```

---

## 7. Performance Targets

- **Detection latency**: &lt;100ms p95
- **CPU usage**: &lt;10% sustained
- **Memory**: &lt;150 MB peak
- **Startup time**: &lt;2 seconds
- **False positives**: &lt;5%

---

## 8. Deployment Checklist

- [ ] ONNX models downloaded and quantized
- [ ] SQLite schema migrated
- [ ] Discord webhook configured
- [ ] Performance profiling complete
- [ ] All tests pass
- [ ] No sensitive data in logs
- [ ] Database vacuum scheduled

---

**Owner**: Backend Lead  
**Last Updated**: February 6, 2026
