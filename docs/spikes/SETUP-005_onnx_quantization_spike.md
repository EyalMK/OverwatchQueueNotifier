# SETUP-005 Spike: INT8 vs FP32 ONNX Quantization

## Goal
Decide whether INT8 quantized models meet latency (<50ms p95) and accuracy targets vs FP32.

## Approach
1. Obtain two models:
   - `tiny_classifier_fp32.onnx`
   - `tiny_classifier_int8.onnx`
2. Run local benchmark script:

```bash
cd backend
uv sync --extra onnx --dev
uv run python scripts/benchmark_onnx.py
```

3. Compare p95 latency and note accuracy deltas from validation set.

## Script
See `backend/scripts/benchmark_onnx.py`.

## Status
Blocked. Model files and validation dataset are not present in `backend/models/`.

## Blockers
- Missing `backend/models/tiny_classifier_fp32.onnx`
- Missing `backend/models/tiny_classifier_int8.onnx`
- Validation dataset for accuracy comparison not available

## Next Steps
1. Add both model files to `backend/models/`.
2. Provide a small labeled validation set (images + labels).
3. Run:
```bash
cd backend
uv sync --extra onnx --dev
uv run python scripts/benchmark_onnx.py
```

## Results
Pending.
