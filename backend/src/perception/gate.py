from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np

from ..config import AppConfig, GATE_THRESHOLDS


@dataclass
class GateSignals:
    pixel_diff_pct: float
    histogram_change: float


class PixelDiffGate:
    def __init__(self, threshold_channel_delta: int = 10) -> None:
        self._threshold_channel_delta = threshold_channel_delta

    def score(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        diff = np.abs(frame1.astype(np.int16) - frame2.astype(np.int16))
        changed = np.any(diff > self._threshold_channel_delta, axis=2)
        return float(changed.mean() * 100.0)


class HistogramDivergenceGate:
    def __init__(self, bins: int = 64) -> None:
        self._bins = bins

    def score(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        divergences = []
        for channel in range(3):
            hist1, _ = np.histogram(
                frame1[:, :, channel],
                bins=self._bins,
                range=(0, 256),
                density=True,
            )
            hist2, _ = np.histogram(
                frame2[:, :, channel],
                bins=self._bins,
                range=(0, 256),
                density=True,
            )
            hist1 = np.clip(hist1, 0.0, None)
            hist2 = np.clip(hist2, 0.0, None)
            bc = float(np.sum(np.sqrt(hist1 * hist2)))
            divergence = float(np.sqrt(max(0.0, 1.0 - min(bc, 1.0))))
            divergences.append(divergence)
        return float(np.mean(divergences))


class GateService:
    def __init__(self, config: AppConfig) -> None:
        self._default_pixel_diff_threshold = config.gate_pixel_diff_threshold_pct
        self._default_histogram_threshold = config.gate_histogram_threshold
        self._pixel_gate = PixelDiffGate()
        self._hist_gate = HistogramDivergenceGate()
        self._last_signals: Optional[GateSignals] = None
        self.skip_count = 0
        self.process_count = 0

    @property
    def last_signals(self) -> Optional[GateSignals]:
        return self._last_signals

    @staticmethod
    def _validate_frame(frame: np.ndarray) -> None:
        if frame.ndim != 3 or frame.shape[2] != 3:
            raise ValueError("Frames must be HxWx3.")
        if frame.dtype != np.uint8:
            raise ValueError("Frames must be uint8.")

    def _thresholds_for_resolution(self, resolution: Tuple[int, int]) -> Tuple[float, float]:
        return GATE_THRESHOLDS.get(
            resolution,
            (self._default_pixel_diff_threshold, self._default_histogram_threshold),
        )

    def should_process(
        self,
        prev_frame: Optional[np.ndarray],
        curr_frame: np.ndarray,
        resolution: Optional[Tuple[int, int]] = None,
    ) -> bool:
        self._validate_frame(curr_frame)

        if prev_frame is None:
            self.process_count += 1
            self._last_signals = GateSignals(pixel_diff_pct=100.0, histogram_change=1.0)
            return True

        self._validate_frame(prev_frame)
        if prev_frame.shape != curr_frame.shape:
            self.process_count += 1
            self._last_signals = GateSignals(pixel_diff_pct=100.0, histogram_change=1.0)
            return True

        frame_resolution = resolution or (curr_frame.shape[1], curr_frame.shape[0])
        pixel_threshold, histogram_threshold = self._thresholds_for_resolution(
            frame_resolution
        )

        pixel_diff_pct = self._pixel_gate.score(prev_frame, curr_frame)
        if pixel_diff_pct < pixel_threshold:
            self.skip_count += 1
            self._last_signals = GateSignals(
                pixel_diff_pct=pixel_diff_pct,
                histogram_change=0.0,
            )
            return False

        histogram_change = self._hist_gate.score(prev_frame, curr_frame)
        self._last_signals = GateSignals(
            pixel_diff_pct=pixel_diff_pct,
            histogram_change=histogram_change,
        )
        should_process = histogram_change >= histogram_threshold
        if should_process:
            self.process_count += 1
        else:
            self.skip_count += 1
        return should_process

    @staticmethod
    def calculate_pixel_diff_pct(prev_frame: np.ndarray, curr_frame: np.ndarray) -> float:
        return PixelDiffGate().score(prev_frame, curr_frame)

    @staticmethod
    def calculate_histogram_divergence(prev_frame: np.ndarray, curr_frame: np.ndarray) -> float:
        return HistogramDivergenceGate().score(prev_frame, curr_frame)
