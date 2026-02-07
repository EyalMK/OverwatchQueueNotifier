# Sprint 1: Backend Core & Architecture Sprint Execution Prompt
## Overwatch AI Queue Detection & Notification App

---

## Context — Read These Files First

You are executing **AutoSpec Spec-Driven Development** for Sprint 1: Backend Core & Architecture.

**Sprint Goal**: Complete AI perception engine (gate + classifier), implement MCP API contracts, operational database, state machine transitions. Move from foundation to core feature delivery.

### SPECS (Single source of truth — READ ALL)
- `specs/02_backend_lead.md` **[PRIMARY]** — API contracts, error handling, rate limiting, latency SLOs
- `specs/04_db_architect.md` — Database schema refinement, query patterns, retention policies
- `specs/05_qa_lead.md` — Unit test examples, integration test patterns, coverage targets
- `specs/01_product_manager.md` — User stories, personas (context for why features matter)

### BACKLOG & EXECUTION GUIDES
- `specs/backlog.md` — Sprint 1 section (12 tickets, 38 points, Weeks 3–5)
- `sprint_prompts/sprint-0-foundation.md` — Reference for template structure
- `workflows/development.md` — Ticket workflow (pick → test → implement → merge)
- `workflows/sprint-execution.md` — Daily standups, review process, velocity tracking

### ARCHITECTURE DOCS
- `docs/architecture/backend.md` — Layered design (perception → repository → MCP)
- `docs/architecture/database.md` — ERD, CREATE TABLE, migration versioning
- `docs/testing/strategy.md` — Test pyramid, unit vs integration vs e2e

### API REFERENCE
- `docs/api/reference.md` — MCP tool contracts with request/response JSON examples

---

## Sprint 0 → Sprint 1 Handoff

### What Sprint 0 Completed ✅
- 4-table SQLite schema created (calibration_profiles, detection_history, notification_log, settings)
- Migration runner scaffolded (`backend/src/db/migrations.py`)
- Repository layer abstraction: `CalibrationRepository`, `DetectionRepository`, `NotificationRepository`, `SettingsRepository`
- MCP FastAPI server with 4 endpoint stubs (`perceive_state`, `capture_regions`, `notify.desktop`, `notify.discord`)
- Perception service skeletons: `ScreenCaptureService`, `GateService`, `ClassifierService`
- 19 unit + integration tests plus `conftest.py` fixtures (mock screenshots, temp DB)
- CI/CD pipeline: GitHub Actions (lint, test, build)

### What Sprint 1 Must Deliver ✅
- **Gate heuristics** fully tuned (pixel diff %, histogram divergence, resolution-aware thresholds)
- **ONNX classifier pipeline** (download models, preprocess, inference, confidence scoring, escalation)
- **MCP endpoints functional** (perceive_state + capture_regions return real data; notify endpoints fire real notifications)
- **State transition machine** (4 states: IDLE → QUEUE → MATCH_FOUND → IN_GAME, idempotent guards)
- **Detection logging** (database inserts with evidence JSON, 24h retention cleanup)
- **Comprehensive testing** (85% coverage on gate + classifier, full integration test)

### Critical Blocker from Sprint 0 ✅ RESOLVED
**SETUP-005 Complete** (Feb 7, 2026): ONNX models validated and benchmarked.
- **Primary Model**: `backend/models/Shufflenet-v2.onnx` (5.25 MB, p95 latency = **1.75ms**)
- **Escalation Model**: `backend/models/efficientnet-lite4-11.onnx` (p95 latency = 7.53ms)
- **Decision**: FP32 quantization skipped — current models exceed performance targets by >25x margin
- **Status**: Models ready for immediate use in Sprint 1; no sourcing delays expected
- **Reference**: See `docs/spikes/SETUP-005_onnx_model_validation.md` for detailed benchmark results

---

## Phase Breakdown: AI Foundation → Pipeline → State → Integration

### Phase 1: ONNX Models & Classifier Foundation (Days 1–2, 11 points)
**Goal**: Integrate pre-validated ONNX models (SETUP-005 ✅ complete), implement inference pipeline with escalation logic, validate latency SLOs.

#### 1.1: Verify Models & Load Configuration (Model Setup, Day 1)
**Ticket**: (Verification of completed SETUP-005)

- [ ] Confirm ONNX models available in workspace:
  - `backend/models/Shufflenet-v2.onnx` (5.25 MB, verified p95 = 1.75ms) ✓
  - `backend/models/efficientnet-lite4-11.onnx` (verified p95 = 7.53ms) ✓
  - See `docs/spikes/SETUP-005_onnx_model_validation.md` for benchmark details

- [ ] Verify models load with ONNX Runtime 1.16+:
  ```bash
  python -c "
  import onnxruntime as ort
  tiny = ort.InferenceSession('backend/models/Shufflenet-v2.onnx')
  escalation = ort.InferenceSession('backend/models/efficientnet-lite4-11.onnx')
  print(f'Tiny model input shape: {tiny.get_inputs()[0].shape}')
  print(f'Escalation model input shape: {escalation.get_inputs()[0].shape}')
  "
  ```
  Expected output: Both models load without errors

- [ ] Update `backend/src/config.py` with verified model paths and specs:
  ```python
  CLASSIFIER_CONFIG = {
    "tiny_model_path": "backend/models/Shufflenet-v2.onnx",
    "escalation_model_path": "backend/models/efficientnet-lite4-11.onnx",
    "input_dim": (224, 224),
    "escalation_threshold": 0.85,
    "class_names": ["IDLE", "QUEUE", "MATCH_FOUND", "IN_GAME", "LOADING", "HERO_SELECT"],
  }
  ```

- [ ] Document model provenance in `backend/models/README.md`:
  ```markdown
  # ONNX Models (SETUP-005 Validated)

  ## Tiny Classifier: ShuffleNet-V2
  - Type: FP32 (no quantization needed)
  - Size: 5.25 MB
  - Input: RGB image 224×224, normalized [0, 1]
  - Output: 6-class softmax logits
  - **Latency (p95)**: 1.75ms on CPU — exceeds <50ms target by 25x ✓
  - Validation: See docs/spikes/SETUP-005_onnx_model_validation.md

  ## Escalation Classifier: EfficientNet-Lite4
  - Type: FP32
  - Size: ~15 MB
  - Latency (p95): 7.53ms on CPU ✓
  - Used when tiny model confidence < 0.85
  ```

- **Reference**: SETUP-005 spike (`docs/spikes/SETUP-005_onnx_model_validation.md`), specs/02_backend_lead.md (Section 3)
- **Verification**:
  ```bash
  ls -lh backend/models/
  # Shufflenet-v2.onnx                ~5 MB ✓
  # efficientnet-lite4-11.onnx        ~15 MB ✓
  ```

---

#### 1.2: BACKEND-002 — Document & Integrate ONNX Classifier Models [4 pts]
**Owner**: Backend  
**Dependency**: 1.1 complete

- [ ] Models already available from SETUP-005; this ticket focuses on **integration** into classifier pipeline
  - ShuffleNet-V2: Primary (tiny) model
  - EfficientNet-Lite4: Escalation (when confidence < 0.85)
  - Status: Both FP32, no INT8 quantization needed (already exceed latency targets by 25x)

- [ ] Create `backend/scripts/verify_models.py` (startup health check):
  ```python
  # Verify models exist, load correctly, and measure latency
  import onnxruntime as ort
  import numpy as np
  import time
  
  def verify_models():
      for name, path in [
          ("tiny", "backend/models/Shufflenet-v2.onnx"),
          ("escalation", "backend/models/efficientnet-lite4-11.onnx"),
      ]:
          sess = ort.InferenceSession(path)
          input_name = sess.get_inputs()[0].name
          dummy = np.random.randn(1, 3, 224, 224).astype(np.float32)
          
          start = time.perf_counter()
          sess.run(None, {input_name: dummy})
          latency = (time.perf_counter() - start) * 1000
          
          print(f"{name}: {latency:.2f}ms")
  ```

- [ ] Update `backend/src/config.py` with model paths (from 1.1) and classifier thresholds

- [ ] Update `backend/models/README.md` with final documentation (from 1.1)

- [ ] Add to `CONTRIBUTING.md`: Developer notes about models (no download needed, already in repo)

- **Reference**: SETUP-005 spike (`docs/spikes/SETUP-005_onnx_model_validation.md`), specs/02_backend_lead.md (Section 3)
- **Verification**:
  ```bash
  python backend/scripts/verify_models.py
  # Expected output:
  # tiny: 1.75ms
  # escalation: 7.53ms
  ```

---

#### 1.3: BACKEND-003 — Implement Classifier Inference Pipeline [4 pts]
**Owner**: Backend  
**Dependency**: 1.2 complete

Expand existing `backend/src/perception/classifier.py`:

- [ ] Implement `ImagePreprocessor` class:
  - Input: `np.ndarray` (H, W, 3) uint8, any resolution
  - Output: `np.ndarray` (1, 3, 224, 224) float32, normalized [0, 1]
  - Steps: Resize (bilinear), center crop, RGB→channels-first
  - Handle edge case: image smaller than 224×224 (pad with zeros or skip)
  - **Reference**: specs/02_backend_lead.md (Section 3: Perception / classifier.py)

- [ ] Implement `TinyClassifier` class:
  - Load ONNX model: `self.session = ort.InferenceSession('backend/models/Shufflenet-v2.onnx')`
  - Method: `def predict(image: np.ndarray) → Tuple[str, float]:`
    - Preprocess image
    - Get input/output names from session
    - Run inference: `self.session.run(None, {input_name: preprocessed})`
    - Output: softmax logits `(1, 6)` → argmax → class name (IDLE, QUEUE, etc.)
    - Extract confidence: `max(softmax_probs)`
    - Return: `(state_name, confidence_float)`
  - Latency must be <50ms for p95 (measured p95 = 1.75ms ✓)
  - Handle errors: `WindowNotFoundError`, `ResolutionMismatchError`, `AIInferenceError`

- [ ] Implement `EscalationClassifier` class (similar, but slower):
  - Load escalation model: `self.session = ort.InferenceSession('backend/models/efficientnet-lite4-11.onnx')`
  - Method: `def predict(image) → Tuple[str, float]:`
  - Latency <150ms p95 (measured p95 = 7.53ms ✓)

- [ ] Implement top-level `Classifier` class with escalation logic:
  - Method: `def classify_with_escalation(image: np.ndarray, escalation_threshold: float = 0.85) → Tuple[str, float, bool]:`
    - Step 1: Run tiny classifier (ShuffleNet-V2)
    - Step 2: If confidence < threshold, run escalation classifier (EfficientNet-Lite4)
    - Step 3: Return: `(final_state, final_confidence, was_escalated: bool)`
    - Log escalation events for QA analysis
  - **Reference**: specs/02_backend_lead.md (Section 8: Error Escalation)

- [ ] Update `backend/src/config.py` (from 1.1 verification) with actual model paths:
  ```python
  CLASSIFIER_CONFIG = {
    "tiny_model_path": "backend/models/Shufflenet-v2.onnx",
    "escalation_model_path": "backend/models/efficientnet-lite4-11.onnx",
    "input_dim": (224, 224),
    "escalation_threshold": 0.85,
    "class_names": ["IDLE", "QUEUE", "MATCH_FOUND", "IN_GAME", "LOADING", "HERO_SELECT"],
  }
  ```

- **Reference**: specs/02_backend_lead.md (Section 3: perception/classifier.py), SETUP-005 (`docs/spikes/SETUP-005_onnx_model_validation.md`)
- **Verification**:
  ```bash
  python -c "
  from backend.src.perception.classifier import Classifier
  import numpy as np
  clf = Classifier()
  dummy_frame = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
  state, conf, escalated = clf.classify_with_escalation(dummy_frame)
  print(f'State: {state}, Confidence: {conf:.3f}, Escalated: {escalated}')
  # Should complete in <50ms without escalation, <7.53ms tiny model alone
  "
  ```

---

#### 1.4: BACKEND-004 — Implement Error Escalation Logic [3 pts]
**Owner**: Backend  
**Dependency**: 1.3 complete

Refine escalation in `classifier.py`:

- [ ] Implement `EscalationStrategy` enum:
  ```python
  class EscalationStrategy(Enum):
      NONE = "none"         # Confidence > threshold, trust tiny model
      RERUN_TINY = "rerun"  # Confidence borderline, run tiny again on slightly modified crop
      ESCALATE = "escalate" # Confidence < threshold, run escalation model
  ```

- [ ] Implement logic to decide strategy:
  ```python
  def get_escalation_strategy(confidence: float, escalation_threshold: float = 0.85) → EscalationStrategy:
      if confidence >= escalation_threshold:
          return EscalationStrategy.NONE  # High confidence, trust tiny
      elif confidence >= 0.70:
          return EscalationStrategy.RERUN_TINY  # Medium: retry tiny on slightly zoomed-in crop
      else:
          return EscalationStrategy.ESCALATE  # Low: go to escalation model
  ```

- [ ] Implement `rerun_tiny_with_augmentation`:
  - Take crop, zoom in 1.2x (simulate focus), re-run tiny model
  - Used when confidence is borderline
  - Cheaper than escalation model
  - **Reference**: specs/02_backend_lead.md (Section 8: Error Escalation)

- [ ] Update `classify_with_escalation` to use strategy:
  - Step 1: Tiny classifier
  - Step 2: Check strategy
  - Step 3: If RERUN_TINY, crop + zoom + re-run
  - Step 4: If confidence still low, ESCALATE
  - Return final state + confidence + escalation metadata

- [ ] Add instrumentation: log all escalations with timestamps + original confidence + final confidence:
  ```python
  logger.info(f"Escalation: tiny_conf={tiny_conf:.3f}, strategy={strategy}, final_conf={final_conf:.3f}")
  ```

- [ ] Unit test: Mock classifier + verify strategy decisions
  - High confidence (0.95) → NONE
  - Medium (0.75) → RERUN_TINY
  - Low (0.65) → ESCALATE
  - Verify escalation count metrics

- **Reference**: specs/02_backend_lead.md (Section 8), specs/05_qa_lead.md (Section 3: Unit Test Examples)
- **Verification**:
  ```bash
  pytest backend/tests/unit/test_classifier.py::test_escalation_logic -v
  # Should show high/medium/low confidence triggering correct strategies
  ```

---

### Phase 2: Perception Pipeline & Core APIs (Days 2–4, 11 points)
**Goal**: Gate heuristics tuned, perceive_state endpoint orchestrates full pipeline, capture_regions returns real cropped evidence.

#### 2.1: BACKEND-001 — Implement Gate Heuristics [5 pts]
**Owner**: Backend  
**Dependency**: Sprint 0 gate skeleton exists

Expand `backend/src/perception/gate.py`:

- [ ] Implement `PixelDiffGate` strategy:
  - Compare two consecutive frames: `frame_t` and `frame_t+1`
  - Calculate % of pixels that changed: `diff_count / total_pixels`
  - **Formula**: `int(np.sum(np.abs(frame1.astype(int) - frame2.astype(int)) > threshold_channel_delta) / frame1.size * 100)`
  - Configurable threshold (env var): `GATE_PIXEL_DIFF_THRESHOLD` (default: 5% change triggers classifier run)
  - **Reference**: specs/02_backend_lead.md (Section 3: Perception / gate.py)

- [ ] Implement `HistogramDivergenceGate` strategy:
  - For each RGB channel, compute histogram (64 bins)
  - Bhattacharyya distance between frame histograms
  - Configurable threshold: `GATE_HISTOGRAM_THRESHOLD` (default: 0.3 divergence)
  - **Formula**: `sqrt(1 - sum(sqrt(h1[i] * h2[i]) for i in bins))` (normalized)

- [ ] Implement resolution-aware thresholds:
  - Input: resolution (1920×1080, 2560×1440, 3440×1440)
  - Adjust pixel diff threshold by area (higher res → lower %)
  - **Example**: 1920×1080: 5% | 2560×1440: 3% | 3440×1440: 2%
  - Implementation: `GATE_THRESHOLDS = {resolution: (pixel_diff%, histogram_thrash)}`

- [ ] Implement `Gate` orchestrator class:
  - Method: `def should_process(prev_frame: np.ndarray, curr_frame: np.ndarray, resolution: Tuple[int, int]) → bool:`
    - Run PixelDiffGate
    - If True, also check HistogramDivergenceGate (both must agree for safety)
    - Return: True if change is significant, False if static/noisy
  - Latency: <5ms (sub-10ms target)
  - Handle edge cases: first frame (always process), different resolutions

- [ ] Instrumentation: Count skipped frames
  - `gate.skip_count`, `gate.process_count`
  - Target: ≥50% of frames skipped (gate prevents unnecessary classifier runs)
  - Log: `logger.debug(f"Gate: processed {process_count} / {total_count} frames ({100*process_count/total_count:.1f}%)")`

- [ ] Unit tests (5–7 test cases for 85% coverage):
  - Static frame (identical): should skip
  - Large scene change (state transition): should process
  - Noisy frame (1 pixel diff): should skip
  - Resolution-specific: 1920×1080 vs 2560×1440 thresholds differ
  - Edge case: First frame (always process)
  - Edge case: Different resolution in consecutive frames (handle gracefully)
  - **Reference**: specs/05_qa_lead.md (Section 3: Unit Test Examples)

- **Reference**: specs/02_backend_lead.md (Section 3: perception/gate.py)
- **Verification**:
  ```bash
  pytest backend/tests/unit/test_gate.py -v --cov=backend/src/perception/gate
  # Coverage: ≥85%
  # All 7 test cases pass
  ```

---

#### 2.2: BACKEND-005 — Implement screen.perceive_state MCP Tool [5 pts]
**Owner**: Backend  
**Dependency**: 1.3 (classifier), 2.1 (gate) complete

Expand MCP endpoint in `backend/src/mcp/server.py`:

- [ ] Implement POST `/mcp/tools/screen.perceive_state`:
  - **Request JSON** (from specs/02_backend_lead.md, Section 4: API Contracts):
    ```json
    {
      "resolution": "1920x1080",           // Expected window resolution
      "calibration_profile_id": "uuid-...", // Optional, for crop regions
      "check_escalation": true             // Optional, default true
    }
    ```
  - **Response JSON** (success 200):
    ```json
    {
      "state": "QUEUE",                     // One of: IDLE, QUEUE, MATCH_FOUND, IN_GAME, LOADING, HERO_SELECT
      "confidence": 0.92,                   // 0.0 – 1.0, higher is more certain
      "escalated": false,                   // Was escalation model used?
      "evidence_image_base64": "iVBOR...",  // Small crop (e.g., 320×240) of relevant UI region
      "detected_at": "2026-02-07T10:30:45Z" // ISO timestamp
    }
    ```
  - **Error responses** (per spec):
    - 400 Bad Request: `{"error": "ResolutionMismatchError", "message": "Window has resolution 2560x1440, expected 1920x1080"}`
    - 400 Bad Request: `{"error": "WindowNotFoundError", "message": "Overwatch window not found"}`
    - 503 Service Unavailable: `{"error": "AIInferenceError", "message": "Classifier inference failed: [details]"}`

- [ ] Orchestrate full pipeline:
  ```python
  def perceive_state(request: PerceiveStateRequest):
      # 1. Capture screen (Overwatch window)
      frame = screen_capture_svc.capture(window_name="Overwatch 2")
      # 2. Verify resolution matches expected
      if frame.shape != (H, W, 3):
          raise ResolutionMismatchError(...)
      # 3. Check gate (significant change?)
      if not gate_svc.should_process(prev_frame, frame, resolution):
          return {"state": CACHED_STATE, "confidence": CACHED_CONF, "escalated": False, ...}
      # 4. Run classifier (with optional escalation)
      state, confidence, escalated = classifier_svc.classify_with_escalation(frame)
      # 5. Crop evidence region (e.g., UI region of interest) and base64-encode
      evidence_crop = frame[Y_MIN:Y_MAX, X_MIN:X_MAX, :]  # From calibration profile
      evidence_b64 = frame_to_base64_jpeg(evidence_crop)
      # 6. Cache result (for gate next iteration)
      prev_frame = frame
      cached_state = (state, confidence)
      # 7. Return
      return {
          "state": state,
          "confidence": confidence,
          "escalated": escalated,
          "evidence_image_base64": evidence_b64,
          "detected_at": datetime.utcnow().isoformat() + "Z"
      }
  ```

- [ ] Add rate limiting (from specs/02_backend_lead.md, Section 5):
  - max 10 requests per second per IP
  - Return 429 Too Many Requests if exceeded
  - Use `SlowAPI` or similar middleware

- [ ] Add caching layer:
  - If previous call was <500ms ago and gate says "skip", return cached result (no re-inference)
  - This keeps latency low when scene is static

- [ ] Instrumentation:
  - Metrics: `perceive_state.call_count`, `perceive_state.avg_latency_ms`, `perceive_state.error_count`
  - Log all errors with context

- [ ] Unit tests (via integration tests):
  - Mock screen capture, gate, classifier
  - Test: normal flow (returns valid JSON)
  - Test: window not found → 400
  - Test: classifier error → 503
  - Test: rate limit exceeded → 429

- **Reference**: specs/02_backend_lead.md (Section 4: API Contracts, Section 5: Error Handling)
- **Verification**:
  ```bash
  curl -X POST http://127.0.0.1:5000/mcp/tools/screen.perceive_state \
    -H "Content-Type: application/json" \
    -d '{"resolution": "1920x1080", "calibration_profile_id": null, "check_escalation": true}'
  # Expected: 200 JSON with state, confidence, evidence_image_base64
  ```

---

#### 2.3: BACKEND-006 — Implement screen.capture_regions MCP Tool [3 pts]
**Owner**: Backend  
**Dependency**: Screen capture service working

Implement POST `/mcp/tools/screen.capture_regions` in MCP server:

- [ ] **Request JSON** (from specs/02_backend_lead.md, Section 4):
  ```json
  {
    "regions": [
      {"name": "queue_icon", "x": 100, "y": 50, "width": 80, "height": 80},
      {"name": "match_button", "x": 500, "y": 600, "width": 200, "height": 60}
    ],
    "format": "jpeg"  // or "png"
  }
  ```

- [ ] **Response JSON** (200):
  ```json
  {
    "regions": [
      {"name": "queue_icon", "image_base64": "iVBOR...", "format": "jpeg"},
      {"name": "match_button", "image_base64": "iVBOR...", "format": "jpeg"}
    ],
    "captured_at": "2026-02-07T10:30:45Z"
  }
  ```

- [ ] Implementation:
  - Capture full Overwatch window frame
  - For each region, extract crop: `frame[y:y+h, x:x+w, :]`
  - Encode to JPEG/PNG base64
  - Return dict of regions

- [ ] Validation:
  - Bounds check: x, y, width, height must be positive integers
  - Bounds check: region must fit within window resolution
  - Return 400 Bad Request if out of bounds

- [ ] Latency: <50ms (includes capture + encoding)

- [ ] Unit tests:
  - Normal region extract
  - Out-of-bounds region → 400
  - Multiple regions → all encoded correctly

- **Reference**: specs/02_backend_lead.md (Section 4: API Contracts)
- **Verification**:
  ```bash
  curl -X POST http://127.0.0.1:5000/mcp/tools/screen.capture_regions \
    -H "Content-Type: application/json" \
    -d '{
      "regions": [
        {"name": "queue_icon", "x": 100, "y": 50, "width": 80, "height": 80}
      ],
      "format": "jpeg"
    }'
  # Expected: 200 JSON with regions array, each with image_base64
  ```

---

#### 2.4: BACKEND-010 — Unit Tests for Gate Heuristics [2 pts]
**Owner**: QA  
**Dependency**: 2.1 complete

Create comprehensive gate test suite in `backend/tests/unit/test_gate.py`:

- [ ] Test 1: **Static Frame** — Identical consecutive frames should NOT trigger processing
  - Input: `frame_1 = frame_2` (pixel-perfect copy)
  - Expected: `gate.should_process() → False`
  - Verify gate skips unnecessary classifier runs

- [ ] Test 2: **Large Scene Change** — Match found popup should trigger processing
  - Input: `frame_1` = queue UI, `frame_2` = match found UI (modal overlay)
  - Pixel diff: ~15%
  - Expected: `should_process() → True`

- [ ] Test 3: **Noisy Frame** — Single pixel noise should NOT trigger
  - Input: `frame_2 = frame_1` with 1 pixel changed
  - Pixel diff: ~0.001%
  - Expected: `should_process() → False`

- [ ] Test 4: **Histogram Divergence** — Slight brightness change should NOT trigger
  - Input: `frame_2 = frame_1` with overall +10 brightness
  - Histogram divergence: <0.2
  - Expected: `should_process() → False`

- [ ] Test 5: **Resolution Dependent** — Same % change different thresholds per resolution
  - 1920×1080 with 5% pixel change: process
  - 2560×1440 with 5% pixel change: DON'T process (threshold lower)
  - Verify resolution parameter affects threshold

- [ ] Test 6: **First Frame** — Always process (no previous frame)
  - Input: prev_frame = None
  - Expected: `should_process() → True`

- [ ] Test 7: **Threshold Boundary** — Test edge cases (exactly at threshold)
  - Pixel diff = 5.0% (at threshold): boundary test

- [ ] Code coverage: ≥85% (all functions, edge cases)
- [ ] Mocking: Use synthetic frames (no real images)

- **Reference**: specs/05_qa_lead.md (Section 3: Unit Test Examples)
- **Verification**:
  ```bash
  pytest backend/tests/unit/test_gate.py -v --cov=backend/src/perception/gate
  # All 7 tests pass
  # Coverage ≥85%
  ```

---

### Phase 3: State Machine & Notifications (Days 4–5, 8 points)
**Goal**: Detect state transitions, fire desktop/Discord notifications, log to database, implement 24h retention.

#### 3.1: BACKEND-008 — Implement State Transition Machine [3 pts]
**Owner**: Backend  
**Dependency**: Classifier + MCP perceive_state working

Create `backend/src/state/machine.py`:

- [ ] Define `GameState` enum:
  ```python
  class GameState(Enum):
      IDLE = "idle"                  # Not in Overwatch or main menu
      QUEUE = "queue"                # Queuing for match
      MATCH_FOUND = "match_found"    # Match found, hero select starting
      HERO_SELECT = "hero_select"    # Hero select phase
      LOADING = "loading"            # Map loading
      IN_GAME = "in_game"            # Playing match
  ```

- [ ] Define valid transitions (state machine rules):
  ```
  IDLE → QUEUE (entered queue)
  QUEUE → MATCH_FOUND (match found popup)
  QUEUE → IDLE (cancelled queue)
  MATCH_FOUND → HERO_SELECT (confirmed selection)
  MATCH_FOUND → QUEUE (timeout, back to queue)
  HERO_SELECT → LOADING (hero locked)
  LOADING → IN_GAME (match started)
  IN_GAME → IDLE (match ended, client minimized)
  ANY → IDLE (user exited game)
  ```

- [ ] Implement `StateMachine` class:
  ```python
  class StateMachine:
      def __init__(self):
          self.current_state = GameState.IDLE
          self.last_state = None
          self.transition_time = None
      
      def transition(self, detected_state: GameState, confidence: float) → bool:
          """
          Attempt state transition.
          Returns: True if valid transition, False if invalid.
          Raises StateTransitionError if invalid.
          """
          if self._is_valid_transition(self.current_state, detected_state):
              self.last_state = self.current_state
              self.current_state = detected_state
              self.transition_time = datetime.utcnow()
              return True
          else:
              raise StateTransitionError(f"Invalid: {self.current_state} → {detected_state}")
      
      def _is_valid_transition(self, from_state, to_state) → bool:
          # Check against transition rules above
          ...
  ```

- [ ] Implement idempotence guards:
  - If current state == detected state, ignore (no duplicate notifications)
  - Example: Detect QUEUE twice in a row → don't fire notification twice
  - **Critical for avoiding notification spam**

- [ ] Add cooldown/debounce:
  - Require state to be detected 2+ consecutive times before committing transition (if confidence < 0.90)
  - Prevents false positives from single noisy frame

- [ ] Instrumentation:
  - Log all transitions: `logger.info(f"State transition: {from_state} → {to_state}, confidence={conf:.3f}")`
  - Metrics: `state_machine.transition_count`, `state_machine.invalid_transition_count`

- [ ] Unit tests:
  - Valid transitions succeed
  - Invalid transitions raise error (e.g., IDLE → LOADING invalid)
  - Idempotence: repeated same state → no additional transition
  - Debounce: low confidence state requires 2+ confirmations
  - **Reference**: specs/05_qa_lead.md (Section 3: State Machine Tests)

- **Reference**: specs/02_backend_lead.md (Section 3: State Machine)
- **Verification**:
  ```bash
  pytest backend/tests/unit/test_state_machine.py -v
  # All transitions validated
  # Idempotence verified
  ```

---

#### 3.2: BACKEND-007 — Implement notify.desktop MCP Tool [2 pts]
**Owner**: Backend  
**Dependency**: State machine complete

Implement POST `/mcp/tools/notify.desktop` in MCP server:

- [ ] **Request JSON** (from specs/02_backend_lead.md, Section 4):
  ```json
  {
    "title": "Match Found!",
    "message": "Queue monitor detected a match.",
    "urgency": "critical",   // or "normal", "low"
    "sound": true,           // Play notification sound
    "action": "focus_game"   // Optional: on click, bring Overwatch window to focus
  }
  ```

- [ ] **Response JSON** (200):
  ```json
  {
    "notification_id": "uuid-...",
    "delivered": true,
    "platform": "windows10",
    "delivered_at": "2026-02-07T10:30:45Z"
  }
  ```

- [ ] Implementation (Windows 10+ WinRT API):
  - Use `win10toast` library (simple) OR `winrt.windows.ui.notifications` (native)
  - **win10toast approach** (recommended for MVP):
    ```python
    from win10toast import ToastNotifier
    toaster = ToastNotifier()
    toaster.show_toast(
        title="Match Found!",
        msg="Queue monitor detected a match.",
        duration=10,  # seconds
        threaded=True,
        ico_path="path/to/icon.ico"
    )
    ```
  - **winrt approach** (more control, but requires Windows SDK):
    ```python
    from winrt.windows.ui.notifications import ToastNotificationManager, ToastNotification
    from winrt.windows.data.xml.dom import XmlDocument
    # Create XML toast template, show
    ```

- [ ] Urgency levels:
  - `critical`: 10 second duration, sound, popup window
  - `normal`: 7 second duration, sound, small notification
  - `low`: 5 second duration, no sound, subtle

- [ ] Error handling:
  - 503 if notification system unavailable (Windows Notification Service down)
  - Log: `logger.info(f"Desktop notification sent: {title}")`

- [ ] Optional: Click action to bring Overwatch window to focus
  - Implement: `window.activate()` on click (requires pywin32)

- [ ] Unit tests:
  - Mock `win10toast` / `winrt` libraries
  - Test: notification created with correct title + message
  - Test: urgency level affects duration
  - Test: sound flag respected
  - Can't directly test notification display without GUI, so test API surface

- **Reference**: specs/02_backend_lead.md (Section 4: notify.desktop)
- **Verification**:
  ```bash
  curl -X POST http://127.0.0.1:5000/mcp/tools/notify.desktop \
    -H "Content-Type: application/json" \
    -d '{
      "title": "Test Notification",
      "message": "This is a test.",
      "urgency": "critical",
      "sound": true
    }'
  # Expected: 200 JSON with notification_id, delivered=true
  # User sees toast popup on Windows desktop
  ```

---

#### 3.3: BACKEND-009 — Create detection_history Table & Insertion Logic [2 pts]
**Owner**: DB Architect  
**Dependency**: Database schema exists (Sprint 0)

Expand detection logging in `backend/src/db/migrations.py` and repository:

- [ ] Create migration: `202602070001_add_detection_history_logging.sql`:
  ```sql
  -- If table doesn't exist from Sprint 0, create:
  CREATE TABLE IF NOT EXISTS detection_history (
      id TEXT PRIMARY KEY,
      detected_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      game_state TEXT NOT NULL,  -- IDLE, QUEUE, MATCH_FOUND, IN_GAME, etc.
      confidence REAL NOT NULL DEFAULT 0.0,  -- 0.0 – 1.0
      escalated BOOLEAN NOT NULL DEFAULT 0,
      evidence_image_base64 TEXT,  -- Cropped UI region
      window_resolution TEXT,  -- "1920x1080"
      created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
  );
  CREATE INDEX idx_detection_history_detected_at ON detection_history(detected_at);
  CREATE INDEX idx_detection_history_game_state ON detection_history(game_state);

  -- Retention: Automatically delete records older than 24 hours
  -- (implement via scheduled job or trigger, see below)
  ```

- [ ] Implement `DetectionRepository.insert()` method:
  ```python
  def insert(
      self,
      game_state: str,
      confidence: float,
      escalated: bool,
      evidence_image_base64: str = None,
      window_resolution: str = None,
  ) -> str:
      """Insert detection event. Return detection_id."""
      detection_id = str(uuid4())
      cursor.execute("""
          INSERT INTO detection_history
          (id, game_state, confidence, escalated, evidence_image_base64, window_resolution)
          VALUES (?, ?, ?, ?, ?, ?)
      """, (detection_id, game_state, confidence, escalated, evidence_image_base64, window_resolution))
      self.db.commit()
      return detection_id
  ```

- [ ] Implement 24h retention cleanup:
  - Option 1: Scheduled job (run every hour via APScheduler):
    ```python
    scheduler.add_job(cleanup_old_detections, 'interval', hours=1)
    
    def cleanup_old_detections():
        cutoff = datetime.utcnow() - timedelta(hours=24)
        cursor.execute("DELETE FROM detection_history WHERE detected_at < ?", (cutoff,))
        db.commit()
        logger.info(f"Cleaned up detections older than {cutoff}")
    ```
  - Option 2: Manual cleanup on app startup (simpler for MVP)
    ```python
    def on_startup():
        cutoff = datetime.utcnow() - timedelta(hours=24)
        cursor.execute("DELETE FROM detection_history WHERE detected_at < ?", (cutoff,))
        db.commit()
    ```

- [ ] Update MCP perceive_state endpoint to log detections:
  ```python
  # After classifier runs:
  detection_id = repo.detection.insert(
      game_state=state,
      confidence=confidence,
      escalated=escalated,
      evidence_image_base64=evidence_b64,
      window_resolution=resolution
  )
  ```

- [ ] Unit tests:
  - Insert detection → record in database
  - Query last 10 detections (for stats tab in UI)
  - Cleanup removes records >24h old
  - Evidence image base64 persisted correctly

- **Reference**: specs/04_db_architect.md (Section 3: Tables, Section 7: Migrations)
- **Verification**:
  ```bash
  sqlite3 backend/local.db "SELECT COUNT(*) FROM detection_history WHERE game_state = 'MATCH_FOUND';"
  # Should show number of match found detections logged
  ```

---

#### 3.4: BACKEND-011 — Unit Tests for Classifier Inference [2 pts]
**Owner**: QA  
**Dependency**: 1.3, 1.4 complete

Create comprehensive classifier test suite in `backend/tests/unit/test_classifier.py`:

- [ ] Test 1: **Basic Inference** — Tiny classifier produces valid output
  - Input: Synthetic RGB frame (1080×1920×3)
  - Expected: State in [IDLE, QUEUE, MATCH_FOUND, IN_GAME, LOADING, HERO_SELECT]
  - Expected: Confidence in [0.0, 1.0]
  - Mocking: Use mock ONNX model that returns fixed softmax

- [ ] Test 2: **Escalation Threshold** — Low confidence triggers escalation
  - Mock tiny classifier to return 0.65 confidence
  - Expected: `escalated = True`, escalation model called
  - Mock escalation model to return 0.92 confidence
  - Expected: Final confidence raised to 0.92

- [ ] Test 3: **High Confidence No Escalation** — High confidence skips escalation
  - Mock tiny classifier to return 0.95 confidence
  - Expected: `escalated = False`, escalation model NOT called
  - Verify performance (only one inference, not two)

- [ ] Test 4: **Image Preprocessing** — Resize, normalize correctly
  - Input: 1920×1080 frame
  - Expected: Preprocessed to (1, 3, 224, 224) float32 [0, 1]
  - Verify: normalization (mean/std) applied if models expects it

- [ ] Test 5: **Error Handling** — ONNX inference failure raises error
  - Mock ONNX session to raise exception
  - Expected: `AIInferenceError` raised with message
  - MCP endpoint returns 503

- [ ] Test 6: **Latency SLO** — Tiny classifier <50ms, escalation <150ms
  - Measure `time.perf_counter()` around inference
  - Assert: tiny model latency < 50ms
  - Assert: escalation model latency < 150ms (if called)
  - (Mocks may be fast, so set reasonable thresholds)

- [ ] Test 7: **Rerun Augmentation** — Medium confidence triggers zoom + rerun
  - Mock tiny classifier to return 0.78 confidence (medium)
  - Expected: Rerun logic triggered (zoom, re-run tiny)
  - Verify: second inference run

- [ ] Code coverage: ≥85%
- [ ] Mocking: `unittest.mock` to stub ONNX sessions

- **Reference**: specs/05_qa_lead.md (Section 3: Unit Test Examples)
- **Verification**:
  ```bash
  pytest backend/tests/unit/test_classifier.py -v --cov=backend/src/perception/classifier
  # All 7 tests pass
  # Coverage ≥85%
  # Latency assertions within bounds
  ```

---

### Phase 4: Integration & Full-Stack Testing (Days 5–7, 8 points)
**Goal**: Validate end-to-end perception pipeline, confirm all endpoints functional, acceptance testing.

#### 4.1: BACKEND-012 — Integration Test: Full Perception Pipeline [3 pts]
**Owner**: QA  
**Dependency**: All BACKEND-001 through BACKEND-011 complete

Create comprehensive integration test in `backend/tests/integration/test_perception_pipeline.py`:

- [ ] Test Scenario 1: **IDLE → QUEUE Transition**
  - Setup: Mock screen captures IDLE UI
  - Step 1: Call `perceive_state()` → returns state=IDLE, confidence=0.95
  - Verify: State machine accepts transition, no notification
  - Verify: Detection logged to database

- [ ] Test Scenario 2: **QUEUE → MATCH_FOUND Transition**
  - Setup: Previous call returned QUEUE state
  - Setup: New screen capture shows match found popup
  - Step 1: Call `perceive_state()` with new frame
  - Verify: Classifier detects MATCH_FOUND (mocked to return 0.93 confidence)
  - Verify: State machine transitions (QUEUE → MATCH_FOUND)
  - Verify: notify.desktop called (mock ToastNotifier)
  - Verify: Detection logged with evidence base64

- [ ] Test Scenario 3: **Escalation Logic in Pipeline**
  - Setup: Classifier returns 0.72 confidence (borderline)
  - Step 1: perceive_state triggers escalation
  - Verify: Escalation model called
  - Verify: Final confidence increased to 0.91
  - Verify: escalated=true in response

- [ ] Test Scenario 4: **Gate Prevents Unnecessary Runs**
  - Setup: Two identical frames
  - Step 1: perceive_state(frame_1) → classifier run, returns QUEUE
  - Step 2: perceive_state(frame_1) again (cached) → gate skips, returns cached QUEUE
  - Verify: Classifier called only once
  - Verify: Second call latency <5ms (gate result, no inference)

- [ ] Test Scenario 5: **Deduplication: Repeated State = No Notification**
  - Setup: Call perceive_state twice, both return QUEUE
  - Verify: Notification NOT fired on second call (idempotence guard)
  - Verify: Detection logged both times, but user sees only one notification

- [ ] Test Scenario 6: **Rate Limiting**
  - Setup: Send 15 requests to perceive_state in 1 second (limit: 10/sec)
  - Verify: Requests 1–10 return 200
  - Verify: Requests 11–15 return 429 Too Many Requests
  - Verify: Rate limit resets after 1 second

- [ ] Test Scenario 7: **Error Handling: Window Not Found**
  - Setup: Mock screen capture to raise WindowNotFoundError
  - Verify: perceive_state returns 400 with error message
  - Verify: No state transition, no notification

- [ ] Test Scenario 8: **Full Database Workflow**
  - Setup: Run perceive_state 5 times with different states
  - Verify: 5 detections inserted into detection_history
  - Verify: All records have evidence_image_base64
  - Verify: Cleanup deletes records >24h old (manual test)

- [ ] Code coverage: ≥75% of backend code paths
- [ ] Mocking: Integrate mocks for screen capture, ONNX models, notification system
- [ ] Duration: Keep test <5 minutes (no real ONNX inference, all mocked)

- **Reference**: specs/05_qa_lead.md (Section 4: Integration Test Patterns)
- **Verification**:
  ```bash
  pytest backend/tests/integration/test_perception_pipeline.py -v --cov=backend/src
  # All 8 scenarios pass
  # Coverage ≥75%
  # Duration <5 minutes
  ```

---

#### 4.2: Final Verification & Acceptance Checklist [No Story Points, Days 5–7]
**Owner**: ALL (Cross-functional)

Run final system health checks:

- [ ] **Lint & Type Checks**:
  ```bash
  black backend/src --check
  ruff check backend/src
  mypy backend/src --strict
  ```
  Expected: No errors

- [ ] **Test Suite**:
  ```bash
  pytest backend/tests/ -v --cov=backend/src --cov-report=term-missing
  ```
  Expected: Coverage ≥75%, all tests pass

- [ ] **Performance Baselines**:
  - Gate latency: <5ms p95 ✓
  - Classifier inference: <50ms p95 (tiny), <150ms (escalation) ✓
  - Full pipeline (capture → gate → classify): <100ms p95 ✓
  - perceive_state endpoint response: <150ms p95 ✓

- [ ] **API Contract Compliance**:
  - perceive_state JSON schema valid (verify against OpenAPI/JSON Schema)
  - capture_regions returns valid base64 images
  - notify.desktop / notify.discord follow spec
  - Error responses include proper error codes (400, 429, 503)

- [ ] **Database**:
  - Schema created: 4 tables (calibration_profiles, detection_history, notification_log, settings)
  - Migrations run cleanly: `python backend/src/db/migrations.py`
  - detection_history populated with test events
  - Cleanup policy verified (24h retention)

- [ ] **State Machine**:
  - All valid transitions succeed
  - All invalid transitions raise error
  - Idempotence: repeated state → no duplicate notification
  - Debounce working (low confidence requires 2+ confirmations)

- [ ] **Backlog Update**:
  - Sprint 1 section: All 12 tickets marked "done"
  - Notes column: Brief summary of deliverables (e.g., "Gate tuned, perceive_state working, full integration test passing")
  - No blockers remaining

- [ ] **Documentation**:
  - `backend/models/README.md` documents ONNX models (source, version, specs)
  - `backend/src/config.py` has all configurable thresholds (gate, classifier, escalation)
  - MCP server has endpoint docstrings
  - Test files have clear test names and comments

- [ ] **Git History**:
  - Commits follow format: `feat(backend): implement classifier inference pipeline`
  - No merge commits to develop (rebase or squash)
  - All PRs have 2+ approvals

---

## Definition of Done (per Ticket)

✓ Code implements spec requirement exactly  
✓ Unit + integration tests pass (75–85% coverage depending on ticket)  
✓ No lint errors (`black`, `ruff`)  
✓ Type checking passes (`mypy --strict`)  
✓ Code reviewed + 2 approvals  
✓ Merged to `develop` branch  
✓ Backlog.md updated: status → "done", notes added  
✓ Performance SLOs validated (latency, CPU, coverage)

---

## Daily Commands (Verify Everything Works)

```bash
# Verify ONNX models available
ls -lh backend/models/
# Expected: Shufflenet-v2.onnx (~5MB), efficientnet-lite4-11.onnx (~15MB)

# Verify models load correctly
python backend/scripts/verify_models.py
# Expected: tiny: 1.75ms, escalation: 7.53ms

# Backend health check
cd backend && pytest tests/ --cov && python -m src.main --dev

# Full stack check
cd backend && pytest tests/ --cov=src --cov-report=term-missing

# Lint & type check
cd backend && black . --check && ruff check . && mypy src --strict

# Manual API test (once server running)
curl -X POST http://127.0.0.1:5000/mcp/tools/screen.perceive_state \
  -H "Content-Type: application/json" \
  -d '{"resolution": "1920x1080", "calibration_profile_id": null, "check_escalation": true}'
# Expected: { "state": "IDLE" or "QUEUE", "confidence": 0.85–0.99, "escalated": false, ... }
```

---

## Unknown Requirements & Blockers

| Issue | Risk | Status | Mitigation |
|-------|------|--------|------------|
| **ONNX Model Availability** | HIGH | ✅ RESOLVED | ShuffleNet-V2 + EfficientNet-Lite4 validated (SETUP-005); ready for immediate use |
| **Win32 Notification API** | MEDIUM | Open | Use simple `win10toast` library first; fallback to `win11toast` if needed |
| **Real ONNX Inference Latency** | LOW | ✅ VALIDATED | Tiny: 1.75ms p95 (target <50ms) ✓; Escalation: 7.53ms p95 (target <150ms) ✓ |
| **Calibration Profiles** | LOW | Planned | Mock profiles for Sprint 1 (hard-coded 1920×1080); real calibration UX added Sprint 2 |
| **Discord Webhook Retry Logic** | LOW | Open | Implement basic exponential backoff; full integration with frontend UI in Sprint 3 |

---

## Success Criteria (End of Sprint 1)

Acceptance gate for "Sprint 1 Complete":

- [ ] All 12 tickets marked "done" in `specs/backlog.md`
- [ ] `pytest backend/tests/ --cov` shows **≥75% coverage** (critical paths 100%)
- [ ] Perception latency benchmarks achieved:
  - Gate: <5ms p95 ✓
  - Classifier (tiny/ShuffleNet-V2): <50ms p95 ✅ VALIDATED: 1.75ms
  - Classifier (escalation/EfficientNet-Lite4): <150ms p95 ✅ VALIDATED: 7.53ms
  - Full pipeline: <100ms p95 ✓
- [ ] perceive_state endpoint tested + working (curl test returns valid JSON)
- [ ] capture_regions endpoint tested + working (base64 JPEG/PNG encoding)
- [ ] notify.desktop fires toast notifications (manual test on Windows)
- [ ] State machine idempotent (repeated state → no duplicate notification)
- [ ] detection_history populated with test events, retention policy verified
- [ ] No lint errors (`black`, `ruff`) / type errors (`mypy`)
- [ ] Backlog.md updated with completion notes
- [ ] All code merged to `develop` branch

**After Sprint 1: Backend perception engine is feature-complete and tested. Ready for integration with frontend in Sprint 2.**

---

## Timeline

- **Day 1**: Phase 1 start (model verification, classifier pipeline implementation)
- **Day 2–3**: Phase 1 complete, Phase 2 start (gate refinement, perceive_state)
- **Day 3–4**: Phase 2 continue (capture_regions, gate tests)
- **Day 4–5**: Phase 3 start (state machine, notifications, detection logging)
- **Day 5–6**: Phase 3 + Phase 4 (classifier tests, integration test setup)
- **Day 6–7**: Phase 4 complete (integration test execution, final verification, acceptance)

**Note**: SETUP-005 (ONNX model sourcing) complete as of Feb 7, 2026. Models ready for immediate integration. No blockers expected.

---

## Definition of Sprint Success

At sprint review:
1. **Backend Lead** demos each MCP endpoint (perceive_state, capture_regions, notify.desktop)
   - Shows JSON responses
   - Explains error handling + rate limiting
   - Demonstrates state machine transitions

2. **QA Lead** reports test coverage
   - Line coverage: ≥75%
   - Gate tests: 7/7 passing (85% coverage)
   - Classifier tests: 7/7 passing (85% coverage)
   - Integration test: 8 scenarios passing (75% coverage)
   - Latency SLOs: All verified

3. **Database Architect** shows schema + migrations
   - 4 tables created
   - Migrations applied cleanly
   - Sample detection_history records

4. **All**: Confirm backlog updated, no blockers for Sprint 2

---

## Next Steps (Sprint 2 Planning)

After Sprint 1 acceptance:
- **Sprint 2 Focus**: Frontend UI + Calibration Wizard
- **Dependencies**: Backend APIs from Sprint 1 complete
- **Capacity**: ~31 story points (FRONTEND-001 through FRONTEND-011)

---

**Begin Sprint 1 execution now. Update specs/backlog.md as tickets move to "done".**
