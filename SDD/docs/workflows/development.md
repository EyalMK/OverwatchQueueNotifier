# Feature Development Workflow
## Overwatch AI Queue Detection & Notification App

**Generated**: February 6, 2026  
**Version**: 1.0

---

## Development Workflow: Ticket → Done

This document describes the step-by-step process for taking a backlog ticket from "todo" → "in-progress" → "done".

---

## Step 1: Pick a Ticket from Backlog

1. Open [specs/backlog.md](../specs/backlog.md)
2. Find the current sprint (e.g., "Sprint 1: Core Perception Pipeline")
3. Select a ticket with status "todo"
   - **Example**: `1.2 | Implement Gate Logic | 3 points | Backend`
4. Update status in backlog.md: `todo` → `in-progress`
5. Create a feature branch: `git checkout -b feat/1.2-gate-logic`

---

## Step 2: Understand Requirements

Read the relevant specification:

**Backend ticket?**
→ Read [specs/02_backend_lead.md](../specs/02_backend_lead.md) + [docs/architecture/backend.md](docs/architecture/backend.md)

**Frontend ticket?**
→ Read [specs/03_frontend_lead.md](../specs/03_frontend_lead.md) + [docs/architecture/frontend.md](docs/architecture/frontend.md)

**Database ticket?**
→ Read [specs/04_db_architect.md](../specs/04_db_architect.md) + [docs/architecture/database.md](docs/architecture/database.md)

**Example**: For ticket `1.2 (Gate Logic)`:
- Gate must detect pixel diff >15% (spec section 3.2, requirement DR-3)
- Must use histogram analysis (Bhattacharyya divergence)
- Must be configurable via environment variables
- Must log heuristic signals for debugging

---

## Step 3: Write Tests (TDD)

**Backend**: pytest

```python
# backend/tests/unit/test_gate.py
# (New or existing test file)

def test_gate_triggers_at_15_percent_pixel_diff():
    """Gate activates when pixel diff exceeds 15%"""
    gate = GateService()
    
    prev_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
    curr_frame = prev_frame.copy()
    curr_frame[:, :] = 40  # ~15.7% change
    
    assert gate.should_process(prev_frame, curr_frame) == True

def test_gate_ignores_small_changes():
    """Gate does not trigger for <5% changes"""
    gate = GateService()
    
    prev_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
    curr_frame = prev_frame.copy()
    curr_frame[0:10, 0:10] = 200  # <0.05% change
    
    assert gate.should_process(prev_frame, curr_frame) == False
```

**Frontend**: vitest + React Testing Library

```typescript
// frontend/src/components/__tests__/StateDisplay.test.tsx
import { render, screen } from '@testing-library/react';
import { StateDisplay } from '../StateDisplay';

describe('StateDisplay', () => {
  it('renders state badge with correct color for MATCH_FOUND', () => {
    render(<StateDisplay state="MATCH_FOUND" confidence={0.94} />);
    
    const badge = screen.getByText('MATCH_FOUND');
    expect(badge).toHaveClass('bg-emerald-500');  // Success color
  });
  
  it('displays confidence as percentage', () => {
    render(<StateDisplay state="QUEUE" confidence={0.87} />);
    
    expect(screen.getByText('87%')).toBeInTheDocument();
  });
});
```

**Run tests**:
```bash
# Backend
cd backend && pytest tests/ -v

# Frontend
cd frontend && npm run test
```

**Goal**: Tests should fail (red); you'll make them pass with implementation.

---

## Step 4: Implement the Feature

### Backend Example: Gate Logic

**File**: `backend/src/perception/gate.py`

```python
import numpy as np
from dataclasses import dataclass
from typing import Optional

@dataclass
class GateSignals:
    pixel_diff_pct: float
    histogram_divergence: float
    should_process: bool

class GateService:
    def __init__(self, config: Config):
        self.pixel_diff_threshold = config.GATE_PIXEL_DIFF_THRESHOLD  # 15.0
        self.histogram_threshold = config.GATE_HISTOGRAM_THRESHOLD    # 0.3
    
    def should_process(self, prev_frame: np.ndarray, curr_frame: np.ndarray) -> bool:
        """Determine if AI inference should run based on heuristics"""
        
        # Check pixel difference
        pixel_diff_pct = self._calculate_pixel_diff(prev_frame, curr_frame)
        if pixel_diff_pct < self.pixel_diff_threshold:
            return False
        
        # Check histogram divergence (if pixel diff triggered)
        hist_div = self._calculate_histogram_divergence(prev_frame, curr_frame)
        if hist_div < self.histogram_threshold:
            return False
        
        return True
    
    def _calculate_pixel_diff(self, prev: np.ndarray, curr: np.ndarray) -> float:
        """Calculate pixel difference percentage"""
        diff = np.abs(prev.astype(float) - curr.astype(float))
        changed_pixels = np.sum(diff > 10)  # Threshold: 10/255
        total_pixels = prev.size
        return (changed_pixels / total_pixels) * 100.0
    
    def _calculate_histogram_divergence(self, prev: np.ndarray, curr: np.ndarray) -> float:
        """Bhattacharyya divergence between histograms"""
        hist_prev = cv2.calcHist([prev], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        hist_curr = cv2.calcHist([curr], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        
        hist_prev = cv2.normalize(hist_prev, hist_prev).flatten()
        hist_curr = cv2.normalize(hist_curr, hist_curr).flatten()
        
        return cv2.compareHist(hist_prev, hist_curr, cv2.HISTCMP_BHATTACHARYYA)
```

### Frontend Example: State Display Component

**File**: `frontend/src/components/StateDisplay.tsx`

```typescript
import React from 'react';
import { GameState } from '../types/game';
import { getStateIcon, getStateColor } from '../lib/gameStateUtils';

interface StateDisplayProps {
  state: GameState;
  confidence: number;
}

export const StateDisplay: React.FC<StateDisplayProps> = ({ state, confidence }) => {
  const Icon = getStateIcon(state);
  const bgColor = getStateColor(state);
  
  return (
    <div className="state-display">
      <div className={`state-badge ${bgColor}`}>
        <Icon size={24} />
        <span className="state-label">{state}</span>
      </div>
      
      <div className="confidence-section">
        <span className="confidence-label">Confidence: {Math.round(confidence * 100)}%</span>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${confidence * 100}%` }} />
        </div>
      </div>
    </div>
  );
};
```

---

## Step 5: Run Tests & Verify

```bash
# Backend: Run unit + integration tests
cd backend
pytest tests/unit/test_gate.py -v
pytest tests/integration/ -v
pytest --cov=src --cov-report=term-color tests/

# Frontend: Run component tests
cd frontend
npm run test -- StateDisplay.test.tsx
npm run test:coverage
```

**Exit criteria**:
- ✓ All unit tests pass
- ✓ Coverage >75% for critical paths
- ✓ No TypeScript errors (`npm run typecheck`)
- ✓ No linter errors (`npm run lint`)

---

## Step 6: Integration Testing

**Backend**: Test the service in isolation first; then with other services.

```python
# backend/tests/integration/test_perception_pipeline.py
def test_perception_pipeline_detects_match_found():
    """Full pipeline: capture → gate → classifier → detection"""
    
    # Setup
    perception = PerceptionService(config)
    sample_frame = load_test_image("tests/fixtures/match_found_1920x1080.png")
    
    # Execute
    detection = perception.detect(sample_frame)
    
    # Verify
    assert detection.state == GameState.MATCH_FOUND
    assert detection.confidence > 0.90
    assert detection.timestamp is not None
```

**Frontend**: Test component in context with store.

```typescript
// frontend/tests/integration/tray-window.test.tsx
import { fireEvent, screen, waitFor } from '@testing-library/react';
import { TrayWindow } from '../pages/TrayWindow';
import { useGameStore } from '../store/gameStore';

it('displays updated state when store changes', async () => {
  render(<TrayWindow />);
  
  // Simulate backend update
  act(() => {
    useGameStore.setState({
      currentState: GameState.MATCH_FOUND,
      currentConfidence: 0.94,
    });
  });
  
  await waitFor(() => {
    expect(screen.getByText('MATCH_FOUND')).toBeInTheDocument();
    expect(screen.getByText('94%')).toBeInTheDocument();
  });
});
```

---

## Step 7: Code Review Checklist

Before committing, verify:

- [ ] **Spec compliance**: Implementation matches spec requirements
- [ ] **Test coverage**: >75% line coverage + critical paths
- [ ] **TypeScript**: `npm run typecheck` succeeds
- [ ] **Linting**: `npm run lint` / `black .` succeeds
- [ ] **Git history**: Commit messages follow convention (`feat(backend): implement gate logic`)
- [ ] **Documentation**: Added inline comments for complex logic
- [ ] **No hardcoded values**: All thresholds in config or env vars
- [ ] **Error handling**: Exceptions caught and logged

---

## Step 8: Commit & Push

```bash
git add backend/src/perception/gate.py backend/tests/unit/test_gate.py
git commit -m "feat(backend): implement gate logic service

- Calculate pixel diff % and histogram divergence
- Heuristic gate determines when to run AI inference
- Configurable thresholds via environment variables
- Closes #1.2"

git push origin feat/1.2-gate-logic
```

**Commit format**: `<type>(<scope>): <subject>`
- `type`: feat, fix, test, docs, refactor, chore
- `scope`: backend, frontend, db, devops
- `subject`: imperative verb, lowercase, no period

---

## Step 9: Create Pull Request

1. Go to GitHub → Create Pull Request
2. **Title**: "Gate Logic Service Implementation (1.2)" 
3. **Description**:
   ```
   ## Ticket
   Closes #1.2: Implement Gate Logic
   
   ## Changes
   - Added `GateService` with pixel diff + histogram detection
   - Tests for heuristic logic (pixel diff >15%, histogram divergence)
   - Integrated with `PerceptionService` pipeline
   
   ## Testing
   - Unit tests: 5 new tests, all passing
   - Integration: Full perception pipeline tested
   - Coverage: 88% in gate.py
   
   ## Spec Compliance
   - Implements design requirement DR-3 (heuristic gate)
   - <5ms latency target achieved
   - Configurable thresholds per environment
   ```

4. **Request review** from team leads
5. **Wait for approval** before merging

---

## Step 10: Merge & Update Backlog

Once PR is approved:

```bash
git checkout develop
git pull origin develop
git merge --ff-only feat/1.2-gate-logic
git push origin develop
```

**Update backlog**:
1. Open [specs/backlog.md](../specs/backlog.md)
2. Find ticket `1.2`
3. Update status: `in-progress` → `done`
4. Add notes: `Merged PR #123 on 2026-02-06`

---

## Definition of Done

✓ Code merged to `develop`  
✓ Tests passing (unit + integration)  
✓ Coverage >75%  
✓ No lint/type errors  
✓ Spec requirements met  
✓ Peer-reviewed & approved  
✓ Jira/Backlog updated to "done"  
✓ Release notes prepared (if release-ready)

---

## Common Pitfalls

1. **Writing tests after code**: Red-green-refactor order helps catch bugs early
2. **Hardcoding thresholds**: Use env vars + config; enables runtime tuning
3. **No error logging**: Always log errors with context; critical for debugging
4. **Skipping integration tests**: Unit tests can pass, but integration can fail
5. **Merge conflicts**: Rebase frequently to avoid large conflicts

---

## Summary

Each feature develops through:
1. Ticket selection + branch creation
2. Spec review (understand requirements)
3. TDD (write failing tests)
4. Implementation (make tests pass)
5. Integration testing (full pipeline)
6. Code review (peer approval)
7. Merge to develop
8. Backlog update

**This workflow ensures quality, maintainability, and spec compliance.**
