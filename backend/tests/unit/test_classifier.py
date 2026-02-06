from __future__ import annotations

import numpy as np

from src.config import AppConfig
from src.perception.classifier import ClassifierService


def _config(threshold: float = 0.85) -> AppConfig:
    return AppConfig(
        mcp_port=5000,
        log_level="INFO",
        db_path=":memory:",
        overwatch_window_title="Overwatch 2",
        gate_pixel_diff_threshold_pct=15.0,
        gate_histogram_threshold=0.3,
        escalation_confidence_threshold=threshold,
        screen_capture_interval_ms=500,
        discord_webhook_url=None,
    )


def test_predict_returns_unknown_without_models() -> None:
    service = ClassifierService(_config())
    image = np.zeros((224, 224, 3), dtype=np.uint8)

    state, confidence = service.predict(image)

    assert state == "UNKNOWN"
    assert confidence == 0.0


def test_predict_with_escalation_marks_escalated_when_low_confidence() -> None:
    service = ClassifierService(_config(threshold=0.5))
    image = np.zeros((224, 224, 3), dtype=np.uint8)

    result = service.predict_with_escalation(image)

    assert result.escalated is True
    assert result.state in {"UNKNOWN", "IDLE", "QUEUE", "MATCH_FOUND", "HERO_SELECT", "LOADING", "IN_GAME"}


def test_preprocess_resizes_to_224() -> None:
    service = ClassifierService(_config())
    image = np.zeros((320, 240, 3), dtype=np.uint8)

    blob = service._preprocess(image)

    assert blob.shape == (1, 3, 224, 224)
