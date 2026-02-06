from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from ..config import AppConfig


@dataclass
class GateSignals:
    pixel_diff_pct: float
    histogram_change: float


class GateService:
    def __init__(self, config: AppConfig) -> None:
        self._pixel_diff_threshold = config.gate_pixel_diff_threshold_pct
        self._histogram_threshold = config.gate_histogram_threshold
        self._last_signals: Optional[GateSignals] = None

    @property
    def last_signals(self) -> Optional[GateSignals]:
        return self._last_signals

    def should_process(self, prev_frame: np.ndarray, curr_frame: np.ndarray) -> bool:
        if prev_frame.shape != curr_frame.shape:
            raise ValueError("Frames must have the same shape.")
        if prev_frame.ndim != 3 or prev_frame.shape[2] != 3:
            raise ValueError("Frames must be HxWx3.")

        pixel_diff_pct = self.calculate_pixel_diff_pct(prev_frame, curr_frame)
        if pixel_diff_pct < self._pixel_diff_threshold:
            self._last_signals = GateSignals(
                pixel_diff_pct=pixel_diff_pct,
                histogram_change=0.0,
            )
            return False

        histogram_change = self.calculate_histogram_divergence(prev_frame, curr_frame)
        self._last_signals = GateSignals(
            pixel_diff_pct=pixel_diff_pct,
            histogram_change=histogram_change,
        )
        return histogram_change >= self._histogram_threshold

    @staticmethod
    def calculate_pixel_diff_pct(prev_frame: np.ndarray, curr_frame: np.ndarray) -> float:
        diff = np.abs(curr_frame.astype(np.int16) - prev_frame.astype(np.int16))
        changed = np.any(diff > 10, axis=2)
        return float(changed.mean() * 100.0)

    @staticmethod
    def calculate_histogram_divergence(
        prev_frame: np.ndarray, curr_frame: np.ndarray
    ) -> float:
        divergences = []
        for channel in range(3):
            hist_prev, _ = np.histogram(
                prev_frame[:, :, channel], bins=32, range=(0, 255), density=True
            )
            hist_curr, _ = np.histogram(
                curr_frame[:, :, channel], bins=32, range=(0, 255), density=True
            )
            bc = float(np.sum(np.sqrt(hist_prev * hist_curr)))
            divergence = max(0.0, 1.0 - bc)
            divergences.append(divergence)
        return float(np.mean(divergences))
