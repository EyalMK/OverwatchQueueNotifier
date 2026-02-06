from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np

from ..config import AppConfig

try:  # pragma: no cover - optional dependency
    import onnxruntime as ort
except Exception:  # pragma: no cover - optional dependency
    ort = None


@dataclass
class ClassifierResult:
    state: str
    confidence: float
    escalated: bool


def _softmax(logits: np.ndarray) -> np.ndarray:
    logits = logits.astype(np.float32)
    logits = logits - np.max(logits)
    exp = np.exp(logits)
    return exp / np.sum(exp)


class ClassifierService:
    def __init__(
        self,
        config: AppConfig,
        tiny_model_path: Optional[Path] = None,
        escalation_model_path: Optional[Path] = None,
    ) -> None:
        self._config = config
        self._classes: List[str] = [
            "IDLE",
            "QUEUE",
            "MATCH_FOUND",
            "HERO_SELECT",
            "LOADING",
            "IN_GAME",
        ]
        self._tiny_session = self._load_session(
            tiny_model_path or Path("models") / "tiny_classifier.onnx"
        )
        self._escalation_session = self._load_session(
            escalation_model_path or Path("models") / "escalation_model.onnx"
        )

    @staticmethod
    def _load_session(model_path: Path):
        if ort is None:
            return None
        if not model_path.exists():
            return None
        return ort.InferenceSession(str(model_path))

    def _preprocess(self, image: np.ndarray) -> np.ndarray:
        if image.ndim != 3 or image.shape[2] != 3:
            raise ValueError("Input image must be HxWx3.")
        resized = self._resize_to_224(image)
        normalized = resized.astype(np.float32) / 255.0
        chw = np.transpose(normalized, (2, 0, 1))
        return np.expand_dims(chw, axis=0)

    @staticmethod
    def _resize_to_224(image: np.ndarray) -> np.ndarray:
        if image.shape[0] == 224 and image.shape[1] == 224:
            return image
        # Simple nearest-neighbor resize to avoid extra deps.
        y_idx = (np.linspace(0, image.shape[0] - 1, 224)).astype(int)
        x_idx = (np.linspace(0, image.shape[1] - 1, 224)).astype(int)
        return image[np.ix_(y_idx, x_idx)]

    def _run(self, session, image: np.ndarray) -> Tuple[str, float]:
        if session is None:
            return "UNKNOWN", 0.0
        input_name = session.get_inputs()[0].name
        outputs = session.run(None, {input_name: image})
        logits = outputs[0].squeeze()
        probs = _softmax(np.asarray(logits))
        idx = int(np.argmax(probs))
        return self._classes[idx], float(probs[idx])

    def predict(self, image: np.ndarray) -> Tuple[str, float]:
        blob = self._preprocess(image)
        return self._run(self._tiny_session, blob)

    def predict_with_escalation(self, image: np.ndarray) -> ClassifierResult:
        state, conf = self.predict(image)
        if conf >= self._config.escalation_confidence_threshold:
            return ClassifierResult(state=state, confidence=conf, escalated=False)

        blob = self._preprocess(image)
        esc_state, esc_conf = self._run(self._escalation_session, blob)
        final_conf = (conf + esc_conf) / 2.0
        return ClassifierResult(
            state=esc_state,
            confidence=final_conf,
            escalated=True,
        )
