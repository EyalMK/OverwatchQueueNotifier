# QA Lead Specification
## Overwatch AI Queue Detection & Notification App

**Generated**: February 6, 2026  
**Version**: 1.0  
**Status**: Draft → Quality Standards

---

## 1. Test Pyramid & Coverage Targets

```
         ▲
        ╱ ╲
       ╱   ╲  E2E Tests (10%)
      ╱     ╲  - Full workflow with mock screenshots
     ╱───────╲ - All resolutions (1920×1080, 2560×1440, 3440×1440)
    ╱         ╲ - 15-20 tests
   ╱───────────╲
  ╱   Step 1    ╲ Integration Tests (20%)
 ╱               ╲ - MCP contracts, DB transactions, Discord webhook retry
╱─────────────────╲ - 25-30 tests
 ╱               ╲
╱                 ╲ Unit Tests (70%)
╱___________________╲ - Gate logic, classifier, state transitions
                    - Mocked AI models, heuristics, deduplication
                    - 50-60 tests
```

**Overall Coverage Target**: **75%+ lines**, **85%+ for critical paths** (classifier, notification logic)

---

## 2. Test File Naming & Location Conventions

```
backend/
├── src/
│   ├── perception/
│   │   ├── gate.py
│   │   ├── classifier.py
│   │   └── calibration.py
│   ├── notification/
│   │   ├── queue.py
│   │   └── discord_notif.py
│   └── ...
│
└── tests/
    ├── unit/
    │   ├── test_gate.py           # test_<module>.py
    │   ├── test_classifier.py
    │   ├── test_state_transitions.py
    │   ├── test_deduplication.py
    │   ├── test_discord_retry.py
    │   └── test_repository.py
    │
    ├── integration/
    │   ├── test_mcp_perceive_state.py    # test_<service>.py
    │   ├── test_notification_flow.py
    │   ├── test_database_migrations.py
    │   └── test_discord_webhook.py
    │
    ├── e2e/
    │   ├── test_full_queue_detection_1920x1080.py
    │   ├── test_full_queue_detection_2560x1440.py
    │   ├── test_match_found_notification.py
    │   ├── test_calibration_wizard.py
    │   └── test_false_positive_mitigation.py
    │
    ├── fixtures/
    │   ├── mock_screenshots/
    │   │   ├── idle_1920x1080.png
    │   │   ├── queue_1920x1080.png
    │   │   ├── match_found_1920x1080.png
    │   │   ├── ...
    │   │   ├── idle_2560x1440.png
    │   │   └── ...
    │   ├── calibration_profiles/
    │   │   ├── 1920x1080.json
    │   │   └── 2560x1440.json
    │   └── conftest.py             # pytest fixtures
    │
    └── coverage_report.html        # From pytest-cov

frontend/
└── tests/
    ├── unit/
    │   ├── test_StateDisplay.tsx
    │   ├── test_useGameStore.ts
    │   └── test_calibrationForm.test.ts
    │
    └── e2e/
        ├── test_tray_opens.spec.ts
        └── test_notification_toast.spec.ts
```

---

## 3. Unit Test Examples (Python: pytest)

### Example 1: Gate Logic (Heuristic Decision)

```python
# backend/tests/unit/test_gate.py
import pytest
import numpy as np
from perception.gate import GateService

@pytest.fixture
def gate():
    return GateService()

class TestGateHeuristics:
    """Test gate logic for determining when to run AI inference"""
    
    def test_gate_detects_pixel_diff_15_percent(self, gate):
        """Gate triggers when pixel diff exceeds 15%"""
        prev_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        curr_frame = np.ones((1080, 1920, 3), dtype=np.uint8) * 127  # ~50% diff
        
        should_process = gate.should_process(prev_frame, curr_frame)
        assert should_process is True
    
    def test_gate_ignores_small_changes(self, gate):
        """Gate does not trigger for <5% pixel changes (noise)"""
        prev_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        curr_frame = prev_frame.copy()
        curr_frame[10:20, 10:20] = 255  # 0.26% change
        
        should_process = gate.should_process(prev_frame, curr_frame)
        assert should_process is False
    
    def test_gate_histogram_analysis(self, gate):
        """Gate uses histogram divergence for change detection"""
        prev_frame = np.random.randint(0, 100, (1080, 1920, 3), dtype=np.uint8)
        curr_frame = np.random.randint(150, 255, (1080, 1920, 3), dtype=np.uint8)
        
        histogram_change = gate.calculate_histogram_divergence(prev_frame, curr_frame)
        assert histogram_change > 0.5  # Significant change
    
    def test_gate_config_sensitivity(self, gate):
        """Gate sensitivity configurable via config"""
        gate.config['pixel_diff_threshold_pct'] = 20.0
        prev_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        curr_frame = prev_frame.copy()
        curr_frame[:] += 30  # ~11.8% diff
        
        should_process = gate.should_process(prev_frame, curr_frame)
        assert should_process is False  # Doesn't trigger at 20% threshold
```

---

### Example 2: Classifier Confidence & Escalation

```python
# backend/tests/unit/test_classifier.py
import pytest
from perception.classifier import ClassifierService
import numpy as np

@pytest.fixture
def classifier():
    service = ClassifierService(
        tiny_model_path="tests/fixtures/models/tiny_mock.onnx",
        escalation_model_path="tests/fixtures/models/escalation_mock.onnx"
    )
    return service

class TestClassifierConfidence:
    """Test state classification and confidence scoring"""
    
    def test_classifier_high_confidence_match_found(self, classifier):
        """Classifier returns MATCH_FOUND with 94% confidence"""
        mock_image = np.ones((224, 224, 3), dtype=np.uint8) * 150
        state, conf = classifier.predict(mock_image, model="tiny")
        
        assert state == "MATCH_FOUND"
        assert conf > 0.90
    
    def test_escalation_triggers_below_85_percent_confidence(self, classifier):
        """When tiny conf <0.85, escalation model is used"""
        # Mock scenario: tiny model gives 78% conf on QUEUE
        mock_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        
        state, final_conf, escalation_used = classifier.predict_with_escalation(
            mock_image,
            escalation_threshold=0.85
        )
        
        assert escalation_used is True
        # Final confidence should be average of both models
        assert 0.70 <= final_conf <= 1.0
    
    def test_classifier_model_versions(self, classifier):
        """Classifier tracks which model produced output"""
        mock_image = np.ones((224, 224, 3), dtype=np.uint8)
        state, conf = classifier.predict(mock_image, model="tiny")
        
        evidence = classifier.get_evidence()
        assert evidence['model_version'] == 'TinyMobileNetV3_v1.0'
        assert evidence['model_size_bytes'] < 300_000  # <300KB
```

---

### Example 3: Deduplication Logic (Notification Spam Prevention)

```python
# backend/tests/unit/test_deduplication.py
import pytest
from datetime import datetime, timedelta
from notification.queue import NotificationQueue

@pytest.fixture
def notif_queue(tmp_path):
    db_path = tmp_path / "test.db"
    return NotificationQueue(db_path=str(db_path))

class TestDeduplication:
    """Ensure notifications don't fire multiple times per match"""
    
    def test_notification_deduplicated_within_5_seconds(self, notif_queue):
        """Second MATCH_FOUND within 5s window is skipped"""
        
        # First detection
        result1 = notif_queue.should_notify("MATCH_FOUND", confidence=0.94)
        assert result1 is True
        notif_queue.log_notification_sent("MATCH_FOUND")
        
        # Second detection 2 seconds later (same state)
        result2 = notif_queue.should_notify("MATCH_FOUND", confidence=0.96)
        assert result2 is False  # Deduped
    
    def test_notification_fires_after_5_second_window(self, notif_queue):
        """After 5s dedup window, new MATCH_FOUND fires"""
        
        notif_queue.log_notification_sent("MATCH_FOUND")
        
        # Advance time 5.1 seconds
        with pytest.freeze_time() as frozen_time:
            frozen_time.move_to(datetime.now() + timedelta(seconds=5.1))
            result = notif_queue.should_notify("MATCH_FOUND", confidence=0.94)
            assert result is True
    
    def test_state_change_overrides_dedup_window(self, notif_queue):
        """State transition (QUEUE → MATCH_FOUND) bypasses dedup"""
        
        notif_queue.log_notification_sent("QUEUE")
        
        # New state: different from last
        result = notif_queue.should_notify("MATCH_FOUND", confidence=0.94)
        assert result is True  # Not deduped; state changed
```

---

## 4. Integration Test Examples

### Example 1: MCP Tool Contract (perceive_state)

```python
# backend/tests/integration/test_mcp_perceive_state.py
import pytest
import json
from mcp.server import perceive_state_tool

@pytest.fixture
def mcp_handler():
    """MCP tool connected to real (mocked) backend services"""
    return perceive_state_tool

class TestMCPPerceiveStateTool:
    """Test MCP tool contract and data flow"""
    
    def test_perceive_state_returns_valid_response(self):
        """Tool returns required fields: state, confidence, evidence"""
        request = {
            "timestamp": "2026-02-06T14:30:45.123Z",
            "resolution": "1920x1080",
        }
        
        response = mcp_handler(request)
        
        # Validate response structure
        assert "state" in response
        assert "confidence" in response
        assert "evidence" in response
        assert "timestamp" in response
        
        # Validate types
        assert isinstance(response['state'], str)
        assert isinstance(response['confidence'], float)
        assert 0.0 <= response['confidence'] <= 1.0
    
    def test_perceive_state_error_window_not_found(self):
        """Tool returns 400 error if Overwatch window not found"""
        # Mock screen capture to return no window found
        request = {"resolution": "1920x1080"}
        
        response = mcp_handler(request)
        
        assert response.get('error_code') == 'ERR_WIN_NOT_FOUND'
        assert response.get('http_status') == 400
```

---

### Example 2: Notification Queue + Discord Retry

```python
# backend/tests/integration/test_discord_webhook_retry.py
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import time
from notification.discord_notif import DiscordNotificationService

@pytest.fixture
def discord_service():
    return DiscordNotificationService(
        webhook_url="https://discordapp.com/api/webhooks/123/abc",
        retry_config={"max_retries": 3, "base_delay_ms": 100}
    )

class TestDiscordRetryLogic:
    """Test Discord webhook delivery with exponential backoff"""
    
    @patch("requests.post")
    def test_discord_webhook_success(self, mock_post, discord_service):
        """Successful webhook post (200 OK)"""
        mock_post.return_value = MagicMock(status_code=200)
        
        result = discord_service.send_notification(
            title="MATCH FOUND",
            body="Confidence: 94%"
        )
        
        assert result['status'] == 'sent'
        assert mock_post.call_count == 1
    
    @patch("requests.post")
    def test_discord_rate_limit_retry(self, mock_post, discord_service):
        """Exponential backoff on 429 rate limit"""
        # First call: 429 (rate limited)
        # Second call: 200 (success)
        mock_post.side_effect = [
            MagicMock(status_code=429, headers={'Retry-After': '1'}),
            MagicMock(status_code=200),
        ]
        
        result = discord_service.send_notification_with_retry(
            title="MATCH FOUND",
            body="Confidence: 94%"
        )
        
        assert result['status'] == 'sent'
        assert result['retry_count'] == 1
        assert mock_post.call_count == 2
    
    @patch("requests.post")
    def test_discord_max_retries_exceeded(self, mock_post, discord_service):
        """After 3 retries, give up and log failure"""
        mock_post.return_value = MagicMock(status_code=500)  # Server error
        
        result = discord_service.send_notification_with_retry(
            title="MATCH FOUND",
            body="Confidence: 94%"
        )
        
        assert result['status'] == 'failed'
        assert result['retry_count'] == 3
```

---

## 5. E2E Test Examples

### Example 1: Full Queue → Match Found → Notification Flow

```python
# backend/tests/e2e/test_full_queue_to_notification.py
import pytest
import os
from pathlib import Path
from datetime import datetime

@pytest.fixture
def e2e_context(tmp_path):
    """E2E test environment: real services, mock images"""
    return {
        "db_path": tmp_path / "e2e_test.db",
        "screenshot_dir": Path(__file__).parent / "fixtures" / "mock_screenshots",
        "config": {
            "pixel_diff_threshold_pct": 15.0,
            "escalation_confidence_threshold": 0.85,
        }
    }

class TestFullQueueDetectionFlow:
    """End-to-end: simulate Overwatch queue → match found"""
    
    def test_full_1920x1080_workflow(self, e2e_context):
        """
        1. Load calibration for 1920x1080
        2. Process idle screenshot
        3. Process queue screenshot
        4. Process match_found screenshot
        5. Verify notification queued
        """
        from app import OverwatchQueueApp
        
        app = OverwatchQueueApp(db_path=str(e2e_context['db_path']))
        
        # Step 1: Calibration loaded
        assert app.calibration.get_profile("1920x1080") is not None
        
        # Step 2: Process idle
        idle_img = app.load_fixture_image("idle_1920x1080.png")
        state, conf = app.perceive_state(idle_img)
        assert state == "IDLE"
        
        # Step 3: Process queue
        queue_img = app.load_fixture_image("queue_1920x1080.png")
        state, conf = app.perceive_state(queue_img)
        assert state == "QUEUE"
        
        # Step 4: Process match found
        match_img = app.load_fixture_image("match_found_1920x1080.png")
        state, conf = app.perceive_state(match_img)
        assert state == "MATCH_FOUND"
        assert conf > 0.85
        
        # Step 5: Verify notifications
        notifications = app.get_queued_notifications()
        assert len(notifications) >= 1
        assert notifications[0]['type'] == 'desktop'
        
        # Verify deduplication (second match_found should not re-notify)
        state2, conf2 = app.perceive_state(match_img)
        assert state2 == "MATCH_FOUND"
        notifications2 = app.get_queued_notifications()
        assert len(notifications2) == len(notifications)  # No new notifications
    
    def test_false_positive_mitigation_requires_2_consecutive_detections(self, e2e_context):
        """Prevent jitter: require 2 consecutive same-state detections"""
        from app import OverwatchQueueApp
        
        app = OverwatchQueueApp(db_path=str(e2e_context['db_path']))
        
        queue_img = app.load_fixture_image("queue_1920x1080.png")
        noise_img = app.load_fixture_image("queue_with_noise_1920x1080.png")
        
        # First detection: QUEUE
        state1, _ = app.perceive_state(queue_img)
        app.process_detection(state1)
        
        # Second detection (noisy): might classify as MATCH_FOUND (false positive)
        state2, _ = app.perceive_state(noise_img)
        # But should NOT transition state (hysteresis)
        app.process_detection(state2, require_consecutive=True)
        
        # Verify state machine didn't jump
        assert app.current_state == "QUEUE"
```

---

## 6. Performance Benchmarks

| Operation | Target | Measurement Method |
|-----------|--------|-------------------|
| **Screen Capture** | <10ms | Time it(/perceive_state) |
| **Gate Logic** | <5ms | Time gate.should_process() |
| **Tiny Classifier** | <50ms p95 | Repeated inference timing |
| **Escalation Classifier** | <100ms | Full inference + post-process |
| **Deduplication Check** | <1ms | DB query timing |
| **Full Perception Cycle** | <100ms p95 | End-to-end perceive_state |
| **Notification Send** | <200ms desktop, <500ms discord | Async send timing |
| **CPU Usage (Idle Queue)** | <10% sustained | `psutil.Process().cpu_percent()` |
| **Memory Usage** | <200 MB average | `psutil.Process().memory_info().rss` |

### Benchmark Test Suite

```python
# backend/tests/benchmark/test_performance.py
import pytest
import time
from perception.classifier import ClassifierService

class TestPerformanceBenchmarks:
    """Measure and assert performance targets"""
    
    def test_classifier_latency_p95(self):
        """Tiny classifier must complete in <50ms at p95"""
        classifier = ClassifierService("models/tiny_classifier.onnx")
        mock_image = np.ones((224, 224, 3), dtype=np.uint8)
        
        latencies = []
        for _ in range(100):
            start = time.perf_counter()
            classifier.predict(mock_image)
            latencies.append((time.perf_counter() - start) * 1000)
        
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        assert p95_latency < 50, f"p95 latency {p95_latency}ms exceeds 50ms target"
```

---

## 7. Security Testing Checklist (OWASP Top 10)

| OWASP Issue | Project Mapping | Test |
|-------------|-----------------|------|
| **A01: Broken Access Control** | Single-user app, no auth | ✓ Verified: no multi-user paths |
| **A02: Cryptographic Failures** | Discord webhook URL in env vars, not plaintext | ✓ Test: URL not logged, masked in logs |
| **A03: Injection** | SQLite queries use parameterized statements | ✓ Test: SQL injection attempt blocked |
| **A04: Insecure Design** | No full-screen storage (privacy-first) | ✓ Test: Only cropped regions saved, not full screenshots |
| **A05: Security Misconfiguration** | HTTPS only for Discord, TLS enforced | ✓ Test: Webhook URL must be HTTPS |
| **A06: Vulnerable & Outdated** | Dependency audits in CI, SCA scanning | ✓ Test: `npm audit`, `pip audit` pass |
| **A07: Authentication** | N/A (local-only) | ✓ Verified: no auth layer |
| **A08: Software & Data Integrity** | Updates signed, checksums verified | ✓ Test: Auto-update validates signature |
| **A09: Logging & Monitoring** | Logs don't contain PII or cropped images | ✓ Test: Sensitive data never logged |
| **A10: SSRF** | No external API calls except Discord | ✓ Verified: Discord webhook only |

---

## 8. QA Process: When, Who, What

### When to Test

| Phase | Trigger | Owner | Duration |
|-------|---------|-------|----------|
| **Unit** | Developer commits | Backend Dev | 5–10 min (local) |
| **Integration** | PR created | CI/CD pipeline | 10–15 min |
| **E2E** | Merge to `develop` | QA team | 20–30 min (nightly) |
| **Manual** | Release candidate | QA + Marketing team | 1–2 hours (UAT) |

### Who Reviews

- **Code Review**: Backend Lead + Frontend Lead (before merge)
- **Test Coverage**: QA Lead (>75% overall, >85% critical)
- **Performance**: DevOps Lead (CPU/GPU/memory targets)
- **Security**: Backend Lead (no PII leaks, env var handling)

### Definition of Done (per User Story)

- [ ] Code reviewed and approved
- [ ] All unit tests passing (>80% coverage for new code)
- [ ] Integration tests passing (MCP contracts, DB, notifications)
- [ ] E2E test for happy path passing
- [ ] No performance regressions (benchmarks stable)
- [ ] No new security issues (SAST scan clean)
- [ ] Documentation updated

---

## 9. Continuous Integration (GitHub Actions)

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with: { python-version: '3.11' }
      - run: pip install -r backend/requirements.txt pytest pytest-cov
      - run: pytest backend/tests --cov=backend/src --cov-report=lcov
      - uses: coverallsapp/github-action@v1
        with: { github-token: ${{ secrets.GITHUB_TOKEN }}, path-to-lcov: lcov.info }

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with: { node-version: '18' }
      - run: cd frontend && npm install && npm run test:unit && npm run test:e2e
```

---

## 10. Next Steps

1. ✅ **QA spec approved** → Create test fixtures
2. ⏭️ **Mock screenshot library** → 1920×1080, 2560×1440, 3440×1440 samples (Sprint 0)
3. ⏭️ **Unit test scaffolding** → pytest setup, conftest, mocks (Sprint 0)
4. ⏭️ **First test suite run** → Baseline coverage report (Sprint 1)
5. ⏭️ **CI/CD integration** → GitHub Actions on every PR (Sprint 2)

**Owner**: QA Lead  
**Stakeholders**: Backend Lead, Frontend Lead, DevOps Lead
