# System Architecture Overview
## Overwatch AI Queue Detection & Notification App

**Version**: 1.0  
**Last Updated**: February 6, 2026  
**Audience**: Engineers, DevOps, architects  

---

## 1. System Design Context

### Problem Statement
Players spend 5–15 minutes idle in Overwatch 2 queues, checking their monitor periodically. The solution: AI detects queue state automatically and sends an instant notification without interrupting gameplay.

### Constraints
- **Platform**: Windows 10/11 only, single-machine, local-first
- **Latency**: Detection <100ms p95, <50ms typical
- **Resource**: CPU <10% sustained, no GPU required
- **Privacy**: No full screenshot storage, local-only processing
- **Dependencies**: Minimal external APIs (Discord webhook optional)

---

## 2. Three-Tier Layered Architecture

```
┌────────────────────────────────────────────────────┐
│  Presentation Layer (Electron React)               │
│  ├─ Tray Window (status, settings, calibration)   │
│  ├─ Settings Modal (Discord, logs, stats)         │
│  └─ Notification Toast (match found alert)        │
└────────────────┬─────────────────────────────────┘
                 │ (IPC Messages)
                 ▼
┌────────────────────────────────────────────────────┐
│  Business Logic Layer (Python Backend)             │
│  ├─ AI Perception (gate heuristics + classifier)  │
│  ├─ State Machine (idle → queue → match_found)    │
│  ├─ MCP Tools (screen capture, notifications)     │
│  └─ Error Handling & Escalation                   │
└────────────────┬─────────────────────────────────┘
                 │ (SQLite Queries)
                 ▼
┌────────────────────────────────────────────────────┐
│  Data Layer (SQLite, Local Storage)                │
│  ├─ calibration_profiles (resolution-specific)    │
│  ├─ detection_history (recent detections)         │
│  ├─ notification_log (Discord, Desktop sent)      │
│  └─ settings (user preferences)                   │
└────────────────────────────────────────────────────┘
```

---

## 3. Key Components & Data Flow

### 3.1 AI Perception Engine (Backend)

**Two-tier inference**:

```
┌─────────────────────────┐
│  Screen Capture (MCP)   │
│  (24-bit BGR raw image) │
└─────────────┬───────────┘
              │
              ▼
    ┌─────────────────────┐
    │  Gate Heuristics    │ ← Fast (1–5ms)
    │  (brightness check) │   Always-on
    └────────┬────────────┘
             │
       ┌─────▼──────┐
       │ Confidence │
       │   < 60%?   │
       └─────┬──────┘
             │ YES
             ▼
    ┌──────────────────┐
    │  Classifier AI   │ ← Medium (30–40ms)
    │  (Int8 ONNX)     │   Only on gate pass
    └────────┬─────────┘
             │
       ┌─────▼──────┐
       │ Confidence │
       │   < 85%?   │
       └─────┬──────┘
             │ YES
             ▼
    ┌───────────────────────┐
    │  Escalation Model     │ ← Slow (100–150ms)
    │  (full-precision FP32)│   Only on classifier fail
    └───────────┬───────────┘
                │
                ▼
    ┌──────────────────────┐
    │  Final Confidence    │
    │  Score & State       │
    └──────────────────────┘
```

**Design rationale**:
- **Gate**: Cheap, always-on, filters 95% of non-queue frames
- **Classifier**: Runs only if gate is uncertain (saves CPU)
- **Escalation**: Runs only on classifier uncertainty (validation)
- **Result**: 99% of frames <10ms latency

---

### 3.2 State Machine

```
        ┌─────────────┐
        │    IDLE     │ (not in queue, no match)
        │ Confidence  │
        │    >80%     │
        └─────┬───────┘
              │
    ┌─────────▼──────────┐
    │ Queue detected,    │
    │ send notification  │
    ▼                    │
┌─────────┐              │
│ QUEUE   │◄─────────────┘
│Conf>80% │
└────┬────┘
     │
     │ Match found in UI
     ▼
┌──────────────┐
│ MATCH_FOUND  │
│ (blue screen)│
└────┬─────────┘
     │
     │ Hero select screen
     ▼
┌────────────────┐
│ HERO_SELECT    │
│ (char screen)  │
└────┬───────────┘
     │
     │ Game loaded
     ▼
┌──────────┐
│ IN_GAME  │
└────┬─────┘
     │
     │ Game ended
     ▼
┌──────────┐
│ IDLE     │◄────────────────┐
│          │                 │
└──────────┘   ┌─────────────┘
               │
         (cycle repeats)
```

**State → Notification Trigger**:
- **IDLE → QUEUE**: Send desktop + Discord notification
- **QUEUE → MATCH_FOUND**: Send "Match found! Click to play"
- Other transitions: Logged, not notified

---

### 3.3 IPC Bridge (Electron Main ↔ Renderer)

```
Renderer Process (React)        Main Process (Node.js)
┌──────────────────┐            ┌──────────────────┐
│ Settings Modal   │            │ IPC Router       │
│ (user changes    │──request───▶│ (dispatch to     │
│  Discord webhook)│            │  Python backend) │
│                  │            │                  │
│ updates state    │◀──response─│ (via socket)     │
└──────────────────┘            └──────────────────┘
                                        │
                                        ▼
                                ┌──────────────┐
                                │ Python Daemon│
                                │ (perception  │
                                │  + notifiers)│
                                └──────────────┘
```

**Key IPC Channels**:
- `notificationSend` → dispatch notification to UI
- `settingsUpdate` → update user preferences
- `calibrationSave` → persist calibration profiles
- `logsRead` → fetch detection history
- `statsRead` → CPU, memory, latency metrics

---

## 4. Technology Stack Detail

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Frontend** | Electron | 28.x | Desktop app wrapper, main process |
| | React | 18.x | UI components, state management |
| | TypeScript | 5.3+ | Type safety |
| | Tailwind CSS | 3.x | Styling (dark theme) |
| | Zustand | 4.x | Global state (Discord, settings) |
| **Backend** | Python | 3.11+ | Core logic, AI inference |
| | ONNX Runtime | 1.16+ | AI model inference (CPU-only, INT8 quantized) |
| | Strands Agents SDK | Latest | Agentic orchestration |
| | pydantic | 2.x | Config validation, API contracts |
| **Database** | SQLite | 3.45+ | Local persistence, WAL mode |
| | Alembic | 1.12+ | Schema migrations |
| **DevOps** | GitHub Actions | Latest | CI/CD, lint, test, build |
| | Docker | 24.x | Dev environment (optional) |
| | electron-builder | 24.x | MSI packaging |
| | electron-updater | 6.x | Auto-update mechanism |

---

## 5. Cross-Component Communication Patterns

### Pattern A: Perception Pipeline to UI Update

```
1. Backend: perceive_state() called every 100ms
2. Backend: State machine evaluates (idle → queue?)
3. Backend: If state changed, emit IPC event
4. Main: IPC handler receives event
5. Renderer: Redux/Zustand updates, re-renders State Badge
6. UI: Badge shows "QUEUE" with 87% confidence
```

**Latency SLA**: Perception (50ms) + IPC (5ms) + React render (20ms) = ~75ms p95

---

### Pattern B: User Settings Change → Persist → Trigger

```
1. UI: User enters Discord webhook URL
2. UI: Clicks "Test Webhook"
3. IPC: Sends `settingsUpdate` with URL to main
4. Backend: Calls notify.discord to validate
5. Backend: Returns success/error via IPC
6. UI: Toast "Webhook connected ✓" or error message
7. DB: SQLite settings table updated
```

**Latency SLA**: <2 seconds (includes Discord HTTP request)

---

### Pattern C: Calibration Workflow

```
1. User clicks "Calibrate" in Settings
2. UI: Open Calibration Wizard modal
3. UI: Step 2 — User marks regions on live screenshot
4. IPC: `calibrationSave` with region bounds + resolution
5. Backend: Insert into calibration_profiles table
6. Backend: Return confirmation + display profile
7. UI: Step 4 — "Success! Profile saved for 1920×1080"
```

**Latency SLA**: <100ms for region save (DB insert + IPC)

---

## 6. Data Models Snapshot

### calibration_profiles
```sql
CREATE TABLE calibration_profiles (
  id INTEGER PRIMARY KEY,
  width INTEGER NOT NULL,
  height INTEGER NOT NULL,
  queue_region BLOB,  -- JSON {x, y, w, h}
  match_button_region BLOB,  -- JSON {x, y, w, h}
  created_at TIMESTAMP,
  UNIQUE(width, height)
);
```

### detection_history
```sql
CREATE TABLE detection_history (
  id INTEGER PRIMARY KEY,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  state TEXT NOT NULL,  -- idle, queue, match_found, hero_select, in_game
  confidence REAL NOT NULL,
  evidence BLOB,  -- JSON {gate_score, classifier_score, escalation_score}
  -- Retention: 24 hours
);
```

### notification_log
```sql
CREATE TABLE notification_log (
  id INTEGER PRIMARY KEY,
  timestamp TIMESTAMP,
  channel TEXT,  -- 'desktop', 'discord'
  state_transition TEXT,  -- e.g., 'idle→queue'
  success BOOLEAN DEFAULT 1,
  error_message TEXT
);
```

### settings
```sql
CREATE TABLE settings (
  key TEXT PRIMARY KEY,
  value TEXT,  -- JSON for complex types
  updated_at TIMESTAMP
);
-- Examples: 'discord_webhook_url', 'auto_start_enabled', 'log_level'
```

---

## 7. Deployment Architecture

```
Developer's Machine
├─ Git clone repo
├─ `npm install` + `pip install -r requirements.txt`
├─ `npm run dev` → Electron + React hot-reload + Python daemon
└─ `npm run test` → Vitest + pytest

GitHub CI/CD
├─ On push to main:
│  ├─ Lint (eslint + pylint)
│  ├─ Type-check (tsc + mypy)
│  ├─ Unit tests (vitest + pytest)
│  ├─ Build Electron app (vite build)
│  └─ Create MSI installer (electron-builder)
├─ On tag push (v1.0.0):
│  ├─ Codesign MSI (Windows authenticode)
│  ├─ Create GitHub Release
│  ├─ Upload MSI artifact
│  └─ Publish RELEASES manifest (for auto-updater)

User's Machine (After Install)
├─ Run installer (MSI)
├─ App checks for updates (auto-updater via RELEASES)
├─ Runs Electron main process
├─ Starts Python daemon (subprocess)
├─ Monitors Overwatch window
└─ Shows tray notifications
```

---

## 8. Security & Privacy

### Data Stored Locally
- ✅ Calibration profiles (screen geometry)
- ✅ Detection history (state transitions, confidence scores)
- ✅ Notification log (what was sent, when)
- ✅ Settings (Discord webhook URL, preferences)

### Data NOT Stored
- ❌ Screenshots (captured, processed, discarded)
- ❌ Gameplay video (never recorded)
- ❌ User identity (no accounts, purely local)

### External Calls
- Optional: Discord webhook (HTTP POST) — user-provided URL only
- Optional: Analytics (privacy-first, no PII)

### Code Signing
- MSI installer signed with Windows authenticode
- Update manifest verified before auto-update applies

---

## 9. Performance Targets (from SRS)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Detection latency** | <100ms p95 | Time from screen capture → state decision |
| **CPU usage** | <10% sustained | During queue monitoring |
| **Memory** | <150 MB peak | React UI + Python daemon |
| **Startup time** | <2 seconds | Launch → ready to monitor |
| **False positives** | <5% | During beta testing |
| **Frame rate** | ≥30 FPS tray window | Smooth UI animations |
| **Disk usage** | <500 MB | App + dependencies |

---

## 10. Scaling Considerations (Future)

### v2.0+ Multi-Device
If expanding to mobile/web frontend:
- Backend logic extracts to microservice
- SQLite → PostgreSQL (shared state)
- IPC → gRPC or REST API
- Electron → Remains Windows desktop only; web dashboard optional

### Handling More Games
- Game-agnostic state machine (configurable regions, models)
- Config file format for new game detection profiles
- Community-contributed models (marketplace)

---

## 11. Architecture Decision Records (ADR)

### ADR-001: Why SQLite (Not PostgreSQL)?
**Decision**: Use SQLite 3.45+  
**Rationale**: Single-user local app, no network access needed, zero ops overhead, WAL mode for performance, VACUUM for storage  
**Alternatives Considered**: PostgreSQL (overkill), JSON files (poor query perf)  
**Trade-off**: No distributed queries, but not needed for this use case

### ADR-002: Why Tiered AI (Not Single Model)?
**Decision**: Gate + Classifier + Escalation  
**Rationale**: 99% latency <10ms via gate (cheap pass), scales to large confidence range  
**Alternatives Considered**: Single large model (expensive CPU), lightweight-only (high false positive)  
**Trade-off**: Complexity cost, but justified by latency & accuracy

### ADR-003: Why Local Processing (Not Cloud)?
**Decision**: All AI runs on-device  
**Rationale**: Privacy (no screenshots uploaded), latency (<50ms vs 500ms+ cloud), offline capability, zero API costs  
**Alternatives Considered**: Cloud inference (Faster tuning, but privacy risk;ToS)  
**Trade-off**: GPU optional, requires Windows machine capable enough

---

## 12. Diagram: Full System Flow (Initialization → Steady State)

```
User launches app
│
├─ Electron main process spawns
├─ React UI renders (tray window)
├─ Settings loaded from SQLite
├─ Python daemon subprocess started
├─ Calibration profiles loaded
│
└─ MONITORING LOOP (every 100ms):
   │
   ├─ MCP: screen.capture_regions (5ms)
   ├─ Gate: brightness heuristics (1ms)
   │
   ├─ If conf >60%:
   │  └─ Go to "Check Classifier"
   │
   ├─ If conf >85%:
   │  └─ Go to "State Transition"
   │
   ├─ Otherwise, Escalation model (100ms)
   │
   └─ State Transition Logic:
      │
      ├─ If IDLE → QUEUE:
      │  ├─ MCP: notify.desktop ("Queue detected!")
      │  └─ MCP: notify.discord (if webhook configured)
      │
      ├─ Otherwise:
      │  └─ Log to detection_history, skip notify
      │
      └─ IPC: Update React UI with new state
         └─ Tray window refreshes badge
```

---

## Next Steps

1. **Sprint 0**: Validate architecture decisions (ADR reviews, spike ONNX latency)
2. **Sprint 1**: Implement perception layer exactly as described
3. **Sprint 2+**: Build UI and integrate per this design
4. **Maintenance**: Update ADRs if major decisions change

**Owner**: Backend Lead, Frontend Lead, DB Architect  
**Stakeholders**: Product Manager, QA Lead, DevOps Lead
