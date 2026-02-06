# Test Strategy
## Overwatch AI Queue Detection & Notification App

**Generated**: February 6, 2026  
**Version**: 1.0

---

## Test Pyramid & Coverage Targets

```
         ▲
        ╱ ╲
       ╱   ╲  E2E Tests (10%)
      ╱     ╲  - Full workflows with mock screenshots
     ╱───────╲ - Critical user journeys
    ╱         ╲ - 15-20 tests
   ╱───────────╲
  ╱   Step 1    ╲ Integration Tests (20%)
 ╱               ╲ - MCP contracts, DB transactions
╱─────────────────╲ - API endpoint tests
 ╱               ╲ - 25-30 tests
╱                 ╲
╱___________________╲ Unit Tests (70%)
                    - Gate logic, classifier, deduplication
                    - Mocked dependencies, fast execution
                    - 50-60 tests
```

**Overall Targets**:
- **Line coverage**: 75%+ (required for merge)
- **Critical paths**: 100% (classifier, notification sender, deduplication)
- **Test-to-code ratio**: 1:1 or better

---

## Test File Organization

```
backend/
└── tests/
    ├── unit/              (70%)
    │   ├── test_gate.py
    │   ├── test_classifier.py
    │   ├── test_state.py
    │   ├── test_deduplication.py
    │   └── test_repository.py
    │
    ├── integration/       (20%)
    │   ├── test_perception_pipeline.py
    │   ├── test_notification_flow.py
    │   ├── test_mcp_tools.py
    │   └── test_db_migrations.py
    │
    ├── e2e/              (10%)
    │   ├── test_queue_to_match_1920x1080.py
    │   ├── test_false_positive_mitigation.py
    │   └── test_calibration_flow.py
    │
    ├── fixtures/
    │   ├── sample_screenshots/
    │   │   ├── idle_1920x1080.png
    │   │   ├── queue_1920x1080.png
    │   │   └── match_found_1920x1080.png
    │   ├── test_data.json
    │   └── conftest.py   (pytest fixtures)
    │
    └── coverage_report.html

frontend/
└── tests/
    ├── unit/
    │   ├── __tests__/StateDisplay.test.tsx
    │   ├── __tests__/useGameStore.test.ts
    │   └── __tests__/calibrationForm.test.tsx
    │
    └── e2e/
        ├── tray-window.spec.ts
        └── settings-modal.spec.ts
```

---

## Unit Test Example (Backend)

```python
# backend/tests/unit/test_gate.py
import pytest
import numpy as np
from perception.gate import GateService
from config import Config

@pytest.fixture
def gate_service():
    config = Config()
    config.GATE_PIXEL_DIFF_THRESHOLD = 15.0
    return GateService(config)

class TestGateLogic:
    def test_gate_triggers_above_15_percent_threshold(self, gate_service):
        """Gate activates when pixel diff exceeds 15%"""
        prev = np.zeros((1080, 1920, 3), dtype=np.uint8)
        curr = prev.copy()
        curr[:, :] = 40  # ~15.7% change
        
        assert gate_service.should_process(prev, curr) is True
    
    def test_gate_ignores_below_5_percent(self, gate_service):
        """Gate does not trigger for <5% changes (noise)"""
        prev = np.zeros((1080, 1920, 3), dtype=np.uint8)
        curr = prev.copy()
        curr[0:10, 0:10] = 255  # <0.05% change
        
        assert gate_service.should_process(prev, curr) is False
    
    def test_gate_histogram_divergence(self, gate_service):
        """Gate checks histogram divergence"""
        prev = np.random.randint(0, 100, (1080, 1920, 3), dtype=np.uint8)
        curr = np.random.randint(150, 255, (1080, 1920, 3), dtype=np.uint8)
        
        divergence = gate_service._calculate_histogram_divergence(prev, curr)
        assert divergence > 0.5  # Significant change
```

---

## Integration Test Example

```python
# backend/tests/integration/test_perception_pipeline.py
import pytest
from perception.perception_service import PerceptionService
from state.models import GameState

@pytest.fixture
def perception_service(config):
    return PerceptionService(config)

def test_full_perception_pipeline_detects_match_found(perception_service):
    """Full pipeline: capture → gate → classifier → detection"""
    sample_frame = load_test_image("tests/fixtures/match_found_1920x1080.png")
    
    detection = perception_service.detect(sample_frame)
    
    assert detection.state == GameState.MATCH_FOUND
    assert detection.confidence > 0.90
    assert detection.evidence is not None
    assert detection.inference_latency_ms < 150
```

---

## E2E Test Example (User Journey)

```python
# backend/tests/e2e/test_queue_to_match_1920x1080.py
def test_user_queues_and_match_found_notifies():
    """Critical path: Queue → Wait → Match Found → Notification"""
    
    # Setup
    frames = [
        load_frame("idle.png"),
        load_frame("queue.png"),
        load_frame("queue.png"),  # Still queueing
        load_frame("match_found.png"),
    ]
    notifications = []
    
    # Execute
    perception = PerceptionService(config)
    notifier = MockNotifier(notifications)
    
    for frame in frames:
        detection = perception.detect(frame)
        if detection.state == GameState.MATCH_FOUND:
            notifier.notify_desktop(
                title="MATCH FOUND!",
                body=f"Confidence: {detection.confidence:.0%}"
            )
    
    # Verify
    assert len(notifications) >= 1
    assert "MATCH FOUND" in notifications[0]['title']
```

---

## Coverage Report

Run after each commit:

```bash
# Backend
cd backend
pytest --cov=src --cov-report=html --cov-report=term-color tests/

# Frontend
cd frontend
npm test -- --coverage

# View report
open htmlcov/index.html   # macOS/Linux
start htmlcov/index.html  # Windows
```

**Targets by module**:
| Module | Target |
|--------|--------|
| `perception/` | 90%+ |
| `notification/` | 85%+ |
| `state/` | 95%+ |
| `mcp/` | 80%+ |

---

## Performance Benchmarks

Each test should complete quickly:

- **Unit test**: <100ms per test
- **Integration test**: <500ms per test
- **E2E test**: <2s per test

**Total test suite**: <2 minutes (CI should be fast)

---

## Continuous Integration

**GitHub Actions** runs all tests on:
- PR creation / push
- Before merge to develop

**Gate**: Tests must pass before merge to develop.

---

## Test Data Management

**Fixtures** (immutable, checked into repo):
- Sample screenshots per resolution (idle, queue, match_found)
- Mock ONNX models (tiny size for fast tests)
- Calibration profiles (JSON)

**Seed data** (runtime):
- SQLite in-memory DB for integration tests
- Reset between tests via fixtures

---

## Accessibility & Browser Testing

**Upcoming** (not MVP):
- WCAG 2.1 AA automated tests
- Keyboard navigation tests
- Screen reader testing

---

## Summary

**Test strategy**:
1. **Unit** (70%): Fast, isolated, mocked dependencies
2. **Integration** (20%): Real APIs, real database (in-memory for tests)
3. **E2E** (10%): Full user journeys with real data

**Coverage**: 75%+ required; 100% for critical paths.

**Speed**: <2 minutes total test suite.

**This ensures quality without sacrificing development velocity.**
