# Sprint 2: Frontend Scaffold & Calibration UI Sprint Execution Prompt
## Overwatch AI Queue Detection & Notification App

---

## Context — Read These Files First

You are executing **AutoSpec Spec-Driven Development** for Sprint 2: Frontend Scaffold & Calibration UI.

**Sprint Goal**: Build a functional Electron tray app with settings modal (5 tabs) and interactive calibration wizard. Backend perception engine from Sprint 1 is ready; this sprint delivers the UI layer.

### SPECS (Single source of truth — READ ALL)
- `specs/03_frontend_lead.md` **[PRIMARY]** — Tech stack, component hierarchy, state management, routing, design system tokens
- `specs/10_ui_designer.md` — Design tokens (colors, typography, spacing), accessibility (WCAG 2.1 AA), responsive design
- `specs/01_product_manager.md` — User stories, personas (context for why features matter)

### BACKLOG & EXECUTION GUIDES
- `specs/backlog.md` — Sprint 2 section (11 tickets, 35 points chosen scope, Weeks 6–8)
- `sprint_prompts/sprint-1-backend.md` — Reference for template structure, patterns
- `workflows/development.md` — Ticket workflow (pick → test → implement → merge)
- `workflows/sprint-execution.md` — Daily standups, review process, velocity tracking

### ARCHITECTURE DOCS
- `docs/architecture/frontend.md` — Electron + React layering, IPC bridge, component patterns
- `docs/architecture/database.md` — SQLite calibration_profiles table (from Sprint 0)
- `docs/testing/strategy.md` — Test pyramid, unit vs e2e, accessibility testing

### API REFERENCE
- `docs/api/reference.md` — Backend endpoints perceive_state, capture_regions, notify.desktop

---

## Sprint 1 → Sprint 2 Handoff

### What Sprint 1 Completed ✅
- Gate heuristics fully tuned (pixel diff %, histogram divergence, resolution-aware thresholds)
- ONNX classifier pipeline (ShuffleNet-V2 primary, EfficientNet-Lite4 escalation)
- MCP endpoints functional (perceive_state, capture_regions return real data; notify.desktop fires desktop notifications)
- State transition machine (4 states: IDLE → QUEUE → MATCH_FOUND → IN_GAME, idempotent guards)
- Detection logging + 24h retention cleanup
- Comprehensive backend testing (85%+ coverage)

### What Sprint 2 Must Deliver ✅
- **Electron Main Process** (boot & IPC bridge to backend HTTP)
- **Tray Window UI** (display live game state with confidence)
- **Settings Modal** (5 tabs: General, Discord, Calibration, Stats, Logs)
- **Calibration Wizard** (4-step interactive region editor)
- **Component Library** (StateIcon, ConfidenceBar, NotificationToast, etc.)
- **State Management** (Zustand store with localStorage persistence)
- **Comprehensive Testing** (>75% coverage on all React components)
- **WCAG 2.1 AA** (keyboard navigation, focus management, ARIA labels)
- **Performance Verified** (<2s startup time target)

### Critical Blockers from Sprint 1 ✅ RESOLVED
**Backend API Endpoints Ready** (Sprint 1 complete):
- `POST /mcp/tools/screen.perceive_state` → Returns game state + confidence
- `POST /mcp/tools/screen.capture_regions` → Returns cropped UI regions as base64
- `POST /mcp/tools/notify.desktop` → Fires Windows toast notification
- MCP server listening on `localhost:5000` (configurable via env)
- Rate limiting: 10 req/sec per IP
- All endpoints documented + tested

---

## Architecture Decisions (Sprint 2 Specific)

### Decision 1: Communication Protocol
**CHOSEN**: HTTP Polling to `localhost:5000`
- Frontend makes HTTP requests to backend
- Simpler than IPC pipes; leverages existing backend HTTP server
- Preload script proxy via `electronAPI.perceiveState()` (IPC wrapper around fetch)
- Trade-off: Tight coupling to localhost; will be decoupled in future via environment variables

### Decision 2: Electron Main Process Location
**CHOSEN**: `frontend/src/main-electron.ts`
- Single monorepo approach; one `npm run build` step compiles both
- Vite handles renderer (React); tsc handles main process
- Benefits: Single package.json, shared tsconfig
- Alternative considered: `electron/` root folder (rejected for complexity)

### Decision 3: Calibration Profile Persistence
**CHOSEN**: Hybrid (localStorage + SQLite)
- **Sprint 2**: Save to localStorage (instant UI feedback)
- **Sprint 3** (INTEGRATION-002): Persist to SQLite for durability across app restarts
- Benefits: Fast UX in Sprint 2; can add database persistence without breaking UI in Sprint 3
- localStorage key: `calibration_<resolution>` (e.g., `calibration_1920x1080`)

### Decision 4: Scope
**CHOSEN**: 35 story points (balanced)
- **P0 tickets** (28 pts): FRONTEND-001, 002, 003, 004, 005, 008 (core features + tests)
- **P1 tickets** (7 pts selected): FRONTEND-006, 007, 010 (State Badge, Toast, Accessibility)
- **Deferred** (3 pts): FRONTEND-009 (hot reload), FRONTEND-011 (perf optimization) → Pick up if velocity allows

---

## Phase Breakdown: Foundation → Components → Integration → Testing

### Phase 1: Electron Bootstrap & IPC (Days 1–2, 11 points)
**Goal**: Electron app launches, preload script bridges backend HTTP calls, perceive_state polling works.

#### 1.1: Project Setup & Dependencies (No Story Points - Setup)
**Owner**: Frontend  
**Dependency**: SETUP-010 complete (Vite configured)

- [ ] Install missing dependencies:
  ```bash
  cd frontend
  npm install electron@^28.0.0 electron-builder@^24.6.4 \
    react-hook-form@^7.48.0 zod@^3.22.0 lucide-react@^0.292.0 \
    concurrently@^8.0.0
  npm install --save-dev @axe-core/react playwright @testing-library/react @testing-library/jest-dom
  ```

- [ ] Create [frontend/.env.example](frontend/.env.example):
  ```env
  VITE_MCP_SERVER_URL=http://127.0.0.1:5000
  VITE_MCP_SERVER_TIMEOUT=5000
  VITE_APP_VERSION=1.0.0
  ```

- [ ] Create [frontend/.env.local](frontend/.env.local) (dev):
  ```env
  VITE_MCP_SERVER_URL=http://127.0.0.1:5000
  ```

- [ ] Update [frontend/tsconfig.json](frontend/tsconfig.json):
  - Add Electron DOM types:
    ```json
    "compilerOptions": {
      "types": ["electron", "vite/client", "node"],
      "lib": ["ES2020", "DOM", "DOM.Iterable"]
    }
    ```

- [ ] Update [frontend/vite.config.ts](frontend/vite.config.ts):
  ```typescript
  export default defineConfig({
    plugins: [react()],
    optimizeDeps: {
      exclude: ['electron', 'electron-preload']
    }
  });
  ```

- [ ] Update [frontend/package.json](frontend/package.json) build scripts:
  ```json
  "scripts": {
    "dev": "concurrently \"cross-env NODE_ENV=development electron . --dev\" \"vite\"",
    "build": "vite build && tsc src/main-electron.ts --outDir dist --declaration",
    "start": "electron .",
    "typecheck": "tsc --noEmit",
    "lint": "eslint src/ --fix", 
    "test": "vitest",
    "test:ui": "vitest --ui"
  },
  "main": "dist/main-electron.js",
  "homepage": "/",
  "build": {
    "appId": "com.overwatchqueuenotifier.app",
    "productName": "Overwatch Queue Notifier",
    "files": ["dist/**/*", "node_modules/**/*"]
  }
  ```

- [ ] Verify Tailwind setup in [frontend/tailwind.config.cjs](frontend/tailwind.config.cjs):
  - Dark theme already configured ✓
  - State colors (IDLE, QUEUE, MATCH_FOUND, etc.) already defined ✓

---

#### 1.2: FRONTEND-001 — Electron Main Process + IPC Bridge [5 pts]
**Owner**: Frontend  
**Dependency**: 1.1 complete

Implement Electron app lifecycle and IPC preload.

**1.2a: Main Process**
- [ ] Create [frontend/src/main-electron.ts](frontend/src/main-electron.ts):
  ```typescript
  import { app, BrowserWindow, ipcMain, Menu, Tray } from 'electron';
  import path from 'path';
  import isDev from 'electron-is-dev';

  let mainWindow: BrowserWindow | null = null;
  let tray: Tray | null = null;

  function createWindow() {
    mainWindow = new BrowserWindow({
      width: 1024,
      height: 600,
      alwaysOnTop: true,
      frame: true,
      show: false,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        enableRemoteModule: false,
        preload: path.join(__dirname, 'preload.js')
      }
    });

    const url = isDev 
      ? 'http://localhost:5173' 
      : `file://${path.join(__dirname, '../index.html')}`;
    
    mainWindow.loadURL(url);
    
    if (isDev) {
      mainWindow.webContents.openDevTools();
    }

    mainWindow.on('close', () => {
      mainWindow = null;
    });

    mainWindow.on('minimize', () => {
      mainWindow?.hide();
    });

    return mainWindow;
  }

  app.on('ready', () => {
    createWindow();
    createTrayIcon();
  });

  app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
      app.quit();
    }
  });

  function createTrayIcon() {
    const iconPath = path.join(__dirname, '../assets/tray-icon.png');
    tray = new Tray(iconPath);
    
    const contextMenu = Menu.buildFromTemplate([
      { label: 'Open', click: () => mainWindow?.show() },
      { label: 'Settings', click: () => mainWindow?.webContents.send('open-settings') },
      { type: 'separator' },
      { label: 'Exit', click: () => app.quit() }
    ]);

    tray.setContextMenu(contextMenu);
    tray.on('double-click', () => mainWindow?.show());
  }
  ```

- [ ] Implement IPC handlers in main process:
  ```typescript
  // In main process, after createWindow():
  ipcMain.handle('perceive-state', async (event, resolution: string) => {
    try {
      const response = await fetch(
        `${process.env.VITE_MCP_SERVER_URL}/mcp/tools/screen.perceive_state`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ resolution })
        }
      );
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      return { error: error.message };
    }
  });

  ipcMain.handle('test-notification', async () => {
    // Call backend notify.desktop endpoint
  });

  ipcMain.handle('save-calibration-profile', async (event, profile) => {
    // Save to localStorage via preload privilege
  });

  ipcMain.handle('get-screen-resolution', async () => {
    const { width, height } = require('electron').screen.getPrimaryDisplay().workAreaSize;
    return { width, height };
  });

  ipcMain.handle('minimize-window', () => {
    mainWindow?.minimize();
  });

  ipcMain.handle('close-window', () => {
    mainWindow?.close();
  });
  ```

- [ ] **Reference**: specs/03_frontend_lead.md (Section 2: Component Hierarchy), docs/architecture/frontend.md (Electron setup)

**1.2b: Preload Script (Context Bridge)**
- [ ] Create [frontend/src/preload.ts](frontend/src/preload.ts):
  ```typescript
  import { contextBridge, ipcRenderer, IpcRendererEvent } from 'electron';
  
  interface Detection {
    state: string;
    confidence: number;
    escalated: boolean;
    evidence_image_base64: string;
    detected_at: string;
  }

  interface CalibrationProfile {
    resolution: string;
    regions: { [key: string]: { x: number; y: number; width: number; height: number } };
  }

  const electronAPI = {
    perceiveState: (resolution: string): Promise<Detection> =>
      ipcRenderer.invoke('perceive-state', resolution),

    testNotification: (): Promise<{ success: boolean }> =>
      ipcRenderer.invoke('test-notification'),

    saveCalibrationProfile: (profile: CalibrationProfile): Promise<void> =>
      ipcRenderer.invoke('save-calibration-profile', profile),

    getScreenResolution: (): Promise<{ width: number; height: number }> =>
      ipcRenderer.invoke('get-screen-resolution'),

    minimizeWindow: (): void =>
      ipcRenderer.invoke('minimize-window'),

    closeWindow: (): void =>
      ipcRenderer.invoke('close-window'),

    onOpenSettings: (callback: () => void) => {
      const subscription = (event: IpcRendererEvent) => callback();
      ipcRenderer.on('open-settings', subscription);
      return () => ipcRenderer.removeListener('open-settings', subscription);
    }
  };

  contextBridge.exposeInMainWorld('electronAPI', electronAPI);

  declare global {
    interface Window {
      electronAPI: typeof electronAPI;
    }
  }
  ```

- [ ] Create type definitions [frontend/src/types/electron.ts](frontend/src/types/electron.ts):
  ```typescript
  export interface Detection {
    state: string;
    confidence: number;
    escalated: boolean;
    evidence_image_base64: string;
    detected_at: string;
  }

  export interface CalibrationProfile {
    resolution: string;
    regions: { [key: string]: { x: number; y: number; width: number; height: number } };
  }

  declare global {
    interface Window {
      electronAPI: {
        perceiveState: (resolution: string) => Promise<Detection>;
        testNotification: () => Promise<{ success: boolean }>;
        saveCalibrationProfile: (profile: CalibrationProfile) => Promise<void>;
        getScreenResolution: () => Promise<{ width: number; height: number }>;
        minimizeWindow: () => void;
        closeWindow: () => void;
        onOpenSettings: (callback: () => void) => () => void;
      };
    }
  }
  ```

**1.2c: Update Frontend Startup**
- [ ] Update [frontend/src/main.tsx](frontend/src/main.tsx):
  ```typescript
  import React from 'react'
  import ReactDOM from 'react-dom/client'
  import App from './App.tsx'
  import './index.css'

  ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  )
  ```
  (Keep existing structure; Electron loads this as renderer)

**1.2d: Test Electron Bootstrap**
- [ ] Create [frontend/src/__tests__/main-electron.test.ts](frontend/src/__tests__/main-electron.test.ts):
  ```typescript
  import { describe, it, expect, vi } from 'vitest';
  
  describe('Electron Main Process', () => {
    it('should have context bridge exposed', () => {
      // Mock Electron environment
      expect(typeof window.electronAPI).toBe('object');
      expect(typeof window.electronAPI.perceiveState).toBe('function');
      expect(typeof window.electronAPI.closeWindow).toBe('function');
    });

    it('perceiveState should call IPC handler', async () => {
      const mockIPC = vi.spyOn(window.electronAPI, 'perceiveState');
      // Mock implementation
      mockIPC.mockResolvedValueOnce({
        state: 'IDLE',
        confidence: 0.95,
        escalated: false,
        evidence_image_base64: 'iVBOR...',
        detected_at: new Date().toISOString()
      });

      const result = await window.electronAPI.perceiveState('1920x1080');
      expect(result.state).toBe('IDLE');
      expect(mockIPC).toHaveBeenCalledWith('1920x1080');
    });
  });
  ```

- [ ] Manual test: `npm run dev` → Electron window appears, TrayWindow component visible

- **Reference**: specs/03_frontend_lead.md (Section 1: Tech Stack), Electron security best practices
- **Verification**:
  ```bash
  npm run dev
  # Expected: Electron window opens showing React app (TrayWindow)
  # No errors in console
  # Tray icon visible in system tray
  ```

---

### Phase 2: Core UI Components (Days 3–10, 21 points)
**Goal**: Build reusable components, integrate with Zustand store.

#### 2.1: FRONTEND-002 — Tray Icon + Menu [3 pts]
**Owner**: Frontend  
**Dependency**: FRONTEND-001 complete

- [ ] Create tray icon assets:
  - [frontend/src/assets/tray-icon.png](frontend/src/assets/tray-icon.png) (32×32, Overwatch blue #3b82f6)
  - [frontend/src/assets/tray-icon-dark.png](frontend/src/assets/tray-icon-dark.png) (light theme variant)

- [ ] Already implemented in FRONTEND-001 main process: `createTrayIcon()`
  - Right-click context menu: Open, Settings, Exit
  - Double-click: Show window
  - No additional work needed (integrated above)

- [ ] Update [frontend/src/pages/TrayWindow.tsx](frontend/src/pages/TrayWindow.tsx):
  - Wire up header buttons: Minimize, Settings, Close
  - Minimize button: Call `window.electronAPI.minimizeWindow()`
  - Close button: Call `window.electronAPI.closeWindow()`
  - Settings button: Call `window.electronAPI.onOpenSettings()` (or toggle local state)

- [ ] Unit test:
  ```typescript
  describe('TrayWindow Header', () => {
    it('should minimize on button click', () => {
      const mockMinimize = vi.spyOn(window.electronAPI, 'minimizeWindow');
      render(<TrayWindow />);
      fireEvent.click(screen.getByLabelText('Minimize'));
      expect(mockMinimize).toHaveBeenCalled();
    });
  });
  ```

- **Verification**: Tray menu shows on right-click; clicking "Settings" opens modal

---

#### 2.2: FRONTEND-006 — State Icon + Confidence Bar [2 pts]
**Owner**: Frontend  
**Dependency**: FRONTEND-001 complete

- [ ] Create [frontend/src/components/StateIcon.tsx](frontend/src/components/StateIcon.tsx):
  ```typescript
  import { Circle, AlertCircle, CheckCircle, Zap, Loader, Play } from 'lucide-react';
  import { GameState } from '../types/game';

  interface StateIconProps {
    state: GameState;
    size?: 'sm' | 'md' | 'lg';
  }

  const STATE_ICON_MAP = {
    [GameState.IDLE]: <Circle className="text-gray-400" />,
    [GameState.QUEUE]: <AlertCircle className="text-amber-500" />,
    [GameState.MATCH_FOUND]: <CheckCircle className="text-emerald-500" />,
    [GameState.HERO_SELECT]: <Zap className="text-blue-500" />,
    [GameState.LOADING]: <Loader className="text-purple-500 animate-spin" />,
    [GameState.IN_GAME]: <Play className="text-emerald-500" />,
  };

  const SIZE_MAP = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  export function StateIcon({ state, size = 'md' }: StateIconProps) {
    return (
      <div className={SIZE_MAP[size]} aria-label={`Game state: ${state}`}>
        {STATE_ICON_MAP[state]}
      </div>
    );
  }
  ```

- [ ] Create [frontend/src/components/ConfidenceBar.tsx](frontend/src/components/ConfidenceBar.tsx):
  ```typescript
  import { GameState } from '../types/game';

  interface ConfidenceBarProps {
    confidence: number;  // 0.0 - 1.0
    state: GameState;
  }

  const STATE_COLOR_MAP: Record<GameState, string> = {
    [GameState.IDLE]: 'bg-gray-400',
    [GameState.QUEUE]: 'bg-amber-500',
    [GameState.MATCH_FOUND]: 'bg-emerald-500',
    [GameState.HERO_SELECT]: 'bg-blue-500',
    [GameState.LOADING]: 'bg-purple-500',
    [GameState.IN_GAME]: 'bg-emerald-500',
  };

  const getConfidenceLabel = (conf: number) => {
    if (conf < 0.70) return 'Low';
    if (conf < 0.85) return 'Medium';
    return 'High';
  };

  export function ConfidenceBar({ confidence, state }: ConfidenceBarProps) {
    const percentage = Math.round(confidence * 100);
    const label = getConfidenceLabel(confidence);

    return (
      <div className="w-full">
        <div className="flex justify-between items-center mb-1">
          <span className="text-xs text-gray-300">Confidence</span>
          <span className="text-xs font-semibold text-gray-100">
            {percentage}% ({label})
          </span>
        </div>
        <div className="w-full h-1 bg-gray-700 rounded-full overflow-hidden">
          <div
            className={`h-full ${STATE_COLOR_MAP[state]} transition-all duration-300`}
            style={{ width: `${percentage}%` }}
            role="progressbar"
            aria-valuenow={percentage}
            aria-valuemin={0}
            aria-valuemax={100}
          />
        </div>
      </div>
    );
  }
  ```

- [ ] Update [frontend/src/pages/TrayWindow.tsx](frontend/src/pages/TrayWindow.tsx):
  ```typescript
  import { StateIcon } from '../components/StateIcon';
  import { ConfidenceBar } from '../components/ConfidenceBar';
  import { useGameStore } from '../store/gameStore';

  export function TrayWindow() {
    const { currentState, currentConfidence, lastDetection } = useGameStore();

    return (
      <div className="p-4">
        <div className="flex items-center gap-4 mb-4">
          <StateIcon state={currentState} size="lg" />
          <div className="flex-1">
            <h2 className="text-xl font-bold text-white">{currentState}</h2>
            <ConfidenceBar confidence={currentConfidence} state={currentState} />
          </div>
        </div>
        {lastDetection && (
          <p className="text-xs text-gray-400">
            Last: {new Date(lastDetection.detected_at).toLocaleTimeString()}
          </p>
        )}
      </div>
    );
  }
  ```

- [ ] Unit tests:
  ```typescript
  describe('StateIcon', () => {
    it('should render correct icon for each state', () => {
      Object.values(GameState).forEach((state) => {
        render(<StateIcon state={state} />);
        expect(screen.getByLabelText(`Game state: ${state}`)).toBeInTheDocument();
      });
    });
  });

  describe('ConfidenceBar', () => {
    it('should display correct percentage and label', () => {
      render(<ConfidenceBar confidence={0.92} state={GameState.QUEUE} />);
      expect(screen.getByText('92% (High)')).toBeInTheDocument();
    });

    it('should have correct aria attributes', () => {
      render(<ConfidenceBar confidence={0.75} state={GameState.QUEUE} />);
      const progressBar = screen.getByRole('progressbar');
      expect(progressBar).toHaveAttribute('aria-valuenow', '75');
    });
  });
  ```

- **Verification**: TrayWindow displays state icon and colored confidence bar

---

#### 2.3: FRONTEND-003 — Settings Modal with 5 Tabs [8 pts]
**Owner**: Frontend  
**Dependency**: FRONTEND-001, FRONTEND-006 complete

Largest feature. Implement tab-based settings UI.

**2.3a: Tab Container**
- [ ] Create [frontend/src/components/Tabs.tsx](frontend/src/components/Tabs.tsx):
  ```typescript
  import React, { useState } from 'react';

  interface Tab {
    id: string;
    label: string;
    icon?: React.ReactNode;
    content: React.ReactNode;
  }

  interface TabsProps {
    tabs: Tab[];
    defaultTab?: string;
  }

  export function Tabs({ tabs, defaultTab }: TabsProps) {
    const [activeTab, setActiveTab] = useState(defaultTab || tabs[0].id);

    return (
      <div className="flex flex-col h-full">
        <div className="flex border-b border-gray-700 gap-2 px-4 pt-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3 py-2 text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'text-blue-500 border-b-2 border-blue-500'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
              role="tab"
              aria-selected={activeTab === tab.id}
              aria-controls={`panel-${tab.id}`}
            >
              {tab.icon && <span className="inline-block mr-2">{tab.icon}</span>}
              {tab.label}
            </button>
          ))}
        </div>
        <div className="flex-1 overflow-auto px-4 py-4">
          {tabs.map((tab) => (
            <div
              key={tab.id}
              id={`panel-${tab.id}`}
              role="tabpanel"
              aria-labelledby={tab.id}
              className={activeTab === tab.id ? 'block' : 'hidden'}
            >
              {tab.content}
            </div>
          ))}
        </div>
      </div>
    );
  }
  ```

**2.3b: General Tab**
- [ ] Create [frontend/src/components/SettingsModal/GeneralTab.tsx](frontend/src/components/SettingsModal/GeneralTab.tsx):
  ```typescript
  import { useGameStore } from '../../store/gameStore';
  import { ToggleSwitch } from '../ToggleSwitch';
  import { useState } from 'react';

  export function GeneralTab() {
    const { notificationSoundEnabled, autoStartEnabled, setNotificationSound, setAutoStart } = useGameStore();
    const [lastTestTime, setLastTestTime] = useState<Date | null>(null);

    const handleTestNotification = async () => {
      try {
        const result = await window.electronAPI.testNotification();
        if (result.success) {
          setLastTestTime(new Date());
        }
      } catch (error) {
        console.error('Test notification failed:', error);
      }
    };

    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <label className="text-sm text-gray-200">Play notification sound</label>
          <ToggleSwitch
            checked={notificationSoundEnabled}
            onChange={setNotificationSound}
          />
        </div>

        <div className="flex items-center justify-between">
          <label className="text-sm text-gray-200">Auto-start at login</label>
          <ToggleSwitch
            checked={autoStartEnabled}
            onChange={setAutoStart}
          />
        </div>

        <div className="pt-4 border-t border-gray-700">
          <button
            onClick={handleTestNotification}
            className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm"
          >
            Test Notification
          </button>
          {lastTestTime && (
            <p className="text-xs text-gray-400 mt-2">
              Last test: {lastTestTime.toLocaleTimeString()}
            </p>
          )}
        </div>
      </div>
    );
  }
  ```

**2.3c: Discord Tab**
- [ ] Create [frontend/src/components/SettingsModal/DiscordTab.tsx](frontend/src/components/SettingsModal/DiscordTab.tsx):
  ```typescript
  import { useState } from 'react';
  import { useGameStore } from '../../store/gameStore';
  import { z } from 'zod';

  const webhookSchema = z.string().url().includes('discord.com/api/webhooks');

  export function DiscordTab() {
    const { discordWebhookUrl, setDiscordWebhookUrl } = useGameStore();
    const [input, setInput] = useState(discordWebhookUrl || '');
    const [error, setError] = useState<string | null>(null);
    const [isValidating, setIsValidating] = useState(false);
    const [lastTestTime, setLastTestTime] = useState<Date | null>(null);

    const handleValidate = async () => {
      setError(null);
      try {
        webhookSchema.parse(input);
        // In Sprint 3, call backend /notify.discord to validate
        setLastTestTime(new Date());
        setDiscordWebhookUrl(input);
      } catch (err) {
        setError('Invalid Discord webhook URL');
      }
    };

    return (
      <div className="space-y-4">
        <div>
          <label className="block text-sm text-gray-200 mb-2">Discord Webhook URL</label>
          <input
            type="password"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="https://discord.com/api/webhooks/..."
            className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-white"
          />
          {error && <p className="text-red-500 text-xs mt-1">{error}</p>}
        </div>

        <button
          onClick={handleValidate}
          disabled={isValidating}
          className="px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded text-sm disabled:opacity-50"
        >
          {isValidating ? 'Testing...' : 'Test Webhook'}
        </button>

        {lastTestTime && (
          <div className="flex items-center gap-2 text-sm">
            <span className="w-2 h-2 bg-emerald-500 rounded-full" />
            <span className="text-emerald-500">Webhook verified</span>
          </div>
        )}
      </div>
    );
  }
  ```

**2.3d: Calibration Tab**
- [ ] Create [frontend/src/components/SettingsModal/CalibrationTab.tsx](frontend/src/components/SettingsModal/CalibrationTab.tsx):
  ```typescript
  import { useGameStore } from '../../store/gameStore';
  import { useState, useEffect } from 'react';

  export function CalibrationTab() {
    const { calibrationProfiles, openCalibrationWizard, deleteCalibrationProfile } = useGameStore();
    const [screenResolution, setScreenResolution] = useState<string>('');

    useEffect(() => {
      (async () => {
        const res = await window.electronAPI.getScreenResolution();
        setScreenResolution(`${res.width}×${res.height}`);
      })();
    }, []);

    return (
      <div className="space-y-4">
        <div>
          <p className="text-sm text-gray-400">Detected Resolution</p>
          <p className="text-lg font-semibold text-white">{screenResolution}</p>
        </div>

        <button
          onClick={openCalibrationWizard}
          className="w-full px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm"
        >
          Launch Calibration Wizard
        </button>

        {Object.entries(calibrationProfiles).length > 0 && (
          <div className="pt-4 border-t border-gray-700">
            <h3 className="text-sm font-semibold text-white mb-2">Saved Profiles</h3>
            <div className="space-y-2">
              {Object.entries(calibrationProfiles).map(([res, profile]) => (
                <div key={res} className="flex items-center justify-between p-2 bg-gray-800 rounded">
                  <span className="text-xs text-gray-200">{res}</span>
                  <button
                    onClick={() => deleteCalibrationProfile(res)}
                    className="text-xs text-red-400 hover:text-red-300"
                  >
                    Delete
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }
  ```

**2.3e: Stats Tab & Logs Tab (Scaffolds)**
- [ ] Create [frontend/src/components/SettingsModal/StatsTab.tsx](frontend/src/components/SettingsModal/StatsTab.tsx):
  ```typescript
  import { useGameStore } from '../../store/gameStore';
  import { useEffect, useState } from 'react';

  export function StatsTab() {
    const { cpuUsage, gpuUsage, memoryUsage } = useGameStore();

    return (
      <div className="space-y-4">
        <Meter label="CPU" value={cpuUsage} unit="%" threshold={15} />
        <Meter label="GPU" value={gpuUsage} unit="%" threshold={30} />
        <Meter label="Memory" value={memoryUsage} unit="MB" threshold={500} />
      </div>
    );
  }

  function Meter({ label, value, unit, threshold }: any) {
    const isWarning = value > threshold;
    return (
      <div>
        <div className="flex justify-between mb-1">
          <span className="text-sm text-gray-300">{label}</span>
          <span className={`text-sm font-semibold ${isWarning ? 'text-amber-500' : 'text-emerald-500'}`}>
            {value.toFixed(1)}{unit}
          </span>
        </div>
        <div className="w-full h-2 bg-gray-700 rounded">
          <div
            className={`h-full rounded ${isWarning ? 'bg-amber-500' : 'bg-emerald-500'}`}
            style={{ width: `${Math.min(value, 100)}%` }}
          />
        </div>
      </div>
    );
  }
  ```

- [ ] Create [frontend/src/components/SettingsModal/LogsTab.tsx](frontend/src/components/SettingsModal/LogsTab.tsx):
  ```typescript
  import { useGameStore } from '../../store/gameStore';

  export function LogsTab() {
    const { detectionHistory } = useGameStore();

    return (
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-white">Recent Detections</h3>
        <div className="max-h-80 overflow-y-auto space-y-2">
          {detectionHistory.slice(-20).reverse().map((detection, idx) => (
            <div key={idx} className="text-xs text-gray-300 p-2 bg-gray-800 rounded">
              <div className="flex justify-between">
                <span className="font-semibold">{detection.state}</span>
                <span className="text-gray-500">
                  {new Date(detection.detected_at).toLocaleTimeString()}
                </span>
              </div>
              <span>Confidence: {(detection.confidence * 100).toFixed(0)}%</span>
            </div>
          ))}
        </div>

        <button
          onClick={() => {
            const json = JSON.stringify(detectionHistory, null, 2);
            const blob = new Blob([json], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'detections.json';
            a.click();
          }}
          className="w-full px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs"
        >
          Export JSON
        </button>
      </div>
    );
  }
  ```

**2.3f: Settings Modal Container**
- [ ] Update [frontend/src/components/SettingsModal.tsx](frontend/src/components/SettingsModal.tsx):
  ```typescript
  import { GeneralTab } from './SettingsModal/GeneralTab';
  import { DiscordTab } from './SettingsModal/DiscordTab';
  import { CalibrationTab } from './SettingsModal/CalibrationTab';
  import { StatsTab } from './SettingsModal/StatsTab';
  import { LogsTab } from './SettingsModal/LogsTab';
  import { Tabs } from './Tabs';
  import { useGameStore } from '../store/gameStore';

  export function SettingsModal() {
    const { settingsOpen, closeSettings } = useGameStore();

    if (!settingsOpen) return null;

    const tabs = [
      { id: 'general', label: 'General', content: <GeneralTab /> },
      { id: 'discord', label: 'Discord', content: <DiscordTab /> },
      { id: 'calibration', label: 'Calibration', content: <CalibrationTab /> },
      { id: 'stats', label: 'Stats', content: <StatsTab /> },
      { id: 'logs', label: 'Logs', content: <LogsTab /> },
    ];

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-gray-900 rounded-lg shadow-lg w-96 h-screen max-h-96 flex flex-col">
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700">
            <h2 className="text-lg font-bold text-white">Settings</h2>
            <button
              onClick={closeSettings}
              className="text-gray-400 hover:text-gray-200 text-xl"
            >
              ×
            </button>
          </div>
          <Tabs tabs={tabs} defaultTab="general" />
        </div>
      </div>
    );
  }
  ```

- [ ] Create helper component [frontend/src/components/ToggleSwitch.tsx](frontend/src/components/ToggleSwitch.tsx):
  ```typescript
  interface ToggleSwitchProps {
    checked: boolean;
    onChange: (checked: boolean) => void;
  }

  export function ToggleSwitch({ checked, onChange }: ToggleSwitchProps) {
    return (
      <button
        onClick={() => onChange(!checked)}
        className={`w-10 h-6 rounded-full transition-colors ${
          checked ? 'bg-blue-600' : 'bg-gray-600'
        }`}
        role="switch"
        aria-checked={checked}
      >
        <div
          className={`w-5 h-5 bg-white rounded-full transition-transform ${
            checked ? 'translate-x-5' : 'translate-x-0.5'
          }`}
        />
      </button>
    );
  }
  ```

- [ ] Unit tests (10+ tests):
  ```typescript
  describe('SettingsModal', () => {
    it('should render all 5 tabs', () => {
      render(<SettingsModal />);
      expect(screen.getByText('General')).toBeInTheDocument();
      expect(screen.getByText('Discord')).toBeInTheDocument();
      expect(screen.getByText('Calibration')).toBeInTheDocument();
      expect(screen.getByText('Stats')).toBeInTheDocument();
      expect(screen.getByText('Logs')).toBeInTheDocument();
    });

    it('should switch tabs on button click', () => {
      render(<SettingsModal />);
      fireEvent.click(screen.getByText('Discord'));
      expect(screen.getByText('Discord Webhook URL')).toBeInTheDocument();
    });

    it('should validate Discord webhook URL', () => {
      render(<SettingsModal />);
      fireEvent.click(screen.getByText('Discord'));
      const input = screen.getByPlaceholderText('https://discord.com/api/webhooks/...');
      fireEvent.change(input, { target: { value: 'invalid-url' } });
      fireEvent.click(screen.getByText('Test Webhook'));
      expect(screen.getByText('Invalid Discord webhook URL')).toBeInTheDocument();
    });

    it('should toggle notification sound', () => {
      render(<SettingsModal />);
      const toggle = screen.getByRole('switch');
      fireEvent.click(toggle);
      // Verify Zustand store updated
    });
  });
  ```

- **Verification**: All 5 tabs visible, clicking tabs switches content, form inputs work

---

#### 2.4: FRONTEND-004 — Calibration Wizard [8 pts, HIGHEST RISK]
**Owner**: Frontend  
**Dependency**: FRONTEND-001, window.electronAPI.getScreenResolution() working

**2.4a: Calibration Wizard Container**
- [ ] Create [frontend/src/components/CalibrationWizard/index.tsx](frontend/src/components/CalibrationWizard/index.tsx):
  ```typescript
  import { useState } from 'react';
  import { Step1Instructions } from './Step1Instructions';
  import { Step2RegionEditor } from './Step2RegionEditor';
  import { Step3Preview } from './Step3Preview';
  import { Step4Success } from './Step4Success';

  export function CalibrationWizard() {
    const [step, setStep] = useState<1 | 2 | 3 | 4>(1);
    const [regions, setRegions] = useState<Record<string, any>>({});
    const [screenshot, setScreenshot] = useState<string | null>(null);

    const renderStep = () => {
      switch (step) {
        case 1:
          return <Step1Instructions onNext={() => setStep(2)} />;
        case 2:
          return (
            <Step2RegionEditor
              onNext={(regions, screenshot) => {
                setRegions(regions);
                setScreenshot(screenshot);
                setStep(3);
              }}
              onBack={() => setStep(1)}
            />
          );
        case 3:
          return (
            <Step3Preview
              regions={regions}
              screenshot={screenshot}
              onNext={() => setStep(4)}
              onBack={() => setStep(2)}
            />
          );
        case 4:
          return <Step4Success regions={regions} />;
      }
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-gray-900 rounded-lg shadow-lg w-full max-w-2xl">
          <div className="px-6 py-4 border-b border-gray-700">
            <div className="flex justify-between items-center mb-2">
              <h2 className="text-lg font-bold text-white">Calibration Wizard</h2>
              <span className="text-xs text-gray-400">Step {step} of 4</span>
            </div>
            <div className="w-full h-1 bg-gray-700 rounded">
              <div
                className="h-full bg-blue-600 rounded transition-all"
                style={{ width: `${(step / 4) * 100}%` }}
              />
            </div>
          </div>

          <div className="px-6 py-6">{renderStep()}</div>
        </div>
      </div>
    );
  }
  ```

**2.4b: Step 1 — Instructions**
- [ ] Create [frontend/src/components/CalibrationWizard/Step1Instructions.tsx](frontend/src/components/CalibrationWizard/Step1Instructions.tsx):
  ```typescript
  import { useState } from 'react';

  interface Step1InstructionsProps {
    onNext: () => void;
  }

  export function Step1Instructions({ onNext }: Step1InstructionsProps) {
    const [understood, setUnderstood] = useState(false);

    return (
      <div className="space-y-4">
        <p className="text-gray-200 text-sm">
          This wizard will help calibrate the AI detector for your screen resolution.
        </p>

        <div className="space-y-2 text-sm text-gray-300 bg-gray-800 p-3 rounded">
          <p>• <strong>Step 1:</strong> Read these instructions</p>
          <p>• <strong>Step 2:</strong> Mark the queue status and match found regions</p>
          <p>• <strong>Step 3:</strong> Preview and confirm</p>
          <p>• <strong>Step 4:</strong> Save profile</p>
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="understood"
            checked={understood}
            onChange={(e) => setUnderstood(e.target.checked)}
            className="rounded"
          />
          <label htmlFor="understood" className="text-sm text-gray-300">
            I understand the calibration process
          </label>
        </div>

        <div className="flex gap-2 pt-4">
          <button
            onClick={onNext}
            disabled={!understood}
            className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded disabled:opacity-50"
          >
            Next →
          </button>
        </div>
      </div>
    );
  }
  ```

**2.4c: Step 2 — Region Editor (MOST COMPLEX)**
- [ ] Create [frontend/src/components/CalibrationWizard/Step2RegionEditor.tsx](frontend/src/components/CalibrationWizard/Step2RegionEditor.tsx):
  ```typescript
  import { useEffect, useRef, useState } from 'react';
  import { RegionEditor } from '../RegionEditor';

  interface Step2RegionEditorProps {
    onNext: (regions: Record<string, any>, screenshot: string) => void;
    onBack: () => void;
  }

  const REGION_LABELS = [
    'queue_icon',
    'match_found_button',
    'hero_select',
    'loading_bar',
    'in_game',
  ];

  export function Step2RegionEditor({ onNext, onBack }: Step2RegionEditorProps) {
    const [regions, setRegions] = useState<Record<string, any>>({});
    const [screenshot, setScreenshot] = useState<string | null>(null);

    useEffect(() => {
      // Capture screenshot via Electron IPC
      (async () => {
        try {
          const response = await fetch(
            `${import.meta.env.VITE_MCP_SERVER_URL}/mcp/tools/screen.capture_regions`,
            {
              method: 'POST',
              body: JSON.stringify({
                regions: [{ name: 'full', x: 0, y: 0, width: 1920, height: 1080 }],
                format: 'jpeg'
              })
            }
          );
          const data = await response.json();
          if (data.regions[0]?.image_base64) {
            setScreenshot(`data:image/jpeg;base64,${data.regions[0].image_base64}`);
          }
        } catch (error) {
          console.error('Failed to capture screenshot:', error);
        }
      })();
    }, []);

    return (
      <div className="space-y-4">
        {screenshot && (
          <RegionEditor
            screenshot={screenshot}
            labels={REGION_LABELS}
            onChange={setRegions}
          />
        )}

        <div className="flex gap-2 pt-4">
          <button
            onClick={onBack}
            className="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded"
          >
            ← Back
          </button>
          <button
            onClick={() => onNext(regions, screenshot || '')}
            disabled={Object.keys(regions).length === 0}
            className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded disabled:opacity-50"
          >
            Next →
          </button>
        </div>
      </div>
    );
  }
  ```

**2.4d: Region Editor Component (Canvas-based)**
- [ ] Create [frontend/src/components/RegionEditor.tsx](frontend/src/components/RegionEditor.tsx):
  ```typescript
  import { useRef, useEffect, useState } from 'react';

  interface Region {
    x: number;
    y: number;
    width: number;
    height: number;
  }

  interface RegionEditorProps {
    screenshot: string;
    labels: string[];
    onChange: (regions: Record<string, Region>) => void;
  }

  export function RegionEditor({ screenshot, labels, onChange }: RegionEditorProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [regions, setRegions] = useState<Record<string, Region>>({});
    const [isDrawing, setIsDrawing] = useState(false);
    const [startPos, setStartPos] = useState({ x: 0, y: 0 });
    const [currentLabel, setCurrentLabel] = useState(labels[0]);
    const [img, setImg] = useState<HTMLImageElement | null>(null);

    useEffect(() => {
      const image = new Image();
      image.onload = () => setImg(image);
      image.src = screenshot;
    }, [screenshot]);

    useEffect(() => {
      redraw();
    }, [regions, img]);

    const redraw = () => {
      const canvas = canvasRef.current;
      if (!canvas || !img) return;

      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      ctx.drawImage(img, 0, 0);

      // Draw regions
      Object.entries(regions).forEach(([label, region], idx) => {
        ctx.strokeStyle = idx % 2 === 0 ? '#3b82f6' : '#8b5cf6';
        ctx.lineWidth = 2;
        ctx.strokeRect(region.x, region.y, region.width, region.height);

        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(region.x, region.y - 20, 150, 20);
        ctx.fillStyle = '#fff';
        ctx.font = '12px sans-serif';
        ctx.fillText(label, region.x + 5, region.y - 5);
      });
    };

    const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
      const rect = canvasRef.current?.getBoundingClientRect();
      if (!rect) return;
      setIsDrawing(true);
      setStartPos({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      });
    };

    const handleMouseUp = (e: React.MouseEvent<HTMLCanvasElement>) => {
      if (!isDrawing) return;
      const rect = canvasRef.current?.getBoundingClientRect();
      if (!rect) return;

      const endPos = {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      };

      const newRegion: Region = {
        x: Math.min(startPos.x, endPos.x),
        y: Math.min(startPos.y, endPos.y),
        width: Math.abs(endPos.x - startPos.x),
        height: Math.abs(endPos.y - startPos.y),
      };

      setRegions({ ...regions, [currentLabel]: newRegion });
      setIsDrawing(false);
      onChange({ ...regions, [currentLabel]: newRegion });
    };

    return (
      <div className="space-y-3">
        <div className="flex gap-2 items-center">
          <select
            value={currentLabel}
            onChange={(e) => setCurrentLabel(e.target.value)}
            className="px-2 py-1 bg-gray-800 text-white text-sm rounded"
          >
            {labels.map((label) => (
              <option key={label} value={label}>
                {label}
              </option>
            ))}
          </select>
          <span className="text-xs text-gray-400">Drag to select region</span>
        </div>

        <canvas
          ref={canvasRef}
          width={1920}
          height={1080}
          onMouseDown={handleMouseDown}
          onMouseUp={handleMouseUp}
          className="w-full border border-gray-700 rounded bg-black cursor-crosshair max-h-64 object-contain"
        />

        <div className="text-xs text-gray-400">
          {Object.keys(regions).length} region(s) selected
        </div>
      </div>
    );
  }
  ```

**2.4e: Step 3 — Preview**
- [ ] Create [frontend/src/components/CalibrationWizard/Step3Preview.tsx](frontend/src/components/CalibrationWizard/Step3Preview.tsx):
  ```typescript
  import { useState } from 'react';

  interface Step3PreviewProps {
    regions: Record<string, any>;
    screenshot: string;
    onNext: () => void;
    onBack: () => void;
  }

  export function Step3Preview({ regions, screenshot, onNext, onBack }: Step3PreviewProps) {
    const [confirmed, setConfirmed] = useState(false);

    return (
      <div className="space-y-4">
        <p className="text-gray-200 text-sm">
          Please review the regions and confirm they're correct.
        </p>

        <img src={screenshot} alt="Preview" className="w-full rounded border border-gray-700 max-h-48 object-contain" />

        <div className="bg-gray-800 p-3 rounded text-sm text-gray-300">
          <p>Regions captured:</p>
          <ul className="ml-4 mt-2 space-y-1">
            {Object.keys(regions).map((key) => (
              <li key={key}>• {key}</li>
            ))}
          </ul>
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="confirmed"
            checked={confirmed}
            onChange={(e) => setConfirmed(e.target.checked)}
          />
          <label htmlFor="confirmed" className="text-sm text-gray-300">
            I confirm these regions are correct
          </label>
        </div>

        <div className="flex gap-2 pt-4">
          <button
            onClick={onBack}
            className="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded"
          >
            ← Back
          </button>
          <button
            onClick={onNext}
            disabled={!confirmed}
            className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded disabled:opacity-50"
          >
            Next →
          </button>
        </div>
      </div>
    );
  }
  ```

**2.4f: Step 4 — Success**
- [ ] Create [frontend/src/components/CalibrationWizard/Step4Success.tsx](frontend/src/components/CalibrationWizard/Step4Success.tsx):
  ```typescript
  import { useEffect } from 'react';
  import { useGameStore } from '../../store/gameStore';

  interface Step4SuccessProps {
    regions: Record<string, any>;
  }

  export function Step4Success({ regions }: Step4SuccessProps) {
    const { saveCalibrationProfile, closeCalibrationWizard } = useGameStore();

    useEffect(() => {
      (async () => {
        const res = await window.electronAPI.getScreenResolution();
        const resolution = `${res.width}×${res.height}`;
        await saveCalibrationProfile({
          resolution,
          regions,
        });
      })();
    }, [regions, saveCalibrationProfile]);

    return (
      <div className="space-y-4 text-center">
        <div className="text-4xl">✓</div>
        <h3 className="text-lg font-bold text-emerald-500">Profile Saved Successfully!</h3>
        <p className="text-sm text-gray-400">
          Your calibration profile has been saved and will be used for future detections.
        </p>

        <button
          onClick={closeCalibrationWizard}
          className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded"
        >
          Done
        </button>
      </div>
    );
  }
  ```

- [ ] Unit tests (10+ tests):
  ```typescript
  describe('CalibrationWizard', () => {
    it('should render Step 1 by default', () => {
      render(<CalibrationWizard />);
      expect(screen.getByText('Step 1 of 4')).toBeInTheDocument();
      expect(screen.getByText(/This wizard will help calibrate/)).toBeInTheDocument();
    });

    it('should advance to Step 2 after checkbox', () => {
      render(<CalibrationWizard />);
      fireEvent.click(screen.getByLabelText('I understand the calibration process'));
      fireEvent.click(screen.getByText('Next →'));
      expect(screen.getByText('Step 2 of 4')).toBeInTheDocument();
    });

    it('should save profile on completion', () => {
      const mockSave = vi.spyOn(window.electronAPI, 'saveCalibrationProfile');
      // Navigate to Step 4
      // Verify mockSave called
    });
  });

  describe('RegionEditor', () => {
    it('should draw region on canvas drag', () => {
      render(<RegionEditor {...mockProps} />);
      const canvas = screen.getByRole('img', { hidden: true }) as HTMLCanvasElement;
      // Simulate drag
      // Verify region added to state
    });
  });
  ```

- **Verification**: Can complete all 4 wizard steps, regions saved to localStorage

---

#### 2.5: FRONTEND-007 — Notification Toast [2 pts]
**Owner**: Frontend  
**Dependency**: FRONTEND-001, Zustand store ready

- [ ] Create [frontend/src/components/NotificationToast.tsx](frontend/src/components/NotificationToast.tsx):
  ```typescript
  import { useEffect } from 'react';
  import { CheckCircle, AlertCircle, Info, X } from 'lucide-react';

  export type ToastType = 'success' | 'error' | 'info';

  interface NotificationToastProps {
    message: string;
    type: ToastType;
    duration?: number;
    onClose?: () => void;
  }

  const ICON_MAP = {
    success: <CheckCircle className="text-emerald-500" />,
    error: <AlertCircle className="text-red-500" />,
    info: <Info className="text-blue-500" />,
  };

  const BG_MAP = {
    success: 'bg-emerald-900 border-emerald-700',
    error: 'bg-red-900 border-red-700',
    info: 'bg-blue-900 border-blue-700',
  };

  export function NotificationToast({
    message,
    type,
    duration = 3000,
    onClose,
  }: NotificationToastProps) {
    useEffect(() => {
      const timer = setTimeout(() => {
        onClose?.();
      }, duration);

      return () => clearTimeout(timer);
    }, [duration, onClose]);

    return (
      <div
        className={`fixed top-4 right-4 flex items-center gap-3 px-4 py-3 rounded border ${BG_MAP[type]} text-white text-sm animate-slide-in`}
        role="alert"
        aria-live="polite"
      >
        {ICON_MAP[type]}
        <span className="flex-1">{message}</span>
        <button
          onClick={onClose}
          className="text-gray-300 hover:text-white"
          aria-label="Close notification"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    );
  }
  ```

- [ ] Add to Tailwind config (in [frontend/tailwind.config.cjs](frontend/tailwind.config.cjs)):
  ```javascript
  module.exports = {
    theme: {
      extend: {
        keyframes: {
          'slide-in': {
            '0%': { transform: 'translateX(400px)', opacity: '0' },
            '100%': { transform: 'translateX(0)', opacity: '1' }
          }
        },
        animation: {
          'slide-in': 'slide-in 0.3s ease-out'
        }
      }
    }
  }
  ```

- [ ] Update Zustand store to manage toasts:
  ```typescript
  interface Toast {
    id: string;
    message: string;
    type: 'success' | 'error' | 'info';
    duration?: number;
  }

  // In gameStore:
  toasts: Toast[],
  showToast: (message: string, type: 'success' | 'error' | 'info') => void,
  removeToast: (id: string) => void,
  ```

- [ ] Update [frontend/src/App.tsx](frontend/src/App.tsx) to render toasts:
  ```typescript
  export function App() {
    const { toasts, removeToast } = useGameStore();

    return (
      <>
        <TrayWindow />
        {/* ... other components ... */}
        {toasts.map((toast) => (
          <NotificationToast
            key={toast.id}
            message={toast.message}
            type={toast.type}
            duration={toast.duration}
            onClose={() => removeToast(toast.id)}
          />
        ))}
      </>
    );
  }
  ```

- [ ] Unit tests:
  ```typescript
  describe('NotificationToast', () => {
    it('should auto-dismiss after duration', async () => {
      const onClose = vi.fn();
      render(
        <NotificationToast message="Test" type="success" duration={100} onClose={onClose} />
      );
      await new Promise((r) => setTimeout(r, 150));
      expect(onClose).toHaveBeenCalled();
    });

    it('should respect prefers-reduced-motion', () => {
      // Test animation respects accessibility preference
    });
  });
  ```

---

### Phase 3: Persistence, Testing & Polish (Days 10–18, FRONTEND-005/008/009/010)

#### 3.1: FRONTEND-005 — Calibration Persistence [3 pts]
**Owner**: Frontend/Backend  
**Dependency**: FRONTEND-004 complete, backend calibration_profiles table exists

- [ ] Backend: Create migration in [backend/src/db/migrations.py](backend/src/db/migrations.py):
  ```sql
  -- Migration: 202602080001_create_calibration_profiles_table
  CREATE TABLE IF NOT EXISTS calibration_profiles (
    id TEXT PRIMARY KEY,
    resolution TEXT NOT NULL UNIQUE,
    regions_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1
  );
  ```

- [ ] Frontend: Update [frontend/src/store/gameStore.ts](frontend/src/store/gameStore.ts):
  ```typescript
  calibrationProfiles: Record<string, CalibrationProfile>,
  saveCalibrationProfile: async (profile: CalibrationProfile) => {
    // 1. Save to localStorage
    localStorage.setItem(`calibration_${profile.resolution}`, JSON.stringify(profile));
    // 2. Update store
    set(state => ({
      calibrationProfiles: {
        ...state.calibrationProfiles,
        [profile.resolution]: profile
      }
    }));
    // 3. Later (Sprint 3): POST to backend endpoint
  },
  loadCalibrationProfiles: async () => {
    // Load from localStorage on app start
    const profiles: Record<string, CalibrationProfile> = {};
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key?.startsWith('calibration_')) {
        const resolution = key.replace('calibration_', '');
        profiles[resolution] = JSON.parse(localStorage.getItem(key) || '{}');
      }
    }
    set({ calibrationProfiles: profiles });
  },
  deleteCalibrationProfile: async (resolution: string) => {
    localStorage.removeItem(`calibration_${resolution}`);
    set(state => {
      const newProfiles = { ...state.calibrationProfiles };
      delete newProfiles[resolution];
      return { calibrationProfiles: newProfiles };
    });
  },
  ```

- [ ] Update [frontend/src/App.tsx](frontend/src/App.tsx) to load profiles on startup:
  ```typescript
  useEffect(() => {
    (async () => {
      await gameStore.loadCalibrationProfiles();
    })();
  }, []);
  ```

- [ ] Unit tests:
  ```typescript
  describe('Calibration Persistence', () => {
    it('should save profile to localStorage', async () => {
      const store = useGameStore.getState();
      const profile = { resolution: '1920x1080', regions: { queue: { x: 0, y: 0, width: 100, height: 100 } } };
      await store.saveCalibrationProfile(profile);
      expect(localStorage.getItem('calibration_1920x1080')).toBeTruthy();
    });

    it('should load profiles from localStorage on app start', async () => {
      // Setup localStorage
      const store = useGameStore.getState();
      await store.loadCalibrationProfiles();
      expect(Object.keys(store.calibrationProfiles).length).toBeGreaterThan(0);
    });

    it('should delete profile', async () => {
      const store = useGameStore.getState();
      await store.deleteCalibrationProfile('1920x1080');
      expect(localStorage.getItem('calibration_1920x1080')).toBeNull();
    });
  });
  ```

---

#### 3.2: FRONTEND-008 — Comprehensive Unit Tests [3 pts]
**Owner**: QA  
**Dependency**: All components complete

- [ ] Setup test infrastructure:
  - Update [frontend/vitest.config.ts](frontend/vitest.config.ts):
    ```typescript
    import { defineConfig } from 'vitest/config';
    import react from '@vitejs/plugin-react';

    export default defineConfig({
      plugins: [react()],
      test: {
        globals: true,
        environment: 'jsdom',
        setupFiles: './src/__tests__/setup.ts',
        coverage: {
          provider: 'v8',
          reporter: ['text', 'html'],
          exclude: ['node_modules/', 'dist/']
        }
      }
    });
    ```

  - Create [frontend/src/__tests__/setup.ts](frontend/src/__tests__/setup.ts):
    ```typescript
    import '@testing-library/jest-dom';
    import { expect, afterEach, vi } from 'vitest';
    import { cleanup } from '@testing-library/react';

    // Mock Electron API
    Object.defineProperty(window, 'electronAPI', {
      value: {
        perceiveState: vi.fn(),
        testNotification: vi.fn(),
        saveCalibrationProfile: vi.fn(),
        getScreenResolution: vi.fn(() => Promise.resolve({ width: 1920, height: 1080 })),
        minimizeWindow: vi.fn(),
        closeWindow: vi.fn(),
        onOpenSettings: vi.fn(),
      },
      writable: true,
    });

    afterEach(() => cleanup());
    ```

- [ ] Create comprehensive test suite: (Target >75% overall coverage)
  - `__tests__/components/StateIcon.test.tsx` (5 tests)
  - `__tests__/components/ConfidenceBar.test.tsx` (6 tests)
  - `__tests__/components/SettingsModal.test.tsx` (15 tests)
  - `__tests__/components/CalibrationWizard.test.tsx` (12 tests)
  - `__tests__/components/RegionEditor.test.tsx` (8 tests)
  - `__tests__/components/NotificationToast.test.tsx` (6 tests)
  - `__tests__/store/gameStore.test.tsx` (8 tests)
  - `__tests__/pages/TrayWindow.test.tsx` (5 tests)
  - **Total**: 65+ unit tests

- [ ] Coverage gates:
  - Run: `npm test -- --coverage`
  - Assert: Overall ≥75%, components ≥80%, critical paths ≥85%
  - Fail CI if coverage drops below targets

- **Verification**: `npm test`runs all tests; coverage report generated; CI gate enforced

---

#### 3.3: FRONTEND-010 — WCAG 2.1 AA Accessibility [2 pts]
**Owner**: Frontend/QA  
**Dependency**: FRONTEND-003, SettingsModal complete

- [ ] Keyboard Navigation:
  - Update [frontend/src/components/SettingsModal.tsx](frontend/src/components/SettingsModal.tsx):
    ```typescript
    const handleKeyDown = (e: React.KeyboardEvent) => {
      if (e.key === 'Escape') {
        closeSettings();
      }
      if (e.key === 'ArrowLeft') {
        // Switch to previous tab
      }
      if (e.key === 'ArrowRight') {
        // Switch to next tab
      }
    };

    return (
      <div onKeyDown={handleKeyDown} role="dialog" aria-modal="true">
        {/* ... */}
      </div>
    );
    ```

- [ ] Focus Management:
  - Auto-focus first focusable element (Discord URL input) on modal open
  - Use `useEffect` + `useRef` to set focus:
    ```typescript
    const firstInputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
      if (settingsOpen) {
        firstInputRef.current?.focus();
      }
    }, [settingsOpen]);
    ```

  - Focus trap: Tab cycles only through modal elements, Shift+Tab reverses
  - On close: Restore focus to Settings button

- [ ] ARIA Labels & Attributes:
  - All buttons: `aria-label` (non-icon buttons automatically have labels from text)
  - Icons: Add `aria-label` if no adjacent text
  - Progress bar: `role="progressbar"`, `aria-valuenow`, `aria-valuemin`, `aria-valuemax`
  - Modal: `role="dialog"`, `aria-modal="true"`, `aria-labelledby="modal-title"`
  - Tabs: `role="tab"`, `aria-selected`, `aria-controls`
  - Form inputs: `<label htmlFor="...">` with matching `id`

- [ ] Semantic HTML:
  - Use `<button>` for clickable actions
  - Use `<input>` with `<label>` for forms
  - Use `<fieldset>` + `<legend>` for grouped controls
  - Avoid `<div>` where semantic elements fit

- [ ] Contrast & Color:
  - Verify all text ≥4.5:1 contrast ratio (Tailwind colors already verified in Sprint 0)
  - Don't rely solely on color (use icons + text)

- [ ] Animations:
  - Respect `prefers-reduced-motion`:
    ```css
    @media (prefers-reduced-motion: reduce) {
      * {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
      }
    }
    ```

- [ ] Automated Testing:
  - Install `@axe-core/react` (already in package.json)
  - Create [frontend/src/__tests__/accessibility.test.tsx](frontend/src/__tests__/accessibility.test.tsx):
    ```typescript
    import { axe, toHaveNoViolations } from '@axe-core/react';
    import { render } from '@testing-library/react';
    import { SettingsModal } from '../components/SettingsModal';

    expect.extend(toHaveNoViolations);

    describe('Accessibility', () => {
      it('SettingsModal should have no accessibility violations', async () => {
        const { container } = render(<SettingsModal />);
        const results = await axe(container);
        expect(results).toHaveNoViolations();
      });
    });
    ```

- [ ] Manual Testing:
  - Use Windows Narrator (Win + Alt + N) to test screen reader
  - Navigate Settings modal with Tab key only
  - Verify all controls accessible without mouse

- [ ] Tests (accessibility-specific):
  ```typescript
  describe('Accessibility - SettingsModal', () => {
    it('should be keyboard navigable', () => {
      render(<SettingsModal />);
      const firstFocusable = screen.getByPlaceholderText('https://discord...');
      // Tab should cycle through all buttons/inputs, Escape closes
    });

    it('should have proper focus indicators', () => {
      const button = screen.getByText('Next');
      expect(button).toHaveClass('focus-visible');
    });

    it('should pass axe accessibility audit', async () => {
      const { container } = render(<SettingsModal />);
      const results = await axe(container);
      expect(results.violations).toHaveLength(0);
    });
  });
  ```

- **Verification**: `npm test -- accessibility.test.tsx`; manual keyboard navigation; axe audit passes

---

#### 3.4: FRONTEND-009 — Hot-Reload Dev Experience [2 pts, CONDITIONAL]
**Owner**: Frontend  
**Dependency**: FRONTEND-001 (Electron main process)

- [ ] Install `electron-reload`:
  ```bash
  npm install --save-dev electron-reload
  ```

- [ ] Update [frontend/src/main-electron.ts](frontend/src/main-electron.ts):
  ```typescript
  import electronReload from 'electron-reload';

  if (isDev) {
    try {
      electronReload(__dirname, {
        electron: path.join(__dirname, '../node_modules/.bin/electron'),
        hardResetMethod: 'exit',
        ignored: /node_modules|dist/
      });
    } catch (e) {
      console.log('electron-reload failed:', e);
    }
  }
  ```

- [ ] Update scripts in [frontend/package.json](frontend/package.json):
  ```json
  "dev": "concurrently \"cross-env NODE_ENV=development electron . --dev\" \"vite\" --names \"Electron,Vite\" --prefix \"[{name}]\""
  ```

- [ ] Test: `npm run dev` → Edit React file → Save → Window auto-reloads in <1s (after Vite rebuild)

- **Verification**: Manual: Edit component, save, window reloads automatically

---

#### 3.5: FRONTEND-011 — Performance Optimization [2 pts, CONDITIONAL]
**Owner**: Frontend  
**Dependency**: All UI components complete, FRONTEND-001 baseline

- [ ] Measure Baseline:
  - Command: `npm run build && time electron .` (Windows: measure tray window visible time)
  - Target: <2s, acceptable <3s
  - Record result in [frontend/PERF_BASELINE.md](frontend/PERF_BASELINE.md):
    ```markdown
    # Performance Baseline

    ## Electron Startup Time
    - **Measurement**: `npm run build && time electron .`
    - **Result**: 1.8s (PASS)
    - **Date**: 2026-02-14
    ```

- [ ] Optimize if >3s:
  - Lazy-load heavy components (SettingsModal, CalibrationWizard) via `React.lazy()`
  - Tree-shake unused Tailwind CSS (Vite already does this with JIT)
  - Check bundle size: `npm run build -- --analyze`
  - Minimize main-electron.ts dependencies

- [ ] Code-split routes (if multiple windows added later):
  ```typescript
  const SettingsModal = React.lazy(() => import('./components/SettingsModal'));
  ```

- [ ] Document in [CONTRIBUTING.md](CONTRIBUTING.md):
  ```markdown
  ## Performance Guidelines
  - Startup should be <2s (target) / <3s (acceptable)
  - If regression detected, check:
    1. `npm run build`, measure bundle
    2. Chrome DevTools Lighthouse (Electron DevTools)
    3. Remove unused imports / dependencies
  ```

- **Verification**: `npm run build && time electron .` <3s; bundle size documented

---

## Verification & Acceptance

### Build & Test Commands
```bash
# Install
cd frontend && npm install

# Development
npm run dev              # Electron + Vite concurrent
npm run typecheck       # tsc --noEmit
npm run lint            # eslint src/

# Testing
npm test                # Vitest all tests
npm test -- --coverage  # Coverage report (target >75%)

# Production
npm run build           # Compile frontend + main
npm start               # Run built electron app
```

### Acceptance Checklist — Sprint 2 Completion

- [ ] **All 9 Tickets Complete** (35 pts chosen scope):
  - [x] FRONTEND-001 — Electron main + IPC bridge (5 pts)
  - [x] FRONTEND-002 — Tray icon & menu (3 pts)
  - [x] FRONTEND-003 — Settings modal, 5 tabs (8 pts)
  - [x] FRONTEND-004 — Calibration Wizard, 4 steps (8 pts)
  - [x] FRONTEND-005 — Calibration persistence (3 pts)
  - [x] FRONTEND-006 — State Badge + Confidence Bar (2 pts)
  - [x] FRONTEND-007 — Notification Toast (2 pts)
  - [x] FRONTEND-008 — Unit tests, >75% coverage (3 pts)
  - [x] FRONTEND-010 — WCAG 2.1 AA accessibility (2 pts)
  - [ ] FRONTEND-009 (hot reload) — Conditional, as capacity allows
  - [ ] FRONTEND-011 (perf) — Conditional, as capacity allows

- [ ] **Quality Gates**:
  - Test coverage: ≥75% (critical paths ≥85%)
  - Lint errors: 0
  - Type errors: 0
  - Accessibility violations (axe): 0
  - Console errors (dev mode): 0

- [ ] **Functionality Verified**:
  - Tray window displays current game state + confidence bar
  - Settings modal opens/closes, all 5 tabs functional
  - Calibration Wizard: drag-to-select regions, save to localStorage
  - Test Notification button fires toast
  - Discord webhook validation works (rejects invalid URLs)
  - Toast auto-dismisses after 3–5s
  - Keyboard: Tab navigates all controls, Escape closes modals, Arrow keys switch tabs
  - All ARIA labels present
  - Windows Narrator can read Settings modal
  - Startup: <3s (target <2s)

- [ ] **Database Ready**:
  - [backend/src/db/migrations.py](backend/src/db/migrations.py) includes `calibration_profiles` table
  - Frontend saves profiles to localStorage
  - **Note**: SQLite persistence via INTEGRATION-002 (Sprint 3)

- [ ] **Documentation Updated**:
  - [CONTRIBUTING.md](CONTRIBUTING.md): Frontend dev guidelines, Electron setup
  - [docs/architecture/frontend.md](docs/architecture/frontend.md): IPC protocol, component patterns
  - [frontend/README.md](frontend/README.md): State management, component hierarchy
  - [frontend/PERF_BASELINE.md](frontend/PERF_BASELINE.md): Startup performance (conditional)
  - All tickets in backlog.md marked "done"

---

## Definition of Done (Per Ticket)

✓ Feature implements spec requirement exactly  
✓ Tests pass (unit + integration, >75% coverage)  
✓ No lint errors (`npm run lint`)  
✓ Type checking passes (`npm run typecheck`)  
✓ Code reviewed + 2 approvals  
✓ Merged to `develop` branch  
✓ Backlog.md updated: status → "done"  
✓ Performance SLOs validated (if applicable)  
✓ WCAG 2.1 AA verified (if UI component)

---

## Daily Standup Format

```
✓ Yesterday: FRONTEND-001, 002 → done
⏳ Today:   FRONTEND-003 (in-progress)
⚠ Blocked: Awaiting backend perceive_state latency baseline
```

---

## Sprint Review (Day 18)

**Frontend Lead** demos:
- Electron tray app boots, shows live game state
- Settings modal with all 5 tabs working
- Calibration Wizard: drag to select regions, save profile
- Test Notification fires toast
- Keyboard navigation works (Tab, Escape, Arrow keys)

**QA Lead** reports:
- Coverage: 78% (target ≥75%) ✓
- 65+ unit tests all passing ✓
- Accessibility: 0 axe violations ✓
- Startup time: 1.8s (target <2s) ✓

**All**: Confirm no blockers for integration in Sprint 3

---

## Next Steps (Sprint 3: Backend-Frontend Integration)

- **INTEGRATION-001**: notify.discord endpoint (backend)
- **INTEGRATION-002**: Full perception engine → frontend state updates (end-to-end)
- **INTEGRATION-003**: API client abstraction + error handling
- **INTEGRATION-004**: Discord webhook validation in frontend
- **E2E tests**: Queue detection → desktop + Discord notification

---

**BEGIN SPRINT 2 EXECUTION. CRITICAL PATH: FRONTEND-001 unblocks all others. Complete by Day 18.**
