# System Architecture Overview
## Overwatch AI Queue Detection & Notification App

**Generated**: February 6, 2026  
**Version**: 1.0

---

## High-Level System Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                Windows User Desktop (10/11)                   │
│                                                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              Tray Application (Electron)               │  │
│  │  ┌──────────────┐           ┌──────────────────────┐   │  │
│  │  │ Tray UI      │─ IPC ────▶│ Settings Modal       │   │  │
│  │  │ State        │           │ Calibration Wizard   │   │  │
│  │  │ Notifications│           │ Dashboard (opt)      │   │  │
│  │  └──────────────┘           └──────────────────────┘   │  │
│  └────────────┬─────────────────────────────────────────────┘  │
│               │ (IPC/Named Pipes)                               │
│  ┌────────────▼─────────────────────────────────────────────┐  │
│  │          Backend Services (Python/Node.js)              │  │
│  │                                                          │  │
│  │  ┌─────────────────────────────────────────────────┐   │  │
│  │  │  Perception Pipeline Agent (Strands + Python)  │   │  │
│  │  │  1. Screen Capture (Windows DCE API)           │   │  │
│  │  │  2. Gate Service (pixel diff, histogram)       │   │  │
│  │  │  3. AI Classifier (ONNX Runtime)               │   │  │
│  │  └──────────────────┬──────────────────────────────┘   │  │
│  │                     │                                   │  │
│  │  ┌──────────────────▼──────────────────────────────┐   │  │
│  │  │  Notification Pipeline                         │   │  │
│  │  │  1. Deduplication Queue (5s window)           │   │  │
│  │  │  2. Desktop Notifier (Windows Toast)          │   │  │
│  │  │  3. Discord Webhook (retry + rate-limit)      │   │  │
│  │  └──────────────────────────────────────────────────┘   │  │
│  │                                                          │  │
│  │  ┌─────────────────────────────────────────────────┐   │  │
│  │  │  MCP HTTP Server (127.0.0.1:5000)              │   │  │
│  │  │  - screen.perceive_state (state + confidence)  │   │  │
│  │  │  - screen.capture_regions (cropped regions)    │   │  │
│  │  │  - notify.desktop, notify.discord              │   │  │
│  │  └─────────────────────────────────────────────────┘   │  │
│  └────────────┬─────────────────────────────────────────────┘  │
│               │                                                 │
│  ┌────────────▼─────────────────────────────────────────────┐  │
│  │  SQLite Database (local.db)                             │  │
│  │  - calibration_profiles                                 │  │
│  │  - detection_history                                    │  │
│  │  - notification_log                                     │  │
│  │  - settings                                             │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  AI Models (ONNX Format)                                │  │
│  │  - tiny_classifier.onnx (200 KB, INT8)                 │  │
│  │  - escalation_model.onnx (5 MB)                        │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
└──────────────────────────────────────────────────────────────┘
         │
         │ (External Integrations - Optional)
         │
  ┌──────▼──────────┐         ┌──────────────────┐
  │ GitHub Releases │         │ Discord Webhooks │
  │ (Auto-Update)   │         │ (User-configured)│
  └─────────────────┘         └──────────────────┘
```

---

## Tech Stack Summary

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Tray UI** | Electron 28 + React 18 + TypeScript | Cross-platform desktop UI, real-time state display |
| **Screen Capture** | Windows DCE API (ctypes) | Low-latency access to Overwatch game window |
| **Gate Logic** | NumPy + OpenCV | Fast heuristic checks (pixel diff, histogram) |
| **AI Inference** | ONNX Runtime | Hardware-accelerated model execution (CPU/GPU) |
| **Tiny Model** | TinyMobileNetV3 (200 KB) | Real-time state classification (<50ms) |
| **Escalation Model** | MobileNetV2 (5 MB) | Higher accuracy for uncertain cases |
| **Backend Services** | Python 3.11 + Strands SDK | Agent-based orchestration and perception |
| **MCP Server** | Node.js + Express | Tool interface for Electron ↔ Python communication |
| **Local Storage** | SQLite 3.45+ | Zero-setup database for profiles, history, settings |
| **Notifications** | Windows Toast API + Discord HTTP | User alerts across platforms |
| **Testing** | pytest + vitest | Backend + frontend test coverage |
| **Build & Package** | Vite + electron-builder | MSI installer for Windows distribution |

---

## Request Lifecycle (Browser → Database → Notification)

### 1. User Interaction Flow (Tray Window)

```
User Alt-Tabs to other app
  │
  ▼
Tray Window Minimized (still visible in system tray)
  │
  ▼
Backend Perception Loop Runs Every 500ms
  │
  ├──► Screen Capture: GetWindowDC → BitBlt → DIB conversion (8ms)
  │
  ├──► Gate Check: Pixel diff vs previous frame (2ms)
  │    ├─ No change? Exit, return cached state
  │    └─ Change detected? Continue to AI
  │
  ├──► AI Inference:
  │    ├─ Crop UI regions (normalized 0-1)
  │    ├─ Run tiny classifier (ONNX Int8 quantized)
  │    ├─ Output: state (QUEUE, MATCH_FOUND, etc.) + confidence
  │    ├─ If confidence <0.85: Run escalation model (150ms)
  │    └─ Final: state + confidence + evidence
  │
  ├──► State Check: Is this a NEW state or MATCH_FOUND?
  │    ├─ Deduplication: 5-second window per state
  │    ├─ No duplicate in 5s? Proceed
  │    └─ Duplicate? Skip notification
  │
  └──► Notification Pipeline:
       ├─ Desktop Toast: Windows Toast API (instant)
       ├─ Discord Webhook: POST to webhook URL (HTTP retry, 5s timeout)
       └─ Log to SQLite: detection_history + notification_log entries
```

### 2. Database Operations

```
Detection Result
  │
  ├─→ INSERT detection_history
  │    (id, state, confidence, timestamp, evidence_json, resolution)
  │
  └─→ INSERT notification_log
       (detection_id, type='desktop|discord', status='sent|failed', retry_count, timestamp)
```

### 3. API Request → Response (for reference)

```
POST /mcp/tools/screen.perceive_state (internal, called by Strands agent)

← Response (JSON):
{
  "state": "MATCH_FOUND",
  "confidence": 0.94,
  "timestamp": "2026-02-06T14:30:45.500Z",
  "inference_latency_ms": 42,
  "evidence": {
    "gate_triggered": true,
    "gate_signals": {
      "pixel_diff_pct": 15.3,
      "histogram_change": 0.78
    },
    "classifier": "tiny_v1.0",
    "escalation_used": false
  }
}
```

---

## Non-Functional Requirements Summary

### Performance Targets

| Metric | Target | Rationale |
|--------|--------|-----------|
| **Screen Capture Latency** | <10ms | Real-time perception loop |
| **Gate Logic Latency** | <5ms | Cheap heuristic check |
| **Tiny Model Inference** | <50ms | Frequent (every 500ms cycle) |
| **Escalation Model Inference** | <150ms | Rare (only if confidence <0.85) |
| **Notification Send Latency** | <500ms (desktop), <2s (Discord) | User perceives "instantly" |
| **MATCH_FOUND Detection** | <1000ms from appearance | Game provides 10s to accept match |
| **CPU Usage (Idle Queue)** | 5-10% single-core | Not competing with game |
| **GPU Usage** | Negligible (<1% 99th percentile) | Optional; CPU-only fallback |
| **Memory Footprint** | <300 MB | Lightweight tray app |

### Reliability & Availability

```
Uptime Target: 99.5% (local hardware reliability)
False Positive Rate: <1 per hour during active queueing
False Negative Rate: <1 per 100 matches detected
Notification Retry: Exponential backoff (1s → 2s → 4s, max 30s) for Discord
Deduplication Window: 5 seconds per state (prevents spam)
```

### Privacy & Security

- **No cloud data transmission**: All AI inference runs locally
- **Cropped regions only**: Evidence stored as UI-region crops, never full frames
- **Secrets management**: Discord webhook URL stored encrypted in SQLite
- **No interaction with game**: Read-only screen perception, zero input automation
- **Local database**: SQLite on user's machine, no external dependencies

### Maintainability

- **Model versioning**: Models tagged with version (e.g., `tiny_v1.0`)
- **MCP tool contracts**: API changes documented in [docs/api/reference.md](api/reference.md)
- **Pluggable models**: Classifier can swap ONNX models without code changes
- **Configuration management**: Env vars + SQLite settings table for runtime config
- **Logging**: Structured JSON logs for debugging and auditing

---

## Key Architectural Decisions

### 1. **Local-First Architecture**

**Decision**: All processing on user's machine; no cloud services.  
**Rationale**: 
- Privacy: Overwatch window cropped regions never leave device
- Latency: No network roundtrips, instant detection
- Reliability: Works offline; no SaaS dependencies

---

### 2. **Tiered Perception Pipeline**

**Decision**: Gate → Tiny AI → Escalation AI  
**Rationale**:
- **Gate**: <5ms heuristic check; skip inference if screen unchanged
- **Tiny**: Lightweight model runs frequently (every 500ms)
- **Escalation**: Larger, slower model only if confidence <0.85
- **Result**: CPU cost amortized; 95% of cycles = cheap gate check

---

### 3. **Electron Desktop App**

**Decision**: Electron 28 (React UI + Node.js backend in same process).  
**Rationale**:
- **Cross-platform readiness**: Codebase prepared for future macOS/Linux
- **Native system integration**: Tray icon, toast notifications, auto-update via MSIX
- **Rapid iteration**: React HMR + Vite for quick UI development

---

### 4. **SQLite Over Network DB**

**Decision**: SQLite (local) instead of cloud database.  
**Rationale**:
- **Zero setup**: User downloads app, runs; no configuration
- **Privacy**: All data stays on device
- **Reliability**: No network/auth failures
- **Scale**: Single-user local app; SQLite sufficient

---

### 5. **ONNX Runtime for AI**

**Decision**: ONNX (Open Neural Network Exchange) format + ONNX Runtime.  
**Rationale**:
- **Model agnostic**: Train in PyTorch/TensorFlow, export to ONNX, run anywhere
- **Performance**: CPU + optional GPU acceleration (no CUDA lock-in)
- **Int8 Quantization**: 200 KB tiny model; <50ms inference
- **No Python dependencies**: Runtime can be standalone C++ (future)

---

### 6. **Deduplication & Rate Limiting**

**Decision**: 5-second deduplication window + exponential backoff for Discord.  
**Rationale**:
- **Prevents spam**: QUEUE state triggers once per 5s window
- **Prevents duplicate notifications**: E.g., MATCH_FOUND fires once per match
- **Discord reliability**: Rate-limit aware retry (429 handling)

---

## Component Interaction Diagram

```
┌──────────────────────┐
│  Tray UI (React)     │
│  - State Display     │
│  - Settings Modal    │
│  - Calibration      │
└───────────┬──────────┘
            │ IPC
            ▼
┌──────────────────────────────────┐
│  Strands Agent Orchestration     │
│  (Async event-driven)            │
└───────┬───────────────────────────┘
        │
    ┌───┴───────┬─────────────┬──────────────┐
    │ Calls     │             │              │
    ▼           ▼             ▼              ▼
┌────────┐ ┌──────────┐ ┌──────────────┐ ┌────────────┐
│Gateway │ │Classifier│ │Notification  │ │Database    │
│(heur.) │ │(AI)      │ │Services      │ │(SQLite)    │
└────────┘ └──────────┘ └──────────────┘ └────────────┘
    │           │            │                │
    └─────┬─────┘            └────────┬───────┘
          │                           │
          ▼                           ▼
    ┌──────────────┐      ┌──────────────────┐
    │ Evidence     │      │ Detection History│
    │ (cropped UI) │      │ Notification Log │
    └──────────────┘      └──────────────────┘
            │
            └─────────────┬──────────────────┐
                          │                  │
                          ▼                  ▼
                    ┌─────────────┐  ┌─────────────┐
                    │Desktop Toast│  │Discord Hook │
                    │(Windows API)│  │(HTTP POST)  │
                    └─────────────┘  └─────────────┘
```

---

## Summary

**Overwatch Queue Notifier** is a local-first, privacy-preserving desktop application that:
1. Captures Overwatch screen in real-time
2. Uses a tiered AI pipeline to detect match states
3. Notifies users instantly via desktop toast or Discord
4. Stores calibration & history locally
5. Maintains <10% CPU with minimal overhead

The architecture prioritizes **low latency**, **high accuracy**, and **user privacy** while remaining maintainable and extensible for future enhancements.
