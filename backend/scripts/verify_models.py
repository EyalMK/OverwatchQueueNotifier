from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import onnxruntime as ort


def _resolve(path: Path) -> Path:
    if path.exists():
        return path
    repo_root = Path(__file__).resolve().parents[2]
    backend_root = Path(__file__).resolve().parents[1]
    candidates = [
        repo_root / path,
        backend_root / path,
        backend_root / "models" / path.name,
    ]
    if len(path.parts) >= 2 and path.parts[0] == "backend":
        candidates.append(repo_root / Path(*path.parts[1:]))
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return path


def verify_models() -> None:
    models = [
        ("tiny", Path("backend/models/Shufflenet-v2.onnx")),
        ("escalation", Path("backend/models/efficientnet-lite4-11.onnx")),
    ]

    for name, path in models:
        session = ort.InferenceSession(str(_resolve(path)))
        input_meta = session.get_inputs()[0]
        input_name = input_meta.name
        shape = list(input_meta.shape)
        if len(shape) == 4 and shape[1] == 3:
            dummy = np.random.randn(1, 3, 224, 224).astype(np.float32)
        elif len(shape) == 4 and shape[-1] == 3:
            dummy = np.random.randn(1, 224, 224, 3).astype(np.float32)
        else:
            dummy = np.random.randn(1, 3, 224, 224).astype(np.float32)
        start = time.perf_counter()
        session.run(None, {input_name: dummy})
        latency_ms = (time.perf_counter() - start) * 1000
        print(f"{name}: {latency_ms:.2f}ms")


if __name__ == "__main__":
    verify_models()
