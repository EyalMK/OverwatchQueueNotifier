# Frontend Architecture
## Overwatch AI Queue Detection & Notification App

**Version**: 1.0  
**Owner**: Frontend Lead  
**Last Updated**: February 6, 2026

---

## 1. Frontend Technology Stack

**Framework**: Electron 28.x + React 18.x + TypeScript 5.3+

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "zustand": "^4.4.0",
    "electron": "^28.0.0",
    "electron-updater": "^6.1.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "typescript": "^5.3.0",
    "tailwindcss": "^3.3.0",
    "@vitejs/plugin-react": "^4.0.0"
  }
}
```

---

## 2. Project Structure

```
frontend/
├── src/
│   ├── main.tsx                  # React entry point
│   ├── App.tsx                   # Root component
│   ├── pages/
│   │   ├── Dashboard.tsx         # Main tray window
│   │   ├── Settings.tsx          # Settings modal
│   │   └── Calibration.tsx       # Calibration wizard
│   ├── components/
│   │   ├── StatusBadge.tsx       # Queue state badge
│   │   ├── NotificationCenter.tsx# Notification list
│   │   ├── LogViewer.tsx         # Detection log viewer
│   │   └── StatsPanel.tsx        # Performance stats
│   ├── hooks/
│   │   ├── useAppState.ts        # Global state hook
│   │   ├── useIPC.ts             # IPC communication
│   │   └── usePerformance.ts     # Performance metrics
│   ├── store/
│   │   └── index.ts              # Zustand store
│   ├── types/
│   │   ├── app.ts                # App types
│   │   ├── ipc.ts                # IPC event types
│   │   └── models.ts             # Data models
│   ├── styles/
│   │   └── globals.css           # Tailwind + custom styles
│   └── utils/
│       ├── ipc.ts                # IPC utilities
│       ├── format.ts             # Formatting helpers
│       └── validators.ts         # Input validation
├── electron/
│   ├── main.ts                   # Electron main process
│   ├── preload.ts                # Context isolation bridge
│   └── ipc.ts                    # IPC handlers
├── public/
│   └── icon.png                  # App icon
├── package.json
├── tsconfig.json
├── vite.config.ts
└── electron-builder.json
```

---

## 3. Main Process (Electron)

```typescript
// electron/main.ts

import { app, BrowserWindow, ipcMain } from 'electron';
import { spawn } from 'child_process';
import path from 'path';

let mainWindow: BrowserWindow;
let pythonProcess: any;

app.on('ready', () => {
  // Create window
  mainWindow = new BrowserWindow({
    width: 600,
    height: 400,
    webPreferences: {
      preload: path.join(__dirname, 'preload.ts'),
      contextIsolation: true,
      enableRemoteModule: false,
    },
  });

  // Load React app
  const isDev = !app.isPackaged;
  const url = isDev 
    ? 'http://localhost:5173' 
    : `file://${path.join(__dirname, '../dist/index.html')}`;
  mainWindow.loadURL(url);

  // Start Python daemon
  const pythonScript = path.join(__dirname, '../backend/src/main.py');
  pythonProcess = spawn('python', [pythonScript]);

  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python Error: ${data}`);
  });
});

// IPC Handlers
ipcMain.handle('perceive-state', async () => {
  // Call Python backend
  return { state: 'queue', confidence: 0.87 };
});

ipcMain.handle('settings-update', async (event, settings) => {
  // Persist to backend
  return { success: true };
});

app.on('window-all-closed', () => {
  if (pythonProcess) pythonProcess.kill();
  app.quit();
});
```

---

## 4. React Components & State Management

### App State (Zustand)

```typescript
// src/store/index.ts

import { create } from 'zustand';

interface AppState {
  state: string;
  confidence: number;
  isMonitoring: boolean;
  discordWebhook: string;
  
  setState: (state: string, confidence: number) => void;
  setMonitoring: (isMonitoring: boolean) => void;
  updateSettings: (settings: Partial<AppState>) => void;
}

export const useAppStore = create<AppState>((set) => ({
  state: 'idle',
  confidence: 0,
  isMonitoring: true,
  discordWebhook: '',

  setState: (state, confidence) => set({ state, confidence }),
  setMonitoring: (isMonitoring) => set({ isMonitoring }),
  updateSettings: (settings) => set(settings),
}));
```

### Dashboard Component

```typescript
// src/pages/Dashboard.tsx

import React, { useEffect } from 'react';
import { useAppStore } from '../store';
import { useIPC } from '../hooks/useIPC';

export const Dashboard = () => {
  const { state, confidence, isMonitoring } = useAppStore();
  const { perceiveState, sendNotification } = useIPC();

  useEffect(() => {
    const interval = setInterval(async () => {
      if (isMonitoring) {
        const result = await perceiveState();
        useAppStore.setState(result.state, result.confidence);
      }
    }, 100); // Every 100ms

    return () => clearInterval(interval);
  }, [isMonitoring]);

  return (
    <div className="p-4 bg-slate-900 text-white rounded-lg">
      <h1 className="text-2xl font-bold">Overwatch Queue Monitor</h1>
      
      <div className="mt-4">
        <div className={`inline-block px-4 py-2 rounded ${
          state === 'queue' ? 'bg-red-500' : 'bg-green-500'
        }`}>
          {state.toUpperCase()}
        </div>
        <p className="mt-2 text-slate-300">
          Confidence: {(confidence * 100).toFixed(1)}%
        </p>
      </div>

      <button
        onClick={() => useAppStore.setState('isMonitoring', !isMonitoring)}
        className="mt-4 px-4 py-2 bg-blue-600 rounded hover:bg-blue-700"
      >
        {isMonitoring ? 'Stop' : 'Start'} Monitoring
      </button>
    </div>
  );
};
```

---

## 5. IPC Communication

### IPC Bridge (preload.ts)

```typescript
// electron/preload.ts

import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('api', {
  perceiveState: () => ipcRenderer.invoke('perceive-state'),
  updateSettings: (settings: any) => 
    ipcRenderer.invoke('settings-update', settings),
  onStateChange: (callback: Function) =>
    ipcRenderer.on('state-change', (event, data) => callback(data)),
});
```

### IPC Hook

```typescript
// src/hooks/useIPC.ts

export const useIPC = () => {
  const api = (window as any).api;

  const perceiveState = async () => {
    try {
      return await api.perceiveState();
    } catch (error) {
      console.error('IPC error:', error);
      return null;
    }
  };

  const updateSettings = async (settings: any) => {
    return await api.updateSettings(settings);
  };

  return { perceiveState, updateSettings };
};
```

---

## 6. Styling with Tailwind CSS

**Configuration**: Dark theme, custom color palette for queue states

```tailwind
theme {
  extend: {
    colors: {
      'queue-idle': '#10b981',      # Green - Ready
      'queue-active': '#f87171',    # Red - Queue
      'queue-match': '#fbbf24',     # Amber - Match
    }
  }
}
```

---

## 7. Build & Packaging

### Vite Config

```typescript
// vite.config.ts

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    target: 'esnext',
    minify: 'terser',
  },
});
```

### Electron Builder Config

```json
{
  "appId": "com.ow-queue-notifier.app",
  "productName": "OW Queue Notifier",
  "files": [
    "dist/**/*",
    "electron/main.js",
    "backend/**/*"
  ],
  "win": {
    "target": ["msi"],
    "certificateFile": "cert.pfx",
    "certificatePassword": "${process.env.CERT_PASS}"
  }
}
```

---

## 8. Performance Optimization

- **Code splitting**: React.lazy for modal routes
- **Memoization**: useMemo for expensive calculations
- **Virtual scrolling**: Long log lists use windowing
- **Request debouncing**: Settings updates debounced to 500ms

---

## 9. Accessibility

- Semantic HTML
- ARIA labels for interactive elements
- Keyboard navigation support
- High contrast dark theme for low-light envs

---

## 10. Deployment

```bash
# Development
npm run dev

# Build for production
npm run build

# Package MSI
npm run electron-builder

# Create signed MSI
CERT_PASS=xxx npm run electron-builder -- --publish always
```

---

**Owner**: Frontend Lead  
**Last Updated**: February 6, 2026
