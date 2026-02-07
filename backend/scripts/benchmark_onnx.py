#!/usr/bin/env python3
"""
SETUP-005 Spike: ONNX Model Latency Benchmark
Tests EfficientNet-Lite4 and ShuffleNet-V2 models for inference latency.

Target: <50ms per inference (p95)
Requirement: Validate tiny classifier meets performance budget
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import onnxruntime as ort


def _load_session(model_path: Path) -> ort.InferenceSession:
    """Load ONNX model with CPU execution provider."""
    return ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])


def _get_model_info(session: ort.InferenceSession) -> dict[str, Any]:
    """Extract model I/O information."""
    inputs = session.get_inputs()
    outputs = session.get_outputs()
    
    return {
        "input_name": inputs[0].name,
        "input_shape": inputs[0].shape,
        "output_names": [o.name for o in outputs],
        "output_shapes": [o.shape for o in outputs],
    }


def _create_dummy_input(input_shape: list) -> np.ndarray:
    """Create normalized dummy input based on model shape."""
    # Convert shape to list of ints, handle dynamic dimensions (None/?)
    shape = [s if isinstance(s, int) and s > 0 else 1 for s in input_shape]
    dummy = np.random.rand(*shape).astype(np.float32)
    return dummy


def _run_benchmark(
    session: ort.InferenceSession,
    input_name: str,
    input_shape: list,
    runs: int = 100,
) -> dict[str, float]:
    """
    Run inference multiple times and measure latency.
    
    Returns: Dict with latency statistics
    """
    # Warmup
    dummy = _create_dummy_input(input_shape)
    for _ in range(2):
        session.run(None, {input_name: dummy})
    
    latencies_ms = []
    for i in range(runs):
        dummy = _create_dummy_input(input_shape)
        start = time.perf_counter()
        session.run(None, {input_name: dummy})
        elapsed = (time.perf_counter() - start) * 1000
        latencies_ms.append(elapsed)
        
        if (i + 1) % 25 == 0:
            print(f"    Progress: {i + 1}/{runs}")
    
    latencies_sorted = sorted(latencies_ms)
    
    return {
        "min_ms": float(np.min(latencies_ms)),
        "max_ms": float(np.max(latencies_ms)),
        "mean_ms": float(np.mean(latencies_ms)),
        "median_ms": float(np.median(latencies_ms)),
        "p95_ms": float(np.percentile(latencies_ms, 95)),
        "p99_ms": float(np.percentile(latencies_ms, 99)),
        "stdev_ms": float(np.std(latencies_ms)),
    }


def format_results(results: dict[str, dict[str, float]]) -> str:
    """Format benchmark results as readable table."""
    lines = []
    lines.append("\n" + "=" * 100)
    lines.append("ONNX MODEL LATENCY BENCHMARK RESULTS (SETUP-005 Spike)")
    lines.append("=" * 100)
    
    # Header
    header = f"{'Model':<25} {'Min':<12} {'Mean':<12} {'Median':<12} {'p95':<12} {'p99':<12} {'Max':<12}"
    lines.append(header)
    lines.append("-" * 100)
    
    # Data rows
    for model_name, metrics in results.items():
        line = f"{model_name:<25}"
        line += f"{metrics['min_ms']:<12.2f}"
        line += f"{metrics['mean_ms']:<12.2f}"
        line += f"{metrics['median_ms']:<12.2f}"
        line += f"{metrics['p95_ms']:<12.2f}"
        line += f"{metrics['p99_ms']:<12.2f}"
        line += f"{metrics['max_ms']:<12.2f}"
        lines.append(line)
    
    lines.append("=" * 100)
    lines.append("TARGET REQUIREMENT: p95 latency < 50ms")
    lines.append("=" * 100)
    
    return "\n".join(lines)


def main() -> None:
    """Run benchmark for both models."""
    models_dir = Path(__file__).resolve().parents[1] / "models"
    
    model_configs = {
        "EfficientNet-Lite4": models_dir / "efficientnet-lite4-11.onnx",
        "ShuffleNet-V2": models_dir / "Shufflenet-v2.onnx",
    }
    
    # Check models exist
    print("Checking for ONNX models...")
    for name, path in model_configs.items():
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024)
            print(f"✓ {name}: {path.name} ({size_mb:.2f} MB)")
        else:
            print(f"✗ {name}: NOT FOUND at {path}")
            sys.exit(1)
    
    # Run benchmarks
    results = {}
    num_iterations = 100
    
    print(f"\nRunning {num_iterations} inference iterations per model...")
    print("(This may take 1-2 minutes)\n")
    
    for model_name, model_path in model_configs.items():
        print(f"\nBenchmarking {model_name}...")
        try:
            session = _load_session(model_path)
            info = _get_model_info(session)
            
            print(f"  Input shape: {info['input_shape']}")
            print(f"  Output shapes: {info['output_shapes']}")
            print(f"  Running {num_iterations} iterations...")
            
            metrics = _run_benchmark(
                session,
                info["input_name"],
                info["input_shape"],
                runs=num_iterations,
            )
            results[model_name] = metrics
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            sys.exit(1)
    
    # Display results
    print(format_results(results))
    
    # Analysis
    print("\nANALYSIS:")
    print("-" * 100)
    
    for model_name, metrics in results.items():
        p95 = metrics['p95_ms']
        status = "✓ PASS" if p95 < 50 else "✗ FAIL"
        print(f"{model_name}:")
        print(f"  p95 Latency: {p95:.2f}ms {status}")
        print(f"  Mean Latency: {metrics['mean_ms']:.2f}ms")
        print(f"  Jitter (stdev): {metrics['stdev_ms']:.2f}ms")
    
    print("\nRECOMMENDATION:")
    print("-" * 100)
    
    # Choose model with best p95
    best_model = min(results.items(), key=lambda x: x[1]['p95_ms'])
    best_name, best_metrics = best_model
    
    all_pass = all(m['p95_ms'] < 50 for m in results.values())
    
    print(f"Selected Model: {best_name}")
    print(f"Reason: Best p95 latency ({best_metrics['p95_ms']:.2f}ms)")
    print(f"Status: {'✓ All models meet <50ms requirement' if all_pass else '⚠ Some models exceed 50ms - consider filtering'}")
    
    # Save results to JSON
    output_file = Path(__file__).resolve().parents[1] / "benchmark_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "iterations": num_iterations,
            "target_p95_ms": 50,
            "recommendation": best_name,
            "all_models_pass": all_pass,
            "results": results,
        }, f, indent=2)
    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
