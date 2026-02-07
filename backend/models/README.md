# ONNX Models (SETUP-005 Validated)

## Tiny Classifier: ShuffleNet-V2
- Type: FP32
- Size: 5.25 MB
- Input: RGB image 224x224, normalized [0, 1]
- Output: 6-class softmax logits
- Latency (p95): 1.75ms on CPU
- Path: `backend/models/Shufflenet-v2.onnx`

## Escalation Classifier: EfficientNet-Lite4
- Type: FP32
- Size: ~15 MB
- Input: RGB image 224x224, normalized [0, 1]
- Output: 6-class softmax logits
- Latency (p95): 7.53ms on CPU
- Path: `backend/models/efficientnet-lite4-11.onnx`

## Notes
- Quantization was intentionally skipped because FP32 already exceeds latency SLOs.
- Validation benchmark: `docs/spikes/SETUP-005_onnx_model_validation.md`.
