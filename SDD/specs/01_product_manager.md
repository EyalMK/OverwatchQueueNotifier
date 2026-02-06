# Product Manager Specification
## Overwatch AI Queue Detection & Notification App

**Generated**: February 6, 2026  
**Version**: 1.0  
**Status**: Draft → Foundation Sprint

---

## 1. Project Vision & Elevator Pitch

**Overwatch Queue Notifier** is a local-first Windows desktop application that uses AI-based screen perception to detect when a match is found in Overwatch 2, eliminating the need to constantly watch the game window while queueing. The app runs silently in the system tray, monitors the game in real time with minimal CPU/GPU overhead, and notifies the user instantly via desktop notification and optional Discord webhook when a match is active.

---

## 2. Problem Statement

### Pain Points
- **Alt-tab fatigue**: Players frequently leave Overwatch 2 queueing (especially in tank/support roles with long queues) to do other tasks, but must periodically check if a match has arrived. Missing the notification means missing the match start or a lengthy PvP queue restart.
- **False hope**: Current queue times are unpredictable. Players manually refresh/alt-tab, creating context switching overhead and anxiety.
- **Streaming friction**: Streamers multi-tasking during queue periods must choose between watching Overwatch (boring content) or risking missing matches (lost audience engagement).
- **No existing solution**: Current queue notification tools are either:
  - Closed-source third-party tools (trust / privacy concerns, may violate ToS)
  - Manual browser-based queue time predictions (inaccurate, requires manual refresh)
  - Audio-only cues (insufficient for alt-tab players, false positives from menu sounds)

---

## 3. Solution Overview

**Overwatch Queue Notifier** combines three techniques to detect "MATCH_FOUND" state with minimal false positives:

1. **Always-on gate** (cheap diff-based heuristics) — detects if screen has changed significantly since last check
2. **Tiny AI classifier** (lightweight local model, INT8 quantized) — runs frequently on cropped UI regions to detect game state
3. **Escalation AI** (larger, slower model) — runs only if confidence is uncertain, for final decision

This tiered approach ensures:
- **Low CPU usage** (single-digit percentage during idle queue)
- **Low false positives** (<1 per busy queue hour)
- **Fast detection** (<1 second from match appearance to notification)
- **Privacy-first** (all processing local, no cloud/external APIs, only cropped UI regions analyzed)

---

## 4. Target Users & Personas

### Persona 1: Marcus (Competitive Ranked Player)
- **Age / Background**: 28, software engineer, plays 2–3 hours on weeknights
- **Tech Comfort**: Very high (comfortable with command-line tools, config files, local development)
- **Goals**: 
  - Minimize queue wait perception (wants to play other games during queue)
  - Never miss a match start
  - Low-overhead monitoring (no performance impact on gaming)
- **Frustrations**: 
  - Alt-tab cycles break game immersion
  - Third-party tools require Discord permissions
  - Missed matches due to distraction
- **Expected Usage**: Queue frequently (role-specific), alt-tabs to browse/code, needs instant notification
- **Willingness**: High (can contribute to development, comfortable with beta)

### Persona 2: Jennifer (Casual Streamer)
- **Age / Background**: 24, streams on Twitch 20 hours/week, plays for fun
- **Tech Comfort**: Medium (knows basic Windows settings, prefers UI over CLI)
- **Goals**:
  - Fill queue time with engaging content (don't want dead air)
  - Instant alert when match arrives (notification, Discord ping)
  - Low interference with streaming setup
- **Frustrations**:
  - Staring at Overwatch queue screen is bad content
  - Discord doesn't notify of Overwatch events
  - Existing tools are unreliable (false positives interrupt stream)
- **Expected Usage**: Always queueing during streams, watches Discord for notification
- **Willingness**: Medium (wants reliability, not interested in contributing to development)

### Persona 3: David (Tank Main)
- **Age / Background**: 35, plays evening/weekend, has limited time
- **Tech Comfort**: Low (prefers one-click setup, no configuration)
- **Goals**:
  - Instantly know when match is ready (tank queue times: 5–10 min)
  - Spend queue time on phone or household tasks
  - Reliable notifications (no false alarms during matches)
- **Frustrations**:
  - Checking game repeatedly is tedious
  - False positives are worse than missing a queue (re-queue)
  - Doesn't want to fiddle with settings
- **Expected Usage**: Queueing solo, expects "download → run → notify" with zero configuration
- **Willingness**: Low technical engagement, but will evangelize if it works

### Persona 4: Alex (Competitive Streamer / Content Creator)
- **Age / Background**: 22, streams Overwatch competitively, growing channel (500K followers)
- **Tech Comfort**: High (technical streaming setup, multi-monitor, OBS custom plugins)
- **Goals**:
  - Queue notifications integrated with stream alerts
  - Evidence/transparency (understand why a match was detected)
  - Control over sensitivity (don't want mobile push during matches)
- **Frustrations**:
  - Third-party tools lag or have false positives on camera overlays
  - No audit trail (why did the notification fire?)
  - Privacy concerns with cloud-based tools
- **Expected Usage**: Always streaming, needs Discord webhook + optional mobile push, wants calibration per resolution
- **Willingness**: Very high (early adopter, will test beta, may feature on stream)

### Persona 5: Casual Player (Control Group)
- **Age / Background**: Plays once a week, not pursuing rank
- **Tech Comfort**: Very low
- **Goals**: Play when time permits, zero setup friction
- **Frustrations**: Complexity, unnecessary features
- **Expected Usage**: Rare queueing, wants simple one-click notification
- **Willingness**: Low (not target user, but should not break their experience)

---

## 5. User Stories & Acceptance Criteria

### US-1: Download and Install Application
**As a** player  
**I want to** download the application and get it running with minimal setup  
**So that** I can start queueing immediately

**Acceptance Criteria:**
- [ ] Windows MSI installer is available on project GitHub
- [ ] Installation completes in <2 minutes
- [ ] Application appears in system tray after install
- [ ] Default settings (no Discord webhook) allow desktop notifications immediately
- [ ] First-run experience is <30 seconds

---

### US-2: Detect Queue State
**As a** player  
**I want to** the application to constantly monitor my Overwatch game window while I do other tasks  
**So that** I can focus on other activities without fear of missing a match

**Acceptance Criteria:**
- [ ] Application detects the Overwatch 2 game window (windowed fullscreen or fullscreen)
- [ ] Classifier returns QUEUE state within 1 second of input
- [ ] State updates every 500ms (configurable)
- [ ] CPU usage remains <10% single-digit during queue monitoring
- [ ] GPU usage is optional/burst-only (<5% 99th percentile)

---

### US-3: Detect Match Found
**As a** player  
**I want to** receive a notification within 1 second of a match starting  
**So that** I don't miss the hero select or loading screen

**Acceptance Criteria:**
- [ ] When Overwatch shows "MATCH FOUND" popup, notification fires within 1000ms
- [ ] Notification includes game state (MATCH_FOUND) with confidence score
- [ ] False positives <1 per busy queueing session (4 hours)
- [ ] Notification only fires once per match (no duplicate alerts)
- [ ] Works across all supported resolutions (1920×1080, 2560×1440, 3440×1440)

---

### US-4: Calibrate Per Resolution
**As a** player with a 2560×1440 monitor  
**I want to** calibrate the AI classifier for my specific screen resolution  
**So that** detection is accurate on my setup

**Acceptance Criteria:**
- [ ] Calibration wizard guides user through marking UI regions (e.g., "queue icon", "match found button")
- [ ] Application stores profiles per resolution
- [ ] Profiles are reloaded when resolution changes (e.g., alt-tab to different monitor)
- [ ] Calibration takes <5 minutes per resolution
- [ ] Saved profiles can be exported/shared

---

### US-5: View Detection History
**As a** player and creator  
**I want to** review recent detection events (timestamps, states, confidence, evidence)  
**So that** I can audit false positives or understand why a notification fired

**Acceptance Criteria:**
- [ ] Application maintains a local log of last 100 detections
- [ ] Log includes: timestamp, state, confidence, cropped evidence image
- [ ] UI allows filtering by state and date range
- [ ] Evidence images are shown with bounding boxes/annotations
- [ ] Log can be exported to JSON

---

### US-6: Test Notification
**As a** player  
**I want to** send a test desktop and Discord notification  
**So that** I can verify my configuration works

**Acceptance Criteria:**
- [ ] "Test Notification" button in settings fires a desktop notification immediately
- [ ] If Discord webhook is configured, also sends test message to Discord
- [ ] Test notification is clearly marked as test (not a real match)
- [ ] Both notifications fire within 2 seconds

---

### US-7: Performance Monitoring
**As a** technical user  
**I want to** see real-time CPU/GPU/memory usage stats  
**So that** I know the application isn't impacting my gaming performance

**Acceptance Criteria:**
- [ ] Tray window displays current CPU%, GPU%, memory usage
- [ ] Metrics update every 1 second
- [ ] Optional performance charts over last hour
- [ ] Alerts if CPU usage exceeds 15% sustained

---

## 6. User Flows

### Flow 1: Initial Setup

```
┌─────────────────────────────────────────────────────────┐
│  User Downloads & Installs                              │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Windows MSI Installer                                  │
│  - Adds application to system tray                       │
│  - Creates default config (no Discord webhook)           │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Application Boots (First Run)                           │
│  - Detects screen resolution                             │
│  - Checks for existing calibration profile               │
│  - If missing: suggests calibration wizard               │
└────────────────┬────────────────────────────────────────┘
                 │
          ┌──────┴──────┐
          ▼             ▼
     [Calibrate]   [Skip]
          │             │
          │             └───────────┐
          │                         │
          ▼                         ▼
    [Wizard runs]        [Uses default profile]
    [User marks UI                  │
     regions]                       │
          │                         │
          └────────────┬────────────┘
                       │
                       ▼
         ┌──────────────────────────────┐
         │  Ready: Display in Tray       │
         │  - State: IDLE or QUEUE       │
         │  - Monitoring: Active         │
         └──────────────────────────────┘
```

### Flow 2: Queue → Match Detection

```
User opens Overwatch 2 and queues for a match
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Application Monitors Window            Every 500ms      │
│  1. Capture cropped UI regions                           │
│  2. Run gate logic (pixel diff + heuristics)             │
│  3. If change detected: run AI classifier                │
│  4. Escalate if confidence <0.85                         │
└────────────────┬────────────────────────────────────────┘
                 │
          ┌──────┴──────┐
          ▼             ▼
    [State = QUEUE] [State = other]
          │             │
          │             └─→ [No action]
          │
          ▼
    [Application Idle]
    [Low CPU usage]
    [Update tray: "Queuing"]
                 │
                 ▼
  [Wait for screen change...]
                 │
                 ▼
 ┌────────────────────────────────┐
 │ Overwatch: "MATCH FOUND!"      │  (UI appears on screen)
 └────────────────┬───────────────┘
                  │
         ┌────────┴─────────┐
         │ (within 500ms)   │
         ▼                  ▼
    [Gate detects]    [Full screenshot
     major diff]      captured]
         │                  │
         └────┬─────────────┘
              │
              ▼
    ┌──────────────────────────┐
    │ Run AI Classifier        │
    │ Crop: Match Found button │
    │ Model: Tiny classifier   │
    │ Confidence: 0.94         │
    └────────┬─────────────────┘
             │
      ┌──────┴──────┐
      ▼             ▼
  [High conf]  [Low conf]
      │        [Run escalation
      │         model]────┐
      │                   │
      │                   ▼
      │        ┌──────────────────┐
      │        │ Escalation Model  │
      │        │ Confidence: 0.92  │
      │        └────┬─────────────┘
      │             │
      └─────┬───────┘
            ▼
    ┌──────────────────────────┐
    │ Decision: MATCH_FOUND    │
    │ Confidence: 0.94         │
    └────────┬─────────────────┘
             │
       ┌─────┴──────┐
       ▼            ▼
   [Log entry] [Check for duplicates
   stored]     (within 5s window)]
       │             │
       └─────┬───────┘
             ▼
    ┌──────────────────────────┐
    │ Send Notifications       │
    │ 1. Desktop notify        │
    │ 2. Discord webhook (if   │
    │    configured)           │
    └────────┬─────────────────┘
             │
             ▼
    ┌──────────────────────────┐
    │ Tray Updates:            │
    │ - State: MATCH_FOUND     │
    │ - Timestamp: HH:MM:SS    │
    │ - Last notif: ✓          │
    └──────────────────────────┘
```

### Flow 3: Settings

```
┌────────────────────────────┐
│ User Click: Settings       │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────────────┐
│ Settings Modal / Dashboard         │
│ - Notification frequency (test)    │
│ - Calibration per resolution       │
│ - Performance stats display        │
│ - Log viewer + export              │
└────────────┬───────────────────────┘
             │
             ▼
    ┌──────────────────────────────┐
    │ User Clicks: Test Notif      │
    └────────┬─────────────────────┘
             │
       ┌─────┴
       ▼       
  [Desktop]   
   notify]     
       │            
       │
       └──────┬
              │
              ▼
     ┌──────────────────────┐
     │ Both Notifications   │
     │ Fire (if no errors)  │
     └──────────────────────┘
```

---

## 7. Feature Prioritization (MoSCoW)

### MUST (MVP - Sprint 0-2)
- [ ] Game state detection (IDLE, QUEUE, MATCH_FOUND, HERO_SELECT, LOADING, IN_GAME)
- [ ] Desktop notifications on MATCH_FOUND
- [ ] Discord webhook notifications (optional in config)
- [ ] Calibration wizard per resolution (1920×1080, 2560×1440, 3440×1440)
- [ ] Tray application with state display
- [ ] Detection history logging (last 100 events)
- [ ] CPU usage <10% single-digit during monitoring
- [ ] False positives <1/hour during queue-heavy sessions
- [ ] Windows MSI installer + auto-update

### SHOULD (Sprint 3-4)
- [ ] Optional React dashboard with full detection history
- [ ] Export detection logs to JSON/CSV
- [ ] Evidence image browser (cropped UI regions for each detection)
- [ ] Performance metrics (CPU/GPU/memory real-time)
- [ ] Keyboard shortcut to open settings/tray
- [ ] Multi-profile support (day vs night modes)
- [ ] Customizable notification sounds

### COULD (Sprint 5-6, Uncertain ROI)
- [ ] Audio cue corroboration (detect notification sound from Overwatch)
- [ ] Mobile push notifications (via mobile app)
- [ ] Advanced explainability UI (show ML model reasoning)
- [ ] Integration with streaming software (auto-mute/unmute)
- [ ] Web dashboard for remote monitoring

### WON'T (Out of Scope v1)
- [ ] Game strategy automation (macro playing, climbing rank)
- [ ] Skin/cosmetic detection
- [ ] Cross-game queue monitoring (Valorant, CS2, etc.)
- [ ] Cloud sync of profiles
- [ ] AI-powered team composition analysis

---

## 8. Success Metrics & Goals

| Metric | Target | Measurement | Priority |
|--------|--------|-------------|----------|
| **Adoption** | 500 GitHub stars in 3 months | GitHub stars | High |
| **Daily Active Users** | 50 concurrent monitor sessions/day | Local telemetry | High |
| **Detection Latency (MATCH_FOUND)** | <1000ms from UI appearance | Log timestamps + frame analysis | Critical |
| **False Positive Rate** | <1 per 4-hour queue session | User reports + manual testing | Critical |
| **CPU Usage (Idle)** | <10% sustained, <5% p50 | System monitor integration | Critical |
| **GPU Usage (Optional)** | <5% burst, <1% idle | System monitor integration | Medium |
| **User Setup Time** | <2 minutes (download → notify) | First-run UX testing | High |
| **Notification Reliability** | 99% of MATCH_FOUND states detected | E2E test suite | Critical |
| **Discord Webhook Success Rate** | 99% post success (retry logic) | Webhook delivery logs | High |
| **Retention** | 70% of installers still running after 2 weeks | Auto-update telemetry | Medium |

---

## 9. Assumptions

1. **Overwatch window title** is always "Overwatch 2" on Windows (verified by SRS § 2.3)
2. **Resolution detection** is reliable via Windows Screen Capture API (DCE)
3. **Match Found UI** appears visibly on screen for ≥2 seconds (sufficient for detection)
4. **No game input automation** is required (out of scope, reduces ban risk)
5. **SQLite** is acceptable for local state storage (no internet requirement)
6. **Users have Discord** for webhook notifications (optional, not critical)
7. **Calibration per resolution** is user-acceptable friction (vs. one-shot ML model)
8. **INT8 quantization** maintains 95%+ accuracy vs. FP32 models (based on research)
9. **Local-only processing** is sufficient (no Overwatch API, no third-party ML services)
10. **Windows Defender / antivirus** does not flag AI inference (will validate during DevOps sprint)

---

## 10. Out of Scope (v1)

- MacOS / Linux support (Windows-only app, per SRS)
- Voice assistant integration (Cortana, etc.)
- Anti-cheat system interaction (read-only perception only)
- Real-time voice chat notifications (Discord handles this)
- Competitive rank predictions (not part of queue detection)
- Game patch analysis or meta tracking

---

## 11. Competitive Landscape

| Competitor | Strengths | Weaknesses |
|-----------|-----------|-----------|
| **Manual checking** | Guaranteed accuracy, no setup | Requires constant alt-tab, misses matches |
| **OW2 native sounds** | Free, built-in, no install | Doesn't work for alt-tab players, ambiguous |
| **Browser queue timer** | Shows estimated time | Inaccurate, requires manual refresh, web-only |
| **Third-party Windows tools** | Some have AI | Closed-source, privacy concerns, inconsistent accuracy |
| **Discord bots** | Integrates with Discord | Server-hosted, not real-time, high latency |
| **This app (OWN)** | Local AI, low latency, private, open-source | Requires calibration, Windows-only, new tool |

---

## 12. Version Roadmap

**v1.0 (MVP)** — Foundation + Core Features (4 sprints)
- Game state detection (6 states)
- Desktop + Discord notifications
- Tray UI with state display
- Calibration per resolution
- Windows MSI installer

**v1.1 (Polish)** — Quality & Reliability (2 sprints)
- E2E test suite (critical paths)
- Performance optimization (CPU <5% p50)
- Advanced evidence viewer
- Detailed error logging
- Auto-update mechanism

**v2.0 (Enhancement)** — Advanced Features (Q3 2026)
- Optional React dashboard
- Multi-profile support
- Mobile push notifications
- Audio cue corroboration
- API for third-party integrations

---

## 13. Next Steps

1. **Approve this spec** → Kickoff with Backend & Frontend leads
2. **Generate remaining specs** (Backend, Frontend, DB, QA, DevOps, etc.)
3. **Create detailed backlog** → Sprint 0: Foundation (15–20 points)
4. **Set up dev environment** → MCP scaffold + Electron skeleton
5. **First detection demo** → IDLE/QUEUE states on 1920×1080 (by end Sprint 0)
