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

The perception pipeline uses a cascading approach to minimize latency while maintaining high accuracy.

### 3.2 State Machine

The state machine manages Overwatch game state transitions from idle through queue detection to in-game.

### 3.3 IPC Bridge

Electron's inter-process communication enables real-time updates between the Python backend and React frontend.

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

---

## 7. Next Steps

1. **Sprint 0**: Validate architecture decisions
2. **Sprint 1**: Implement perception layer
3. **Sprint 2+**: Build UI and integrate
4. **Maintenance**: Update docs as needed

**Owner**: Backend Lead, Frontend Lead, DB Architect  
**Stakeholders**: Product Manager, QA Lead, DevOps Lead
