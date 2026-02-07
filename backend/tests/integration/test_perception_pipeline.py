from __future__ import annotations

import os

import numpy as np
from fastapi.testclient import TestClient

from src.db.migrations import run_migrations
from src.errors import WindowNotFoundError
from src.mcp.server import create_app


def test_pipeline_idle_to_queue_transition(monkeypatch, temp_db: str) -> None:
    run_migrations(temp_db)
    monkeypatch.setenv("DB_PATH", temp_db)

    calls = {"count": 0}

    def _classify(_self, _frame):
        calls["count"] += 1
        return ("QUEUE", 0.95, False)

    monkeypatch.setattr(
        "src.mcp.server.ClassifierService.classify_with_escalation",
        _classify,
        raising=True,
    )
    monkeypatch.setattr(
        "src.mcp.server.ScreenCaptureService.capture",
        lambda _self: np.zeros((1080, 1920, 3), dtype=np.uint8),
        raising=True,
    )

    client = TestClient(create_app())
    response = client.post(
        "/mcp/tools/screen.perceive_state",
        json={"resolution": "1920x1080", "check_escalation": True},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["state"] == "QUEUE"
    assert payload["confidence"] == 0.95
    assert calls["count"] == 1


def test_pipeline_queue_to_match_found_triggers_notification_log(monkeypatch, temp_db: str) -> None:
    run_migrations(temp_db)
    monkeypatch.setenv("DB_PATH", temp_db)
    sequence = [("QUEUE", 0.95, False), ("MATCH_FOUND", 0.93, False)]

    def _classify(_self, _frame):
        return sequence.pop(0)

    monkeypatch.setattr(
        "src.mcp.server.ClassifierService.classify_with_escalation",
        _classify,
        raising=True,
    )
    frames = [
        np.zeros((1080, 1920, 3), dtype=np.uint8),
        np.ones((1080, 1920, 3), dtype=np.uint8) * 255,
    ]
    monkeypatch.setattr(
        "src.mcp.server.ScreenCaptureService.capture",
        lambda _self: frames.pop(0),
        raising=True,
    )

    client = TestClient(create_app())
    first = client.post("/mcp/tools/screen.perceive_state", json={"resolution": "1920x1080"})
    second = client.post("/mcp/tools/screen.perceive_state", json={"resolution": "1920x1080"})
    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["state"] == "MATCH_FOUND"


def test_pipeline_escalation_flag_returned(monkeypatch, temp_db: str) -> None:
    run_migrations(temp_db)
    monkeypatch.setenv("DB_PATH", temp_db)
    monkeypatch.setattr(
        "src.mcp.server.ClassifierService.classify_with_escalation",
        lambda _self, _frame: ("QUEUE", 0.91, True),
        raising=True,
    )
    monkeypatch.setattr(
        "src.mcp.server.ScreenCaptureService.capture",
        lambda _self: np.zeros((1080, 1920, 3), dtype=np.uint8),
        raising=True,
    )

    client = TestClient(create_app())
    response = client.post("/mcp/tools/screen.perceive_state", json={"resolution": "1920x1080"})
    assert response.status_code == 200
    assert response.json()["escalated"] is True


def test_pipeline_gate_uses_cached_result(monkeypatch, temp_db: str) -> None:
    run_migrations(temp_db)
    monkeypatch.setenv("DB_PATH", temp_db)
    calls = {"count": 0}

    def _classify(_self, _frame):
        calls["count"] += 1
        return ("QUEUE", 0.95, False)

    frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
    monkeypatch.setattr(
        "src.mcp.server.ClassifierService.classify_with_escalation",
        _classify,
        raising=True,
    )
    monkeypatch.setattr(
        "src.mcp.server.ScreenCaptureService.capture",
        lambda _self: frame.copy(),
        raising=True,
    )

    client = TestClient(create_app())
    one = client.post("/mcp/tools/screen.perceive_state", json={"resolution": "1920x1080"})
    two = client.post("/mcp/tools/screen.perceive_state", json={"resolution": "1920x1080"})
    assert one.status_code == 200
    assert two.status_code == 200
    assert calls["count"] == 1


def test_pipeline_deduplicates_repeated_state_notifications(monkeypatch, temp_db: str) -> None:
    run_migrations(temp_db)
    monkeypatch.setenv("DB_PATH", temp_db)
    monkeypatch.setattr(
        "src.mcp.server.ClassifierService.classify_with_escalation",
        lambda _self, _frame: ("QUEUE", 0.95, False),
        raising=True,
    )
    monkeypatch.setattr(
        "src.mcp.server.ScreenCaptureService.capture",
        lambda _self: np.zeros((1080, 1920, 3), dtype=np.uint8),
        raising=True,
    )

    client = TestClient(create_app())
    first = client.post("/mcp/tools/screen.perceive_state", json={"resolution": "1920x1080"})
    second = client.post("/mcp/tools/screen.perceive_state", json={"resolution": "1920x1080"})
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["state"] == second.json()["state"] == "QUEUE"


def test_pipeline_rate_limiting(monkeypatch, temp_db: str) -> None:
    run_migrations(temp_db)
    monkeypatch.setenv("DB_PATH", temp_db)
    monkeypatch.setattr(
        "src.mcp.server.ClassifierService.classify_with_escalation",
        lambda _self, _frame: ("QUEUE", 0.95, False),
        raising=True,
    )
    monkeypatch.setattr(
        "src.mcp.server.ScreenCaptureService.capture",
        lambda _self: np.zeros((1080, 1920, 3), dtype=np.uint8),
        raising=True,
    )
    client = TestClient(create_app())
    codes = [
        client.post("/mcp/tools/screen.perceive_state", json={"resolution": "1920x1080"}).status_code
        for _ in range(12)
    ]
    assert codes[:10] == [200] * 10
    assert 429 in codes[10:]


def test_pipeline_window_not_found_error(monkeypatch, temp_db: str) -> None:
    run_migrations(temp_db)
    monkeypatch.setenv("DB_PATH", temp_db)
    monkeypatch.setattr(
        "src.mcp.server.ScreenCaptureService.capture",
        lambda _self: (_ for _ in ()).throw(WindowNotFoundError("Overwatch window not found")),
        raising=True,
    )
    client = TestClient(create_app())
    response = client.post("/mcp/tools/screen.perceive_state", json={"resolution": "1920x1080"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["state"] == "IDLE"
    assert payload["confidence"] == 0.0


def test_pipeline_detection_logging_and_cleanup(monkeypatch, temp_db: str) -> None:
    run_migrations(temp_db)
    monkeypatch.setenv("DB_PATH", temp_db)
    states = [("QUEUE", 0.95, False), ("MATCH_FOUND", 0.95, False), ("IN_GAME", 0.95, False), ("IDLE", 0.95, False), ("QUEUE", 0.95, False)]
    monkeypatch.setattr(
        "src.mcp.server.ClassifierService.classify_with_escalation",
        lambda _self, _frame: states.pop(0),
        raising=True,
    )
    frames = [
        np.zeros((1080, 1920, 3), dtype=np.uint8),
        np.ones((1080, 1920, 3), dtype=np.uint8) * 30,
        np.ones((1080, 1920, 3), dtype=np.uint8) * 60,
        np.ones((1080, 1920, 3), dtype=np.uint8) * 90,
        np.ones((1080, 1920, 3), dtype=np.uint8) * 120,
    ]
    monkeypatch.setattr(
        "src.mcp.server.ScreenCaptureService.capture",
        lambda _self: frames.pop(0),
        raising=True,
    )
    client = TestClient(create_app())
    for _ in range(5):
        client.post("/mcp/tools/screen.perceive_state", json={"resolution": "1920x1080"})

    import sqlite3

    conn = sqlite3.connect(temp_db)
    count = conn.execute("SELECT COUNT(*) FROM detection_history").fetchone()[0]
    conn.close()
    assert count == 5

    os.environ.pop("DB_PATH", None)
