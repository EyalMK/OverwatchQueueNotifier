from __future__ import annotations

import time

import numpy as np
import pytest

from src.errors import AIInferenceError
from src.perception.classifier import (
    Classifier,
    EscalationStrategy,
    ImagePreprocessor,
    get_escalation_strategy,
)


class FakeModel:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def predict(self, _image):
        self.calls += 1
        if not self.responses:
            return "IDLE", 0.99
        result = self.responses[min(self.calls - 1, len(self.responses) - 1)]
        if isinstance(result, Exception):
            raise result
        return result


def _fake_classifier(tiny_responses, escalation_responses):
    classifier = Classifier.__new__(Classifier)
    classifier._escalation_threshold = 0.85
    classifier.tiny = FakeModel(tiny_responses)
    classifier.escalation = FakeModel(escalation_responses)
    return classifier


def test_escalation_strategy_decision_points() -> None:
    assert get_escalation_strategy(0.95, 0.85) == EscalationStrategy.NONE
    assert get_escalation_strategy(0.75, 0.85) == EscalationStrategy.RERUN_TINY
    assert get_escalation_strategy(0.65, 0.85) == EscalationStrategy.ESCALATE


def test_preprocess_resize_and_normalization() -> None:
    pre = ImagePreprocessor((224, 224))
    image = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
    blob = pre.preprocess(image)
    assert blob.shape == (1, 3, 224, 224)
    assert blob.dtype == np.float32
    assert float(blob.min()) >= 0.0
    assert float(blob.max()) <= 1.0


def test_low_confidence_triggers_escalation() -> None:
    classifier = _fake_classifier([("QUEUE", 0.65)], [("MATCH_FOUND", 0.92)])
    state, conf, escalated = classifier.classify_with_escalation(np.zeros((100, 100, 3), dtype=np.uint8))
    assert escalated is True
    assert state == "MATCH_FOUND"
    assert conf == 0.92
    assert classifier.escalation.calls == 1


def test_high_confidence_skips_escalation() -> None:
    classifier = _fake_classifier([("IDLE", 0.95)], [("MATCH_FOUND", 0.92)])
    state, conf, escalated = classifier.classify_with_escalation(np.zeros((100, 100, 3), dtype=np.uint8))
    assert escalated is False
    assert state == "IDLE"
    assert conf == 0.95
    assert classifier.escalation.calls == 0


def test_rerun_tiny_with_augmentation_path() -> None:
    classifier = _fake_classifier([("QUEUE", 0.78), ("QUEUE", 0.88)], [("MATCH_FOUND", 0.9)])
    state, conf, escalated = classifier.classify_with_escalation(np.zeros((100, 100, 3), dtype=np.uint8))
    assert state == "QUEUE"
    assert conf == 0.88
    assert escalated is False
    assert classifier.tiny.calls == 2


def test_inference_error_bubbles_as_ai_inference_error() -> None:
    classifier = _fake_classifier([AIInferenceError("boom")], [])
    with pytest.raises(AIInferenceError):
        classifier.classify_with_escalation(np.zeros((10, 10, 3), dtype=np.uint8))


def test_latency_slo_with_mock_models() -> None:
    classifier = _fake_classifier([("QUEUE", 0.95)], [])
    start = time.perf_counter()
    classifier.classify_with_escalation(np.zeros((100, 100, 3), dtype=np.uint8))
    tiny_latency_ms = (time.perf_counter() - start) * 1000
    assert tiny_latency_ms < 50
