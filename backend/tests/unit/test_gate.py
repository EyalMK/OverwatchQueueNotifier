from __future__ import annotations

import numpy as np

from src.config import AppConfig
from src.perception.gate import GateService


def _config(
    pixel_diff_threshold_pct: float = 15.0, histogram_threshold: float = 0.3
) -> AppConfig:
    return AppConfig(
        mcp_port=5000,
        log_level="INFO",
        db_path=":memory:",
        overwatch_window_title="Overwatch 2",
        gate_pixel_diff_threshold_pct=pixel_diff_threshold_pct,
        gate_histogram_threshold=histogram_threshold,
        escalation_confidence_threshold=0.85,
        screen_capture_interval_ms=500,
        discord_webhook_url=None,
    )


def test_gate_triggers_on_large_pixel_diff() -> None:
    gate = GateService(_config(pixel_diff_threshold_pct=5.0, histogram_threshold=0.1))
    prev = np.zeros((10, 10, 3), dtype=np.uint8)
    curr = np.ones((10, 10, 3), dtype=np.uint8) * 255

    assert gate.should_process(prev, curr) is True


def test_gate_ignores_small_changes() -> None:
    gate = GateService(_config(pixel_diff_threshold_pct=15.0, histogram_threshold=0.1))
    prev = np.zeros((100, 100, 3), dtype=np.uint8)
    curr = prev.copy()
    curr[0:2, 0:2] = 255

    assert gate.should_process(prev, curr) is False


def test_histogram_divergence_detects_change() -> None:
    prev = np.zeros((10, 10, 3), dtype=np.uint8)
    curr = np.ones((10, 10, 3), dtype=np.uint8) * 200

    divergence = GateService.calculate_histogram_divergence(prev, curr)

    assert divergence > 0.1


def test_gate_rejects_shape_mismatch() -> None:
    gate = GateService(_config())
    prev = np.zeros((10, 10, 3), dtype=np.uint8)
    curr = np.zeros((12, 10, 3), dtype=np.uint8)

    try:
        gate.should_process(prev, curr)
        assert False, "Expected ValueError"
    except ValueError:
        assert True
