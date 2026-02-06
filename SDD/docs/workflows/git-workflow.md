# Git Workflow & Branching Strategy
## Overwatch AI Queue Detection & Notification App

**Generated**: February 6, 2026  
**Version**: 1.0

---

## Branch Strategy (Git Flow)

```
main (production, stable releases)
  ↑
  └── (PR with release notes)

develop (staging, integration branch)
  ↑
  ├── (PR from feature branches)
  │
  ├── feat/1.1-screen-capture
  ├── feat/1.2-gate-logic
  ├── feat/1.3-classifier
  │
  ├── fix/critical-null-ptr
  │
  └── chore/update-dependencies
```

---

## Branching Rules

### Feature Branch
```bash
git checkout -b feat/1.2-gate-logic
```
- **Naming**: `feat/<ticket-id>-<description>`
- **Example**: `feat/1.2-gate-logic`, `feat/2.5-discord-webhook`
- **Parent**: Branch from `develop`
- **Merge**: Back to `develop` via PR (peer review required)

### Bug Fix Branch
```bash
git checkout -b fix/crash-null-classifier
```
- **Naming**: `fix/<description>` or `fix/<issue-id>-<description>`
- **Example**: `fix/crash-null-classifier`, `fix/429-rate-limit-retry`
- **Parent**: Branch from `develop` (or `main` if production hotfix)
- **Merge**: Back to `develop` via PR

### Hotfix Branch (Production)
```bash
git checkout -b hotfix/v1.0.1-null-crash
git checkout main && git pull
git pull --ff-only origin develop
git checkout -b hotfix/v1.0.1
```
- **Naming**: `hotfix/<version>-<description>`
- **Parent**: Branch from `main`
- **Merge**: Back to `main` + `develop` (Cherry-pick commits)

---

## Commit Message Convention

**Format**: `<type>(<scope>): <subject>`

```
feat(backend): implement screen capture service

fix(frontend): correct state badge color for MATCH_FOUND

test(backend): add gate logic unit tests

docs(architecture): update database schema diagram

chore(deps): update ONNX Runtime to 1.16.0
```

### Types
- `feat`: New feature (PR required)
- `fix`: Bug fix
- `test`: Test additions/fixes
- `docs`: Documentation
- `refactor`: Code refactoring (no behavior change)
- `perf`: Performance improvement
- `chore`: Dependency updates, tooling, housekeeping
- `ci`: CI/CD pipeline changes

### Scope (Optional)
- `backend`, `frontend`, `db`, `devops`, `qa`, `docs`, `deps`

### Subject
- Imperative verb ("implement", "add", "fix", not "implemented")
- Lowercase
- No period at end
- < 50 characters

### Body (Optional, for complex commits)
```
feat(backend): implement escalation classifier

- Load larger ONNX model when tiny confidence < 0.85
- Cache escalation results (TTL 500ms)
- Add exponential backoff if inference timeout

Closes #1.3
```

---

## Pull Request Process

### 1. Create PR
```bash
git push origin feat/1.2-gate-logic
# GitHub: Create PR from feat/1.2-gate-logic → develop
```

### 2. PR Title & Description
**Title**: `Gate Logic Service Implementation (1.2)`

**Description**:
```markdown
## Ticket
Closes #1.2

## Changes
- Implemented GateService with pixel diff detection
- Added histogram divergence heuristic
- Integrated with PerceptionService

## Testing
- 5 new unit tests (all passing)
- Integration test with full pipeline
- Coverage: 88% in gate.py

## Spec Compliance
✓ Requirement DR-3: Heuristic gate < 5ms
✓ Requirement FR-2: Each detection includes confidence

## Checklist
- [x] Tests pass locally
- [x] No lint errors
- [x] TypeScript strict mode passes
- [x] Spec requirements met
- [x] Updated backlog.md status
```

### 3. Status Checks (Automated)
GitHub Actions must pass:
- ✓ Lint (eslint / black / pylint)
- ✓ Type check (TypeScript / mypy)
- ✓ Unit tests (pytest / vitest)
- ✓ Integration tests
- ✓ Coverage (>75% required)
- ✓ Security scan (npm audit)

### 4. Peer Review
- At least 2 approvals required before merge
- Reviewers check:
  - ✓ Code quality & patterns
  - ✓ Test coverage
  - ✓ Spec compliance
  - ✓ No security issues
  - ✓ Clear commit messages

### 5. Merge
```bash
# Option A: Squash (for small features)
git checkout develop
git pull origin develop
git merge --squash feat/1.2-gate-logic
git commit -m "feat(backend): implement gate logic (1.2)"
git push origin develop

# Option B: Rebase (for clean history)
git fetch origin
git rebase origin/develop
git push origin feat/1.2-gate-logic (force)
# Then merge on GitHub (linear history)
```

### 6. Delete Branch
```bash
git push origin --delete feat/1.2-gate-logic
```

---

## Merge Conflict Resolution

If `develop` has moved ahead:

```bash
git fetch origin
git rebase origin/develop
# Resolve conflicts in editor
git add <resolved-files>
git rebase --continue
git push origin feat/1.2-gate-logic -f
```

---

## Release Workflow

### Before Release (v1.0.0)

1. **Merge final PRs** to `develop`
2. **Create release branch**:
   ```bash
   git checkout -b release/v1.0.0 develop
   ```

3. **Bump version** in package.json + pyproject.toml:
   ```json
   { "version": "1.0.0" }
   ```

4. **Update CHANGELOG.md**:
   ```markdown
   ## [1.0.0] - 2026-02-06
   
   ### Added
   - Core perception pipeline (gate + tiny + escalation models)
   - Desktop notifications (Windows Toast)
   - Discord webhook integration
   - Calibration wizard
   ```

5. **Merge release branch**:
   ```bash
   git checkout main
   git merge --no-ff release/v1.0.0 -m "Merge release v1.0.0"
   git tag -a v1.0.0 -m "Release v1.0.0: Core perception + notifications"
   ```

6. **Merge back to develop**:
   ```bash
   git checkout develop
   git merge main  # Brings version bump + tag back to develop
   ```

7. **Push**:
   ```bash
   git push origin main develop --tags
   ```

### Build & Publish

GitHub Actions (on tag):
1. Build MSI installer
2. Sign binary (with EV cert, eventually)
3. Upload to GitHub Releases
4. Update auto-update manifest

---

## Tag Naming

```bash
git tag -a v1.0.0 -m "Release v1.0.0: Core features"
git tag -a v1.0.1 -m "Hotfix v1.0.1: Null classifier crash"
git tag -a v1.1.0-beta.1 -m "Beta v1.1.0: Multi-agent support"
```

**Format**: `v<major>.<minor>.<patch>[-<prerelease>]`
- `v1.0.0`: Stable release
- `v1.0.1`: Patch (hotfix)
- `v1.1.0`: Minor (features)
- `v2.0.0`: Major (breaking changes)
- `v1.1.0-beta.1`: Pre-release

---

## Local Development

### Initial Setup
```bash
git clone https://github.com/user/ow-notifier.git
cd ow-notifier
git checkout develop
```

### Before Starting Work
```bash
git fetch origin
git pull origin develop
git checkout -b feat/your-ticket
```

### Throughout Development
```bash
# Stage changes
git add src/perception/gate.py tests/unit/test_gate.py

# Commit (atomic, focused commits)
git commit -m "feat(backend): implement pixel diff heuristic"
git commit -m "feat(backend): add histogram divergence check"
git commit -m "test(backend): unit tests for gate logic"

# Push for review
git push origin feat/your-ticket
```

### Syncing with Main Development
```bash
git fetch origin
git rebase origin/develop  # Rebase on latest develop
git push origin feat/your-ticket -f
```

---

## Summary

- **Branches**: `main` (stable) ← `develop` (integration) ← feature branches
- **Commits**: Atomic, clear messages with type/scope/subject
- **PRs**: Require tests, linting, peer review (2 approvals)
- **Merges**: Squash for small changes, rebase for clean history
- **Releases**: Tag on main, auto-publish via GitHub Actions
- **Hotfixes**: Branch from main, merge back to both main + develop

This workflow ensures **code quality**, **clear history**, and **safe releases**.
