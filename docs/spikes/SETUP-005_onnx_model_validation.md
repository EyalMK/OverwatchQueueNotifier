# SETUP-005 Spike: ONNX Model Quantization & Latency Validation
**Date**: February 7, 2026  
**Status**: ✓ COMPLETE  
**Type**: Spike / Technical Validation  
**Story Points**: 4  

---

## Executive Summary

**Decision**: Use **ShuffleNet-V2** as the primary tiny classifier model.

| Metric | EfficientNet-Lite4 | ShuffleNet-V2 | Winner |
|--------|-------------------|---------------|--------|
| **Model Size** | 49.54 MB | 5.25 MB | ShuffleNet-V2 (9.4x smaller) |
| **p95 Latency** | 7.53ms | **1.75ms** | ShuffleNet-V2 (4.3x faster) |
| **Mean Latency** | 6.16ms | 1.29ms | ShuffleNet-V2 |
| **Jitter (stddev)** | 0.74ms | 0.23ms | ShuffleNet-V2 (more consistent) |
| **Max Latency** | 8.59ms | 2.53ms | ShuffleNet-V2 |
| **Passes <50ms?** | ✓ YES | ✓ YES | Both Pass |

---

## Objective

Validate that the available ONNX models (EfficientNet-Lite4 and ShuffleNet-V2) can meet the strict latency requirement of **<50ms p95** for real-time queue detection.

---

## Methodology

### Test Setup
- **Environment**: Windows 10/11, CPU-only (no GPU acceleration)
- **Model Format**: ONNX Runtime (CPUExecutionProvider)
- **Input Shape**: 224×224×3 (RGB, normalized float32)
- **Iterations**: 100 inference runs per model
- **Warmup**: 2 additional runs before measurement (to stabilize)
- **Latency Measurement**: Per-inference wall-clock time using `time.perf_counter()`

### Test Procedure
1. Load ONNX model via ONNX Runtime with CPU provider
2. Run 2 warmup iterations
3. Run 100 timed inferences with random normalized input
4. Calculate percentiles (min, p50, p95, p99, max, mean, stdev)
5. Compare against 50ms threshold

### Results

#### EfficientNet-Lite4 (49.54 MB)
```
Input Shape: [1, 224, 224, 3]
Output Shape: [1, 1000]

Latency Distribution:
  Min:    4.88ms
  Mean:   6.16ms
  Median: 6.02ms
  p95:    7.53ms ✓ PASS
  p99:    8.49ms
  Max:    8.59ms
  Jitter: 0.74ms (stdev)
```

#### ShuffleNet-V2 (5.25 MB)
```
Input Shape: [1, 3, 224, 224]
Output Shape: [1, 1000]

Latency Distribution:
  Min:    1.03ms
  Mean:   1.29ms
  Median: 1.23ms
  p95:    1.75ms ✓ PASS
  p99:    2.28ms
  Max:    2.53ms
  Jitter: 0.23ms (stdev)
```

---

## Analysis

### Both Models Exceed Target
- ✓ EfficientNet-Lite4: 7.53ms << 50ms target
- ✓ ShuffleNet-V2: 1.75ms << 50ms target

Both models deliver **exceptional performance**, well below the 50ms requirement. This provides:
- **Headroom for escalation inference** (100-150ms budget per spec)
- **Comfortable margin for gate heuristics** (<5ms)
- **Total perception cycle <100ms p95** achievable

### ShuffleNet-V2 is Superior

**Recommendation: ShuffleNet-V2**

**Rationale:**
1. **4.3x faster p95 latency** (1.75ms vs 7.53ms) — exceeds every performance target
2. **9.4x smaller model** (5.25 MB vs 49.54 MB) — reduces memory footprint, faster loading
3. **Lower variance** (0.23ms vs 0.74ms) — more predictable, deterministic performance
4. **Margin for error**: Even at p99, only 2.28ms — plenty of room for system variability
5. **Production-ready**: Compact model enables faster iteration, testing, and deployment

---

## Quantization Analysis

### Observations
- Both models appear to be **FP32** (float32 precision) based on:
  - ONNX opset handling standard float32 operations
  - Model file sizes consistent with uncompressed weights
  
- Neither requires conversion to INT8 quantization:
  - Already meet <50ms requirement by **>25x margin**
  - Quantization would add development complexity without benefit
  - Risk of accuracy loss not justified

### Decision: Skip Quantization
- **Focus on accuracy gains** in Sprint 1 (escalation logic, per-resolution calibration)
- **FP32 inference is production-ready** now

---

## Next Steps (Sprint 1)

1. **Implement `backend/src/perception/classifier.py`** using ShuffleNet-V2
   - Load model from `backend/models/Shufflenet-v2.onnx`
   - Support escalation with EfficientNet-Lite4 if confidence < 0.85

2. **Add calibration profiles** (per-resolution input normalization)
   - Per-device brightness/contrast adjustment
   - User-friendly calibration wizard (Sprint 2)

3. **Validate accuracy with real Overwatch screenshots**
   - True positive rate (queue detection)
   - False positive rate (heuristic filtering)
   - Target: >95% TP, <5% FP

4. **Performance monitoring in production**
   - Track actual p95 latency across user base
   - Monitor accuracy metrics over time

---

## Recommendation Summary

| Item | Decision |
|------|----------|
| **Primary Tiny Classifier** | ShuffleNet-V2 |
| **Escalation Model** | EfficientNet-Lite4 (optional, for low-confidence cases) |
| **Quantization** | Skip — FP32 sufficient |
| **Inference Engine** | ONNX Runtime (CPU) |
| **Target Latency** | p95 < 50ms (Achieved: 1.75ms) |
| **Margin** | >25x overshoot — excellent headroom |

---

## Reference Files

- **Benchmark Script**: `backend/scripts/benchmark_onnx.py`
- **Results**: `backend/benchmark_results.json`
- **Models**: 
  - `backend/models/Shufflenet-v2.onnx` (5.25 MB) — PRIMARY
  - `backend/models/efficientnet-lite4-11.onnx` (49.54 MB) — ESCALATION (optional)

---

**Owner**: Backend Lead  
**Date Completed**: February 7, 2026  
**Status**: Unblocks BACKEND-003, BACKEND-004 in Sprint 1
