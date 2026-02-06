from __future__ import annotations

import numpy as np
import pytest

from src.errors import WindowNotFoundError
from src.perception.screen_capture import ScreenCaptureService


def test_screen_capture_uses_provider() -> None:
    expected = np.zeros((1080, 1920, 3), dtype=np.uint8)

    def provider(_title: str) -> np.ndarray:
        return expected

    service = ScreenCaptureService(window_title="Overwatch 2", provider=provider)

    frame = service.capture()

    assert frame is expected
    assert frame.shape == (1080, 1920, 3)
    assert frame.dtype == np.uint8


def test_screen_capture_raises_when_provider_missing() -> None:
    service = ScreenCaptureService(window_title="Overwatch 2")
    with pytest.raises(WindowNotFoundError):
        service.capture()
