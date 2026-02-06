from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import onnxruntime as ort


def _load_session(model_path: Path) -> ort.InferenceSession:
    return ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])


def _run_benchmark(session: ort.InferenceSession, runs: int = 100) -> float:
    input_name = session.get_inputs()[0].name
    # Assume model expects NCHW float32, 1x3x224x224
    sample = np.random.rand(1, 3, 224, 224).astype(np.float32)

    latencies_ms = []
    for _ in range(runs):
        start = time.perf_counter()
        session.run(None, {input_name: sample})
        latencies_ms.append((time.perf_counter() - start) * 1000)

    latencies_ms.sort()
    p95 = latencies_ms[int(len(latencies_ms) * 0.95)]
    return p95


def main() -> None:
    models_dir = Path(__file__).resolve().parents[1] / "models"
    fp32_path = models_dir / "tiny_classifier_fp32.onnx"
    int8_path = models_dir / "tiny_classifier_int8.onnx"

    if not fp32_path.exists() or not int8_path.exists():
        raise SystemExit(
            "Missing model files. Expected: "
            f"{fp32_path} and {int8_path}"
        )

    fp32_p95 = _run_benchmark(_load_session(fp32_path))
    int8_p95 = _run_benchmark(_load_session(int8_path))

    print(f"FP32 p95 latency: {fp32_p95:.2f}ms")
    print(f"INT8 p95 latency: {int8_p95:.2f}ms")


if __name__ == "__main__":
    main()
