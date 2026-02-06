# Multi-Agent Execution: Sprint Parallel Development
## Backend Agent + Frontend Agent Coordination

---

## Overview

This sprint uses **two agents working in parallel**:
- **Agent Backend**: Python services, API contracts, database, testing
- **Agent Frontend**: React components, state management, UI, integration

Both agents share a single `develop` branch with **integration checkpoint** on Day 5.

---

## Pre-Sprint Setup (Human: 30 mins)

### 1. Create Shared Backlog View

Create sprint board in backlog.md or Jira with columns:
```
TODO | BACKEND IN-PROGRESS | FRONTEND IN-PROGRESS | INTEGRATION | CODE REVIEW | DONE
```

Assign tickets:
- **Tickets N.1–N.7**: Backend priority (services, APIs, DB)
- **Tickets N.8–N.11**: Frontend priority (UI, state, components)
- **Tickets N.12–N.14**: Integration (IPC bridge, e2e tests, docs)

### 2. Establish Integration Rules

**Rule 1: API Contracts First**  
Before code: Backend defines API response schema (docs/api/reference.md format)

**Rule 2: Shared Fixtures**  
Test data in `backend/tests/fixtures/` + `frontend/tests/fixtures/`

**Rule 3: Git Workflow**  
```
main (production)
 ↑
develop (integration point)
 ↑
 +-- feat/backend-* (Agent Backend)
 +-- feat/frontend-* (Agent Frontend)
```

**Rule 4: Daily Sync (5 mins)**  
- 09:00: Backend agent posts progress + blockers
- 09:05: Frontend agent posts progress + blockers
- 09:10: Resolve dependencies (if frontend blocked on API)

**Rule 5: Integration Checkpoint (Day 5)**  
- Backend merge all PRs → develop
- Frontend merge all PRs → develop
- Run full e2e test suite (docs/testing/e2e-tests.md)
- If failures: debug together, create joint fix PR

---

## Backend Agent Instructions

### Daily Workflow (Days 1–7)

**Day 1–2: Core Services**
1. Pick tickets from N.1–N.3 (highest priority APIs)
2. For each ticket:
   - Write spec → TDD test → implement → merge
   - Post API response schema to shared docs
3. **Deliverable**: At end of Day 2, POST endpoints respond per specs/02_backend_lead.md (Section 4)

```python
# Example: Ticket N.1 (Gate Service API)
# backend/tests/unit/test_gate_service.py
def test_gate_triggers_above_threshold():
    gate = GateService(threshold=0.15)
    diff_percent = 0.18
    result = gate.evaluate(diff_percent)
    assert result["triggered"] == True
    assert result["confidence"] == 0.18
```

**Day 2–4: Data Layer**
1. Pick tickets N.4–N.5 (database + repositories)
2. Each ticket:
   - Create migration (docs/architecture/database.md)
   - Write repository tests
   - Verify end-to-end with sample data
3. **Deliverable**: `python backend/src/db/migrations.py` runs all migrations successfully

**Day 4–6: Advanced Features**
1. Pick tickets N.6–N.7 (notification, error handling)
2. Implement per error-handling patterns (docs/architecture/backend.md)
3. Add rate limiting (docs/api/reference.md—status 429)
4. **Deliverable**: All 4 API endpoints return error codes per spec

**Day 5: Integration Checkpoint**
1. Merge all PRs to develop
2. Run integration tests: `pytest backend/tests/integration/`
3. Check frontend can connect: Test frontend POST to backend endpoints
4. If failures: Create `fix/integration-*` branch, debug with frontend agent

**Day 6–7: Polish + Testing**
1. Review coverage: `pytest --cov backend/src/ --cov-report html`
2. Must be >75%
3. Run security checks: `bandit -r backend/src/`
4. Final merge to develop + tag

### Backend Success Criteria

- ✓ All API endpoints from specs/02_backend_lead.md (Section 4) working
- ✓ Database migrations run cleanly
- ✓ Test coverage >75%
- ✓ No SQL injection (audit all queries)
- ✓ Error codes match docs/api/reference.md
- ✓ Line 1 of each service documents dependencies (e.g., "Depends on GateService, ScreenCapture")

---

## Frontend Agent Instructions

### Daily Workflow (Days 1–7)

**Day 1–2: Component Foundation**
1. Pick tickets N.8–N.9 (atomic components, Zustand store)
2. For each ticket:
   - Create component template per specs/10_ui_designer.md
   - TDD: test state + renders
   - Implement with design tokens (docs/ui-design-system/tokens.md)
3. **Deliverable**: `npm test` all pass, Zustand store accessible in DevTools

```typescript
// Example: Ticket N.8 (StateDisplay component)
// frontend/tests/unit/StateDisplay.test.tsx
import { render, screen } from '@testing-library/react';
import { StateDisplay } from '@/components/StateDisplay';

it('renders MATCH_FOUND state in red', () => {
  render(<StateDisplay state="MATCH_FOUND" confidence={0.92} />);
  expect(screen.getByText(/MATCH FOUND/i)).toHaveClass('bg-red-600');
});
```

**Day 2–4: Page Layouts**
1. Pick tickets N.10–N.11 (main window, settings modal)
2. Each ticket:
   - Build page per specs/03_frontend_lead.md
   - Connect to Zustand store
   - Test responsive design (mobile, tablet, 4K)
   - Accessibility audit (WCAG 2.1 AA)
3. **Deliverable**: Pages render without errors, connect to mock backend

**Day 4–6: Integration Setup**
1. Pick integration tickets N.12 (IPC bridge setup in frontend)
2. Implement IPC client: `window.api.callBackend(method, params)`
3. Connect StateDisplay to live backend (after Day 5 checkpoint)
4. Write super basic e2e: Click button → backend responds → state updates

**Day 5: Integration Checkpoint**
1. Merge all PRs to develop
2. Start Electron app: `npm run dev`
3. Verify IPC works: Click notifier button → backend receives call
4. If failures: Create `fix/integration-*` branch, debug with backend agent
5. Record any backend API changes needed (feedback loop)

**Day 6–7: Polish + Testing**
1. Review coverage: `npm test -- --coverage`
2. Must be >75%
3. Run a11y checks: `npm run a11y`
4. Final merge to develop

### Frontend Success Criteria

- ✓ All UI components from specs/10_ui_designer.md implemented
- ✓ Zustand store fully typed + persisted
- ✓ Test coverage >75%
- ✓ Responsive design (Windows 10 800×600 → 4K)
- ✓ Accessibility: no color-only indicators, focus visible, screen-reader friendly
- ✓ IPC communication working (verified Day 5)

---

## Shared Integration Tests (Day 5–7)

Create integration test that exercises **both** agents:

```python
# backend/tests/integration/test_ipc_e2e.py
import json
import subprocess
import time

def test_frontend_detects_match_and_displays():
    """E2E: Screen → Backend → Frontend (full loop)"""
    
    # 1. Start backend MCP server
    backend_proc = subprocess.Popen(['python', 'backend/src/main.py'])
    time.sleep(2)  # Wait for startup
    
    # 2. Call perceive endpoint (simulating frontend request)
    import requests
    response = requests.post(
        'http://127.0.0.1:5000/screen/perceive_state',
        json={"resolution": [2560, 1440]}
    )
    
    # 3. Verify response schema matches spec
    data = response.json()
    assert 'state' in data
    assert 'confidence' in data
    assert data['state'] in ['QUEUE', 'LOADING', 'MATCH_FOUND', 'IN_GAME']
    
    # 4. Stop backend
    backend_proc.terminate()
```

Run before final merge:
```bash
cd backend && pytest tests/integration/test_ipc_e2e.py -v
```

---

## Daily Standup Format (Async, Posted to Shared Doc)

### Backend Agent (09:00)
```
✓ Completed: N.1 (Gate Service), N.2 (Screen Capture)
⏳ In Progress: N.3 (Classifier Service)
⚠ Blocked by: None
🚨 Issues: Classifier inference taking 250ms, need to profile
📦 API Ready: /perceive_state, /capture_regions
```

### Frontend Agent (09:05)
```
✓ Completed: N.8 (Zustand store), N.9 (StateDisplay component)
⏳ In Progress: N.10 (Settings Modal)
⚠ Waiting on: Backend API schema for /perceive_state (needed for types)
🎨 UI Status: 2/6 screens done, 4 pending
```

### Resolution (09:10)
If Frontend blocked: Backend posts API schema immediately (can be WIP, just needs types)

---

## Version Control: Merge Strategy

### Before Day 5 Integration Checkpoint

Both agents work independently on feature branches:
```
develop
 ├── feat/backend-gate (Backend only)
 ├── feat/backend-classifier (Backend only)
 └── feat/frontend-ui (Frontend only)
```

### Day 5: Merge to Develop

```bash
# Backend agent
git checkout develop && git pull
git merge feat/backend-gate && git merge feat/backend-classifier
git push origin develop

# Frontend agent
git checkout develop && git pull
git merge feat/frontend-ui
git push origin develop

# Run integration tests before proceeding
pytest backend/tests/integration/ -v
npm run e2e
```

### Day 7: Merge Develop → Main (Release Branch)

```bash
git checkout main && git pull
git merge develop
git tag -a v1.X.0 -m "Release: Sprint N complete"
git push origin main --tags
```

---

## Communication Rules

1. **No direct commits to develop** (always via PR + review)
2. **All PRs reference spec + backlog ticket** (e.g., "feat(backend): Implements N.3, specs/02_backend_lead.md Section 5")
3. **Post API changes to shared document** before merging (so frontend doesn't break types)
4. **If merge conflict**: Both agents discuss resolution synchronously (5-min call), not async
5. **Blockers escalated immediately** (don't wait for next standup)

---

## Failure Recovery

### If Backend API Delayed (Day 4)

**Frontend Action**: Build mock API server that matches expected schema (docs/api/reference.md). Use mock until real API ready.

```typescript
// frontend/src/mocks/msw.ts
import { rest } from 'msw';

export const handlers = [
  rest.post('http://127.0.0.1:5000/screen/perceive_state', (req, res, ctx) => {
    return res(ctx.json({
      state: 'MATCH_FOUND',
      confidence: 0.92,
      timestamp: Date.now(),
    }));
  }),
];
```

### If Frontend UI Blocked (Day 3)

**Backend Action**: Continue with API tests using curl (no dependency on frontend).

```bash
curl -X POST http://127.0.0.1:5000/screen/perceive_state \
  -H "Content-Type: application/json" \
  -d '{"resolution": [2560, 1440]}'
```

### If Integration Tests Fail (Day 5)

Both agents:
1. Run tests locally: identify root cause (schema mismatch, IPC error, race condition)
2. Create `fix/integration-error` branch
3. Fix together (pairing session if complex)
4. Merge back to develop

---

## Success Criteria (Day 7)

- ✓ All backend API endpoints working + >75% coverage
- ✓ All frontend components rendering + >75% coverage
- ✓ Integration test passing (backend + frontend together)
- ✓ Both agents merged to develop
- ✓ Zero blockers outstanding
- ✓ Ready for release/next sprint

---

## Metrics to Track

| Metric | Target |
|--------|--------|
| Parallel ticket rate | 80%+ (min cross-team blocking) |
| Integration issues | <2 bugs found at checkpoint |
| Cycle time (average) | 3 days/ticket |
| Test coverage | >75% per team |
| Merge conflicts | <3 total |

---

**Note**: After Sprint 0 is complete, this becomes the standard format for all sprints. Adjust ticket assignments per sprint backlog priorities.
