
# Software Requirements Specification (SRS)
## Overwatch AI Queue Detection & Notification App

---

## 1. Introduction

### 1.1 Purpose
This document specifies the requirements for a Windows-only desktop application that detects Overwatch 2 queue and match states using AI-based screen perception and notifies the user in real time.

The SRS is intended to serve as a **single source of truth** for spec-driven development (AutoSpec-style) and to guide agent-based implementation using MCP and Strands Agents SDK.

### 1.2 Scope
The system monitors the Overwatch 2 game window, classifies the current game state using minimal-overhead AI inference, and sends notifications when a match is found.

### 1.3 Definitions
- **State**: One of the predefined game phases (IDLE, QUEUE, MATCH_FOUND, etc.)
- **Evidence**: Visual artifacts (cropped images, detected text) supporting a classification
- **Gate**: Ultra-low-cost pre-check that decides whether AI inference should run
- **MCP**: Model Context Protocol (tool interface layer)
- **Agent**: Strands agent responsible for orchestration, perception, or notification

---

## 2. Overall Description

### 2.1 Product Perspective
The application is a local-first Windows tray application consisting of:
- Tray UI
- Local MCP servers (screen perception, notifications)
- Strands-based agent orchestration
- Lightweight AI inference pipeline

No cloud services are required for MVP functionality.

### 2.2 User Characteristics
- PC gamer using Overwatch 2
- Frequently alt-tabs while queueing
- Sensitive to false-positive notifications
- Uses Discord

### 2.3 Operating Environment
- OS: Windows 10 / Windows 11
- Supported resolutions:
  - 1920×1080
  - 2560×1440
  - 3440×1440
- GPU optional; CPU-only operation must be supported
- Windowed fullscreen or fullscreen modes

### 2.4 Constraints
- CPU usage must remain near-idle during queue monitoring
- GPU usage must be negligible and burst-based only
- All perception must be local (privacy constraint)
- No interaction with game input (no automation)

---

## 3. System Features

### 3.1 Game State Detection

#### Description
The system shall classify the current Overwatch game state using AI-based screen perception.

#### States
- IDLE
- QUEUE
- MATCH_FOUND
- HERO_SELECT
- LOADING
- IN_GAME

#### Functional Requirements
- FR-1: The system shall return a state classification every perception cycle.
- FR-2: Each classification shall include a confidence score (0.0–1.0).
- FR-3: Each classification shall include evidence metadata.
- FR-4: MATCH_FOUND must be detected within 1 second of appearance.

### 3.2 AI Perception Pipeline

#### Design Requirements
- DR-1: The system shall use a tiered perception pipeline:
  1. Always-on gate (cheap diff / heuristics)
  2. Tiny AI classifier (frequent)
  3. Escalation AI (rare)
- DR-2: Full-frame inference is prohibited.
- DR-3: Cropped regions shall be resolution-normalized.
- DR-4: INT8 quantization shall be used where possible.
- DR-5: 1-bit inference is optional and non-blocking.

### 3.3 Calibration

#### Description
The system shall calibrate UI anchor regions per resolution.

#### Functional Requirements
- FR-5: The system shall detect the Overwatch window.
- FR-6: The system shall compute relative crop regions (0–1 normalized).
- FR-7: Profiles shall be saved per resolution.

### 3.4 Notifications

#### Description
Notify the user when a match is found.

#### Functional Requirements
- FR-8: Desktop notification shall be sent on MATCH_FOUND.
- FR-9: Discord webhook notification shall be sent on MATCH_FOUND.
- FR-10: Notifications shall fire only once per match.
- FR-11: Notification retries must respect rate limits.

### 3.5 Tray Application

#### Description
Minimal always-on tray UI.

#### Functional Requirements
- FR-12: Display current state and confidence.
- FR-13: Display last event timestamp.
- FR-14: Provide “Test Notification” action.
- FR-15: Provide access to calibration.

---

## 4. External Interface Requirements

### 4.1 MCP Interfaces

#### screen.perceive_state
Input:
- Cropped image regions
Output:
- state
- confidence
- evidence

#### screen.capture_regions
- Captures defined UI regions

#### notify.desktop
- Sends Windows notification

#### notify.discord
- Sends Discord webhook message

### 4.2 User Interface
- Tray icon
- Simple dashboard (optional MVP)
- Evidence viewer for last detection

---

## 5. Non-Functional Requirements

### 5.1 Performance
- CPU usage: single-digit percentage during idle queue
- GPU usage: optional, burst-only
- Detection latency: <1s for MATCH_FOUND

### 5.2 Reliability
- False positives <1/hour during queue-heavy sessions
- Debounce and hysteresis required

### 5.3 Privacy & Security
- No full-screen storage
- Cropped evidence only (optional debug)
- Discord secrets stored securely

### 5.4 Maintainability
- Tool contracts must be versioned
- Models must be swappable without agent changes

---

## 6. Acceptance Criteria

- All supported resolutions pass calibration
- MATCH_FOUND reliably detected across UI scale changes
- No duplicate notifications per match
- Application remains responsive and low-overhead

---

## 7. Future Enhancements (Non-MVP)

- Audio cue corroboration
- Multi-profile policies (night mode, streaming)
- Advanced explainability UI
- Optional mobile push notifications

---

## 8. Appendix

### A. State Transition Summary
IDLE → QUEUE → MATCH_FOUND → HERO_SELECT → LOADING → IN_GAME → IDLE

### B. Glossary
- **Gate**: Low-cost signal to trigger AI inference
- **Evidence**: Visual justification for AI decision
