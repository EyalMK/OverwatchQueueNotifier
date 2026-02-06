# Sprint Execution Workflow
## Overwatch AI Queue Detection & Notification App

**Version**: 1.0  
**Owner**: Product Manager, Scrum Master  
**Last Updated**: February 6, 2026  
**Purpose**: Define repeatable sprint cadence and decision gates for quality delivery

---

## 1. Sprint Cadence (2-Week Sprints)

```
Week 1 (Monday–Friday)
├─ Monday 9:00 AM: Sprint Planning (2 hours)
│  ├─ Review backlog priorities
│  ├─ Estimate story points
│  ├─ Commit to sprint goal
│  └─ Assign DRI (Directly Responsible Individual) per ticket
│
├─ Tuesday–Thursday: Development
│  ├─ Daily standup 10:00 AM (15 min)
│  │  ├─ What did I complete?
│  │  ├─ What am I working on?
│  │  └─ Any blockers?
│  │
│  └─ Continuous Integration
│     ├─ All code pushed to feature branch
│     ├─ GitHub Actions runs (lint, type-check, test)
│     └─ Merge to main after approval
│
└─ Friday 2:00 PM: Code Review Sync (1 hour)
   ├─ Review outstanding PRs
   ├─ Discuss blockers
   └─ Plan Sprint 2

Week 2 (Monday–Friday)
├─ Monday–Thursday: Continued Development
│  ├─ Daily standup
│  └─ Complete remaining tickets
│
├─ Thursday 5:00 PM: Sprint Testing & QA Prep
│  ├─ All tickets moved to "Ready for QA"
│  ├─ QA team runs full test suite
│  └─ File bugs, assign severity
│
└─ Friday 3:00 PM: Sprint Review & Retrospective (2 hours)
   ├─ Demo completed work to stakeholders
   ├─ Discuss what went well / what to improve
   ├─ Update metrics (velocity, test coverage)
   └─ Plan next sprint

(Cycle repeats)
```

---

## 2. Ticket Workflow & States

```
Backlog (Priority Queue)
│
├─ Ready for Development
│  └─ Meets Definition of Ready (DOR)
│
├─ In Progress
│  └─ DRI working, branch created, linked to PR
│
├─ Code Review
│  └─ PR submitted, awaiting approval
│
├─ Ready for QA
│  └─ Code merged to main, QA assigned
│
├─ QA In Progress
│  └─ QA testing, may discover bugs
│
├─ QA Done / Ready to Release
│  └─ QA approved, signed off
│
└─ Done / Released
   └─ Deployed or included in release

At any point: BLOCKED (external dependency, spike) or CLOSED (won't implement)
```

---

## 3. Definition of Ready (DOR)

A ticket is ready to be picked up if it meets ALL criteria:

- [ ] **Description**: Clear, non-ambiguous
  - What needs to be done?
  - Why? (customer value, technical debt, etc.)
- [ ] **Acceptance Criteria**: Specific, testable
  - Example: "Classifier inference latency <40ms p95 on 1920×1080 screenshot"
  - Not: "Make classifier fast"
- [ ] **Story Points**: Estimated (1–13 scale)
  - If >8 points, break into smaller tickets
- [ ] **Dependencies**: Listed
  - What other tickets must be done first?
- [ ] **Owner Assigned**: DRI named
  - Frontend Lead: "Jane"
  - Backend Lead: "Bob"
- [ ] **Related Specs/Docs**: Linked
  - Link to relevant spec (e.g., "02_backend_lead.md")
  - Link to related tickets
- [ ] **Environment/Secrets Needed**: Listed
  - Example: "Discord webhook URL for testing"

---

## 4. Definition of Done (DoD)

A ticket is "Done" when ALL criteria met:

- [ ] **Code Complete**
  - Feature implemented per acceptance criteria
  - No hardcoded tokens or secrets
  - No console.log / print statements (use structured logging)
- [ ] **Unit Tests**: ≥75% of feature code covered
  - Feature code: tests for happy path + edge cases
  - Test file: `test_<feature>.py` or `<feature>.test.ts`
  - Run locally: `pytest` or `npm test` passes
- [ ] **Type Safety**: All types defined
  - Python: mypy passes (`mypy src/`)
  - TypeScript: `tsc --noEmit` passes
- [ ] **Code Review**: ≥1 approval
  - PR linked to ticket
  - Comments addressed
  - Approved by codeowner
- [ ] **Documentation**: Docstrings + inline comments where needed
  - Functions: Docstring with input/output types
  - Complex logic: Inline comments explaining "why"
- [ ] **Performance**: Within budget (if applicable)
  - Feature latency <100ms (backend)
  - Bundle size impact <50KB (frontend)
  - Memory leak test passing (hold reference, check gc)
- [ ] **Accessibility**: WCAG 2.1 AA (UI features only)
  - Color contrast ≥4.5:1
  - Keyboard navigable
  - Screen reader friendly (aria-labels)
- [ ] **CI/CD Green**: All checks pass
  - Lint (eslint, pylint)
  - Type-check
  - Tests
  - Build
- [ ] **Commit Hygiene**: Meaningful messages
  - Format: `[TICKET-123] Brief description\n\nLonger explanation`
  - One conceptual change per commit
- [ ] **Merged**: Code in main branch
  - No stale branches

---

## 5. Sprint Planning Meeting (Monday 9:00 AM, 2 Hours)

### Part 1: Backlog Review (30 min)

```
Facilitator: Product Manager

Activity:
├─ Review top 15 backlog items (in priority order)
├─ Call out any newly-discovered dependencies or risks
├─ Confirm story point estimates with team
└─ Identify items ready to pull into sprint

Questions to ask:
├─ Does this ticket have clear acceptance criteria?
├─ Are blockers resolved?
├─ Is the story points estimate still valid?
└─ Do we have the right skills on the team?
```

### Part 2: Capacity Planning (30 min)

```
Facilitator: Scrum Master

Data:
├─ Team capacity: 1 FTE (8 hours/day × 5 days = 40 hours)
├─ Planned time off: (list any vacations)
├─ Non-sprint work: (code review, meetings, unexpected bugs)
└─ Historical velocity: ~25–30 story points/sprint

Calculation:
├─ Available capacity: 40 - 8 (meetings/admin) = 32 hours
├─ Velocity estimate: 25 story points
└─ Plan for 80% utilization buffer

Sprint commitment:
├─ We will complete these tickets: [list 5–8 tickets, total ~25 points]
├─ If we finish early: [list stretch goals, total ~8 points]
└─ Out of scope for this sprint: [list 2-3 high-value tickets for next sprint]
```

### Part 3: Team Assignment (30 min)

```
Facilitator: Product Manager + DRI

For each ticket:
├─ Assign DRI (Directly Responsible Individual)
├─ Ask: "Confident in 40 hours?" (typical ticket)
├─ Identify skill gaps or pairing opportunities
└─ Record estimated start date

Example:
│ BACKEND-001: Gate heuristics (5 pts)
│ ├─ DRI: Backend Lead (Bob)
│ ├─ Start: Monday 2pm
│ ├─ Expected completion: Wednesday 5pm
│ └─ Dependencies: SETUP-002 (Python env ready)
│
│ FRONTEND-001: Electron tray icon (3 pts)
│ ├─ DRI: Frontend Lead (Jane)
│ ├─ Start: Monday 9am
│ ├─ Expected completion: Tuesday 12pm
│ └─ Dependencies: SETUP-010 (Vite configured)
```

### Part 4: Sprint Goal Definition (30 min)

```
Team discusses: "What is the outcome we want by Friday of week 2?"

Sprint 0 Goal Example:
"Establish development environment with working CI/CD pipeline,
 validate ONNX quantization latency <50ms, and finish database schema."

Technical:
├─ Hypothesis: "Int8 ONNX quantization achieves <50ms latency"
├─ Definition of success: "Profiling shows P95 <50ms on test images"
└─ If false: Escalate to team and plan contingency

Business:
├─ Hypothesis: "Calibration wizard UX will reduce support load"
├─ Definition of success: "5 internal users calibrate successfully with <2 min training"
└─ If false: Redesign wizard based on feedback

Documented in: Jira Epic or Obsidian sprint_planning note
```

---

## 6. Daily Standup (Tuesday–Thursday 10:00 AM, 15 Minutes)

```
Format: Timebox 15 minutes, end on time even if not everyone speaks

Each person (1 min per person):
├─ What did I complete since last standup?
├─ What am I working on until next standup?
├─ Any blockers? (if yes, flag for sync after standup)
└─ Any help needed? (ask specific person, not whole team)

Example, Bob (Backend Lead):
├─ ✅ Completed: SETUP-001 (venv configured), SETUP-005 (ONNX latency spike)
├─ ⏳ Next: BACKEND-001 (gate heuristics), targeting PR by EOD Wednesday
├─ 🚫 Blocker: Need Discord webhook URL for testing (Jane to provide)
└─ ❓ Help: None needed

Outcome:
├─ Issues flagged → 15 min sync after standup with relevant people
├─ Progress tracked
└─ Velocity updated (points completed so far)

Note:
─ "15 minutes" is hard stop; longer discussions move to separate sync
─ Remote-friendly: Use Slack huddle or Zoom
─ Async fallback: If timezone issues, post in #standup Slack channel daily
```

---

## 7. Code Review Process

### Pull Request Template

```markdown
# [TICKET-123] Brief Description

## Changes
- List major changes here
- What was added/removed/refactored

## Testing
- [ ] Unit tests added
- [ ] Tested locally: `npm test` / `pytest`
- [ ] Manual testing: [describe steps]

## Checklist
- [ ] Code is type-safe
- [ ] Docstrings added
- [ ] No console.log / print() statements
- [ ] No hardcoded secrets
- [ ] Lint passes: `npm lint` / `pylint`
- [ ] CI/CD green

## Related
- Closes #[TICKET-123]
- Related to #[OTHER-456]

## Screenshots / Videos (if applicable)
[Attach UI changes, test results]
```

### Reviewer Checklist

```
As a reviewer, check:

Code Quality:
├─ Does the code match the existing style?
├─ Are variable names clear?
├─ Is there unnecessary duplication?
└─ Are there obvious bugs or edge cases missed?

Tests:
├─ Are tests present?
├─ Do tests cover happy path + edge cases?
├─ Could the tests be more robust?
└─ Are there shared test utilities that could be reused?

Documentation:
├─ Are docstrings present and clear?
├─ Is the commit message descriptive?
├─ Would a future reader understand this code?
└─ Are related tickets / docs linked?

Performance:
├─ Could this cause latency regression?
├─ Are there N+1 queries or unnecessary DB calls?
└─ Memory leaks possible?

Security:
├─ Are user inputs validated?
├─ Is sensitive data (tokens, passwords) logged?
└─ Any new external dependencies? (Check for vulnerabilities)

Decision: Approve / Request Changes / Comment
├─ Approve: "Looks good!"
├─ Request Changes: "Please address X before merging"
├─ Comment: "Nice refactor, but consider Y in future"
```

---

## 8. End-of-Sprint Testing (Thursday Week 2, 4:00 PM)

### QA Checklist

```
QA Lead runs full test suite:

Automated:
├─ Unit tests: pytest --cov (target ≥75%)
├─ Type checks: mypy src/ + tsc --noEmit
├─ Linting: flake8 + eslint
└─ Integration tests: Special test suite for APIs

Manual:
├─ Smoke test: App launches, core flow works
├─ Accessibility: Tab through UI, screen reader
├─ Performance: Dashboard shows CPU <10%, latency <100ms
├─ Edge cases: Handled errors gracefully, no crashes
└─ Platform: Test on Windows 10 & Windows 11

Regression:
├─ Re-test features from prior sprints
├─ Ensure no new issues introduced
└─ Compare latency/CPU metrics with baselines

Output:
├─ Test report (automated + manual)
├─ Bug count: Critical / High / Medium / Low
├─ Coverage report (trend over sprints)
└─ Recommendation: Approved / Needs fixes / Blocked
```

### Bug Triage

```
If bugs found:

Critical (blocks release):
├─ Assigned to dev, must fix before Monday
├─ Example: "App crashes on startup"
└─ If not fixable in 4 hours, defer feature

High (serious, workaround exists):
├─ Assigned to dev, target fix by next Wednesday
├─ Example: "Discord webhook retry fails after 3 attempts"
└─ Can be included in next sprint

Medium (nice to fix, not urgent):
├─ Added to backlog, prioritized
├─ Example: "Settings tab scroll is laggy"
└─ Revisit in sprint planning

Low (cosmetic):
├─ Backlog, low priority
├─ Example: "Button padding slightly off"
└─ Consider as tech debt item

(All bugs documented in GitHub Issues or Jira)
```

---

## 9. Sprint Review & Retrospective (Friday Week 2, 3:00 PM, 2 Hours)

### Part 1: Review (1 Hour)

```
Audience: Team + Product Manager + Stakeholders

Format:
─ Live demo of completed features
─ Walking through acceptance criteria
─ Showing test coverage & metrics
─ Discussing what was cut (if any)

Example, Sprint 0 Review:
├─ "✅ SETUP-001 through SETUP-010 complete"
├─ Demo: Show Python env, Electron app launching, GitHub Actions pipeline
├─ Metrics:
│  ├─ 26 / 28 story points completed (93%)
│  ├─ Test coverage: 78% (target 75%)
│  ├─ P95 latency: 48ms ✅ (target <50ms)
│  └─ Zero critical bugs found in QA
│
├─ What didn't make it (if anything):
│  ├─ "SETUP-008 docstring generation — deferred to Sprint 1"
│  └─ Why: "Discovered RTD integration more complex than estimated"
│
└─ Questions from stakeholders:
   ├─ "Any risks for next sprint?"
   ├─ "Will we hit the v1.0 release target?"
   └─ Product Manager answers based on velocity trend

Outcome:
├─ Stakeholders informed and aligned
├─ Completed work documented
└─ Confidence level for next sprint determined
```

### Part 2: Retrospective (1 Hour)

```
Audience: Dev team only (psychological safety)

Format: 4 questions (5 min discussion each)

Question 1: "What went well?"
├─ Positive feedback, celebrate wins
├─ Example: "SETUP-005 spike was well-scoped, we got clear answers"
├─ Capture: Repeat these practices next sprint
└─ (5 min, quiet writing, then discussion)

Question 2: "What didn't go well?"
├─ Identify pain points without blame
├─ Example: "Waiting for Discord webhook config slowed down INTEGRATION-004"
├─ Capture: What can we do differently?
└─ (5 min)

Question 3: "What surprised us?"
├─ Unexpected blockers or wins
├─ Example: "ONNX quantization was faster than expected"
├─ Capture: Adjust future estimates
└─ (5 min)

Question 4: "What will we commit to improve next sprint?"
├─ Pick 1–2 specific actions
├─ Example: "We'll review Discord config in sprint planning, not week 1"
├─ Owner: Name who will do it
└─ Review goal next retro
   (5 min)

Outcome:
├─ 1–2 "process improvements" identified
├─ No blame, focus on systems
├─ Commitment to specific changes
└─ Measured in next retro
```

---

## 10. Ticket Estimation Meeting (Async, Before Sprint Planning)

```
Product Manager: "Let me estimate backlog items for next sprint"

For each ticket:

1. Read description + acceptance criteria
   └─ Is it clear? If not, ask team

2. Compare to similar past tickets
   └─ "This is like BACKEND-002 (4 pts)"

3. Ask: "Could one person complete this in 40 hours?"
   ├─ 1–3 pts:  Yes, definitely (<15 hours)
   ├─ 5–8 pts:  Yes, but 15–32 hours
   ├─ 13 pts:   Too big, break into smaller tickets
   └─ Example: If feature estimate >8, split into:
      ├─ FRONTEND-001a: Component structure (3 pts)
      ├─ FRONTEND-001b: State management (5 pts)
      └─ FRONTEND-001c: Testing (2 pts)

4. Risk adjustments
   ├─ Known unknowns: +2 pts
   │  └─ Example: "ONNX quantization spike adds uncertainty → +2"
   ├─ Dependency on other team: +1 pt
   └─ Many edge cases: +1 pt

5. Record estimate in Jira/backlog
   ├─ Visible to team
   ├─ Confidence: High / Medium / Low
   └─ Notes on assumptions

Velocity tracking:
├─ Actual completed points (end of sprint)
├─ Estimate vs actual
├─ Adjust future estimates based on trend
└─ Typical range: 25–30 pts/sprint (1 FTE)
```

---

## 11. Release Criteria & Sign-Off

### Pre-Release Checklist

```
Gate 1: Code Quality
├─ All tickets in "Done" (DoD met)
├─ Test coverage ≥75%
├─ Zero critical bugs
├─ Zero high-severity bugs (unless explicitly deferred)
└─ Lint + type-check passing

Gate 2: Performance
├─ P95 latency <100ms (detection end-to-end)
├─ CPU <10% sustained
├─ Memory <150MB peak
├─ Startup <2 seconds
└─ No memory leaks (profiled for 1 hour)

Gate 3: Security
├─ No hardcoded secrets in code
├─ No obvious OWASP Top 10 issues
├─ Dependencies scanned for CVEs
├─ Code signed (MSI only)
└─ Update mechanism verified

Gate 4: User Readiness
├─ User manual reviewed
├─ Installation tested on Windows 10 & 11
├─ First-run experience smooth (calibration <5 min)
├─ Support channels ready (Discord, GitHub Issues)
└─ Release notes written

Gate 5: PM Sign-Off
├─ All sprint goals met
├─ No scope creep for this release
├─ Go/No-go decision recorded
└─ If any gate fails: Defer feature or delay release

Approval chain:
├─ Backend Lead: ✅ Code review, performance
├─ Frontend Lead: ✅ UI/UX, accessibility
├─ QA Lead: ✅ Test coverage, bug status
├─ DevOps Lead: ✅ Build, deployment, security
└─ Product Manager: ✅ Final decision
```

---

## 12. Communication Plan

### Weekly Communication

```
Monday 9:00 AM: Sprint Planning meeting
├─ Attendees: Full team
├─ Slack: #sprint-planning
└─ Outcome: Sprint goal posted in team channel

Tuesday–Thursday 10:00 AM: Daily Standup
├─ Attendees: Full team
├─ Format: Slack huddle or Zoom
└─ Async option: #standup Slack thread

Friday 2:00 PM: Code Review Sync
├─ Attendees: Full team
├─ Format: Zoom (15 min)
└─ Discuss any blockers, plan next week

Friday 3:00 PM: Sprint Review & Retro
├─ Attendees: Team + stakeholders (review) / team-only (retro)
├─ Format: Zoom + screen share
└─ Outcome: Notes posted in #sprint-review

### Async Communication

```
Slack channels:
├─ #sprint-planning: Backlog items, estimates, Q&A
├─ #standup: Daily updates (if not attending standup)
├─ #engineering: Technical discussions, code reviews
├─ #blocked: Blockers requiring immediate help
└─ #sprint-review: Completed work, metrics

GitHub:
├─ Issues: Detailed ticket descriptions, comments, attachments
├─ PRs: Code review, linked to issues
├─ Projects: Visible sprint board (To Do → In Progress → Done)
└─ Wiki: Long-form docs (architecture, processes)

Docs:
├─ Notion / Obsidian: Specification docs, architecture
├─ Google Docs: Shared planning (architecture decisions, risk log)
└─ Spreadsheets: Velocity tracking, metrics dashboard

Escalation path (if blocked):
├─ Level 1: Mention in #blocked + tag person
├─ Level 2: Ping in standup
├─ Level 3: Sync meeting
└─ Level 4: Escalate to PM / Leadership
```

---

## 13. Metrics Tracked by Sprint

```
Team Velocity:
├─ Story points started this sprint
├─ Story points completed this sprint
├─ Carry-over (incomplete from last sprint)
├─ Trend: Should stabilize 25–30 pts/sprint
└─ Action: If <20 pts, investigate capacity issues

Quality Metrics:
├─ Test coverage: Target ≥75%
├─ Bugs found in QA: Target <3 per sprint
├─ Critical bugs: Target 0
├─ Re-opened issues: Track (indicates incomplete DoD)
└─ Trend: Should improve over time

Performance Metrics:
├─ P95 latency: Target <100ms
├─ CPU: Target <10% sustained
├─ Memory: Target <150MB
├─ Startup time: Target <2 seconds
└─ Trend: Watch for regressions, baseline every sprint

Process Metrics:
├─ PR review time: Target <24 hours
├─ Time from "Done" to "Released": Target <1 day
├─ Retro action completion: What % of last sprint's actions completed?
└─ Team satisfaction: Brief pulse check every sprint

Dashboard / Reporting:
├─ Sprint board visible to team (GitHub Projects)
├─ Velocity chart (historical trend)
├─ Test coverage report (trend)
├─ Latency graph (baseline + trend)
└─ Published weekly in #sprint-metrics
```

---

## 14. Common Anti-Patterns & How to Avoid Them

| Anti-Pattern | What Goes Wrong | Prevention |
|-----------|-----------|-----------|
| **Scope creep** | "While we're in there..." new features added mid-sprint | Sprint planning: Lock scope, document out-of-scope |
| **Incomplete DoD** | Feature merged but untested, breaks later | Enforce DoD checklist, block merge without sign-off |
| **Estimation drift** | "5-pointer takes 40 hours" → velocity metric unreliable | Post-mortem: Why? Adjust future estimates |
| **Blocked tickets** | Waiting on external person, spins wheels | Record blocker immediately, escalate in standup |
| **Technical debt** | Never schedule refactoring → code quality decays | Reserve 10% velocity annually for tech debt |
| **Skip testing under pressure** | "We'll test later" → bugs in prod | No exception: DoD includes testing |
| **Unclear acceptance criteria** | Dev guesses, QA rejects → rework | Template: "Given X, when Y, then Z" |
| **Retro becomes complaint session** | No action, just venting → nothing changes | Facilitate: "What will we DO next sprint?" |

---

## 15. Sprint Success Criteria

**A sprint is successful if:**

1. ✅ Sprint goal clearly stated and communicated
2. ✅ Backlog items meet DoR before sprint starts
3. ✅ Daily standup happens (mostly) on time
4. ✅ Completed work meets DoD (no debt passed to QA)
5. ✅ QA validates all done tickets
6. ✅ Zero or near-zero critical bugs
7. ✅ Performance targets maintained or improved
8. ✅ Team morale positive (retro feedback)
9. ✅ Velocity predictable (±20% of target)
10. ✅ Retrospective action items identified & assigned

---

**Owner**: Scrum Master / Product Manager  
**Review Frequency**: Every 2 sprints (align with process changes)  
**Last Updated**: February 6, 2026
