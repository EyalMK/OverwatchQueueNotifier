# Project Backlog
## Overwatch AI Queue Detection & Notification App

**Generated**: February 6, 2026  
**Version**: 1.0  
**Total Story Points**: ~175  
**Sprint Capacity**: 25â€“30 points/sprint  
**Planned Duration**: 6 sprints (~18 weeks)

---

## Overview

| Phase | Sprints | Duration | FTE | Focus |
|-------|---------|----------|-----|-------|
| **Foundation** | Sprint 0, 1 | Weeks 1â€“5 | 1 FTE | Project setup, architecture, core backend |
| **Core Features** | Sprint 2, 3 | Weeks 6â€“10 | 1 FTE | AI models, Electron UI, calibration |
| **Polish & Release** | Sprint 4, 5 | Weeks 11â€“18 | 1 FTE | Testing, deployment, documentation, v1.0 launch |

---

## Sprint 0: Project Foundation (Weeks 1â€“2, 28 points)

**Goal**: Achieve working development environment, architecture decisions locked, CLI scaffolding.

| Ticket | Type | Title | Story Points | Owner | Priority | Status |
|--------|------|-------|--------------|-------|----------|--------|
| **SETUP-001** | Setup | Initialize Python 3.11 virtual environment + dependency management | 3 | Backend | P0 | Done |
| **SETUP-002** | Setup | Configure Electron + React + TypeScript development environment | 4 | Frontend | P0 | Done |
| **SETUP-003** | Setup | Create SQLite database schema + migrations scaffolding | 2 | DB Architect | P0 | Done |
| **SETUP-004** | Setup | Set up GitHub Actions CI/CD pipeline (lint, test, type-check) | 3 | DevOps | P0 | Done |
| **SETUP-005** | Spike | Decision: Int8 ONNX quantization vs full float32 models (validate latency <50ms) | 4 | Backend | P0 | Done |
| **SETUP-006** | Docs | Auto-generate design token JSON from 10_ui_designer.md | 2 | UI Designer | P1 | Done |
| **SETUP-007** | Config | Create .env.example + environment configuration loader | 2 | DevOps | P0 | Done |
| **SETUP-008** | Docs | Write developer onboarding guide (5 min bootstrap) | 2 | DevOps | P1 | Done |
| **SETUP-009** | Test | Create test fixtures + pytest base structure for backend | 2 | QA | P0 | Done |
| **SETUP-010** | Build | Configure Vite build + source maps for Electron | 2 | Frontend | P0 | Done |

**Sprint 0 Total**: 26 points | **Carry-over Risk**: Low (all setup tasks)

Notes:
- SETUP-002: frontend scaffold created in frontend/ (Vite + React + TypeScript + Tailwind).
- SETUP-010: Vite build configured with source maps for Electron (base ./).
- SETUP-005: ✓ COMPLETE (2026-02-07) — ONNX benchmark validation complete. See `docs/spikes/SETUP-005_onnx_model_validation.md` for detailed results.
  - **Decision**: Use **ShuffleNet-V2** (5.25 MB) as primary tiny classifier
  - **Performance**: p95 latency = 1.75ms (target <50ms) ✓ PASS
  - **Escalation**: EfficientNet-Lite4 available for low-confidence cases (p95 = 7.53ms)
  - **Model Paths**: 
    - Primary: `backend/models/Shufflenet-v2.onnx`
    - Escalation: `backend/models/efficientnet-lite4-11.onnx`
  - **Quantization**: Skipped — FP32 models already exceed performance targets by >25x margin
  - **Classifier Updated**: `backend/src/perception/classifier.py` now loads ShuffleNet-V2 by default
- SETUP-004: Added GitHub Actions workflow `test.yml` (ruff lint, frontend type-check, backend tests, frontend build).
- SETUP-008: Added `docs/onboarding.md` with 5-minute bootstrap.
- SETUP-006: Added `frontend/src/styles/design-tokens.json` generated from `SDD/specs/10_ui_designer.md`.
- Sprint-0 prompt alignment: Implemented repository layer + unit tests in `backend/src/state/repository.py` and `backend/tests/unit/test_repository.py`.
- Sprint-0 prompt alignment: MCP server endpoints now validate inputs and enforce rate limits in `backend/src/mcp/server.py`.
- Sprint-0 prompt alignment: Backend entrypoint now supports `--dev` to run MCP server after migrations in `backend/src/main.py`.
- Sprint-0 prompt alignment: Gate heuristics implemented with unit tests in `backend/src/perception/gate.py` and `backend/tests/unit/test_gate.py`.
- Sprint-0 prompt alignment: Screen capture service stub + tests added in `backend/src/perception/screen_capture.py` and `backend/tests/unit/test_screen_capture.py`.
- Sprint-0 prompt alignment: Classifier skeleton + tests added in `backend/src/perception/classifier.py` and `backend/tests/unit/test_classifier.py`.
- Sprint-0 prompt alignment: MCP perceive_state now wired to capture + gate + classifier logic with caching in `backend/src/mcp/server.py`.
- Sprint-0 prompt alignment: MCP capture_regions now performs real crop + base64 encoding in `backend/src/mcp/server.py`.
- Sprint-0 prompt alignment: Frontend tray UI + settings modal + Zustand store scaffolded in `frontend/src/pages/TrayWindow.tsx`, `frontend/src/components/SettingsModal.tsx`, and `frontend/src/store/gameStore.ts`.
- Sprint-0 prompt alignment: Added Vitest setup and store tests in `frontend/vitest.config.ts` and `frontend/src/store/gameStore.test.ts`.
- Sprint-0 prompt alignment: IPC bridge stub + polling added in `frontend/src/lib/ipc.ts` and `frontend/src/store/gameStore.ts`.
- Sprint-0 prompt alignment: Added root docs `README.md` and `CONTRIBUTING.md`.
- Sprint-0 prompt alignment: Added backend `pytest.ini`.
- Sprint-0 prompt alignment: Calibration profile loading + optional notification logging added in `backend/src/mcp/server.py`.
- Sprint-0 prompt alignment: Added MCP integration tests in `backend/tests/integration/test_mcp_tools.py`.

---

## Sprint 1: Backend Core + Architecture (Weeks 3â€“5, 29 points)

**Goal**: AI perception layer complete (gate + classifier), API contracts implemented, database operational.

| Ticket | Type | Title | Story Points | Owner | Priority | Status |
|--------|------|-------|--------------|-------|----------|--------|
| **BACKEND-001** | Feature | Implement gate heuristics (queue region brightness check) | 5 | Backend | P0 | Done |
| **BACKEND-002** | Feature | Download + quantize Intel ONNX classifier model (Int8) | 4 | Backend | P0 | Done |
| **BACKEND-003** | Feature | Implement classifier inference pipeline with confidence scoring | 4 | Backend | P0 | Done |
| **BACKEND-004** | Feature | Implement error escalation logic (< 0.85 confidence â†’ escalation model) | 3 | Backend | P0 | Done |
| **BACKEND-005** | Feature | Implement screen.perceive_state MCP tool (API contract from 02_backend_lead.md) | 5 | Backend | P0 | Done |
| **BACKEND-006** | Feature | Implement screen.capture_regions MCP tool | 3 | Backend | P0 | Done |
| **BACKEND-007** | Feature | Implement notify.desktop MCP tool (via win32 notificationmanager) | 2 | Backend | P0 | Done |
| **BACKEND-008** | Feature | Implement state transition machine (idle â†’ queue â†’ match_found â†’ in_game) | 3 | Backend | P0 | Done |
| **BACKEND-009** | Feature | Create detection_history table + insertion logic + retention policy (24h) | 2 | DB Architect | P0 | Done |
| **BACKEND-010** | Test | Unit tests for gate heuristics (pytest) â€” target 85% coverage | 2 | QA | P0 | Done |
| **BACKEND-011** | Test | Unit tests for classifier inference (mock ONNX) â€” target 85% coverage | 2 | QA | P0 | Done |
| **BACKEND-012** | Test | Integration test: Full perception pipeline (gate + classifier + escalation) | 3 | QA | P0 | Done |

**Sprint 1 Total**: 38 points | **Carry-over Risk**: Moderate (BACKEND-002 may unblock late; plan for flex)

Notes:
- Sprint-1 execution completed on February 7, 2026.
- Delivered gate tuning, ONNX classifier + escalation strategy, MCP endpoint implementations, state machine, detection logging retention, and full unit/integration coverage expansion.

---

## Sprint 2: Frontend Scaffold + Calibration UI (Weeks 6â€“8, 31 points)

**Goal**: Electron app boots, Settings modal complete, Calibration Wizard fully functional.

| Ticket | Type | Title | Story Points | Owner | Priority | Status |
|--------|------|-------|--------------|-------|----------|--------|
| **FRONTEND-001** | Feature | Create Electron main process + IPC bridge + context preload | 5 | Frontend | P0 | Done |
| **FRONTEND-002** | Feature | Build tray icon + menu (minimize, settings, exit) | 3 | Frontend | P0 | Done |
| **FRONTEND-003** | Feature | Implement Settings modal with 5 tabs (General, Discord, Calibration, Stats, Logs) | 8 | Frontend | P0 | Done |
| **FRONTEND-004** | Feature | Build Calibration Wizard (4-step modal with region editor) | 8 | Frontend | P0 | Done |
| **FRONTEND-005** | Feature | Integrate Calibration Wizard â†’ SQLite profile creation (calibration_profiles table) | 3 | Frontend | P0 | Done |
| **FRONTEND-006** | Feature | Implement State Badge component + confidence progress bar | 2 | Frontend | P1 | Done |
| **FRONTEND-007** | Feature | Create Notification Toast component (match found animation) | 2 | Frontend | P1 | Done |
| **FRONTEND-008** | Test | Vitest unit tests for all React components (50+ components) | 3 | QA | P0 | Done |
| **FRONTEND-009** | Build | Configure auto-reload for Electron during dev (hot reload) | 2 | Frontend | P1 | Done |
| **FRONTEND-010** | Accessibility | Add WCAG 2.1 AA focus management + keyboard nav to Settings modal | 2 | UI Designer | P1 | Done |
| **FRONTEND-011** | Performance | Measure Electron startup time (target <2s), optimize if >3s | 2 | Frontend | P1 | Done |

**Sprint 2 Total**: 35 points (Chosen Scope: P0 + Selected P1 for Balanced Delivery)

**Sprint 2 Status**: Completed | **Comprehensive Execution Guide**: See `sprint_prompts/sprint-2-frontend.md`

**Architecture Decisions** (Locked for Sprint 2):
1. **Communication Protocol**: HTTP Polling to localhost:5000 (current backend integration)
2. **Main Process**: `frontend/src/main-electron.ts` (monorepo, single build)
3. **Persistence**: Hybrid (localStorage for UX, SQLite persistence deferred to Sprint 3)
4. **Scope**: 35 pts = all P0 (FRONTEND-001 through 005, 008) + key P1 (FRONTEND-006, 007, 010)
5. **Capacity Outcome**: FRONTEND-009 and FRONTEND-011 were initially conditional and are now completed within Sprint 2.

**Success Criteria**:
- ✅ Electron boot <3s (target <2s)
- ✅ Tray window + live game state display
- ✅ Settings modal (5 tabs, all functional)
- ✅ Calibration Wizard (4 steps, interactive region editor)
- ✅ >75% test coverage, WCAG 2.1 AA accessibility
- ✅ Zero lint/type errors

**Critical Path**: FRONTEND-001 (Days 1-2) unblocks all; Parallel Phase 2 (Days 3-10); Phase 3 (Days 10-18)

**Sprint 2 Carry-over Risk**: Low (all P0 in scope; P1 flexible)

Notes:
- Sprint-2 execution delivered Electron main/preload integration in `frontend/src/main-electron.ts` and `frontend/src/preload.ts`, plus renderer bridge types in `frontend/src/types/electron.ts`.
- Tray window, settings modal, calibration wizard, region editor, confidence bar, state icon, and toast components were implemented and wired through Zustand store actions.
- Calibration persistence was implemented in frontend localStorage (`calibration_<resolution>`) and backend migration `backend/src/db/migrations/202602080001_create_calibration_profiles_table.sql` was added for `calibration_profiles`.
- Frontend polling/error handling was hardened: IPC fallback to HTTP, dynamic resolution polling, graceful handling for expected backend runtime states, and improved startup stability in Electron dev flow.
- Backend MCP server added CORS support with configurable origins (`CORS_ALLOWED_ORIGINS`) and preflight (`OPTIONS`) compatibility for frontend polling.
- Backend `screen.perceive_state` behavior was adjusted to return `200 IDLE` for window-not-found and runtime resolution mismatch, preventing noisy 400 loops during normal idle conditions.
- Resolution detection path was corrected to use native display size (`screen.getPrimaryDisplay().size`), and calibration/settings UI now shows detected runtime resolution.
- Queue-accept region concept was removed from calibration flow; wizard now calibrates queue region only (Overwatch has no accept queue button).
- FRONTEND-009 complete: Electron hot reload configured via `electron-reload` in `frontend/src/main-electron.ts` and dev script updated to launch with explicit `--dev`.
- FRONTEND-011 complete: startup instrumentation added (`[startup] window ready in <ms>ms`), repeatable measurement command added (`npm run perf:startup`), baseline file added (`frontend/PERF_BASELINE.md`), and performance guidance documented in `CONTRIBUTING.md`.
- Automated validation passed after these changes: frontend `typecheck` + `vitest` and backend `pytest` suites.

---

## Sprint 3: Backend-Frontend Integration + Discord (Weeks 9â€“11, 28 points)

**Goal**: Notifications flow end-to-end, Discord integration tested, calibration flow proven.

| Ticket | Type | Title | Story Points | Owner | Priority | Status |
|--------|------|-------|--------------|-------|----------|--------|
| **INTEGRATION-001** | Feature | Implement notify.discord MCP tool (webhook retry logic, exponential backoff) | 4 | Backend | P0 | Not Started |
| **INTEGRATION-002** | Feature | Hook up perception engine â†’ notification dispatch (IPC from backend to frontend) | 3 | Backend | P0 | Not Started |
| **INTEGRATION-003** | Feature | Implement API client abstraction (fetch utilities, error handling) | 2 | Frontend | P0 | Not Started |
| **INTEGRATION-004** | Feature | Connect Settings Discord tab to notify.discord MCP (webhook validation) | 3 | Frontend | P0 | Not Started |
| **INTEGRATION-005** | Feature | Implement "Test Notification" button (desktop + Discord) | 2 | Frontend | P0 | Not Started |
| **INTEGRATION-006** | Feature | Implement deduplication logic (prevent duplicate notification bursts) | 3 | Backend | P0 | Not Started |
| **INTEGRATION-007** | Feature | Settings tab: Display last successful notification timestamp | 1 | Frontend | P1 | Not Started |
| **DATABASE-001** | Feature | Create notification_log + settings tables (schema from 04_db_architect.md) | 2 | DB Architect | P0 | Not Started |
| **INTEGRATION-008** | Test | E2E test: Queue state detected â†’ Desktop notification â†’ UI updates | 4 | QA | P0 | Not Started |
| **INTEGRATION-009** | Test | E2E test: Discord webhook failure â†’ Retry with exponential backoff | 2 | QA | P0 | Not Started |
| **INTEGRATION-010** | Spike | Validate calibration UX (internal playtest, 5 manual tests) | 2 | QA | P0 | Not Started |
| **DOCS-001** | Docs | Write API client usage guide (internal) | 1 | Backend | P2 | Not Started |

**Sprint 3 Total**: 29 points | **Carry-over**: 1 point

---

## Sprint 4: Testing, Optimization + Beta Prep (Weeks 12â€“14, 27 points)

**Goal**: 75%+ test coverage, sub-50ms latency validated, beta release package ready.

| Ticket | Type | Title | Story Points | Owner | Priority | Status |
|--------|------|-------|--------------|-------|----------|--------|
| **QA-001** | Test | Full unit test suite for backend (target 85% coverage) | 4 | QA | P0 | Not Started |
| **QA-002** | Test | Integration tests: Database transaction rollback, backup/restore | 3 | QA | P0 | Not Started |
| **QA-003** | Test | Performance test: CPU, memory, GPU under sustained monitoring (8 hours) | 3 | QA | P0 | Not Started |
| **QA-004** | Test | Latency profiling: e2e detection latency (p50, p95, max) | 2 | QA | P0 | Not Started |
| **QA-005** | Test | Accessibility audit (WCAG 2.1 AA, axe-core automated + manual) | 3 | UI Designer | P1 | Not Started |
| **QA-006** | Build | Create MSI installer (electron-builder for Windows) | 4 | DevOps | P0 | Not Started |
| **QA-007** | Build | Configure electron-updater (RELEASES manifest, delta updates) | 3 | DevOps | P0 | Not Started |
| **QA-008** | Security | Code signing certificate setup (Windows authenticode for MSI) | 2 | DevOps | P0 | Not Started |
| **DOCS-002** | Docs | Write user manual (installation, first-run, troubleshooting) | 3 | Marketing | P1 | Not Started |
| **DOCS-003** | Docs | Generate API reference documentation (auto from specs) | 2 | Backend | P1 | Not Started |

**Sprint 4 Total**: 31 points | **Carry-over**: 4 points | **Revised**: 27 points

---

## Sprint 5: Beta Launch + Community (Weeks 15â€“17, 26 points)

**Goal**: Beta version (v0.1) shipped to 50â€“100 users, feedback loop active, analytics tracking.

| Ticket | Type | Title | Story Points | Owner | Priority | Status |
|--------|------|-------|--------------|-------|----------|--------|
| **RELEASE-001** | Feature | Implement analytics event tracking (installs, events, errors â€” privacy-first) | 3 | Marketing | P1 | Not Started |
| **RELEASE-002** | Build | Build v0.1-beta release (MSI + auto-update manifest) | 2 | DevOps | P0 | Not Started |
| **RELEASE-003** | Marketing | Post private beta invitation to 100 community members (Discord, Reddit) | 2 | Marketing | P0 | Not Started |
| **RELEASE-004** | Support | Set up feedback channel (Discord #feedback-beta) + issue triage process | 2 | Marketing | P1 | Not Started |
| **RELEASE-005** | Feature | Bug fix: Handle edge cases found in beta (variance, false positives) | 5 | Backend | P0 | Not Started |
| **RELEASE-006** | Feature | Performance tuning: Further reduce CPU if monitoring shows >10% sustained | 3 | Backend | P1 | Not Started |
| **RELEASE-007** | Feature | Implement user preference: Notification snooze (15min, 1h, 8h options) | 3 | Frontend | P2 | Not Started |
| **RELEASE-008** | Test | Regression test suite: Ensure beta fixes don't break existing features | 2 | QA | P0 | Not Started |
| **DOCS-004** | Docs | Create troubleshooting guide based on beta feedback | 2 | Marketing | P1 | Not Started |

**Sprint 5 Total**: 24 points

---

## Sprint 6: General Release (Weeks 18â€“22, 26 points)

**Goal**: v1.0 stable release, public announcement, sustainable support process.

| Ticket | Type | Title | Story Points | Owner | Priority | Status |
|--------|------|-------|--------------|-------|----------|--------|
| **V1.0-001** | Feature | Polish UI: Theme refinement, dark mode verified | 2 | UI Designer | P1 | Not Started |
| **V1.0-002** | Feature | Implement crash reporting (Sentry integration) | 3 | DevOps | P1 | Not Started |
| **V1.0-003** | Build | Create v1.0-stable release + GitHub release page | 2 | DevOps | P0 | Not Started |
| **V1.0-004** | Marketing | Public launch announcement (Reddit /r/Overwatch, Twitter, Discord) | 3 | Marketing | P0 | Not Started |
| **V1.0-005** | Docs | Final user manual + troubleshooting guide | 2 | Marketing | P1 | Not Started |
| **V1.0-006** | Support | Set up support process (GitHub Issues triage, Discord support channel) | 2 | Marketing | P1 | Not Started |
| **V1.0-007** | Maintenance | Implement health monitoring (error rates, uptime, key metrics dashboard) | 4 | DevOps | P1 | Not Started |
| **V1.0-008** | Feature | Plan v2.0 features + deprecation roadmap | 3 | Product Manager | P2 | Not Started |
| **V1.0-009** | Test | Final UAT (User Acceptance Testing) with 10 external users | 3 | QA | P0 | Not Started |
| **V1.0-010** | Docs | Generate architecture & API documentation for open-source (post-launch) | 2 | Backend | P2 | Not Started |

**Sprint 6 Total**: 26 points

---

## Dependency Graph

```
Sprint 0: SETUP-001..010
  â†“
Sprint 1: BACKEND-001..012
  â†“ (uses outcomes from Sprint 1)
Sprint 2: FRONTEND-001..011
  â†“ (frontend + backend must converge)
Sprint 3: INTEGRATION-001..010 (requires completed BACKEND + FRONTEND tasks)
  â†“
Sprint 4: QA-001..008 (comprehensive testing, installer)
  â†“
Sprint 5: RELEASE-001..008 (beta launch, iteration on feedback)
  â†“
Sprint 6: V1.0-001..010 (general release, sustainable support)
```

---

## Work Allocation by Role

| Role | Sprint 0 | Sprint 1 | Sprint 2 | Sprint 3 | Sprint 4 | Sprint 5 | Sprint 6 | Total Points |
|------|----------|----------|----------|----------|----------|----------|----------|--------------|
| Backend | 3 | 23 | 0 | 10 | 2 | 8 | 0 | 46 |
| Frontend | 4 | 0 | 30 | 5 | 0 | 3 | 2 | 44 |
| Database | 2 | 2 | 0 | 2 | 3 | 0 | 0 | 9 |
| QA | 2 | 5 | 3 | 6 | 12 | 2 | 3 | 33 |
| DevOps | 5 | 0 | 0 | 0 | 9 | 2 | 6 | 22 |
| UI Designer | 2 | 0 | 2 | 0 | 3 | 0 | 2 | 9 |
| Product Manager | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 3 |
| Marketing | 0 | 0 | 0 | 1 | 3 | 2 | 5 | 11 |

**Total Work**: 175 story points across 6 sprints (average 29 points/sprint)  
**Team Capacity**: 1 FTE (~30 points/sprint sustained)  
**Buffer**: Included in ticket estimates (complexity, unknown risks)

---

## Acceptance Criteria by Milestone

### End of Sprint 1 (Week 5)
- [x] AI perception engine running in-process with latency <50ms (p95)
- [x] MCP tools implemented (4 tools, all API contracts from 02_backend_lead.md)
- [x] State machine transitions idempotent and tested
- [x] Database schema created and migrations working

### End of Sprint 2 (Week 8)
- [ ] Electron app boots <2s
- [ ] Settings modal fully functional with all 5 tabs
- [ ] Calibration Wizard accessible and usable (WCAG AA)
- [ ] Auto-deploy to dev environment on every commit

### End of Sprint 3 (Week 11)
- [ ] End-to-end notifications: Detection â†’ Discord + Desktop
- [ ] Calibration profiles persisted, auto-selected by resolution
- [ ] Deduplication prevents alert spam (>500ms debounce)
- [ ] E2E tests cover critical user journeys (queue â†’ notification â†’ UI)

### End of Sprint 4 (Week 14)
- [ ] 75%+ test coverage (unit + integration)
- [ ] MSI installer working on Windows 10/11
- [ ] Auto-update mechanism functional (electron-updater)
- [ ] Code signed and verifiable

### End of Sprint 5 (Week 17)
- [ ] v0.1-beta shipped to 50+ users
- [ ] <5% false positive rate (validated in beta)
- [ ] Crash-free hours >99% in beta cohort
- [ ] Community feedback channel active

### Launch (Week 18)
- [ ] v1.0-stable released publicly
- [ ] Open-source license + documentation
- [ ] Support process documented + responding
- [ ] Post-launch monitoring active

---

## Success Metrics (from SRS + Specs)

| Metric | Target | Owner | Sprint |
|--------|--------|-------|--------|
| Detection latency (p95) | <100ms | Backend | 1, 4 |
| False positive rate | <5% | QA | 5 |
| CPU sustained | <10% | Backend | 4 |
| Startup time | <2s | Frontend | 2, 4 |
| Test coverage | â‰¥75% | QA | 4 |
| Accessibility score | WCAG AA | UI Designer | 4 |
| Beta users (v0.1) | 50â€“100 | Marketing | 5 |
| General release | v1.0 shipped | DevOps | 6 |

---

## Risk Register & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| **ONNX model accuracy** | High | High | Spike SETUP-005 early, validate on diverse hardware |
| **Blizzard ToS violation** | Medium | Critical | Consult legal, avoid persistent logging of gameplay |
| **Auto-update mechanism fails** | Low | High | Extensive testing RELEASE-002, fallback manual install |
| **Community moderation overhead** | Medium | Medium | Set expectations in beta (SLA for response), automate triage |
| **GPU availability on user hardware** | Low | Low | Graceful fallback to CPU, alpha-test on integrated GPU |

---

## Version Roadmap

### v1.0 (General Release, Week 18)
- Free, standalone app
- Queue detection + notifications
- Windows 10/11 only
- Community support model

### v1.1 (Post-Launch, Weeks 18â€“26)
- Bug fixes + stability improvements from v1.0 feedback
- Extended language support (if community demand)
- Crash reporting + telemetry dashboard

### v2.0 (Future, Weeks 26â€“52)
- Optional premium features ($2â€“5/month)
- Dashboard (analytics, detection history, trends)
- API for third-party integrations
- Mobile companion app (iOS/Android)

---

## Notes for PMs & Sprint Leads

1. **Sprint 0 is critical** â€” delays here cascade. Allocate 1 FTE who can work across backend/frontend.
2. **Spike tickets** â€” Use Sprint 0 BACKEND-005 to validate ONNX quantization and plan Sprint 1 exactly.
3. **Integration sprint (Sprint 3)** â€” Most defects surface here. Budget 2â€“3 days for unexpected coupling issues.
4. **Beta cohort selection** â€” Recruit 50â€“100 diverse users (casual, competitive, various hardware).
5. **Blizzard ToS review** â€” Engage legal by end of Sprint 1. Document compliance assumptions.

---

**Owner**: Product Manager  
**Stakeholders**: All roles, Community (feedback Sprint 5+)  
**Last Updated**: February 6, 2026
