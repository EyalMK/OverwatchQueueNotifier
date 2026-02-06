from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np

from ..errors import WindowNotFoundError


CaptureProvider = Callable[[str], np.ndarray]


def _default_provider(_window_title: str) -> np.ndarray:
    raise WindowNotFoundError(
        "Screen capture provider not configured. Implement Windows DCE capture."
    )


@dataclass
class ScreenCaptureService:
    window_title: str
    provider: Optional[CaptureProvider] = None

    def capture(self) -> np.ndarray:
        provider = self.provider or _default_provider
        frame = provider(self.window_title)
        if not isinstance(frame, np.ndarray):
            raise TypeError("Capture provider must return numpy.ndarray.")
        if frame.ndim != 3 or frame.shape[2] != 3:
            raise ValueError("Capture provider must return HxWx3 frame.")
        if frame.dtype != np.uint8:
            raise ValueError("Capture provider must return uint8 frame.")
        return frame
