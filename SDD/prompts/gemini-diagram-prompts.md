# Gemini Diagram Prompts
## Copy-Paste Ready for Gemini Advanced

READ FIRST: All files in docs/architecture/, docs/workflows/, and this folder's sprint prompts.

---

## Diagram 1: System Architecture (High-Level)

**Paste this entire block into Gemini:**

```
Generate a system architecture diagram for an Overwatch Queue Notifier desktop app.

Components:
1. Electron Main (Windows desktop, runs Zustand store)
2. Electron Renderer (React UI, Dashboard window + system tray)
3. Python MCP Server (port 5000, handles AI perception)
4. SQLite Database (local, 4 tables: calibration_profiles, detection_history, notification_log, settings)
5. ONNX Runtime (on-device AI inference, <200KB gate model, 5MB escalation model)
6. Windows Notification API (toast notifications)
7. Discord Webhook (optional user-provided endpoint)
8. Screen Capture Layer (Windows GDI, 2560×1440 regions)

Data Flow:
- Electron Renderer → IPC bridge → Python MCP (perceive_state request)
- Python MCP → ONNX inference (gate <50ms, escalation <150ms)
- ONNX response → response JSON (state: "MATCH_FOUND" | "QUEUE" | "LOADING" | "IN_GAME")
- Renderer receives → Updates Zustand store → Re-renders UI
- If MATCH_FOUND → Call notify.desktop and notify.discord endpoints
- Store to SQLite detection_history

Style: Boxes and arrows, show synchronous flow, label latency targets on arrows.

Include legend:
- Green: User-facing (Electron)
- Blue: Backend (Python)
- Yellow: AI (ONNX)
- Red: Persistence (SQLite)
- Orange: External (Discord, Windows API)
```

**Expected output**: Mermaid diagram (copy to markdown) or image showing flow from screen capture → perception → notification.

---

## Diagram 2: Database Entity-Relationship Diagram (ERD)

**Paste this block:**

```
Create an Entity-Relationship Diagram (ERD) for a Windows desktop app database.

4 Tables:
1. calibration_profiles
   - id (PRIMARY KEY)
   - name (TEXT)
   - crop_region (JSON: {"top": int, "left": int, "width": int, "height": int})
   - resolution (JSON: [width, height])
   - created_at (TIMESTAMP)

2. detection_history
   - id (PRIMARY KEY)
   - timestamp (TIMESTAMP)
   - state (TEXT: QUEUE|LOADING|MATCH_FOUND|IN_GAME)
   - confidence (FLOAT: 0.0–1.0)
   - calibration_id (FOREIGN KEY → calibration_profiles)
   - model_used (TEXT: gate|escalation)

3. notification_log
   - id (PRIMARY KEY)
   - detection_id (FOREIGN KEY → detection_history)
   - notification_type (TEXT: desktop|discord)
   - status (TEXT: sent|failed)
   - timestamp (TIMESTAMP)
   - error_message (TEXT, nullable)

4. settings
   - id (PRIMARY KEY)
   - key (TEXT, UNIQUE)
   - value (TEXT)
   - updated_at (TIMESTAMP)

Relationships:
- calibration_profiles.id ← detection_history.calibration_id (1:M)
- detection_history.id ← notification_log.detection_id (1:M)

Style: Crow's foot notation, include data types.
```

**Expected output**: ERD showing table boxes, columns, data types, and cardinality.

---

## Diagram 3: React Component Hierarchy

**Paste this block:**

```
Create a component tree diagram for a React desktop app (Electron + Zustand).

Component Hierarchy:
Root: App
├── Dashboard Window (Main UI, 800×600 resizable)
│   ├── Header (logo, refresh button)
│   ├── StateDisplay (shows current: QUEUE|LOADING|MATCH_FOUND|IN_GAME, large text, color-coded)
│   ├── ConfidenceBar (0–100%, visual bar, updates real-time)
│   ├── NotificationStatus (shows last notification: "Sent to Discord 2s ago")
│   ├── QuickActions (buttons: Calibrate, Settings, Quit)
│   └── LogViewer (scrollable, shows last 10 state changes)
└── Settings Modal (Optional, overlay)
    ├── Crop Region Editor (visual region picker on screenshot)
    ├── Discord Webhook Input
    ├── Notification Preferences (toggle: desktop on/off, discord on/off)
    └── Debug Section (show current FPS, inference time, queue depth)

Tray Icon (System tray):
├── Show Dashboard
├── Calibrate
├── Settings
└── Quit

State Management (Zustand store):
├── gameState (QUEUE|LOADING|MATCH_FOUND|IN_GAME)
├── confidence (float)
├── lastNotification (timestamp, type)
└── settings (object)

Data Flow:
- MCP Server updates WebSocket/IPC → Zustand action
- Zustand notifies all subscribed components
- Components re-render (only changed parts via React memo)

Style: Tree diagram with component names in boxes, color-code:
- Green: Data input (MCP)
- Blue: State container (Zustand)
- Purple: UI components
- Red: External API (Discord, Windows notification)
```

**Expected output**: Hierarchy tree showing parent-child relationships and data flow arrows.

---

## Diagram 4: CI/CD Pipeline (GitHub Actions)

**Paste this block:**

```
Design a CI/CD pipeline using GitHub Actions for a Windows desktop Electron + Python app.

Pipeline stages:

1. Trigger: Push to develop or PR to main

2. Lint & Format (parallel jobs)
   ├── Backend: pylint, black, flake8 on Python files
   ├── Frontend: eslint, prettier on TypeScript/React files
   └── YAML: yamllint on workflow files

3. Type Checking (parallel)
   ├── Backend: mypy backend/src/
   └── Frontend: tsc frontend/src/

4. Security Scans (parallel)
   ├── pip-audit backend/requirements.txt
   ├── npm-audit frontend/package-lock.json
   └── CodeQL scan (GitHub Advanced)

5. Unit Tests (parallel)
   ├── Backend: pytest backend/tests/unit/ --cov=75%
   └── Frontend: vitest frontend/tests/unit/ --coverage=75%

6. Integration Tests (sequential, only passes if unit tests pass)
   └── pytest backend/tests/integration/

7. Build Artifacts
   ├── Backend: Build Docker image (optional, for future cloud deployment)
   └── Frontend: npm run build → dist/
   └── Electron: electron-builder → *.msi (Windows installer)

8. Release (only on tag v*.*.*  on main)
   ├── Code sign .msi with certificate
   ├── Generate checksums (SHA256, MD5)
   ├── Upload to GitHub Releases
   └── Notify via Discord webhook

Gates:
- All linting must pass
- Coverage must be >75%
- No critical CVEs
- All unit tests must pass before integration
- Integration tests pass before build
- Build must succeed before release

Status badges: [Lint] [Tests] [Coverage] [Security]

Style: Pipeline flowchart, color-code:
- Green: Pass gates
- Red: Fail gates (block merge)
- Blue: Build stages
- Orange: Release stage
```

**Expected output**: Flowchart showing GitHub Actions jobs, gates (stop/continue), and final release.

---

## Diagram 5: Game State Machine (Perception States)

**Paste this block:**

```
Create a state machine diagram for game state detection.

States:
1. QUEUE (loading screen, queue timer visible, blue/purple colors)
2. LOADING (map loading, spinning wheel, game starting)
3. MATCH_FOUND (hero select, team composition, "MATCH FOUND!" text)
4. IN_GAME (in-game HUD, objective, health bars)

Transitions:
QUEUE → LOADING (5% pixel diff threshold crossed)
LOADING → MATCH_FOUND (hero select screen detected, 85% confidence from AI)
MATCH_FOUND → IN_GAME (respawn timer starts, kill feed visible)
IN_GAME → QUEUE (game ends, return to queue)
* → QUEUE (manual calibrate, screen not focused, window closed)

Detection Logic:
- Gate filter: Detects motion >15% pixel difference
  - If triggered: route to Escalation AI (ONNX, 5MB model)
  - Else: stay in current state (confidence 95%)
- Escalation classifier: Returns state + confidence (0–100%)
  - Threshold: 85% required for state change
  - Deduplication: Store new state for 5 seconds before checking again

Notifications:
- Transition to MATCH_FOUND → send desktop toast + Discord webhook
- Other transitions → log only (no notification)

Confidence Scoring:
- QUEUE: 95% (no motion = queue)
- LOADING: 70% (motion detected, no match text yet)
- MATCH_FOUND: 92% (hero select pattern matched)
- IN_GAME: 98% (HUD elements present)

Style: State diagram with circular states, arrows show transitions with labels.
Color code:
- Blue: QUEUE
- Yellow: LOADING
- Green: MATCH_FOUND
- Red: IN_GAME
```

**Expected output**: State machine diagram showing all 4 states, transitions, and confidence levels.

---

## Diagram 6: Desktop App Deployment Architecture

**Paste this block:**

```
Show the deployment and update flow for a Windows desktop Electron app.

Current Architecture (v1.0, Local-First):

User Desktop
├── Electron app (installed via MSI)
├── Python backend (bundled with Electron via PyInstaller)
├── SQLite database (C:\Users\{user}\AppData\Local\OverwatchQueueNotifier\)
└── No cloud connection (fully offline capable)

Auto-Update Flow:
1. App checks GitHub Releases for latest version (on startup, weekly)
2. If newer version found: Download .msi to temp folder
3. User prompted: "Update available. Restart to install?"
4. On restart: Run installer silently (replace existing binary)
5. New version launches

Backup & Recovery:
- Database backed up to AppData\\Local\\..\\Backup\\
- If app crashes: Load last known good database
- RTO (Recovery Time Objective): <5 minutes
- RPO (Recovery Point Objective): <1 minute

Future Cloud Expansion (v2.0+, if needed):
- Optional AWS S3 for backup sync
- Optional cloud dashboard (web app)
- Analytics sent to API (user opt-in)

Style: Deployment diagram, show:
- User machine
- GitHub Releases bucket (source of updates)
- AppData folder (persistence)
- Backup location
- Optional future cloud components (grayed out)
```

**Expected output**: Deployment diagram showing Windows machine, local folders, update flow, and optional cloud.

---

## Diagram 7: User Journey Map (Detection → Notification)

**Paste this block:**

```
Create a user interaction journey map for queue detection and match notification.

Timeline: T+0 to T+1 second

T+0.0s: User in Overwatch queue screen
  - Waiting for match (blue queue UI visible)
  - App is monitoring in background

T+0.1s: Match found on server
  - Match found screen appears (hero select)
  - Screen pixels change from queue to hero select pattern

T+0.1-0.2s: Gate filter detects motion
  - >15% pixel difference detected
  - Routes screen capture to Escalation AI

T+0.2-0.35s: Escalation AI processes
  - ONNX model inference: 150ms
  - Returns: MATCH_FOUND, confidence 0.92

T+0.35s: State published to frontend
  - IPC: Backend → Electron Renderer
  - Zustand store updated
  - StateDisplay component re-renders

T+0.4s: Notifications sent
  - Desktop toast: "MATCH FOUND! [92%]" appears
  - Discord webhook called (if configured)
  - Notification logged to SQLite

T+0.5s: User sees visual + audio feedback
  - Toast notification visible
  - Zustand StateDisplay shows green "MATCH_FOUND"
  - User hears system notification sound

T+0.5-1.0s: Deduplication window active
  - During 5s dedup window: ignore repeated MATCH_FOUND
  - Prevents notification spam if hero select takes 5+ seconds

Emotion/Touchpoint Map:
- T+0: Anticipation (waiting for match)
- T+0.2: Neutral (system working in background)
- T+0.4: Excitement (notification triggered!)
- T+0.5+: Satisfaction (user alerted in <1s)

Error Scenarios:
- If confidence <85%: Don't send notification, log to debug
- If Discord webhook fails: Continue showing desktop notification
- If state same as last 5s: Silently ignore (dedup)

Style: Timeline chart showing:
- Time (x-axis: 0ms to 1000ms)
- Components (y-axis: Gate, AI, Notifications, UI)
- State transitions (colored bars)
- Emotion arc (squiggly line)
```

**Expected output**: Timeline visualization of the detection + notification flow from <1 second.

---

## Diagram 8: Security & Data Flow (Encryption/Validation)

**Paste this block:**

```
Create a data security and validation flow diagram.

Data Entry Points:
1. Screen capture (from Windows GDI)
   → Validation: Verify resolution matches calibration
   → No processing needed (binary image data)

2. Discord webhook URL (user input in settings modal)
   → Validation: URLValidator (must start with https://discord.com/api/)
   → Storage: Encrypted in SQLite (if secrets.key exists)
   → Risk: User webhook leaks to attacker → they spam Discord

3. Crop region (user draws on screenshot)
   → Validation: Bounds check (within 0,0 to resolution)
   → Storage: Plain JSON in calibration_profiles
   → Risk: Low (internal only, no external input)

Data Processing:
Screen → Gate (pixel diff, no validation needed)
       → Escalation AI (ONNX model, no SQL injection possible)
       → Response JSON (validate: state ∈ {QUEUE, LOADING, MATCH_FOUND, IN_GAME}, confidence ∈ [0,1])

Data Storage:
SQLite queries (all parameterized):
INSERT INTO detection_history
  (state, confidence, calibration_id, timestamp)
VALUES (?, ?, ?, ?)
WHERE: state is pre-validated, parameterized

Secret Management:
Discord webhook URL stored as:
- Plain if no secrets.key file
- Encrypted with secrets.key (AES-256) if file exists
- Key NOT stored in repo (add to .gitignore)

Output (Notifications):
- Desktop toast: Rendered by Windows API (safe)
- Discord webhook: POST via requests (parameterized JSON, safe)
  Risk: If Discord is down, HTTP POST timeout (handled with 5s timeout)

OWASP Top 10 Coverage:
1. Injection: 100% (all SQL parameterized, no user input to queries)
2. Broken Authentication: N/A (single-user, local-only)
3. Sensitive Data Exposure: Webhook URL encrypted
4. XML External Entities: N/A (no XML processing)
5. Broken Access Control: N/A (single-user)
6. Security Misconfiguration: TLS not applicable (local only)
7. XSS: N/A (desktop app, no web rendering)
8. Insecure Deserialization: N/A (no object serialization)
9. Using Components with Known Vulns: npm-audit + pip-audit (CI/CD gates)
10. Insufficient Logging: All state changes logged, sensitive data redacted

Style: Data flow diagram with color-coded security zones:
- Green: Validated data
- Yellow: User input (requires validation)
- Red: Sensitive data (encrypted)
- Blue: External API (safe if parameterized)
```

**Expected output**: Data flow diagram showing input validation, storage, encryption, and output safety.

---

## How to Use These Prompts

1. Copy one prompt block (e.g., "Diagram 1: System Architecture")
2. Go to Gemini Advanced (Copilot > Gemini)
3. Paste the entire block
4. Gemini will generate a diagram (usually Mermaid format)
5. Copy Gemini's output → paste into a `.md` file in `docs/diagrams/`
6. Name file: `01_system_architecture.md`, `02_erd.md`, etc.

**Result**: 8 complete architecture diagrams for your documentation.

All diagrams follow the actual project specs and architecture decisions in docs/architecture/deep-dive.md.
