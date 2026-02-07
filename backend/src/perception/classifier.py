from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
from PIL import Image

from ..config import AppConfig, CLASSIFIER_CONFIG
from ..errors import AIInferenceError

try:  # pragma: no cover - optional dependency
    import onnxruntime as ort
except Exception:  # pragma: no cover - optional dependency
    ort = None


def _softmax(logits: np.ndarray) -> np.ndarray:
    logits = logits.astype(np.float32)
    logits -= np.max(logits)
    exp = np.exp(logits)
    return exp / np.sum(exp)


class EscalationStrategy(Enum):
    NONE = "none"
    RERUN_TINY = "rerun"
    ESCALATE = "escalate"


def get_escalation_strategy(
    confidence: float, escalation_threshold: float = 0.85
) -> EscalationStrategy:
    if confidence >= escalation_threshold:
        return EscalationStrategy.NONE
    if confidence >= 0.70:
        return EscalationStrategy.RERUN_TINY
    return EscalationStrategy.ESCALATE


class ImagePreprocessor:
    def __init__(self, input_dim: Tuple[int, int] = (224, 224)) -> None:
        self._input_dim = input_dim

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        if image.ndim != 3 or image.shape[2] != 3:
            raise AIInferenceError("Input image must be HxWx3.")
        if image.dtype != np.uint8:
            raise AIInferenceError("Input image must use uint8 dtype.")

        # Resize shortest edge then center-crop to model input size.
        target_w, target_h = self._input_dim
        pil = Image.fromarray(image, mode="RGB")
        src_w, src_h = pil.size
        scale = max(target_w / max(src_w, 1), target_h / max(src_h, 1))
        resized_w = max(target_w, int(round(src_w * scale)))
        resized_h = max(target_h, int(round(src_h * scale)))
        resized = pil.resize((resized_w, resized_h), Image.BILINEAR)

        left = max(0, (resized_w - target_w) // 2)
        top = max(0, (resized_h - target_h) // 2)
        crop = resized.crop((left, top, left + target_w, top + target_h))

        arr = np.asarray(crop, dtype=np.float32) / 255.0
        chw = np.transpose(arr, (2, 0, 1))
        return np.expand_dims(chw, axis=0).astype(np.float32)

    @staticmethod
    def zoom_center(image: np.ndarray, zoom_factor: float = 1.2) -> np.ndarray:
        if zoom_factor <= 1.0:
            return image
        h, w = image.shape[:2]
        new_w = max(1, int(w / zoom_factor))
        new_h = max(1, int(h / zoom_factor))
        x1 = (w - new_w) // 2
        y1 = (h - new_h) // 2
        x2 = x1 + new_w
        y2 = y1 + new_h
        cropped = image[y1:y2, x1:x2]
        resized = Image.fromarray(cropped, mode="RGB").resize((w, h), Image.BILINEAR)
        return np.asarray(resized, dtype=np.uint8)


class _BaseONNXClassifier:
    def __init__(
        self,
        model_path: Path,
        class_names: List[str],
        preprocessor: ImagePreprocessor,
    ) -> None:
        self._model_path = model_path
        self._class_names = class_names
        self._preprocessor = preprocessor
        self.session = self._load_session(model_path)

    @staticmethod
    def _resolve_model_path(model_path: Path) -> Path:
        if model_path.exists():
            return model_path
        repo_root = Path(__file__).resolve().parents[3]
        backend_root = Path(__file__).resolve().parents[2]
        candidates = [
            repo_root / model_path,
            backend_root / model_path,
            backend_root / "models" / model_path.name,
        ]
        if len(model_path.parts) >= 2 and model_path.parts[0] == "backend":
            candidates.append(repo_root / Path(*model_path.parts[1:]))
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return model_path

    @staticmethod
    def _load_session(model_path: Path):
        resolved_model_path = _BaseONNXClassifier._resolve_model_path(model_path)
        if ort is None:
            raise AIInferenceError("onnxruntime is not installed.")
        if not resolved_model_path.exists():
            raise AIInferenceError(f"Model file not found: {model_path}")
        try:
            return ort.InferenceSession(str(resolved_model_path))
        except Exception as exc:  # pragma: no cover - runtime specific
            raise AIInferenceError(f"Failed to load ONNX model: {model_path}") from exc

    def predict(self, image: np.ndarray) -> Tuple[str, float]:
        try:
            preprocessed = self._preprocessor.preprocess(image)
            input_name = self.session.get_inputs()[0].name
            outputs = self.session.run(None, {input_name: preprocessed})
            logits = np.asarray(outputs[0]).squeeze()
            probs = _softmax(logits)
            best_idx = int(np.argmax(probs))
            return self._class_names[best_idx], float(probs[best_idx])
        except AIInferenceError:
            raise
        except Exception as exc:
            raise AIInferenceError(f"Classifier inference failed: {exc}") from exc


class TinyClassifier(_BaseONNXClassifier):
    pass


class EscalationClassifier(_BaseONNXClassifier):
    pass


@dataclass
class ClassifierResult:
    state: str
    confidence: float
    escalated: bool


class Classifier:
    def __init__(
        self,
        config: Optional[AppConfig] = None,
        tiny_model_path: Optional[Path] = None,
        escalation_model_path: Optional[Path] = None,
    ) -> None:
        self._config = config
        self._escalation_threshold = (
            config.escalation_confidence_threshold
            if config
            else float(CLASSIFIER_CONFIG["escalation_threshold"])
        )
        self._class_names: List[str] = list(CLASSIFIER_CONFIG["class_names"])
        self._preprocessor = ImagePreprocessor(
            input_dim=tuple(CLASSIFIER_CONFIG["input_dim"])
        )
        tiny_path = tiny_model_path or Path(CLASSIFIER_CONFIG["tiny_model_path"])
        escalation_path = escalation_model_path or Path(
            CLASSIFIER_CONFIG["escalation_model_path"]
        )
        self.tiny = TinyClassifier(tiny_path, self._class_names, self._preprocessor)
        self.escalation = EscalationClassifier(
            escalation_path, self._class_names, self._preprocessor
        )

    def rerun_tiny_with_augmentation(self, image: np.ndarray) -> Tuple[str, float]:
        zoomed = ImagePreprocessor.zoom_center(image, zoom_factor=1.2)
        return self.tiny.predict(zoomed)

    def classify_with_escalation(
        self,
        image: np.ndarray,
        escalation_threshold: Optional[float] = None,
    ) -> Tuple[str, float, bool]:
        threshold = (
            escalation_threshold
            if escalation_threshold is not None
            else self._escalation_threshold
        )
        tiny_state, tiny_conf = self.tiny.predict(image)
        strategy = get_escalation_strategy(tiny_conf, threshold)

        if strategy == EscalationStrategy.NONE:
            return tiny_state, tiny_conf, False

        if strategy == EscalationStrategy.RERUN_TINY:
            rerun_state, rerun_conf = self.rerun_tiny_with_augmentation(image)
            if rerun_conf >= threshold:
                return rerun_state, rerun_conf, False
            esc_state, esc_conf = self.escalation.predict(image)
            return esc_state, esc_conf, True

        esc_state, esc_conf = self.escalation.predict(image)
        return esc_state, esc_conf, True

    def predict(self, image: np.ndarray) -> Tuple[str, float]:
        return self.tiny.predict(image)

    def predict_with_escalation(self, image: np.ndarray) -> ClassifierResult:
        state, confidence, escalated = self.classify_with_escalation(image)
        return ClassifierResult(state=state, confidence=confidence, escalated=escalated)


ClassifierService = Classifier
