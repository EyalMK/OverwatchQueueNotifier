# Deep-Dive: Technical Decisions & Trade-Offs
## Overwatch AI Queue Detection & Notification App

**Generated**: February 6, 2026  
**Version**: 1.0

---

## Architectural Decision Log

### Decision 1: Electron vs WinForms vs PyQt

**Problem**: Need a desktop app with:
- Tray icon + minimal UI
- Modern, responsive interface
- Future cross-platform readiness (macOS/Linux)

**Options**:
1. **Electron** (React + Node.js): Larger bundle (~200 MB), but modern dev experience, cross-platform foundation
2. **WinForms** (C#/.NET): Lightweight, native Windows, but tied to Windows ecosystem
3. **PyQt** (Python): Lightweight, cross-platform, but less React ecosystem maturity

**Decision**: **Electron**

**Rationale**:
- React ecosystem mature; large community
- HMR development experience (fast iteration)
- Cross-platform codebase (macOS/Linux migration path)
- Tray icon + notifications well-supported
- Bundle size acceptable (~200 MB) for desktop app

**Trade-Off**:
- Larger memory footprint (~150 MB idle) vs WinForms (~50 MB)
- Startup time ~1.5s vs WinForms ~0.5s
- Build complexity higher
- **Acceptable**: Desktop users expect 150 MB footprint

---

### Decision 2: Local ONNX Inference vs Cloud API

**Problem**: Need ultra-low-latency AI classification (<1s MATCH_FOUND detection).

**Options**:
1. **Local ONNX Runtime** (200 KB + 5 MB models): Instant, offline, privacy-preserving
2. **Azure ML / AWS Sagemaker** (API call): <100ms latency + 500ms network = ~600ms
3. **On-Premise GPU Server** (own hardware): Overkill for single-user app

**Decision**: **Local ONNX Runtime**

**Rationale**:
- Latency: <50ms tiny model + <150ms escalation vs 600ms cloud round-trip
- Privacy: No screenshots leave device
- Reliability: Works offline; no API dependency
- Cost: $0 vs $20/month SaaS

**Trade-Off**:
- Limited model sizes (200 KB → 5 MB)
- CPU-only by default (optional GPU via CUDA, but complex setup)
- Model retraining requires redistribution (no A/B testing)
- **Mitigated**: Quantization (INT8) and distillation techniques

---

### Decision 3: Tiered Perception (Gate + Tiny + Escalation)

**Problem**: Need to balance accuracy and CPU usage.

**Options**:
1. **Single large model** (15 MB): High accuracy (~95%), but always ~100ms latency
2. **Single tiny model** (200 KB): Fast (~50ms), but lower accuracy (~85%)
3. **Tiered (gate → tiny → escalation)**: Cheap heuristic skips 90% of cycles; escalation handles uncertainty

**Decision**: **Tiered approach**

**Rationale**:
- Gate is <5ms (pixel diff + histogram); skips 95% of expensive AI runs
- Tiny model runs frequently (500ms); <50ms, acceptable latency
- Escalation (150ms) runs only if tiny confidence <0.85 (~5% of cycles)
- Net CPU: <1% during idle queue

**Trade-Off**:
- Complexity: Three models to maintain
- False negatives if gate misses changes (mitigated: gate is conservative)
- **Benefit**: Exceptional CPU efficiency

---

### Decision 4: SQLite vs Embedded Postgres

**Problem**: Need local data storage for profiles, history, settings.

**Options**:
1. **SQLite** (3 MB executable): Zero setup, single file, fully ACID
2. **Embedded Postgres** (15 MB executable): More featureful, overkill for single user
3. **JSON files** (simple): Loss of ACID, complex querying

**Decision**: **SQLite**

**Rationale**:
- Single-user app; no concurrent server needed
- ACID transactions for critical operations
- Zero setup (file-based; no daemon)
- Full SQL support for queries (better than JSON)

**Trade-Off**:
- Less featureful than Postgres (no arrays, jsonb)
- Single-file backup (easy, but no streaming)
- **Acceptable**: Features not needed; trade justified

---

### Decision 5: Synchronous vs Asynchronous Perception Loop

**Problem**: Perception must run continuously without blocking UI.

**Options**:
1. **Synchronous** (blocking loop): Simple, but freezes UI during inference
2. **Async (tokio/asyncio)**: Non-blocking, complex error handling
3. **Multi-process** (separate Python process): Decoupled, but IPC overhead

**Decision**: **Multi-process async**

**Backend (Python)**:
```python
while monitoring:
    await perception_loop()  # Async event loop
    await asyncio.sleep(0.5)  # 500ms cycle
```

**Rationale**:
- Python backend runs in separate process (no GIL blocking Electron)
- Async allows 500ms cycle without stuttering
- IPC (named pipes / sockets) decouples frontend from backend

**Trade-Off**:
- Complexity: IPC protocol design
- Latency: IPC overhead ~5–10ms (acceptable)
- **Benefit**: Responsive UI during inference

---

### Decision 6: Deduplication Window (5 Seconds)

**Problem**: Classifier runs every 500ms; state might not change, causing duplicate notifications.

**Options**:
1. **1-second window**: Aggressive dedup; misses legitimate state changes
2. **5-second window**: Balances spam prevention + state change detection
3. **No dedup**: Notify for every MATCH_FOUND (unacceptable spam)

**Decision**: **5-second window**

**Rationale**:
- MATCH_FOUND popup lasts 10+ seconds; one notification per match
- If user misses notification, next cycle in <5s won't re-notify (prevents frustration)
- Hysteresis: Prevents flicker from state oscillation (QUEUE ↔ MATCH_FOUND)

**Trade-Off**:
- If state alternates QUEUE → MATCH_FOUND → QUEUE within 5s, second MATCH_FOUND is missed
- **Mitigated**: Game naturally holds state longer; rare edge case
- **Acceptable**: Trade justified for spam prevention

---

### Decision 7: Escalation Threshold (85% Confidence)

**Problem**: When should tiny model defer to escalation model?

**Options**:
1. **70%**: Very aggressive escalation; high accuracy, high latency
2. **85%**: Balance (current)
3. **95%**: Rarely escalates; fast, but lower accuracy
4. **No escalation**: Always use tiny; simple, but 85% accuracy insufficient

**Decision**: **85% confidence threshold**

**Rationale**:
- 85% confidence means 1 in 20 detections uncertain
- Escalation (150ms) is acceptable rare cost
- False negatives (<85% actual match) reduced by escalation
- Balances latency + accuracy

**Trade-Off**:
- If escalation model also <85% → averaging both (complex logic)
- **Mitigated**: Escalation model is larger; higher baseline accuracy
- **Tunable**: Can adjust via environment variable during runtime

---

### Decision 8: No Database Migration Tool (Use Raw SQL)

**Problem**: How to version schema changes?

**Options**:
1. **Alembic** (heavyweight ORM-driven migration tool): Overkill
2. **Raw SQL files** (manual versioning): Simple, transparent
3. **No migrations** (just run SQL at startup): Fragile

**Decision**: **Raw SQL files with version tracking**

**Rationale**:
- Single-file SQLite; migrations are rare
- SQL transparency (no DSL abstraction)
- Manual control (good for auditing schema changes)
- Lightweight (< 20 lines of Python to execute)

**Trade-Off**:
- No automatic rollback (manual recovery needed)
- **Acceptable**: Desktop app; rollback rarely necessary

---

### Decision 9: Toast Notifications vs Discord-Only

**Problem**: User might not configure Discord webhook; how to notify?

**Options**:
1. **Desktop toast only**: Default experience; no chat notification
2. **Discord only**: Requires setup; blocks MVP
3. **Both** (current): Desktop toast always; Discord optional

**Decision**: **Both (desktop by default, Discord optional)**

**Rationale**:
- Desktop toast works instantly (Windows Toast API, no config)
- Discord enhances (mobile ping, chat history), but optional
- Users who don't set Discord still get desktop notifications
- Gradual feature: MVP = desktop + code path for Discord

**Trade-Off**:
- Two notification channels = more testing
- **Benefit**: Accessible to all users; advanced users get more

---

## Known Limitations & Workarounds

### Limitation 1: Fixed Crop Regions Per Resolution

**Issue**: If user changes custom resolution (1920x1080 → windowed), calibration breaks.

**Workaround**: User re-runs calibration wizard (< 2 min)

**Future Fix**: Automatic recalibration + resolution change detection

---

### Limitation 2: Single Overwatch Window Only

**Issue**: If multiple Overwatch windows open (multiboxing), app monitors only primary.

**Current**: App captures window by name "Overwatch 2"; returns first match

**Workaround**: Close secondary windows

**Future**: Window selection UI (pick window manually)

---

### Limitation 3: Fullscreen Exclusive Mode Not Supported (Partial)

**Issue**: Windows DCE API cannot capture fullscreen exclusive windows (older DX11).

**Current**: Supports windowed fullscreen (most players), fullscreen exclusive untested

**Workaround**: Switch to windowed fullscreen (in-game settings)

**Future**: Attempt to capture via DXGI (Windows 10+)

---

### Limitation 4: False Positives (< 1/hour)

**Issue**: Gate detects non-Overwatch window changes as game state transitions.

**Example**: User scrolls browser during queue; pixel diff triggers; classifier detects IDLE (false positive)

**Mitigation**: 
- Gate checks Overwatch window specifically (not entire desktop)
- Classifier trained on real Overwatch UI
- Deduplication window (5s) reduces rapid flickers

**Acceptance Criteria**: <1 false positive per hour during queue

---

### Limitation 5: No API Versioning

**Issue**: MCP tools have no version field; schema changes break compatibility.

**Current**: v1.0; backward compatibility assumed

**Future**: Add `"api_version": "1.0"` to all responses

---

## Performance Bottlenecks & Optimization Paths

### Current Bottlenecks

1. **Screen Capture** (~8ms)
   - Limited by Windows DCE API; efficient for local app
   - Optimization: Use DXGI (faster, but requires DX11+)

2. **AI Inference** (~50ms tiny + ~150ms escalation)
   - Limited by model size; can't reduce without accuracy loss
   - Optimization: Quantization (INT8 or INT4) or distillation to smaller models

3. **IPC Round-Trip** (~5–10ms per call)
   - Named pipe latency between Electron and Python
   - Optimization: Reduce syscall frequency; batch requests

### Caching Strategy

```
Frame caching:
├─ Current frame held in memory
└─ Gate compares current vs previous
   └─ If same: skip inference (cache hit)
   └─ If different: run classifier

Inference caching (TTL = 500ms):
├─ Tiny model result cached
└─ Used for multiple requests within 500ms window
   └─ Reduces  duplicate inference

Settings caching:
├─ Load from SQLite at startup
└─ Keep in memory (Zustand store)
   └─ Reduces DB queries
```

### TTL Strategy

```
Detection timeout:
├─ If no detection for 30s
├─ Reset state to IDLE (user left game)

Calibration timeout:
├─ If calibration >30 days old
├─ Warn user to re-calibrate (model might drift)

Notification retry:
├─ Max 30s per webhook attempt
├─ Exponential backoff (1s, 2s, 4s, 8s, 16s, 30s)
```

---

## Transaction Isolation & ACID Guarantees

### Critical Transactions

```python
# Atomic: Detect + Log + Notify
with db.transaction():
    detection_id = db.insert('detection_history', {...})
    db.insert('notification_log', {'detection_id': detection_id, 'status': 'sent'})
    # Both succeed or both fail
    if not notify_discord():
        db.update('notification_log', {'status': 'retry'})
```

### Isolation Level: SERIALIZABLE (SQLite Default)

- Prevents dirty reads (won't read uncommitted notifications)
- Prevents lost updates (concurrent edits impossible; single-user app)

---

## Future Migration Paths

### Path 1: Scale to Multi-User (Web Dashboard)

If analytics cloud backend is added:
```python
# Backend: Python FastAPI
# Frontend: React dashboard at analytics.example.com
# Data flow: Local app → Cloud API (encryption key from user account)
```

### Path 2: Replace ONNX with TensorRT

If performance is insufficient:
```python
# ONNX Runtime (current)
interpreter = ort.InferenceSession(model_path)

# TensorRT (lower latency, NVIDIA-only)
engine = trt.Builder(...).build_engine(network)
```

### Path 3: Move Perception to GPU

```python
# Current: ONNX on CPU
# Future: ONNX on CUDA (NVIDIA), ROCm (AMD), Metal (future macOS)

classifier = ONNX(
    model_path,
    providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
)
```

---

## Summary

**Technical decisions** prioritize:
1. **Low latency** (<1s MATCH_FOUND detection)
2. **Low CPU usage** (single-digit % idle queue)
3. **Privacy** (no cloud required; all local)
4. **Simplicity** (zero user setup; download → run)

**Trade-offs** are intentional and documented, with clear **optimization paths** for future versions.

Known **limitations** are acceptable for MVP; future enhancements are planned.
