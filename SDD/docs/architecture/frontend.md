# Frontend Architecture
## Overwatch AI Queue Detection & Notification App

**Generated**: February 6, 2026  
**Version**: 1.0

---

## Component Hierarchy: Atoms → Molecules → Organisms → Pages

```
App (Root)
│
├─── ErrorBoundary
│
├─── Providers
│    ├── GameStateProvider (Zustand)
│    ├── SettingsProvider (Context)
│    └── NotificationProvider (Toast library)
│
└─── RootLayout
     │
     ├─── TrayWindow
     │    │
     │    ├─── Header
     │    │    ├── TitleBar
     │    │    │  ├── AppTitle (atom)
     │    │    │  ├── MinimizeButton (atom)
     │    │    │  └── CloseButton (atom)
     │    │    │
     │    │    └── SettingsButton (atom)
     │    │
     │    ├─── TrayContent
     │    │    │
     │    │    ├─── StateDisplay (molecule)
     │    │    │    ├── StateIcon (atom)
     │    │    │    ├── StateBadge (atom: color-coded IDLE/QUEUE/MATCH_FOUND)
     │    │    │    └── ConfidenceProgress (atom: visual progress bar)
     │    │    │
     │    │    ├─── LastEventSection (molecule)
     │    │    │    ├── Timestamp (atom)
     │    │    │    ├── StateLabel (atom)
     │    │    │    └── ConfidenceValue (atom)
     │    │    │
     │    │    ├─── ActionBar (organism: button group)
     │    │    │    ├── TestNotificationButton (atom, click → notify service)
     │    │    │    ├── CalibrateButton (atom, click → open wizard)
     │    │    │    └── SettingsButton (atom, click → open modal)
     │    │    │
     │    │    └─── PerformanceMetrics (molecule, collapsible)
     │    │         ├── CPUMeter (atom)
     │    │         ├── GPUMeter (atom)
     │    │         └── MemoryMeter (atom)
     │    │
     │    └─── Footer
     │         └── StatusIndicator (atom: green=monitoring, red=paused)
     │
     ├─── SettingsModal
     │    │
     │    ├─── Modal Header (molecule)
     │    │    ├── Title (atom)
     │    │    └── CloseButton (atom)
     │    │
     │    ├─── TabNavigation (atom: horizontal tabs)
     │    │    ├── GeneralTab
     │    │    ├── DiscordTab
     │    │    ├── CalibrationTab
     │    │    ├── StatsTab
     │    │    └── LogsTab
     │    │
     │    ├─── TabContent
     │    │    │
     │    │    ├─── GeneralTab (organism)
     │    │    │    ├── AutoStartToggle (molecule)
     │    │    │    ├── NotificationSoundToggle (molecule)
     │    │    │    ├── ThemeSelector (molecule)
     │    │    │    └── LogLevelDropdown (molecule)
     │    │    │
     │    │    ├─── DiscordTab (organism)
     │    │    │    ├── WebhookURLInput (molecule: password-masked)
     │    │    │    ├── TestWebhookButton (atom)
     │    │    │    ├── WebhookStatusBadge (atom)
     │    │    │    └── InstructionsLink (atom)
     │    │    │
     │    │    ├─── CalibrationTab (organism)
     │    │    │    ├── ResolutionDisplay (molecule)
     │    │    │    ├── CurrentProfileStatus (atom)
     │    │    │    ├── CalibrateButton (atom)
     │    │    │    └── ProfileList (organism)
     │    │    │         └── ProfileListItem (molecule) × N
     │    │    │
     │    │    ├─── StatsTab (organism)
     │    │    │    ├── CPUMeter (molecule)
     │    │    │    ├── MemoryMeter (molecule)
     │    │    │    ├── UptimeDisplay (molecule)
     │    │    │    └── LatencyChart (organism)
     │    │    │
     │    │    └─── LogsTab (organism)
     │    │         ├── LogFilterBar (molecule)
     │    │         ├── DetectionLogTable (organism)
     │    │         │  └── DetectionLogRow (molecule) × N
     │    │         └── ExportButton (atom)
     │    │
     │    └─── Modal Footer (molecule)
     │         └── CloseButton (atom)
     │
     └─── CalibrationWizard (Modal, conditional render)
          │
          ├─── WizardStep1: Instructions
          │    ├── Title (atom)
          │    ├── Description (atom)
          │    └── NextButton (atom)
          │
          ├─── WizardStep2: Region Editor
          │    ├── CanvasEditor (organism: interactive image with draggable ROIs)
          │    │  ├── ScreenPreview (molecule)
          │    │  ├── RegionMarkers (atom × N: draggable rectangles)
          │    │  └── RegionLabels (atom × N)
          │    │
          │    ├── RegionListSidebar (molecule)
          │    │  └── RegionListItem (atom) × N
          │    │
          │    ├── BackButton (atom)
          │    └── NextButton (atom)
          │
          ├─── WizardStep3: Preview & Confirm
          │    ├── CropPreviewGrid (molecule)
          │    │  └── CropPreviewCard (molecule) × N
          │    │
          │    ├── ConfirmButton (atom)
          │    └── BackButton (atom)
          │
          └─── WizardStep4: Success
               ├── SuccessIcon (atom)
               ├── SuccessMessage (atom)
               └── DoneButton (atom)


Optional (v2):
Dashboard
├── DashboardLayout
│   ├── Sidebar (collapsible)
│   └── MainContent
│       │
│       ├── OverviewSection (organism)
│       │  ├── ProjectTitle (atom)
│       │  ├── ProjectDescription (atom)
│       │  └── TechStackBadges (molecule)
│       │
│       ├── ProgressSection (organism)
│       │  ├── ProgressRing (molecule: circular SVG)
│       │  ├── ProgressText (atom: X% done)
│       │  └── ProgressTimeline (organism)
│       │
│       └── StatsSection (organism)
│          ├── StatCard (molecule) × 4: total_tickets, done, in_progress, blocked
│          └── RecentTicketsTable (organism)
│             └── TicketRow (molecule) × N
```

---

## State Management: Global (Zustand) vs Local (React.useState)

### Global State (Zustand Store)

```typescript
// types/game.ts
export enum GameState {
  IDLE = "IDLE",
  QUEUE = "QUEUE",
  MATCH_FOUND = "MATCH_FOUND",
  HERO_SELECT = "HERO_SELECT",
  LOADING = "LOADING",
  IN_GAME = "IN_GAME",
}

export interface Detection {
  state: GameState;
  confidence: number;
  timestamp: Date;
  evidence?: {
    gateTriggered: boolean;
    gateSignals: { pixelDiffPct: number; histogramChange: number };
    classifierVersion: string;
    escalationUsed: boolean;
  };
}

// store/gameStore.ts
interface GameStore {
  // Current state
  currentState: GameState;
  currentConfidence: number;
  lastDetection: Detection | null;
  isMonitoring: boolean;
  
  // History (last 100)
  detectionHistory: Detection[];
  
  // Settings (persistent)
  discordWebhookUrl: string | null;
  notificationSoundEnabled: boolean;
  autoStartEnabled: boolean;
  theme: "system" | "light" | "dark";
  
  // Performance metrics
  cpuUsage: number;
  gpuUsage: number;
  memoryUsage: number;
  uptime: number; // seconds
  
  // Methods
  setState: (state: GameState, confidence: number) => void;
  addDetection: (detection: Detection) => void;
  setDiscordUrl: (url: string) => void;
  setMonitoring: (enabled: boolean) => void;
  updateMetrics: (cpu: number, gpu: number, mem: number) => void;
  clearHistory: () => void;
}

export const useGameStore = create<GameStore>(
  persist(
    (set) => ({
      currentState: GameState.IDLE,
      currentConfidence: 0,
      lastDetection: null,
      isMonitoring: true,
      detectionHistory: [],
      discordWebhookUrl: null,
      notificationSoundEnabled: true,
      autoStartEnabled: false,
      theme: "system",
      cpuUsage: 0,
      gpuUsage: 0,
      memoryUsage: 0,
      uptime: 0,
      
      setState: (state, confidence) => set({
        currentState: state,
        currentConfidence: confidence,
      }),
      
      addDetection: (detection) => set((state) => ({
        lastDetection: detection,
        detectionHistory: [detection, ...state.detectionHistory].slice(0, 100),
      })),
      
      // ... other methods
    }),
    {
      name: "ow-queue-notifier-store", // localStorage key
      partialize: (state) => ({
        // Persist only settings + theme
        discordWebhookUrl: state.discordWebhookUrl,
        notificationSoundEnabled: state.notificationSoundEnabled,
        autoStartEnabled: state.autoStartEnabled,
        theme: state.theme,
      }),
    }
  )
);
```

### Local Component State (React.useState)

```typescript
// Components/SettingsModal.tsx
export const SettingsModal: React.FC<Props> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<"general" | "discord" | "calibration">("general");
  const [discordUrl, setDiscordUrl] = useState("");
  const [isValidating, setIsValidating] = useState(false);
  const [webhookError, setWebhookError] = useState<string | null>(null);
  
  // Local to this modal
  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <Tabs activeTab={activeTab} onChange={setActiveTab}>
        {/* tabs... */}
      </Tabs>
    </Modal>
  );
};

// Components/CalibrationWizard.tsx
export const CalibrationWizard: React.FC = () => {
  const [currentStep, setCurrentStep] = useState<1 | 2 | 3 | 4>(1);
  const [regions, setRegions] = useState<CalibrationRegion[]>([]);
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null);
  
  // Local to wizard
  const handleNextStep = () => setCurrentStep((s) => (s + 1) as any);
  
  return (
    <WizardContainer>
      {currentStep === 1 && <Step1 onNext={handleNextStep} />}
      {currentStep === 2 && <Step2 regions={regions} setRegions={setRegions} onNext={handleNextStep} />}
      {/* ... */}
    </WizardContainer>
  );
};
```

---

## Complete Routing Table

| Route | Component | Window Type | Lazy? | Guard | Description |
|-------|-----------|-------------|-------|-------|-------------|
| `/tray` | TrayWindow | Main tray window (380×540) | No | — | Always-on status display (cannot be lazy, always loaded) |
| `/settings` | SettingsModal | Overlay modal | No | — | Settings panel, triggered from tray button |
| `/calibration/:step` | CalibrationWizard | Overlay modal | Yes | — | Multi-step calibration, triggered from settings |
| `/dashboard` | Dashboard | Separate window (1200×800) | Yes | — | Optional v2: project stats, detection history |
| `/logs` | DetectionLogViewer | Overlay modal | Yes | — | Full detection + notification log viewer |
| `/about` | AboutDialog | Modal | No | — | License, version, credits |

**Notes**:
- `/tray` is the primary window; all modals are children rendered inside it
- Electron `BrowserWindow` for separate windows (dashboard)
- Lazy load modals to reduce initial bundle size

---

## Design System Tokens

### Colors (Dark Theme)

```css
/* root-level CSS variables */
:root {
  /* Semantic backgrounds */
  --color-bg-primary: #0f172a;      /* slate-950, main bg */
  --color-bg-secondary: #1e293b;    /* slate-800, card bg */
  --color-bg-elevated: #334155;     /* slate-700, hovered card */
  --color-bg-overlay: rgba(0, 0, 0, 0.7); /* modal backdrop */
  
  /* Text */
  --color-text-primary: #f1f5f9;    /* slate-100, main text */
  --color-text-secondary: #cbd5e1;  /* slate-300, secondary text */
  --color-text-muted: #94a3b8;      /* slate-400, muted/meta text */
  --color-text-disabled: #64748b;   /* slate-500, disabled state */
  
  /* Semantic colors */
  --color-primary: #3b82f6;         /* blue-500, Overwatch brand */
  --color-success: #10b981;         /* emerald-500, MATCH_FOUND */
  --color-warning: #f59e0b;         /* amber-500, uncertain conf */
  --color-error: #ef4444;           /* red-500, errors/disconnected */
  --color-info: #06b6d4;            /* cyan-500, info messages */
  
  /* Borders */
  --color-border: rgba(255, 255, 255, 0.08);       /* subtle */
  --color-border-strong: rgba(255, 255, 255, 0.12); /* prominent */
  
  /* State-specific */
  --color-state-idle: #94a3b8;             /* muted gray */
  --color-state-queue: #f59e0b;            /* amber */
  --color-state-match-found: #10b981;      /* emerald */
  --color-state-hero-select: #3b82f6;      /* blue */
  --color-state-loading: #a855f7;          /* purple */
  --color-state-in-game: #10b981;          /* emerald */
}
```

### Typography

```css
:root {
  /* Font families */
  --font-sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-mono: "JetBrains Mono", "Courier New", monospace;
  
  /* Font sizes (base 16px = 1rem) */
  --text-xs: 0.75rem;    /* 12px */
  --text-sm: 0.875rem;   /* 14px */
  --text-base: 1rem;     /* 16px */
  --text-lg: 1.125rem;   /* 18px */
  --text-xl: 1.25rem;    /* 20px */
  --text-2xl: 1.5rem;    /* 24px */
  
  /* Font weights */
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  
  /* Line heights */
  --line-height-tight: 1.2;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;
}
```

### Spacing Scale

```css
:root {
  --space-0: 0;
  --space-1: 4px;      /* 0.25rem */
  --space-2: 8px;      /* 0.5rem */
  --space-3: 12px;     /* 0.75rem */
  --space-4: 16px;     /* 1rem */
  --space-5: 20px;     /* 1.25rem */
  --space-6: 24px;     /* 1.5rem */
  --space-8: 32px;     /* 2rem */
  --space-10: 40px;    /* 2.5rem */
  --space-12: 48px;    /* 3rem */
}
```

### Border Radii & Shadows

```css
:root {
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --radius-full: 9999px;
  
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
}
```

---

## Summary

Frontend uses:
- **Electron + React** for native desktop UI
- **Zustand** for global game state (persisted to localStorage)
- **React.useState** for local modal/wizard state
- **Lucide React** for icons
- **Tailwind CSS + CSS variables** for consistent dark theme design system
- **Responsive breakpoints** for tray window (380px fixed width × variable height)
- **Modal-driven UX**: settings, calibration, logs as overlays, not separate routes
