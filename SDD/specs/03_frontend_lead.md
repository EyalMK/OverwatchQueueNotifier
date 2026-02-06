# Frontend Lead Specification
## Overwatch AI Queue Detection & Notification App

**Generated**: February 6, 2026  
**Version**: 1.0  
**Status**: Draft → Technical Foundation

---

## 1. Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Framework** | Electron 28 (main + renderer) | Windows desktop app, quick dev tools |
| **Renderer** | React 18 + TypeScript | Component-driven UI, optional dashboard |
| **Build Tool** | Vite 4 (React preset) | Fast HMR, minimal config for Electron |
| **CSS** | Tailwind CSS + CSS-in-JS | Dark theme, design system consistency |
| **State Management** | Zustand (lightweight) | Global: auth state, game state, settings |
| **HTTP Client** | Axios + custom interceptors | IPC to backend, error handling |
| **Forms** | React Hook Form | Lightweight, calibration wizard forms |
| **Validation** | Zod | Runtime type validation, Discord webhook URL |
| **Icons** | Lucide React + custom SVGs | Overwatch theme, tray icons |
| **Testing** | Vitest + Playwright | Unit, E2E with mock Electron |
| **Development** | concurrently (npm run dev) | Main and renderer run in parallel |

---

## 2. Component Hierarchy: Atoms → Molecules → Organisms → Pages

```
App (Root)
│
├─── Providers
│    ├── GameStateProvider (Zustand)
│    ├── SettingsProvider
│    └── NotificationProvider
│
├─── TrayWindow (Electron: preload IPC)
│    │
│    ├─── Header
│    │    └── MinimizeButton, SettingsButton
│    │
│    └─── TrayContent
│         ├─── StateDisplay
│         │    ├── StateIcon (IDLE, QUEUE, MATCH_FOUND, etc.)
│         │    ├── StateBadge
│         │    └── ConfidenceProgress
│         │
│         ├─── LastEventSection
│         │    ├── Timestamp
│         │    └── StateLabel
│         │
│         └─── ActionBar
│              ├── TestNotificationButton
│              ├── SettingsButton
│              └── ExitButton
│
├─── SettingsModal (if open)
│    │
│    ├─── Tabs: [General, Discord, Calibration, Stats, Logs]
│    │
│    ├─── GeneralTab
│    │    ├── AutoStartCheckbox
│    │    ├── NotificationSoundToggle
│    │    └── ThemeSelector
│    │
│    ├─── DiscordTab
│    │    ├── WebhookURLInput (password-masked)
│    │    ├── TestWebhookButton
│    │    └── WebhookStatusBadge
│    │
│    ├─── CalibrationTab
│    │    ├── ResolutionDisplay (detected)
│    │    ├── CalibrateButton (launches wizard)
│    │    └── CalibrationProfileList
│    │
│    ├─── StatsTab
│    │    ├── CPUMeter
│    │    ├── GPUMeter
│    │    ├── MemoryMeter
│    │    └── Uptime
│    │
│    └─── LogsTab
│         ├── LogFilterBar (state, date range)
│         ├── DetectionLogTable
│         └── ExportButton
│
└─── CalibrationWizard (Modal if triggered)
     │
     ├─── Step 1: Instructions
     ├─── Step 2: Mark Regions (interactive canvas)
     │    └── RegionEditor (drag to select, label)
     ├─── Step 3: Preview & Confirm
     └─── Step 4: Success & Save Profile


Optional (Dashboard in separate window/route):
Dashboard
├── ProjectOverview
│   ├── ProjectTitle, Tagline
│   ├── TechStackBadges
│   └── QuickStats
│
├── SprintInfo
│   ├── ProgressRing (% done)
│   ├── SprintCards (current + next)
│   └── TicketSummary
│
└── BacklogViewer
    └── (complex, see viewer spec)
```

---

## 3. State Management: Global vs Local

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
    cropRegions: { name: string; coords: [number, number, number, number] }[];
    modelUsed: string;
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
  
  // History
  detectionHistory: Detection[];
  
  // Settings
  discordWebhookUrl: string | null;
  notificationSoundEnabled: boolean;
  autoStartEnabled: boolean;
  
  // Performance
  cpuUsage: number;
  gpuUsage: number;
  memoryUsage: number;
  
  // Methods
  setState: (state: GameState, confidence: number) => void;
  addDetection: (detection: Detection) => void;
  setDiscordUrl: (url: string) => void;
  setMonitoring: (enabled: boolean) => void;
  updatePerformanceMetrics: (...) => void;
}

// Usage
export const useGameStore = create<GameStore>((set) => ({
  currentState: GameState.IDLE,
  // ... rest of store
}));
```

### Local Component State (React.useState)

```typescript
// Components/SettingsModal.tsx
const [activeTab, setActiveTab] = useState<"general" | "discord" | "calibration">("general");
const [discordUrl, setDiscordUrl] = useState("");
const [isValidating, setIsValidating] = useState(false);
const [webhookError, setWebhookError] = useState<string | null>(null);
```

---

## 4. Complete Routing Table

| Route | Component | Auth? | Lazy Load? | Description |
|-------|-----------|-------|-----------|-------------|
| `/tray` | TrayWindow | N/A | No | Always-on tray pop-up (always loaded) |
| `/settings` | SettingsModal | N/A | No | Settings, discord, calibration (modal overlay) |
| `/calibration/:step` | CalibrationWizard | N/A | Yes | Multi-step calibration wizard |
| `/dashboard` | Dashboard | N/A | Yes | Optional: project overview, stats (separate window) |
| `/logs` | DetectionLogViewer | N/A | Yes | Detection history viewer |

**Note**: Tray app is single-window model. Additional windows (dashboard) open separately via Electron `BrowserWindow`.

---

## 5. Design System Tokens

### Colors (Dark Theme, Tailwind Slots)

```css
/* OverwatchQueueNotifier.css */
:root {
  /* Backgrounds */
  --color-bg-primary: #0f172a;      /* slate-950 */
  --color-bg-secondary: #1e293b;    /* slate-800 */
  --color-bg-elevated: #334155;     /* slate-700 */
  
  /* Text */
  --color-text-primary: #f1f5f9;    /* slate-100 */
  --color-text-secondary: #cbd5e1;  /* slate-300 */
  --color-text-muted: #94a3b8;      /* slate-400 */
  
  /* Semantic */
  --color-primary: #3b82f6;         /* blue-500 - Overwatch accent */
  --color-success: #10b981;         /* emerald-500 - match found */
  --color-warning: #f59e0b;         /* amber-500 - low confidence */
  --color-error: #ef4444;           /* red-500 - disconnected */
  --color-info: #06b6d4;            /* cyan-500 - info */
  
  /* Borders */
  --color-border: rgba(255, 255, 255, 0.08);
  --color-border-strong: rgba(255, 255, 255, 0.12);
  
  /* State-specific */
  --color-state-idle: #94a3b8;      /* muted */
  --color-state-queue: #f59e0b;     /* amber */
  --color-state-match-found: #10b981; /* emerald */
  --color-state-hero-select: #3b82f6; /* blue */
  --color-state-loading: #a855f7;   /* purple */
  --color-state-in-game: #10b981;   /* emerald */
}
```

### Typography

```css
/* Font scales (rem = 1 = 16px base) */
:root {
  --text-xs: 0.75rem;     /* 12px */
  --text-sm: 0.875rem;    /* 14px */
  --text-base: 1rem;      /* 16px */
  --text-lg: 1.125rem;    /* 18px */
  --text-xl: 1.25rem;     /* 20px */
  --text-2xl: 1.5rem;     /* 24px */
  
  --font-body: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI";
  --font-mono: "JetBrains Mono", "Courier New", monospace;
  
  --font-weight-normal: 400;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  
  --line-height-tight: 1.3;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;
}
```

### Spacing Scale (8px Grid)

```css
:root {
  --spacing-0: 0;
  --spacing-1: 0.25rem;   /* 4px */
  --spacing-2: 0.5rem;    /* 8px */
  --spacing-3: 0.75rem;   /* 12px */
  --spacing-4: 1rem;      /* 16px */
  --spacing-6: 1.5rem;    /* 24px */
  --spacing-8: 2rem;      /* 32px */
  --spacing-12: 3rem;     /* 48px */
  --spacing-16: 4rem;     /* 64px */
}
```

### Border Radius & Shadows

```css
:root {
  --radius-sm: 0.375rem;   /* 6px */
  --radius-md: 0.625rem;   /* 10px */
  --radius-lg: 1rem;       /* 16px */
  --radius-full: 9999px;
  
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.15);
}
```

---

## 6. Form Handling Pattern (Calibration Wizard)

```typescript
// hooks/useCalibrationForm.ts
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const calibrationSchema = z.object({
  resolution: z.string().regex(/^\d+x\d+$/),
  queueIconRegion: z.object({
    x: z.number().min(0).max(1),
    y: z.number().min(0).max(1),
    width: z.number().min(0).max(1),
    height: z.number().min(0).max(1),
  }),
  matchFoundRegion: z.object({
    x: z.number().min(0).max(1),
    y: z.number().min(0).max(1),
    width: z.number().min(0).max(1),
    height: z.number().min(0).max(1),
  }),
});

type CalibrationFormData = z.infer<typeof calibrationSchema>;

export const useCalibrationForm = () => {
  const {
    control,
    handleSubmit,
    watch,
    formState: { errors, isValid },
  } = useForm<CalibrationFormData>({
    resolver: zodResolver(calibrationSchema),
    mode: "onChange",
  });

  const onSubmit = async (data: CalibrationFormData) => {
    try {
      await api.saveCalibrationProfile(data);
      // Success handling
    } catch (error) {
      // Error display
    }
  };

  return { control, onSubmit: handleSubmit(onSubmit), errors, isValid };
};
```

---

## 7. API Client Abstraction

```typescript
// lib/apiClient.ts
import axios, { AxiosInstance, AxiosError } from "axios";

interface ApiResponse<T> {
  data: T;
  status: number;
  error?: { code: string; message: string };
}

class ApiClient {
  private client: AxiosInstance;

  constructor(baseURL = "ipc://backend") {
    // For Electron, use IPC to communicate with main process
    this.client = axios.create({
      baseURL,
      timeout: 5000,
    });

    // Add interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error(`API Error: ${error.response?.status}`, error.response?.data);
        // Dispatch error notification
        return Promise.reject(error);
      }
    );
  }

  async perceiveState(resolution: string): Promise<ApiResponse<Detection>> {
    return this.client.post("/screen/perceive-state", { resolution });
  }

  async sendTestNotification(): Promise<ApiResponse<{ notificationId: string }>> {
    return this.client.post("/notify/test-desktop");
  }

  async saveCalibrationProfile(data: CalibrationData): Promise<ApiResponse<{ profileId: string }>> {
    return this.client.post("/calibration/save", data);
  }

  async getDetectionHistory(limit = 100): Promise<ApiResponse<Detection[]>> {
    return this.client.get(`/history?limit=${limit}`);
  }
}

export const apiClient = new ApiClient();
```

---

## 8. Performance Targets (Web Vitals + Custom)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **LCP (Largest Contentful Paint)** | <2.5s from tray click | Electron devtools timing |
| **FID (First Input Delay)** | <100ms | Interaction timing |
| **CLS (Cumulative Layout Shift)** | <0.1 | No unexpected shifts |
| **Settings Modal Open** | <300ms | Time to interactive |
| **Calibration Wizard Load** | <500ms | Time to interactive |
| **Memory Footprint** | <150 MB (tray idle) | Task Manager |
| **Memory Footprint (dashboard open)** | <250 MB | Task Manager |
| **Frame Rate (animations)** | 60 FPS | Chrome devtools (Electron) |
| **Bundle Size** | <500 KB (gzipped) | webpack-bundle-analyzer |

---

## 9. Electron Integration

### IPC Communication (Preload Bridge)

```typescript
// preload.ts
import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld("electronAPI", {
  // Invoke backend MCP tools
  perceiveState: (resolution: string) =>
    ipcRenderer.invoke("backend:perceive-state", { resolution }),

  // Listen for backend events
  onGameStateChanged: (callback: (state: GameState) => void) =>
    ipcRenderer.on("backend:state-changed", (_event, state) => callback(state)),

  // Control tray window
  minimize: () => ipcRenderer.send("window:minimize"),
  close: () => ipcRenderer.send("window:close"),

  // System
  getScreenResolution: () => ipcRenderer.invoke("system:screen-resolution"),
  openConsoleDevtools: () => ipcRenderer.send("devtools:open"),
});

declare global {
  interface Window {
    electronAPI: typeof electronAPI;
  }
}
```

### Main Process (Electron Main)

```typescript
// main.ts
import { app, BrowserWindow, ipcMain, Tray, Menu } from "electron";
import { spawn } from "child_process";

let trayWindow: BrowserWindow;
let backendProcess: ChildProcess;

app.on("ready", () => {
  // Spawn backend process
  backendProcess = spawn("python", ["backend/src/main.py"]);

  // Create tray window
  trayWindow = new BrowserWindow({
    width: 380,
    height: 540,
    webPreferences: { preload: path.join(__dirname, "preload.ts") },
  });

  trayWindow.loadURL(`file://${__dirname}/dist/index.html#/tray`);

  // IPC handlers
  ipcMain.handle("backend:perceive-state", async (_event, { resolution }) => {
    // Call backend service via stdio or HTTP
    const result = await backendClient.perceiveState(resolution);
    return result;
  });
});
```

---

## 10. Testing Strategy (Unit + E2E)

### Unit Tests (Vitest)

```typescript
// __tests__/components/StateDisplay.test.tsx
import { render, screen } from "@testing-library/react";
import { StateDisplay } from "@/components/StateDisplay";
import { GameState } from "@/types/game";

describe("StateDisplay", () => {
  it("renders state icon for MATCH_FOUND", () => {
    render(<StateDisplay state={GameState.MATCH_FOUND} confidence={0.94} />);
    expect(screen.getByTestId("state-icon-match-found")).toBeInTheDocument();
  });

  it("displays confidence as percentage", () => {
    render(<StateDisplay state={GameState.QUEUE} confidence={0.87} />);
    expect(screen.getByText("87%")).toBeInTheDocument();
  });
});
```

### E2E Tests (Playwright)

```typescript
// e2e/tray-notifications.spec.ts
import { test, expect } from "@playwright/test";

test("should display notification on MATCH_FOUND state", async ({ page }) => {
  await page.goto("app://tray");

  // Simulate backend sending MATCH_FOUND
  await page.evaluate(() => {
    window.electronAPI.onGameStateChanged("MATCH_FOUND");
  });

  // Verify UI updated
  await expect(page.getByTestId("state-badge")).toContainText("MATCH FOUND");
  await expect(page.getByTestId("notification-toast")).toBeVisible();
});
```

---

## 11. Accessibility (WCAG 2.1 AA)

- [ ] All buttons/links have focus indicators (2px outline, blue)
- [ ] Text contrast ratios ≥4.5:1 on text, ≥3:1 on large text
- [ ] Keyboard navigation fully supported (Tab, Enter, Escape)
- [ ] ARIA labels on all icons and interactive elements
- [ ] Screen reader announcements for state changes (`aria-live="polite"`)
- [ ] No color alone used to convey information (state icons + labels)
- [ ] Animations respect `prefers-reduced-motion`

---

## 12. Development Workflow

```bash
# Install dependencies
npm install

# Run both main and renderer processes
npm run dev

# Build for production
npm run build

# Package as Windows MSI
npm run dist

# Type checking
npm run type-check

# Format & lint
npm run format
npm run lint
```

---

## 13. Next Steps

1. ✅ **Frontend spec approved** → Design lead reads this
2. ⏭️ **Electron scaffold** → Main + renderer boilerplate
3. ⏭️ **Tray window** → StateDisplay + basic layout
4. ⏭️ **IPC bridge** → Communicate with backend
5. ⏭️ **Settings modal** → Discord webhook input
6. ⏭️ **Calibration wizard** → 4-step form for region marking

**Owner**: Frontend Lead  
**Stakeholders**: UI Designer, Backend Lead, QA Lead
