from __future__ import annotations

import numpy as np

from src.config import AppConfig
from src.perception.gate import GateService


def _config() -> AppConfig:
    return AppConfig(
        mcp_port=5000,
        log_level="INFO",
        db_path=":memory:",
        overwatch_window_title="Overwatch 2",
        gate_pixel_diff_threshold_pct=5.0,
        gate_histogram_threshold=0.3,
        escalation_confidence_threshold=0.85,
        screen_capture_interval_ms=500,
        discord_webhook_url=None,
    )


def test_first_frame_always_processes() -> None:
    gate = GateService(_config())
    frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
    assert gate.should_process(None, frame, (1920, 1080)) is True


def test_identical_frames_skip() -> None:
    gate = GateService(_config())
    frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
    gate.should_process(None, frame, (1920, 1080))
    assert gate.should_process(frame, frame.copy(), (1920, 1080)) is False
    assert gate.skip_count >= 1


def test_large_scene_change_processes() -> None:
    gate = GateService(_config())
    prev = np.zeros((1080, 1920, 3), dtype=np.uint8)
    curr = np.ones((1080, 1920, 3), dtype=np.uint8) * 255
    gate.should_process(None, prev, (1920, 1080))
    assert gate.should_process(prev, curr, (1920, 1080)) is True


def test_noise_single_pixel_skips() -> None:
    gate = GateService(_config())
    prev = np.zeros((1080, 1920, 3), dtype=np.uint8)
    curr = prev.copy()
    curr[0, 0] = 255
    gate.should_process(None, prev, (1920, 1080))
    assert gate.should_process(prev, curr, (1920, 1080)) is False


def test_resolution_specific_thresholds_differ() -> None:
    gate = GateService(_config())
    prev = np.zeros((1080, 1920, 3), dtype=np.uint8)
    curr = prev.copy()
    curr[: int(1080 * 0.025), :, :] = 255  # ~2.5% change
    gate.should_process(None, prev, (1920, 1080))
    assert gate.should_process(prev, curr, (1920, 1080)) is False
    assert gate.should_process(prev, curr, (3440, 1440)) is True


def test_shape_mismatch_is_treated_as_process() -> None:
    gate = GateService(_config())
    prev = np.zeros((1080, 1920, 3), dtype=np.uint8)
    curr = np.zeros((720, 1280, 3), dtype=np.uint8)
    gate.should_process(None, prev, (1920, 1080))
    assert gate.should_process(prev, curr, (1280, 720)) is True
