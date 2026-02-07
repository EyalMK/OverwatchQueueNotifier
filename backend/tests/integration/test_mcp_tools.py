from __future__ import annotations

import numpy as np
from fastapi.testclient import TestClient

from src.mcp.server import create_app


def test_perceive_state_success(monkeypatch) -> None:
    monkeypatch.setattr(
        "src.mcp.server.ClassifierService.classify_with_escalation",
        lambda _self, _frame: ("QUEUE", 0.93, False),
        raising=True,
    )
    app = create_app()

    def _capture(_self):
        return np.zeros((1080, 1920, 3), dtype=np.uint8)

    monkeypatch.setattr(
        "src.mcp.server.ScreenCaptureService.capture",
        _capture,
        raising=True,
    )

    client = TestClient(app)
    response = client.post(
        "/mcp/tools/screen.perceive_state",
        json={"resolution": "1920x1080", "check_escalation": True},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "state" in payload
    assert "confidence" in payload


def test_capture_regions_success(monkeypatch) -> None:
    app = create_app()

    def _capture(_self):
        return np.zeros((1080, 1920, 3), dtype=np.uint8)

    monkeypatch.setattr(
        "src.mcp.server.ScreenCaptureService.capture",
        _capture,
        raising=True,
    )

    client = TestClient(app)
    response = client.post(
        "/mcp/tools/screen.capture_regions",
        json={
            "resolution": "1920x1080",
            "regions": [
                {
                    "name": "queue_icon",
                    "crop_normalized": [0.1, 0.1, 0.2, 0.2],
                }
            ],
            "format": "png",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["regions"][0]["dims"] == [192, 108]


def test_notify_endpoints_success() -> None:
    app = create_app()
    client = TestClient(app)

    desktop = client.post(
        "/mcp/tools/notify.desktop",
        json={
            "title": "MATCH FOUND!",
            "message": "Test",
            "urgency": "critical",
            "sound": True,
        },
    )
    assert desktop.status_code == 200

    discord = client.post(
        "/mcp/tools/notify.discord",
        json={
            "webhook_url": "https://discord.com/api/webhooks/123/abc",
            "content": "Test",
        },
    )
    assert discord.status_code == 200
