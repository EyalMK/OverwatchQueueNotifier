# Sprint Execution Workflow
## Overwatch AI Queue Detection & Notification App

**Generated**: February 6, 2026  
**Version**: 1.0

---

## How to Execute a Sprint (Single Agent or Multi-Agent)

This document describes the complete process for running a sprint, from planning to review.

---

## Pre-Sprint (Day 1)

### 1. Review Sprint Goal
- Open [specs/backlog.md](../specs/backlog.md)
- Read the sprint goal (e.g., "Sprint 1: Core Perception Pipeline")
- Understand the business value

### 2. Assign Tickets
- Identify "todo" tickets in the sprint
- Assign to team member or agent based on skills
  - Backend specialist: Backend / Database tickets
  - Frontend specialist: Frontend / UI tickets
  - DevOps specialist: Deployment / Infrastructure tickets

### 3. Start Sprint Meeting (5 min)
- Recap goal
- Identify blockers or dependencies
- Confirm capacity (total story points vs sprint velocity)

---

## During Sprint (Days 2–7)

### Daily Standup (5 min)
Each person/agent reports:
1. **Completed yesterday**: Which tickets moved to "done"
2. **Today's focus**: Which tickets in progress
3. **Blockers**: Any issues blocking progress

**Example**:
```
Agent A (Backend):
  ✓ Done: 1.1 (Screen Capture), 1.2 (Gate Logic)
  ⏳ In Progress: 1.3 (Classifier)
  ⚠ Blocked: Awaiting test image fixtures
```

### Development Process
- Follow [development.md](development.md) for each ticket
- Pick ticket → write tests → implement → merge → update backlog
- Aim for 2–3 tickets per day (8–10 story points)

### Daily Commit
- Push changes to `develop` branch
- Update backlog.md with latest status
- Commit: `chore(backlog): update sprint status - day X`

---

## End-of-Sprint (Day 7)

### Sprint Review (30 min)

**Goal**: Demonstrate completed work

1. **Backend Lead**: Demo API endpoints
   - Run MCP tools (screen.perceive_state, notify.*)
   - Show database schema + queries
   - Explain error handling + retry logic

2. **Frontend Lead**: Demo UI
   - Show tray window + settings modal
   - Walk through calibration wizard
   - Show performance metrics

3. **QA Lead**: Report test coverage
   - Coverage % (target: 75%+)
   - Critical path tests (100% coverage)
   - Any known failures

### Sprint Retro (15 min)

**What went well?**
- Fast iteration
- Good test coverage
- Team communication

**What could be better?**
- Need more fixtures (mock images)
- Discord API docs were unclear
- Should distribute tasks earlier

**Actions for next sprint**:
- [ ] Create more test fixtures early
- [ ] Document Discord integration better
- [ ] Parallel assign tickets on day 1

---

## Multi-Agent Execution

If running with **two parallel agents** (Backend A + Frontend B):

### Shared Resources
- Single `develop` branch (both merge PRs daily)
- Shared backlog.md (atomic updates)
- Shared test fixtures in `tests/fixtures/`

### Integration Checkpoint (Day 5)

Both agents pause to integrate:

1. **Agent A (Backend)** pushes latest API
2. **Agent B (Frontend)** pulls + tests against API
3. **Resolve any mismatches**
4. **Both resume** with integration confidence

### Merge Strategy
- Rebase on `develop` (linear history)
- No merge commits on feature branches
- Squash small commits (< 3 commits per ticket)

---

## Post-Sprint

### Update Specs & Docs
- Mark completed tickets as "done" in backlog.md
- Update any spec documentation (if requirements evolved)
- Update architecture docs if design changed

### Release Candidate (Optional)
- If sprint completes features for v1.0, prepare release
- Tag commit: `git tag -a v1.0.0 -m "Release v1.0.0"`
- Build and sign MSI installer

### Start Next Sprint
- Plan next sprint goal
- Estimate unfinished tickets
- Identify new blockers for next iteration

---

## Sprint Velocit Tracking

Use this table to measure team speed:

| Sprint | Points Planned | Points Done | Velocity | Notes |
|--------|---|---|---|---|
| 0 | 20 | 18 | 90% | One blocker (AI model training) |
| 1 | 30 | 28 | 93% | Good parallelization |
| 2 | 32 | 32 | 100% | Team synchronized well |

**Healthy velocity**: 80–100% of planned points

---

## Sprint Metrics

At end of each sprint, capture:

- **Burndown**: Points completed per day (should trend toward 0)
- **Cycle time**: Average days from "todo" → "done"
- **Defect rate**: Bugs found during sprint
- **Test coverage**: % of code with tests

**Example**:
```
Sprint 1 Metrics:
├─ Burndown: Started 30pts → 2pts remaining (93% done)
├─ Cycle time: 3.2 days avg (target: 2–4 days)
├─ Defects found: 2 (both fixed)
├─ Test coverage: 87% (above target 75%)
└─ Recommendation: Increase sprint size to 35pts next time
```

---

## Summary

A sprint is **1 week** of focused development:
- **Plan** (day 1): Review goal, assign tickets
- **Execute** (days 2–7): Daily standups, implement tickets, merge to develop
- **Review** (day 7): Demo work, celebrate completion, identify improvements
- **Iterate**: Apply learnings to next sprint

Each sprint produces **production-ready code** that's tested, documented, and integrated.
