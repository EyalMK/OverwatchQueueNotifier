# Sprint 0: Foundation Sprint Execution Prompt
## Overwatch AI Queue Detection & Notification App

---

## Context — Read These Files First

You are executing **AutoSpec Spec-Driven Development** for the Overwatch Queue Notifier project.

**READ ALL THESE FILES** to understand the complete project scope:

### SPECS (Single source of truth — READ ALL)
- `specs/01_product_manager.md` — Project vision, personas, user stories
- `specs/02_backend_lead.md` — API contracts, authentication, error handling
- `specs/03_frontend_lead.md` — Component architecture, state management, design tokens
- `specs/04_db_architect.md` — Database schema, migrations, SQL
- `specs/05_qa_lead.md` — Test pyramid, coverage targets, test patterns
- `specs/06_devops_lead.md` — Infrastructure, CI/CD, Docker setup
- `specs/10_ui_designer.md` — Screen wireframes, component states, responsive design

### BACKLOG
- `specs/backlog.md` — Sprint 0 tickets (your work items)

### DOCS (Architecture & guidance — READ ALL)
- `docs/architecture/overview.md` — High-level system diagram, request lifecycle
- `docs/architecture/backend.md` — Layered architecture, service design
- `docs/architecture/frontend.md` — Component hierarchy, state management
- `docs/architecture/database.md` — ERD, CREATE TABLE SQL, migrations
- `docs/architecture/security.md` — Authentication, secret management, OWASP checklist
- `docs/workflows/development.md` — Ticket workflow (pick → test → implement → merge)
- `docs/workflows/git-workflow.md` — Branch naming, commit format, PR process
- `docs/testing/strategy.md` — Test pyramid, unit/integration/e2e patterns
- `docs/environments/development.md` — Setup prerequisites, env vars, health checks
- `docs/api/reference.md` — MCP tool contracts, request/response examples

---

## Phase Breakdown: Infrastructure → Database → Backend → Frontend → Quality Gates

### Phase 1: Infrastructure & Project Setup (Days 1–2)
**Goal**: Repo structure, tooling, CI/CD pipeline ready. **Points: 5**

Tickets:
- **1.1: GitHub repo setup + CI/CD pipeline** (3pts)
  - [ ] Create GitHub Actions workflows (lint, test, build)
  - [ ] Set up GitHub branch protection (develop requires 2 reviews)
  - [ ] Configure secrets (for future signing)
  - **Reference**: specs/06_devops_lead.md (Section 2: CI/CD Pipeline)
  - **Verification**: `git push` triggers GitHub Actions; all checks pass

- **1.2: Project scaffolding (frontend + backend)** (2pts)
  - [ ] Create `frontend/` with Vite + React + TypeScript template
  - [ ] Create `backend/` with Python 3.11 + uv setup
  - [ ] Create `shared/` with TypeScript types
  - [ ] Add root `.gitignore`, `README.md`
  - **Reference**: specs/02_backend_lead.md (Section 3: Directory Structure)
  - **Verification**: `npm install && python -m pip install -e .` works without errors

---

### Phase 2: Database Layer (Days 2–3)
**Goal**: SQLite schema + migration framework. **Points: 5**

Tickets:
- **1.3: SQLite schema & migrations** (3pts)
  - [ ] Copy `docs/architecture/database.md` CREATE TABLE SQL into `backend/src/db/migrations/202602060000_init_schema.sql`
  - [ ] Implement migration runner in `backend/src/db/migrations.py`
  - [ ] Test migrations: `python backend/src/db/migrations.py`
  - [ ] Verify schema: 4 tables created (calibration_profiles, detection_history, notification_log, settings)
  - **Reference**: specs/04_db_architect.md (Sections 3–5)
  - **Verification**: `sqlite3 backend/local.db ".tables"` shows 4 tables

- **1.4: Repository layer (data access abstraction)** (2pts)
  - [ ] Implement `backend/src/state/repository.py` with classes:
    - `CalibrationRepository.load(resolution) → profile_data`
    - `DetectionRepository.insert(state, confidence, evidence) → id`
    - `NotificationRepository.insert(detection_id, type, status) → id`
    - `SettingsRepository.get(key) → value`
  - [ ] Add error handling (DatabaseError, IntegrityError)
  - [ ] Write unit tests (`backend/tests/unit/test_repository.py`)
  - **Reference**: specs/04_db_architect.md (Section 5: Index Definitions)
  - **Verification**: All tests pass; coverage >80%

---

### Phase 3: Backend Services Setup (Days 3–5)
**Goal**: MCP HTTP server + perception pipeline skeleton. **Points: 8**

Tickets:
- **1.5: MCP HTTP server & tool interface** (2pts)
  - [ ] Create `backend/src/mcp/server.py` (Node.js Express OR Python FastAPI)
  - [ ] Implement 4 MCP tools:
    - POST `/mcp/tools/screen.perceive_state` → { state, confidence, evidence }
    - POST `/mcp/tools/screen.capture_regions` → { regions: [base64...] }
    - POST `/mcp/tools/notify.desktop` → { notification_id, delivered }
    - POST `/mcp/tools/notify.discord` → { delivered, webhook_id }
  - [ ] Validate JSON schemas for all requests
  - [ ] Return error responses (400, 429, 503) per spec
  - **Reference**: specs/02_backend_lead.md (Section 4: API Contracts)
  - **Verification**: `curl` requests return proper JSON; health check passes

- **1.6: Screen capture service (Windows DCE API)** (2pts)
  - [ ] Implement `backend/src/perception/screen_capture.py`
    - GetWindowDC() → capture Overwatch window to RGB array
    - Return: `np.ndarray(height, width, 3)` uint8
    - Latency target: <10ms
  - [ ] Handle window not found error (WindowNotFoundError)
  - [ ] Write unit tests with mock frames
  - **Reference**: specs/02_backend_lead.md (Section 3: Directory Structure, perception/)
  - **Verification**: `python -c "from perception import screen_capture; frame = screen_capture.capture()" → (1080, 1920, 3)`

- **1.7: Gate logic service (heuristics)** (2pts)
  - [ ] Implement `backend/src/perception/gate.py`
    - Pixel diff % calculation (Requirement DR-3)
    - Histogram divergence (Bhattacharyya)
    - Configurable thresholds (env vars)
  - [ ] Method: `should_process(prev_frame, curr_frame) → bool`
  - [ ] Latency target: <5ms
  - [ ] Write comprehensive unit tests (5-7 test cases)
  - **Reference**: specs/02_backend_lead.md (Section 3: perception/gate.py)
  - **Verification**: `pytest tests/unit/test_gate.py -v` → all pass

- **1.8: AI classifier skeleton (ONNX Runtime)** (2pts)
  - [ ] Download pre-trained tiny + escalation ONNX models
  - [ ] Implement `backend/src/perception/classifier.py`
    - Load models via ONNX Runtime
    - Crop + normalize input to 224×224
    - Run inference: tiny model → output softmax
    - Method: `predict(image) → (state, confidence)`
    - Method: `predict_with_escalation(image, threshold=0.85) → (state, confidence, escalated)`
  - [ ] Latency targets: tiny <50ms, escalation <150ms
  - [ ] Mock models for unit tests (not full inference)
  - **Reference**: specs/02_backend_lead.md (Section 3: perception/classifier.py), specs/04_db_architect.md (Models/)
  - **Verification**: Model inference latency measured; tests pass

---

### Phase 4: Frontend UI Setup (Days 4–6)
**Goal**: Tray window component + state management. **Points: 7**

Tickets:
- **1.9: Zustand store setup (global state)** (2pts)
  - [ ] Create `frontend/src/store/gameStore.ts`
    - State: currentState, confidence, isMonitoring, discordUrl, etc.
    - Persist to localStorage
    - Methods: setState(), addDetection(), setDiscordUrl()
  - [ ] Create types in `frontend/src/types/game.ts` (GameState enum, Detection interface)
  - [ ] Write unit tests for store
  - **Reference**: specs/03_frontend_lead.md (Section 3: State Management)
  - **Verification**: `npm test store/gameStore.test.ts` passes

- **1.10: Tray window component** (3pts)
  - [ ] Create `frontend/src/pages/TrayWindow.tsx`
    - Header: minimize, close buttons
    - StateDisplay: state icon + badge + confidence progress bar
    - LastEventSection: timestamp + state label
    - ActionBar: Test Notif, Calibrate, Settings buttons
    - Footer: CPU/GPU/Memory meters (placeholder)
  - [ ] Size: 380×540 px, dark theme (Tailwind CSS)
  - [ ] Listen to gameStore updates in real-time
  - [ ] All states styled (IDLE gray, QUEUE amber, MATCH_FOUND emerald, etc.)
  - **Reference**: specs/10_ui_designer.md (Section 2: Tray Window wireframe), specs/03_frontend_lead.md (Design Tokens)
  - **Verification**: Electron tray window renders; clicking buttons triggers actions

- **1.11: Settings Modal (tabs)** (2pts)
  - [ ] Create `frontend/src/components/SettingsModal.tsx`
    - 5 tabs: General, Discord, Calibration, Stats, Logs
    - General: auto-start toggle, notification sound toggle, theme selector
    - Discord: webhook URL input (masked), test button, status badge
    - Calibration: resolution display, calibrate button
    - Stats: CPU/GPU/Memory meters
    - Logs: filter bar, detection log table
  - [ ] Modal slides in from right; close on background click or X button
  - [ ] Validate Discord webhook URL format
  - **Reference**: specs/10_ui_designer.md (Section 2: Settings Modal)
  - **Verification**: Modal opens/closes; form inputs work; validation passes

---

### Phase 5: Integration & Quality Gates (Days 5–7)
**Goal**: Full stack working end-to-end; tests passing. **Points: 5**

Tickets:
- **1.12: Backend ↔ Frontend IPC setup** (2pts)
  - [ ] Implement Electron IPC bridge in `frontend/src/lib/ipc.ts`
    - Call backend MCP tools via named pipes or HTTP
    - Handle timeouts + retries
  - [ ] Integrate into gameStore: fetch state every 500ms
  - [ ] Error handling: show toast if backend down
  - **Reference**: docs/workflows/development.md (Step 3: Test-Driven Development)
  - **Verification**: Frontend updates state as backend detects changes

- **1.13: Test suite setup (unit + integration)** (2pts)
  - [ ] Configure pytest (backend): `pytest.ini`, `conftest.py`, fixtures
  - [ ] Configure vitest (frontend): `vitest.config.ts`, test setup
  - [ ] Coverage targets: 75%+ lines, 100% critical paths
  - [ ] Add GitHub Actions CI (lint + test + build)
  - [ ] Mock ONNX models for fast tests
  - **Reference**: specs/05_qa_lead.md (Sections 2–3), docs/testing/strategy.md
  - **Verification**: `pytest tests/ --cov` shows >75% coverage; `npm test` passes

- **1.14: Documentation completion** (1pt)
  - [ ] Verify all docs match generated code (specs/ + docs/)
  - [ ] Add project setup instructions to `README.md`
  - [ ] Add CONTRIBUTING.md (development workflow)
  - **Reference**: All spec files + docs/
  - **Verification**: `README.md` has clone + setup + run instructions

---

## Definition of Done (per Ticket)

✓ Code implements spec requirement exactly  
✓ Unit + integration tests pass (coverage >75%)  
✓ No lint errors (`npm run lint`, `black .`)  
✓ TypeScript strict mode passes (`npm run typecheck`)  
✓ Code reviewed + 2 approvals  
✓ Merged to `develop` branch  
✓ Backlog.md updated: status → "done", notes added  

---

## Daily Commands (Verify Everything Works)

```bash
# Backend health check
cd backend && pytest tests/ --cov && python -m src.main --dev

# Frontend health check
cd frontend && npm run typecheck && npm run lint && npm test

# End-to-end check
curl -X POST http://127.0.0.1:5000/mcp/tools/screen.perceive_state \
  -H "Content-Type: application/json" \
  -d '{"resolution": "1920x1080"}'
# Expected: { "state": "IDLE", "confidence": 0.92, ... }
```

---

## Unknown Requirements (Assumptions Made)

1. **ONNX Models**: Assumed pre-trained models available in `backend/models/`. If not, download from Hugging Face.
2. **Discord Webhook**: Spec assumes user provides URL; not tested in MVP (will be tested in Sprint 1).
3. **Overwatch Window Name**: Assumed "Overwatch 2"; may require adjustment for different regions/versions.

---

## Success Criteria (End of Sprint 0)

✓ All 14 tickets marked "done" in backlog  
✓ GitHub repo buildable without errors  
✓ CI/CD pipeline passing all checks  
✓ Frontend tray window opens with correct UI  
✓ Backend HTTP server responds to MCP tools  
✓ Database schema created with migrations  
✓ Test coverage >75%  
✓ Documentation complete and up-to-date  

**After Sprint 0: You have a working foundation. Sprint 1 adds features.**

---

## Timeline

- **Day 1**: Infrastructure + scaffolding (1.1, 1.2)
- **Day 2–3**: Database + repositories (1.3, 1.4)
- **Day 3–5**: Backend services (1.5–1.8)
- **Day 4–6**: Frontend UI (1.9–1.11)
- **Day 5–7**: Integration + tests + docs (1.12–1.14)

**Buffer**: 1–2 days for blockers or refinement.

---

**Begin Sprint 0 execution now. Update specs/backlog.md as tickets move to "done".**
