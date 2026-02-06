# UI Designer Specification
## Overwatch AI Queue Detection & Notification App

**Generated**: February 6, 2026  
**Version**: 1.0  
**Status**: Draft → Screen Design

---

## 1. Complete Screen Inventory

### Windows / Screens

| Screen | Type | Purpose | Flows | States |
|--------|------|---------|-------|--------|
| **1. Tray Window (Main)** | Windows | Always-on status bar, quick actions | App launch → minimize | idle, queue, match_found, hero_select, loading, in_game |
| **2. Settings Modal** | Modal | Discord webhook, calibration, logs | Tray → Settings btn | General, Discord, Calibration, Stats, Logs tabs |
| **3. Calibration Wizard** | Modal (Multi-step) | Guide user through region marking | Settings tab → "Calibrate" | Step 1–4: Instruction, Region Editor, Preview, Complete |
| **4. Notification Toast** | Transient | Match found alert (3–5 sec) | Auto on MATCH_FOUND state | Default, action-available |
| **5. Dashboard (Optional v2)** | Window | Full project stats, detection history | Tray → Dashboard link | All sprints, tickets, backlog |
| **6. About / License** | Dialog | Open-source credits, version | Settings → "About" | Single view |

---

## 2. Wireframe Descriptions (Detailed)

### Screen 1: Tray Window (Main, 380×540 px)

```
┌──────────────────────────────────────┐
│  ⚙ Settings         [−] [x]           │  ← Header: title, minimize, close
├──────────────────────────────────────┤
│                                       │
│  State Badge                          │
│  ┌──────────────────────────────────┐│
│  │  ⏸ QUEUE                         ││  ← State icon + label
│  │  Confidence: 87%                  ││  ← Confidence percentage
│  │  ━━━━━━━━━━━━━━━━━━━━━━━ 87%    ││  ← Progress bar
│  └──────────────────────────────────┘│
│                                       │
│  Last Event Section                   │
│  ┌──────────────────────────────────┐│
│  │  Last detected:                   ││
│  │  14:30:45 — QUEUE                ││
│  │  Confidence: 87%                  ││
│  └──────────────────────────────────┘│
│                                       │
│  Action Buttons                       │
│  ┌────────────────┬─────────────────┐│
│  │ 🧪 Test Notif  │ 🔄 Calibrate    ││
│  └────────────────┴─────────────────┘│
│                                       │
│  Footer Stats                         │
│  ┌──────────────────────────────────┐│
│  │ CPU: 8% | GPU: 0% | Memory: 120MB││
│  └──────────────────────────────────┘│
│                                       │
│  Status: Monitoring (green indicator)  │
│                                       │
│ [⚙ Settings] [❌ Exit]                │  ← Footer buttons
│                                       │
└──────────────────────────────────────┘
```

**Key interactions**:
- State badge: Click to expand → show evidence (crops, confidence per region)
- Progress bar: Visual confidence (green >80%, yellow 60–80%, red <60%)
- "Test Notif": Sends test desktop + Discord notifications
- "Calibrate": Opens Calibration Wizard modal

---

### Screen 2: Settings Modal (Tabs, 600×700 px)

#### Tab 1: General

```
Settings — General
├─ Auto-start with Windows    [Toggle On/Off]
├─ Notification sound enabled [Toggle On/Off]
├─ Theme                      [System/Light/Dark]
├─ Log level                  [Debug/Info/Warn/Error]
└─ Download logs              [  Export JSON  ]
```

#### Tab 2: Discord

```
Settings — Discord
├─ Discord Webhook URL:       [Enter URL (masked)]
│  └─ (Link to Discord instructions)
├─ Test Webhook               [  Send Test  ]
├─ Status: ① Connected / ② Failed
│  └─ Error: "Invalid webhook URL"
└─ Last successful:           "14:30:45"
```

#### Tab 3: Calibration

```
Settings — Calibration
├─ Detected Resolution:       1920×1080
├─ Current Profile:           ✓ Calibrated (2 weeks ago)
├─ Actions:
│  ├─ Delete Profile          [  Delete  ]
│  └─ Re-calibrate            [  Start Wizard  ]
│
├─ Available Profiles:
│  ├─ 1920×1080 (current)     [Use] [Delete]
│  ├─ 2560×1440               [Use] [Delete]
│  └─ 3440×1440               [Use] [Delete]
```

#### Tab 4: Stats

```
Settings — Performance Stats
Status: Monitoring (✓ Active)

CPU Usage:              ████░░░░░░ 8%  (Target: <10%)
GPU Usage (optional):   ░░░░░░░░░░ 0%  (Not enabled)
Memory:                 ████████░░ 125 MB / 250 MB max

Inference Latency:
├─ Avg: 42 ms
├─ P95: 58 ms
├─ Max: 150 ms

Uptime:                 3 days, 5 hours
Last detection:         2 minutes ago
```

#### Tab 5: Logs

```
Settings — Detection History
Latest 100 detections
┌─────────────────────────────────────────────────┐
│ Filter: [All States ▼] [All Dates ▼] 🔍 Search │
├─────────────────────────────────────────────────┤
│ 14:30:45 │ QUEUE        │ 87% │ [→ View evidence]
│ 14:20:12 │ IDLE         │ 92% │ [→ View evidence]
│ 14:15:33 │ QUEUE        │ 81% │ [→ View evidence]
│ 13:45:20 │ MATCH_FOUND  │ 94% │ [→ View evidence]
│          │              │     │
│ [← Previous] [Next →]       [Export JSON]
└─────────────────────────────────────────────────┘
```

---

### Screen 3: Calibration Wizard (Modal, 700×600 px, 4 Steps)

#### Step 1: Instructions

```
Calibration Wizard — Step 1 of 4
┌──────────────────────────────────────────┐
│  Calibrate for Your Screen               │
│  ─────────────────────────────────────   │
│  This process takes ~5 minutes.           │
│                                          │
│  We'll mark key UI regions on your       │
│  Overwatch window. This helps us         │
│  accurately detect queue states.         │
│                                          │
│  Your resolution: 1920 × 1080            │
│                                          │
│  Ready?                                  │
│                                          │
│  [ ← Back ] [ Skip ] [ Next → ]         │
└──────────────────────────────────────────┘
```

#### Step 2: Region Editor (Interactive)

```
Calibration Wizard — Step 2 of 4
Region Editor
┌──────────────────────────────────────────────────┐
│  Live Overwatch Screenshot                       │
│  ┌────────────────────────────────────────────┐ │
│  │                                             │ │
│  │   Queue Status Area                     ⚪ │ │  ← Current frame
│  │   ┌──────────────────────────────────────┐ │ │
│  │   │ [Click + drag to mark]                │ │ │
│  │   └──────────────────────────────────────┘ │ │
│  │                                             │ │
│  │   Match Found Button (if visible)       ⚪ │ │
│  │   ┌──────────────────────────────────────┐ │ │
│  │   │ [Click + drag to mark]                │ │ │
│  │   └──────────────────────────────────────┘ │ │
│  │                                             │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  Regions marked: 2 / 2                          │
│  ✓ Queue Status  ✓ Match Found Button           │
│                                                  │
│  [ ← Back ] [ Next → ]                         │
└──────────────────────────────────────────────────┘
```

#### Step 3: Preview & Confirm

```
Calibration Wizard — Step 3 of 4
Review Calibration
┌──────────────────────────────────────────┐
│  Your regions:                            │
│                                           │
│  ✓ Queue Status:                         │
│    Bounds: 45% left, 25% top             │
│    Size: 10% × 10%                       │
│                                           │
│  ✓ Match Found Button:                   │
│    Bounds: 40% left, 40% top             │
│    Size: 20% × 20%                       │
│                                           │
│  These will be saved for 1920 × 1080.    │
│                                           │
│  Looks good?                              │
│                                           │
│  [ ← Back ] [ Save & Close ] [ Skip ...]│
│                                           │
└──────────────────────────────────────────┘
```

#### Step 4: Complete

```
Calibration Wizard — Step 4 of 4
Success! ✓
┌──────────────────────────────────────────┐
│                                           │
│       ✓ Calibration Saved                │
│                                           │
│  Profile for 1920 × 1080 is ready.       │
│                                           │
│  Queue detection will now be optimized   │
│  for your screen.                        │
│                                           │
│  You can re-calibrate anytime from       │
│  Settings → Calibration.                 │
│                                           │
│  [ Close ]                               │
│                                           │
└──────────────────────────────────────────┘
```

---

### Screen 4: Notification Toast (Transient, 400×100 px)

```
┌────────────────────────────────────┐
│ 🎮  MATCH FOUND!                   │  ← Toast appears bottom-right
│ Your team has found a match.       │     Duration: 3–5 seconds
│ Confidence: 94%                    │     Auto-dismisses
│ [ ► Play Now ] [ ✕ Dismiss ]      │
└────────────────────────────────────┘
```

---

## 3. Component States & Variations

### State Badge States

| State | Icon | Label | Color | Animation |
|-------|------|-------|-------|-----------|
| **IDLE** | ⏹ | IDLE | Gray (#94a3b8) | None |
| **QUEUE** | ⏸ | QUEUE | Amber (#f59e0b) | Pulse (2s) |
| **MATCH_FOUND** | ✓ | MATCH FOUND! | Emerald (#10b981) | Pulse + bounce (1s) |
| **HERO_SELECT** | 🎯 | HERO SELECT | Blue (#3b82f6) | None |
| **LOADING** | ⌛ | LOADING | Purple (#a855f7) | Spinner (1s) |
| **IN_GAME** | ▶ | IN GAME | Emerald (#10b981) | None |

### Buttons (Default → Hover → Active → Disabled)

```
Primary Button: Settings, Calibrate, Test Notif
├─ Default:  bg-blue, text-white, shadow
├─ Hover:    bg-blue-600, shadow-lg, scale(1.02)
├─ Active:   bg-blue-700, scale(0.98)
└─ Disabled: opacity 0.5, cursor-not-allowed

Secondary Button: Skip, Back
├─ Default:  border, text-gray, no background
├─ Hover:    border-gray, bg-gray-50
├─ Active:   border-gray-600
└─ Disabled: opacity 0.5
```

### Input Field: Discord Webhook URL

```
Label: "Discord Webhook URL"
Field: [Enter URL (masked: https://discordapp...)]
       [Show/Hide toggle]
Help:  "Link to Discord webhook instructions"
Error: "Invalid URL format" (red text) if validation fails
Success: "Connected ✓" (green checkmark)
```

---

## 4. Responsive Design Breakpoints

| Breakpoint | Width | Window Size | Use Case |
|-----------|-------|-------------|----------|
| **Mobile** | <640px | Tray window on small display | Very tight (not primary target, defer) |
| **Tablet** | 640–1024px | Tray on split-screen or tablet | Secondary consideration |
| **Desktop** | >1024px | Standard monitor | Primary target (1920×1080+) |

**v1.0 Focus**: Desktop only (Windows 10/11, 1920×1080+)  
**v2.0 + Consideration**: Mobile responsive (dashboard)

---

## 5. Design Tokens (Repeated from Frontend Spec for Self-Containment)

### Colors (Dark Theme)

```css
--color-bg-primary: #0f172a      /* slate-950 */
--color-bg-secondary: #1e293b    /* slate-800 */
--color-bg-elevated: #334155     /* slate-700 */
--color-text-primary: #f1f5f9    /* slate-100 */
--color-text-secondary: #cbd5e1  /* slate-300 */
--color-text-muted: #94a3b8      /* slate-400 */
--color-primary: #3b82f6         /* blue-500 (Overwatch accent) */
--color-success: #10b981         /* emerald-500 (match found) */
--color-warning: #f59e0b         /* amber-500 (queue) */
--color-error: #ef4444           /* red-500 (disconnected) */
```

### Typography

```
Headings (h1–h3):       Inter, 600–700 weight
Body text:              Inter, 400–500 weight, line-height 1.5
Monospace (code/logs):  JetBrains Mono, 400 weight
Base size:              16px (1 rem)
```

### Spacing

```
4px (0.25rem) — tight padding
8px (0.5rem) — standard padding
12px (0.75rem) — medium space
16px (1rem) — large space
24px (1.5rem) — section gap
```

### Border Radius & Shadows

```
Buttons/cards:          6–10px radius
Modal:                  10–16px radius
Focus rings:            2px blue outline
Shadows:                sm (0.05 opacity black)
                        md (0.1 opacity) on cards
                        lg (0.15 opacity) on nav
```

---

## 6. Interaction Patterns

### Navigation / Tab Switching (Settings Modal)

```
User clicks "General" tab:
1. Tab highlights (blue underline)
2. Content fades out (200ms)
3. New content fades in (200ms)
4. No page reload (instant response)
```

### Region Selection (Calibration Wizard Step 2)

```
User drags to select region:
1. Mouse down on screenshot
2. Blue rectangle appears, follows cursor (live feedback)
3. On mouse up: Region locked, labeled, small handle visible
4. Can re-drag by handle or delete via X button
```

### Notification Toast (Match Found)

```
Automatic appearance:
1. Toast slides in from bottom-right (300ms, ease-out)
2. Stays visible for 4 seconds
3. Optional: User clicks [✕ Dismiss] to close immediately
4. Auto-dismiss after timer expires (fade out, 300ms)
```

---

## 7. Accessibility (WCAG 2.1 AA)

- [ ] **Color Contrast**: All text ≥4.5:1 (WCAG AA), state icons + labels
- [ ] **Focus Management**: Tab key navigates all buttons, blue 2px focus ring
- [ ] **Keyboard Shortcuts**: 
  - `Escape` = close modal
  - `Tab` = cycle through tabs/buttons
  - `Enter` = click selected button
- [ ] **Screen Reader Support**:
  - State badge: `aria-label="Queue status, confidence 87%"`
  - Buttons: descriptive text, no icon-only
  - Progress bar: `aria-valuenow`, `aria-valuemin`, `aria-valuemax`
- [ ] **Reduced Motion**: Respect `prefers-reduced-motion` (disable animations)
- [ ] **High Contrast Mode**: Themes adapt to Windows high-contrast settings

---

## 8. Animation Principles

### Micro-Interactions (Keep Light)

- **Confidence progress bar**: Fills smoothly (200ms linear)
- **Pulse on QUEUE**: Scale 1.0 → 1.05 → 1.0 (2s loop, subtle)
- **Bounce on MATCH_FOUND**: Slide-in from bottom (300ms, cubic-bezier), then bounce
- **Fade transitions**: All fades 200–300ms (ease-in-out)
- **Disabled state**: Fade to 50% opacity (no animation)

### Accessibility: Respect prefers-reduced-motion

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0ms !important;
  }
}
```

---

## 9. Development Notes

- **Framework**: Electron (React Renderer)
- **Styling**: Tailwind CSS + CSS modules
- **Icons**: Lucide React (open-source, consistent)
- **Fonts**: Inter (variable), JetBrains Mono (code)

---

## 10. Next Steps

1. ✅ **UI Designer spec approved** → Create component library (Sprint 0)
2. ⏭️ **Design system tokens** → Tailwind config (Sprint 0)
3. ⏭️ **High-fidelity mockups** → Figma designs per screen (Sprint 0)
4. ⏭️ **Accessibility audit** → WCAG checklist (Sprint 2)
5. ⏭️ **Usability testing** → Test with 5 users during beta (Sprint 3)

**Owner**: UI Designer  
**Stakeholders**: Frontend Lead, Product Manager, QA Lead
