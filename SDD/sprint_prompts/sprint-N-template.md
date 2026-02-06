# Sprint N: Feature Sprint Template
## Overwatch AI Queue Detection & Notification App

---

## Context — Read These Files First (Same as Sprint 0)

READ: specs/01–06, 10 | specs/backlog.md | docs/architecture/* | docs/workflows/* | docs/api/* | docs/testing/*

---

## Phase Breakdown: Implementation → Integration → Testing

### Feature Sprint Workflow (5-7 days)

**Day 1**: Pick tickets from Sprint N in backlog.md. Review corresponding spec sections.

**Days 2–6**: For each ticket, follow [docs/workflows/development.md](../../docs/workflows/development.md):
1. Write tests (TDD: red-green-refactor)
2. Implement feature
3. Integration test
4. Code review (2 approvals)
5. Merge to develop

**Day 7**: Sprint review + retro.

---

## Ticket Categories & Patterns

### Backend Ticket Pattern

```
Ticket: N.X Backend Feature

1. Read spec requirement from specs/02_backend_lead.md
2. TDD: Write failing test in backend/tests/unit/test_*.py
3. Implement in backend/src/<service>/<module>.py
4. Integration test: backend/tests/integration/test_*.py
5. Commit: feat(backend): <description> (N.X)
6. PR reviewer checks:
   - Code follows patterns from docs/architecture/backend.md
   - Error handling per specs/02_backend_lead.md (Section 4)
   - Test coverage >75%
   - No SQL injection (parameterized queries only)
```

### Frontend Ticket Pattern

```
Ticket: N.Y Frontend Feature

1. Read spec requirement from specs/03_frontend_lead.md
2. TDD: Write failing test in frontend/tests/unit/<Component>.test.tsx
3. Implement component in frontend/src/components/ or frontend/src/pages/
4. Update Zustand store if global state needed
5. E2E test: frontend/tests/e2e/<Flow>.spec.ts
6. Commit: feat(frontend): <description> (N.Y)
7. PR reviewer checks:
   - Component follows patterns from docs/architecture/frontend.md
   - Responsive design per specs/10_ui_designer.md
   - Accessibility (WCAG 2.1 AA)
   - Design tokens from docs/ui-design-system/tokens.md
   - Test coverage >75%
```

### Database Ticket Pattern

```
Ticket: N.Z Database Change

1. Review current schema in docs/architecture/database.md
2. Create migration: backend/src/db/migrations/YYYYMMDDHHMMSS_description.sql
3. Test migration: python backend/src/db/migrations.py
4. Update repository layer: backend/src/state/repository.py
5. Write tests: backend/tests/integration/test_db_*.py
6. Commit: feat(db): <migration description> (N.Z)
```

---

## Definition of Done (Per Ticket)

✓ Feature implements spec requirement exactly  
✓ Tests pass (unit + integration + e2e per ticket type)  
✓ Coverage >75% (required for merge)  
✓ Lint + typcheck pass  
✓ Code reviewed + 2 approvals  
✓ Merged to develop  
✓ backlog.md updated: status→"done"

---

## Daily Standup Format

```
✓ Yesterday:  Tickets 2.1, 2.2 → done
⏳ Today:    Ticket 2.3 (in-progress)
⚠ Blocked:   Missing test fixtures for resolution 3440×1440
```

---

## Sprint Review (Day 7)

Demo each completed ticket:
- **Backend**: Show API response, explain error handling
- **Frontend**: Walk through UI, show state changes
- **QA**: Report coverage %, list any failing tests

---

## Retro Questions

- What went well?
- What slowed us down?
- What will we improve next sprint?

---

## Metrics to Track

| Metric | Target | Notes |
|--------|--------|-------|
| Velocity (story points done) | 30–35 | Gradually increase toward healthy sprint |
| Cycle time (days per ticket) | 2–4 | Measure from "todo" → "done" |
| Test coverage | >75% | Required for merge |
| Bug escape rate | <2 bugs per sprint | Caught after merge |

---

## Common Commands (Every Commit)

```bash
# Backend
cd backend
pytest tests/ -v
black src/ && pylint src/ && mypy src/

# Frontend
cd frontend
npm run typecheck && npm run lint && npm test

# Both
git checkout -b feat/N.X-description
# ... implement ...
git commit -m "feat(scope): description (N.X)"
git push origin feat/N.X-description
# Create PR on GitHub
```

---

## Anti-Patterns to Avoid

❌ Tickets > 5 story points (split into smaller tasks)  
❌ Code without tests  
❌ PRs without spec reference  
❌ Merging with <75% coverage  
❌ Skipping integration tests (only unit tests)  
❌ Hardcoded values (use env vars + config)

---

## If Ticket Gets Blocked

1. Log in Jira/backlog with clear description
2. Identify dependency (e.g., "Waiting for backend API")
3. Estimate recovery (days)
4. Move to next unblocked ticket
5. Return when dependency ready

---

## Release Preparation (If Sprint Completes Features for Release)

After all Sprint N tickets → "done":

```bash
git checkout release/v1.X.0
# Update version: package.json + pyproject.toml
# Update CHANGELOG.md
git commit -m "chore: v1.X.0 release prep"
git checkout main
git merge release/v1.X.0
git tag -a v1.X.0 -m "Release v1.X.0: <features>"
git push origin main --tags
# GitHub Actions: Build MSI, upload to Releases
```

---

## Summary

Each feature sprint:
1. Picks 6–8 tickets (25–35 story points)
2. Executes per TDD + integration patterns
3. Maintains >75% test coverage
4. Reviews & celebrates completion
5. Iterates toward perfect sprint

**The only difference from Sprint 0: Focus on features, not infrastructure.**
