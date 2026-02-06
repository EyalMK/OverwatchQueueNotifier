# Frontend Architecture
## Overwatch AI Queue Detection & Notification App

**Version**: 1.0  
**Owner**: Frontend Lead  
**Last Updated**: February 6, 2026

---

## 1. Technology Stack

```json
{
  "runtime": "Electron 28.x (Chromium 120)",
  "ui_framework": "React 18.x with TypeScript 5.3",
  "build_tool": "Vite 5.x (HMR dev, ESM prod)",
  "styling": "Tailwind CSS 3.x + CSS Modules",
  "state_management": "Zustand 4.x (lightweight, TypeScript-first)",
  "form_handling": "React Hook Form 7.x + Zod 3.x",
  "http_client": "native fetch API (with wrapper)",
  "testing": "Vitest 1.x (unit) + Playwright (E2E)",
  "package_manager": "npm 10.x",
  "linter": "ESLint 8.x",
  "formatter": "Prettier 3.x"
}
```

---

## 2. Electron Architecture (Main + Renderer)

### Main Process (Node.js)

```typescript
// main.ts
import { app, BrowserWindow, ipcMain, Menu, Tray } from 'electron';
import { ChildProcess, spawn } from 'child_process';
import * as path from 'path';

class ElectronApp {
  private mainWindow: BrowserWindow | null = null;
  private tray: Tray | null = null;
  private pythonProcess: ChildProcess | null = null;
  private pythonSocket: string = 'ipc:///tmp/ow_queue.sock';

  async initialize(): Promise<void> {
    // 1. Start Python backend daemon
    this.startPythonDaemon();

    // 2. Create main window (hidden initially)
    this.createWindow();

    // 3. Create tray icon
    this.createTray();

    // 4. Register IPC handlers (bridge to Python)
    this.setupIPCHandlers();

    // 5. Set up auto-start + auto-update
    this.setupAutoStartAndUpdate();
  }

  private createWindow(): void {
    this.mainWindow = new BrowserWindow({
      width: 380,
      height: 540,
      show: false,
      icon: path.join(__dirname, '../assets/icon.png'),
      webPreferences: {
        preload: path.join(__dirname, 'preload.ts'),
        contextIsolation: true,
        enableRemoteModule: false,
        sandbox: true,
      },
    });

    // Load React app
    const isDev = process.env.NODE_ENV === 'development';
    if (isDev) {
      this.mainWindow.loadURL('http://localhost:5173');
      this.mainWindow.webContents.openDevTools();
    } else {
      this.mainWindow.loadFile(
        path.join(__dirname, '../dist/index.html')
      );
    }

    // Hide on close, don't quit
    this.mainWindow.on('close', (e) => {
      e.preventDefault();
      this.mainWindow?.hide();
    });
  }

  private createTray(): void {
    const iconPath = path.join(
      __dirname,
      '../assets/tray-icon.png'
    );
    this.tray = new Tray(iconPath);

    const contextMenu = Menu.buildFromTemplate([
      {
        label: 'Settings',
        click: () => this.mainWindow?.show(),
      },
      { type: 'separator' },
      {
        label: 'Test Notification',
        click: () => this.testNotification(),
      },
      { type: 'separator' },
      {
        label: 'Exit',
        click: () => app.quit(),
      },
    ]);

    this.tray.setContextMenu(contextMenu);
    this.tray.on('click', () => {
      if (this.mainWindow?.isVisible()) {
        this.mainWindow.hide();
      } else {
        this.mainWindow?.show();
      }
    });
  }

  private setupIPCHandlers(): void {
    // Settings Update
    ipcMain.handle(
      'settings:update',
      async (_event, settings) => {
        // Forward to Python backend via socket
        const response = await this.callPythonMCP(
          'settings.save',
          settings
        );
        return response;
      }
    );

    // Calibration Save
    ipcMain.handle(
      'calibration:save',
      async (_event, profiles) => {
        const response = await this.callPythonMCP(
          'calibration.save',
          profiles
        );
        return response;
      }
    );

    // Fetch Detection History
    ipcMain.handle('logs:fetch', async (_event, filters) => {
      const response = await this.callPythonMCP(
        'detection.list',
        filters
      );
      return response;
    });

    // Perception state updates (Python → Renderer)
    // Python sends IPC event when state changes
  }

  private startPythonDaemon(): void {
    const pythonExe =
      process.env.PYTHON_WHL || 'python';
    const scriptPath = path.join(
      __dirname,
      '../backend/src/main.py'
    );

    this.pythonProcess = spawn(pythonExe, [scriptPath], {
      stdio: ['ignore', 'pipe', 'pipe'],
      detached: false,
    });

    this.pythonProcess.stdout?.on('data', (data) => {
      console.log(`[Python] ${data}`);
    });

    this.pythonProcess.stderr?.on('data', (data) => {
      console.error(`[Python Error] ${data}`);
      // Potentially send error notification to renderer
    });
  }

  private async callPythonMCP(
    tool: string,
    params: unknown
  ): Promise<unknown> {
    // Send JSON-RPC to Python over IPC socket
    // Receive response, relay to renderer
    return new Promise((resolve, reject) => {
      // socket.send({ jsonrpc: '2.0', method: tool, params }, ...)
      setTimeout(() => reject(new Error('MCP timeout')), 5000);
    });
  }

  private testNotification(): void {
    this.mainWindow?.webContents.send(
      'notification:test',
      { success: true }
    );
  }
}

app.on('ready', () => {
  new ElectronApp().initialize();
});

app.on('window-all-closed', () => {
  // Don't quit on macOS
  if (process.platform !== 'darwin') app.quit();
});
```

### Preload Script (Security Bridge)

```typescript
// preload.ts
import { contextBridge, ipcRenderer } from 'electron';

// Expose secure API to React
contextBridge.exposeInMainWorld('api', {
  // Settings
  updateSettings: (settings) =>
    ipcRenderer.invoke('settings:update', settings),

  // Calibration
  saveCalibration: (profiles) =>
    ipcRenderer.invoke('calibration:save', profiles),

  // Detection History
  fetchLogs: (filters) =>
    ipcRenderer.invoke('logs:fetch', filters),

  // Event listeners
  onNotification: (callback) =>
    ipcRenderer.on('notification:new', (_event, data) =>
      callback(data)
    ),

  onStateChange: (callback) =>
    ipcRenderer.on('state:changed', (_event, state) =>
      callback(state)
    ),
});
```

---

## 3. React Component Hierarchy

```
App
├─ TrayWindow (main UI)
│  ├─ Header (minimize, settings btn, close)
│  ├─ StateBadge (QUEUE | IDLE | MATCH_FOUND)
│  │  ├─ StateIcon
│  │  ├─ ConfidenceBar
│  │  └─ ConfidencePercentage
│  ├─ LastEventSection
│  │  ├─ Timestamp
│  │  ├─ StateLabel
│  │  └─ ViewEvidenceLink
│  ├─ ActionButtons
│  │  ├─ TestNotificationButton
│  │  └─ CalibrateButton
│  ├─ StatsFooter
│  │  ├─ CPUMetric
│  │  ├─ MemoryMetric
│  │  └─ StatusIndicator
│  └─ FooterButtons
│     ├─ SettingsButton
│     └─ ExitButton
│
├─ SettingsModal (lazy-loaded)
│  ├─ TabNavigation
│  │  ├─ GeneralTab
│  │  ├─ DiscordTab
│  │  ├─ CalibrationTab
│  │  ├─ StatsTab
│  │  └─ LogsTab
│  └─ ModalFooter
│
├─ CalibrationWizard (modal, multi-step)
│  ├─ Step1Intro
│  ├─ Step2Editor
│  ├─ Step3Preview
│  └─ Step4Complete
│
└─ NotificationToast (ephemeral)
   ├─ ToastContent
   └─ ToastActions
```

---

## 4. State Management (Zustand)

```typescript
// src/store/app.ts

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AppState {
  // UI
  isSettingsOpen: boolean;
  isCalibrationOpen: boolean;
  currentTab: 'general' | 'discord' | 'calibration' | 'stats' | 'logs';

  // Perception
  currentState: 'idle' | 'queue' | 'match_found' | 'hero_select' | 'loading' | 'in_game';
  confidence: number;
  lastDetectionTime: Date | null;

  // Settings (persisted)
  settings: {
    discordWebhook: string | null;
    autoStart: boolean;
    theme: 'system' | 'light' | 'dark';
    logLevel: 'debug' | 'info' | 'warn' | 'error';
  };

  // Metrics
  metrics: {
    cpu: number;
    memory: number;
    latencyMs: number;
  };

  // Actions
  setSettingsOpen: (open: boolean) => void;
  setCalibrationOpen: (open: boolean) => void;
  setCurrentTab: (tab: AppState['currentTab']) => void;
  updatePerception: (
    state: AppState['currentState'],
    confidence: number
  ) => void;
  updateSettings: (settings: Partial<AppState['settings']>) => void;
  updateMetrics: (metrics: Partial<AppState['metrics']>) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // Initial state
      isSettingsOpen: false,
      isCalibrationOpen: false,
      currentTab: 'general',
      currentState: 'idle',
      confidence: 0,
      lastDetectionTime: null,
      settings: {
        discordWebhook: null,
        autoStart: true,
        theme: 'dark',
        logLevel: 'info',
      },
      metrics: { cpu: 0, memory: 0, latencyMs: 0 },

      // Actions
      setSettingsOpen: (open) => set({ isSettingsOpen: open }),
      setCalibrationOpen: (open) => set({ isCalibrationOpen: open }),
      setCurrentTab: (tab) => set({ currentTab: tab }),
      updatePerception: (state, confidence) =>
        set({
          currentState: state,
          confidence,
          lastDetectionTime: new Date(),
        }),
      updateSettings: (settings) =>
        set((state) => ({
          settings: { ...state.settings, ...settings },
        })),
      updateMetrics: (metrics) =>
        set((state) => ({
          metrics: { ...state.metrics, ...metrics },
        })),
    }),
    {
      name: 'ow-queue-store',
      version: 1,
    }
  )
);
```

---

## 5. API Client Abstraction

```typescript
// src/services/api.ts

interface APIError {
  code: string;
  message: string;
  details?: unknown;
}

class APIClient {
  async request<T>(
    method: string,
    tool: string,
    params?: unknown
  ): Promise<T> {
    try {
      const response = await window.api.callMCP(method, {
        tool,
        params,
      });

      if (!response.success) {
        throw new APIError(response.error.code, response.error.message);
      }

      return response.result as T;
    } catch (error) {
      console.error(`[API] ${tool} failed:`, error);
      throw error;
    }
  }

  // Settings API
  async updateSettings(
    settings: Partial<SettingsPayload>
  ): Promise<void> {
    await this.request('POST', 'settings.update', settings);
  }

  async fetchSettings(): Promise<SettingsPayload> {
    return this.request('GET', 'settings.get');
  }

  // Notification API
  async sendTestNotification(
    channels: ('desktop' | 'discord')[]
  ): Promise<void> {
    await this.request(
      'POST',
      'notification.test',
      { channels }
    );
  }

  // Calibration API
  async saveCalibration(
    profiles: CalibrationProfile[]
  ): Promise<void> {
    await this.request(
      'POST',
      'calibration.save',
      { profiles }
    );
  }

  async getCalibrationProfiles(): Promise<CalibrationProfile[]> {
    return this.request(
      'GET',
      'calibration.list'
    );
  }

  // Logs API
  async fetchDetectionHistory(
    limit: number = 100,
    state?: string
  ): Promise<Detection[]> {
    return this.request(
      'GET',
      'detection.list',
      { limit, state }
    );
  }
}

export const api = new APIClient();
```

---

## 6. Routing (Single-Page App)

```typescript
// src/App.tsx

import { useAppStore } from './store/app';
import TrayWindow from './components/TrayWindow';
import SettingsModal from './components/SettingsModal';
import CalibrationWizard from './components/CalibrationWizard';
import NotificationToast from './components/NotificationToast';

export default function App() {
  const {
    isSettingsOpen,
    isCalibrationOpen,
  } = useAppStore();

  return (
    <div className="bg-slate-950 text-slate-100">
      <TrayWindow />

      {/* Modal Overlays */}
      {isSettingsOpen && <SettingsModal />}
      {isCalibrationOpen && <CalibrationWizard />}

      {/* Notification */}
      <NotificationToast />
    </div>
  );
}
```

---

## 7. Design Tokens (Tailwind Config)

```typescript
// tailwind.config.ts

export default {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        slate: {
          '950': '#0f172a',
          '900': '#0f172a',
          '800': '#1e293b',
          '700': '#334155',
          '400': '#94a3b8',
          '300': '#cbd5e1',
          '100': '#f1f5f9',
        },
      },
      spacing: {
        '1': '4px',
        '2': '8px',
        '3': '12px',
        '4': '16px',
        '6': '24px',
      },
    },
  },
  plugins: [],
};
```

---

## 8. Form Handling Pattern (Settings Modal Example)

```typescript
// src/components/SettingsModal/DiscordTab.tsx

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAppStore } from '../../store/app';
import { api } from '../../services/api';

const discordSchema = z.object({
  webhookUrl: z
    .string()
    .url('Invalid Discord webhook URL')
    .startsWith(
      'https://discordapp.com/api/webhooks/',
      'Must be a valid Discord webhook'
    ),
});

type DiscordFormData = z.infer<typeof discordSchema>;

export default function DiscordTab() {
  const { settings, updateSettings } = useAppStore();
  const { register, handleSubmit, formState: { errors } } = useForm<DiscordFormData>({
    resolver: zodResolver(discordSchema),
    defaultValues: {
      webhookUrl: settings.discordWebhook || '',
    },
  });

  const onSubmit = async (data: DiscordFormData) => {
    try {
      await api.updateSettings({
        discordWebhook: data.webhookUrl,
      });
      updateSettings(data);
      // Show toast: "Webhook saved ✓"
    } catch (error) {
      // Show error toast
      console.error('Failed to save webhook:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label>Discord Webhook URL</label>
        <input
          type="password"
          placeholder="https://discordapp.com/api/webhooks/..."
          {...register('webhookUrl')}
          className="w-full px-3 py-2 bg-slate-800 text-slate-100"
        />
        {errors.webhookUrl && (
          <p className="text-red-500 text-sm">
            {errors.webhookUrl.message}
          </p>
        )}
      </div>

      <button
        type="submit"
        className="px-4 py-2 bg-blue-500 text-white rounded"
      >
        Save
      </button>
    </form>
  );
}
```

---

## 9. Testing Strategy

### Unit Tests (Vitest)

```typescript
// src/components/__tests__/StateBadge.test.ts

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import StateBadge from '../StateBadge';

describe('StateBadge', () => {
  it('displays IDLE state correctly', () => {
    render(<StateBadge state='idle' confidence={0.95} />);
    expect(screen.getByText('IDLE')).toBeInTheDocument();
  });

  it('displays confidence as percentage', () => {
    render(<StateBadge state='queue' confidence={0.87} />);
    expect(screen.getByText('87%')).toBeInTheDocument();
  });

  it('applies correct color class for each state', () => {
    const { rerender } = render(
      <StateBadge state='queue' confidence={0.9} />
    );
    expect(screen.getByRole('status')).toHaveClass('bg-yellow-500');

    rerender(<StateBadge state='match_found' confidence={0.95} />);
    expect(screen.getByRole('status')).toHaveClass('bg-green-500');
  });
});
```

### E2E Tests (Playwright)

```typescript
// tests/e2e/calibration.spec.ts

import { test, expect } from '@playwright/test';

test('calibration wizard completes successfully', async ({
  page,
}) => {
  // 1. Open app
  await page.goto('http://localhost:5173');

  // 2. Click Settings
  await page.click('button:has-text("⚙ Settings")');
  expect(page.locator('.modal')).toBeVisible();

  // 3. Go to Calibration tab
  await page.click('text=Calibration');

  // 4. Click "Calibrate"
  await page.click('button:has-text("Start Wizard")');

  // 5. Step 1: Read instructions
  expect(page.locator('text=Step 1 of 4')).toBeVisible();
  await page.click('button:has-text("Next →")');

  // 6. Step 2: Mark region
  const canvas = page.locator('canvas');
  await canvas.click({ position: { x: 100, y: 100 } });
  await canvas.drag({
    source: { x: 100, y: 100 },
    target: { x: 200, y: 200 },
  });

  await page.click('button:has-text("Next →")');

  // 7. Step 3: Confirm
  expect(page.locator('text=Review Calibration')).toBeVisible();
  await page.click('button:has-text("Save & Close")');

  // 8. Verify success
  expect(page.locator('text=Calibration Saved')).toBeVisible();
});
```

---

## 10. Performance Optimization Checklist

- [ ] **Bundle Size**: <500KB (gzip)
  - Tree-shake unused code (vite build)
  - Lazy-load Settings modal
  - Use dynamic imports for heavy components

- [ ] **Rendering**: 60 FPS (16.67ms per frame)
  - Memoize expensive components (React.memo)
  - Split state by feature (Zustand slices)
  - Profile with DevTools

- [ ] **Memory**: <150MB peak
  - Avoid memory leaks (cleanup listeners)
  - Virtualize long lists (detection history)

- [ ] **Accessibility**: WCAG 2.1 AA
  - Color contrast ≥4.5:1
  - Keyboard nav (Tab, Enter, Escape)
  - Screen reader support (aria-labels)

---

## 11. Development Workflow

```bash
# Dev server (HMR)
npm run dev

# Type-check
npm run typecheck

# Linting
npm run lint

# Testing
npm run test          # Unit tests
npm run test:e2e      # E2E tests

# Build
npm run build

# Package
npm run package       # Create MSI installer
```

---

**Owner**: Frontend Lead  
**Last Updated**: February 6, 2026
