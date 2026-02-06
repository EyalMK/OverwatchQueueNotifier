# Sprint Execution Workflow
## Overwatch AI Queue Detection & Notification App

**Version**: 1.0  
**Owner**: Product Manager, Scrum Master  
**Last Updated**: February 6, 2026

---

## 1. Sprint Cadence

**Duration**: 2 weeks (10 business days)  
**Velocity Target**: 25–30 story points  
**Ceremonies**:
- Sprint Planning: 2 hours (Monday 10:00 AM)
- Daily Standup: 15 minutes (9:30 AM)
- Sprint Review: 1 hour (Friday 4:00 PM)
- Sprint Retrospective: 1 hour (Friday 5:00 PM)

---

## 2. Definition of Ready (DoR)

Tickets must meet all criteria before sprint commitment:

- [ ] User story with clear acceptance criteria
- [ ] Acceptance criteria written from user POV ("As a...", "Given...", "Then...")
- [ ] Acceptance criteria testable (no ambiguity)
- [ ] Story points estimated by team (1, 2, 3, 5, 8)
- [ ] Identified dependencies (blocked by X, blocks Y)
- [ ] Technical spike completed (if required)
- [ ] Acceptance criteria no longer than 5 bullet points
- [ ] Database schema/API contract finalized (for backend)
- [ ] Mockup/wireframe attached (for frontend)

**Role**: Product Manager ensures DoR before sprint planning.

---

## 3. Definition of Done (DoD)

All tickets must pass these gates before marking "Done":

### Code Quality
- [ ] Code review approved (2 approvals minimum for risky changes)
- [ ] All unit tests pass (pytest, vitest)
- [ ] Test coverage ≥ 80% for new code
- [ ] Integration tests pass
- [ ] No linting errors (pylint, eslint)
- [ ] Type checking passes (mypy, tsc)
- [ ] Code formatted (black, prettier)

### Documentation
- [ ] Code comments explain *why*, not *what*
- [ ] Docstrings on public functions
- [ ] Architecture ADR updated (if design decision made)
- [ ] README updated (if setup changes)
- [ ] API contract finalized (for backend)

### Testing & QA
- [ ] Manual QA signed off (QA Lead)
- [ ] No open bugs blocking
- [ ] Performance targets met (latency <100ms p95)
- [ ] Edge cases tested
- [ ] Error cases handled gracefully

### Deployment
- [ ] Migrations applied (Alembic)
- [ ] Environment variables documented
- [ ] GitHub Actions CI passes
- [ ] Artifact builds (Docker, MSI)
- [ ] Rollback plan documented

**Role**: QA Lead enforces DoD before label assignment.

---

## 4. Ticket Workflow States

```
BACKLOG → READY → IN PROGRESS → REVIEW → DONE → SHIPPED
                     ↑                        ↓
                     └────── BLOCKED ────────┘
```

### State Definitions

| State | Meaning | Assigned | Notes |
|-------|---------|----------|-------|
| **BACKLOG** | Not yet ready | No | Waiting for grooming |
| **READY** | Meets DoR, prioritized | No | In current sprint |
| **IN PROGRESS** | Being worked | Yes (1 person) | Active development |
| **REVIEW** | PR open, awaiting approval | Yes | Code review phase |
| **BLOCKED** | Can't progress (depends on Y) | Yes | Linked to blocker |
| **DONE** | Passes DoD, merged to main | Yes | Awaiting release |
| **SHIPPED** | Deployed to production | Yes | In user's hands |

---

## 5. Sprint Planning (Monday 10:00 AM)

### Pre-Planning (Friday before)
- **PM**: Sort backlog by priority, mark top 20 as "Ready"
- **Tech Lead**: Identify blockers, dependencies, risks
- **QA Lead**: Review test coverage gaps

### Planning Meeting Flow

1. **Review Sprint Goal** (5 min)
   - PM states goal: "Complete AI perception layer with 85%+ accuracy"
   - Team aligns on definition of success

2. **Discuss Top Ticket** (10 min)
   - PM presents user story #142: "As a user, I want..."
   - Backend Lead asks clarifying questions
   - Team estimates effort (Fibonacci: 1, 2, 3, 5, 8, 13)

3. **Commit to Sprint** (5 min)
   - If team velocity allows, add ticket
   - Otherwise, defer to future sprint

4. **Repeat** for 25–30 story points
   - Aim for 10–12 tickets
   - Leave 20% buffer for incidents

5. **Identify Blockers** (10 min)
   - List external dependencies
   - Assign owner to unblock

### Planning Output
- **Sprint Backlog**: 10–12 committed tickets
- **Sprint Metrics**: Total points, estimated velocity
- **Risks**: Known unknowns, mitigation plans
- **Success Metrics**: How to measure "done"

---

## 6. Daily Standup (9:30 AM)

**Format**: 15-minute timebox, same room/Zoom

**Speaker Order**: Randomized (fairness)

**Speaker Template** (2 min max per person):
1. "Yesterday I **completed** X"
2. "Today I'm **working on** Y"
3. "I'm **blocked by** Z" (if any)

**Rule**: No technical deep-dives (defer to pairing session)

**Artifacts**:
- Track in GitHub Projects board
- Move tickets → IN PROGRESS when started
- Flag BLOCKED in real-time

**Anti-patterns**:
- ❌ Status report (should be in Jira/board)
- ❌ Design discussion (use separate meeting)
- ❌ Missing without notice (sync async if unavailable)

---

## 7. Code Review Process

### When to Request Review
- Push to feature branch, open draft PR
- Mark "Ready for Review" once tests pass
- Assign 2 reviewers (one senior, one peer)

### Reviewer Responsibilities

**Scope**:
- ✅ Logic correctness (does it solve the problem?)
- ✅ Test coverage (all paths tested?)
- ✅ Performance (acceptable? <100ms p95 for backend)
- ✅ Security (no exposed secrets, SQL injection?)
- ✅ Documentation (clear? docstrings present?)
- ✅ Style consistency (follows team conventions?)

**Not in scope**:
- ❌ Nitpicky formatting (use linters/formatters)
- ❌ Performance micro-optimizations (discuss post-merge)
- ❌ Refactorings outside this PR scope

### Approval Criteria
- ✅ All conversations resolved
- ✅ CI checks pass (linting, tests, type)
- ✅ At least 2 approvals
- ✅ No requested changes outstanding

### Timeline
- **Target**: Review within 4 hours
- **Escalation**: If >12 hours unreviewed, ping on Slack

---

## 8. Sprint Review (Friday 4:00 PM)

**Attendees**: Whole team + stakeholders (Product, leadership)

### Flow

1. **Demo Sprint Goal Achievement** (20 min)
   - Show working features
   - Live performance metrics (latency, CPU)
   - Walk through user journey

2. **Backlog Refinement Demo** (10 min)
   - Quick preview of next sprint backlog
   - Gather stakeholder feedback
   - Confirm priorities

3. **Q&A** (10 min)
   - Stakeholders ask questions
   - Document requests for future sprints

4. **Velocity Tracking** (5 min)
   - Completed points: X / Committed: Y
   - Trend (velocity increasing/stable/decreasing?)
   - Forecast for release: week X

### Meeting Artifacts
- **Sprint Metrics Board**: Velocity, burndown, bugs by severity
- **Demo Recording**: For absent stakeholders
- **Feedback Doc**: Feature requests, bugs found

---

## 9. Sprint Retrospective (Friday 5:00 PM)

**Goal**: Improve team processes, not blame.

### Format: "Went Well / Could Improve / Action Items"

**Went Well** (10 min)
- What did we do right?
- Celebrate wins
- Team morale boost

**Could Improve** (15 min)
- What slowed us down?
- Merge conflicts? Code review delays? Testing gaps?
- Be honest, non-blaming ("The code review SLA made us slower")

**Action Items** (15 min)
- Pick top 3 improvements
- Owner + deadline for each
- Example: "Code review SLA: Within 4 hours (by Dave, implement next sprint)"

### Post-Retro
- **PM**: Adjusts sprint planning ceremony based on feedback
- **Tech Lead**: Updates development practices doc
- **QA Lead**: Prioritizes test automation gaps

---

## 10. Ticket Template

```markdown
## Title
"As a [user role], I want [feature], so that [benefit]"
E.g. "As a streamer, I want queue notifications on Discord, so I don't miss matches"

## Acceptance Criteria
- [ ] Desktop notification shows within 100ms of queue detection
- [ ] User can disable notifications from Settings modal
- [ ] Notification includes queue confidence %
- [ ] No duplicate notifications within 5s window

## Technical Notes
- [ ] Use Strands Agents for notification coordination
- [ ] POST to Discord webhook asynchronously
- [ ] Add deduplication logic (see #98)

## Dependencies
- Blocks: #124 (requires notification infrastructure)
- Blocked by: #89 (Discord webhook config screen)

## Definition of Done Checklist
- [ ] Code review approved
- [ ] Unit tests pass (95%+ coverage)
- [ ] Integration tests pass
- [ ] Manual QA sign-off
- [ ] No performance regressions
- [ ] Updated API contract / Database schema
- [ ] GitHub Actions CI green
```

---

## 11. Release Planning

### Release Cadence
- **v0.1 Beta**: Week 9 (Sprint 3 → 4 end)
- **v1.0 General Release**: Week 18 (Sprint 6 end)
- **Patch releases** (v1.0.1, v1.0.2): As-needed for critical bugs

### Release Checklist
- [ ] All tests pass
- [ ] No critical bugs
- [ ] Release notes written
- [ ] MSI built & code-signed
- [ ] RELEASES manifest updated (for auto-updater)
- [ ] GitHub Release created
- [ ] Announcement tweet posted
- [ ] User guide updated

---

## 12. Metrics to Track

| Metric | Target | Cadence | Owner |
|--------|--------|---------|-------|
| **Velocity** | 25–30 pts | Sprint end | PM |
| **Burndown** | Linear | Daily | PM |
| **Test Coverage** | ≥80% | Daily (CI) | QA Lead |
| **Code Review Lead Time** | <4 hrs | Daily | Tech Lead |
| **Defect Escape Rate** | <5% | Sprint end | QA Lead |
| **Deployment Success** | 100% | Per release | DevOps |
| **Mean Time To Recovery** | <30 min | Per incident | DevOps |

---

## 13. Incident Response (During Sprint)

### P1 (Critical) Bug
- **Definition**: App crash, data loss, security breach
- **Response**: Stop sprint work, all-hands fix
- **Timeline**: Root cause + hotfix within 4 hours
- **Approval**: Product Manager + Tech Lead sign-off

### P2 (Major) Bug
- **Definition**: Feature broken, user blocked, <5% impact
- **Response**: 1 person investigates, sprint continues
- **Timeline**: Fix within 1 day
- **Approval**: QA Lead sign-off

### P3 (Minor) Bug
- **Definition**: Cosmetic, edge case, workaround exists
- **Response**: Log for future sprint
- **Timeline**: Backlog grooming

---

## 14. Example: Sprint 1 Schedule

```
Monday (Week 3)
├─ 10:00 AM: Sprint Planning (2 hrs)
├─ 12:30 PM: Developers start work
├─ 9:30 AM: Daily Standup (all days, 15 min)

Tuesday–Thursday (Weeks 3–4)
├─ Code development
├─ PR reviews (target <4 hrs)
├─ Testing by QA

Friday (Week 4)
├─ 4:00 PM: Sprint Review (1 hr)
├─ 5:00 PM: Sprint Retro (1 hr)
├─ Deploy "done" tickets to dev environment

Next Monday (Week 5)
├─ 10:00 AM: Sprint 2 Planning
```

---

**Owner**: Product Manager, Scrum Master  
**Last Updated**: February 6, 2026  
**Next Review**: End of Sprint 1
