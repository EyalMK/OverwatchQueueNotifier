# CI/CD Pipeline
## Overwatch AI Queue Detection & Notification App

**Generated**: February 6, 2026  
**Version**: 1.0

---

## Pipeline Architecture

```
Code Push (develop branch)
  │
  ▼
GitHub Actions Workflow (test.yml)
  │
  ├─→ [Lint & Format] (5 min)
  │    ├─ eslint (frontend)
  │    ├─ black (backend Python)
  │    ├─ prettier (TypeScript)
  │    └─ FAIL? Block merge
  │
  ├─→ [Type Check] (5 min)
  │    ├─ TypeScript strict mode
  │    ├─ mypy (Python)
  │    └─ FAIL? Block merge
  │
  ├─→ [Security Scan] (3 min)
  │    ├─ npm audit (dependencies)
  │    ├─ pip-audit (Python deps)
  │    ├─ GitHub CodeQL (SAST)
  │    └─ CRITICAL? Block merge
  │
  ├─→ [Unit Tests] (10 min)
  │    ├─ pytest backend/ (50-60 tests)
  │    ├─ vitest frontend/ (40-50 tests)
  │    ├─ Coverage report (lcov)
  │    └─ <75% coverage? Block merge
  │
  ├─→ [Integration Tests] (15 min)
  │    ├─ MCP tool contracts
  │    ├─ API endpoint tests
  │    ├─ Database transactions
  │    └─ FAIL? Block merge
  │
  ├─→ [Build] (10 min)
  │    ├─ npm run build (Vite)
  │    ├─ electron-builder
  │    ├─ .asar bundle created
  │    └─ FAIL? Block merge
  │
  ├─→ [Upload Artifacts] (2 min)
  │    ├─ Store coverage report
  │    ├─ Store build logs
  │    └─ Cache dependencies
  │
  └─→ SUCCESS ✓
       All checks passed; PR ready to merge
```

---

## Workflow File: `.github/workflows/test.yml`

```yaml
name: Test & Build

on:
  push:
    branches: [develop, main]
  pull_request:
    branches: [develop, main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - run: npm install
      - run: npm run lint
      - run: pip install black pylint
      - run: black --check backend/src
      - run: pylint backend/src

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - run: npm install
      - run: npm run typecheck
      - run: pip install mypy
      - run: mypy backend/src

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: github/super-linter@v4
        with:
          VALIDATE_JAVASCRIPT: true
          VALIDATE_PYTHON: true
      - run: npm audit --audit-level=moderate --legacy-peer-deps || true
      - uses: github/codeql-action/init@v2
        with:
          languages: ['python', 'javascript']
      - uses: github/codeql-action/autobuild@v2
      - uses: github/codeql-action/analyze@v2

  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - run: pip install -e ./backend[dev]
      - run: pytest backend/tests --cov=backend/src --cov-report=lcov
      - uses: coverallsapp/github-action@v2
        with:
          file: ./coverage.lcov

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      
      - run: npm ci
      - run: npm run test -- --coverage

  build:
    runs-on: windows-latest
    needs: [lint, typecheck, test-backend, test-frontend]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-artifact@v3
        with:
          name: app-build
          path: dist/

  release:
    runs-on: windows-latest
    if: startsWith(github.ref, 'refs/tags/v')
    needs: [build]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v3
        with:
          name: app-build
          path: dist/
      
      - name: Create MSI
        run: |
          npm install --global @electron-forge/cli
          electron-builder --publish never --win nsis
      
      - name: Sign & Upload to GitHub Releases
        uses: softprops/action-gh-release@v1
        with:
          files: |
            dist/Overwatch-Queue-Notifier-*.msi
            dist/RELEASES
```

---

## Gate Requirements

| Stage | Pass Criteria | Fail Action |
|-------|---|---|
| **Lint** | All linting rules pass | PR blocked; show violations |
| **Type Check** | No type errors (TS strict, mypy strict) | PR blocked; show errors |
| **Security** | No critical CVEs; CodeQL passes | PR blocked; show vulnerabilities |
| **Unit Tests** | >75% coverage; all tests pass | PR blocked; show failures |
| **Integration** | All API & DB tests pass | PR blocked; show failures |
| **Build** | Compiles without errors | PR blocked; show build logs |

---

## Artifact Management

**Duration**: 90 days retention

- Coverage reports: `coverage.lcov` (uploaded to Coveralls)
- Build logs: Stored in GitHub Actions
- Binary artifacts: MSI (on releases only)
- Cache: node_modules + .venv (auto-managed by Actions)

---

## Release Pipeline (v1.0.0)

When tag `v1.0.0` is pushed:

1. **Build**: Compile Windows binary
2. **Sign**: Code sign with EV certificate (future)
3. **Package**: Create MSI installer
4. **Checksum**: SHA256 signatures
5. **Upload**: GitHub Releases + RELEASES manifest
6. **Notify**: Discord webhook (release announcement)

---

## Summary

The CI/CD pipeline **automatically**:
- Validates code quality (lint + type check)
- Runs security scanning
- Tests coverage (>75% required)
- Builds and archives artifacts
- Publishes releases to GitHub

**No manual steps required**; automation reduces human error and accelerates feedback.
