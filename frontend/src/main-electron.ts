import { app, BrowserWindow, ipcMain, Menu, Tray, nativeImage, screen } from "electron";
import path from "path";
import fs from "fs";
import { pathToFileURL } from "url";
import type { CalibrationProfile } from "./types/game";

let mainWindow: BrowserWindow | null = null;
let tray: Tray | null = null;
const calibrationCache = new Map<string, CalibrationProfile>();
const appWithState = app as typeof app & { isQuiting?: boolean };
const isDev = process.env.NODE_ENV === "development" || process.argv.includes("--dev");
const bootStart = Date.now();

const mcpServerUrl = process.env.VITE_MCP_SERVER_URL ?? "http://127.0.0.1:5000";

interface BackendErrorPayload {
  error?: string;
  message?: string;
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1024,
    height: 640,
    minWidth: 520,
    minHeight: 580,
    show: false,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, "preload.js"),
    },
  });

  if (isDev) {
    mainWindow.loadURL("http://localhost:5174");
    mainWindow.webContents.openDevTools({ mode: "detach" });
  } else {
    const indexPath = path.join(__dirname, "index.html");
    mainWindow.loadURL(pathToFileURL(indexPath).toString());
  }

  mainWindow.once("ready-to-show", () => {
    mainWindow?.show();
    const startupMs = Date.now() - bootStart;
    console.log(`[startup] window ready in ${startupMs}ms`);
  });

  mainWindow.on("minimize", () => {
    mainWindow?.hide();
  });

  mainWindow.on("close", (event) => {
    if (!appWithState.isQuiting) {
      event.preventDefault();
      mainWindow?.hide();
    }
  });
}

function createTray() {
  const trayPath = path.join(__dirname, "assets", "tray-icon.png");
  const trayIcon = fs.existsSync(trayPath) ? trayPath : nativeImage.createEmpty();
  tray = new Tray(trayIcon);
  tray.setToolTip("Overwatch Queue Notifier");

  const contextMenu = Menu.buildFromTemplate([
    { label: "Open", click: () => mainWindow?.show() },
    { label: "Settings", click: () => mainWindow?.webContents.send("open-settings") },
    { type: "separator" },
    {
      label: "Exit",
      click: () => {
        appWithState.isQuiting = true;
        app.quit();
      },
    },
  ]);

  tray.setContextMenu(contextMenu);
  tray.on("double-click", () => mainWindow?.show());
}

app.on("ready", () => {
  if (isDev) {
    try {
      const electronBin =
        process.platform === "win32"
          ? path.join(__dirname, "../node_modules/.bin/electron.cmd")
          : path.join(__dirname, "../node_modules/.bin/electron");
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const electronReload = require("electron-reload") as (
        pathToWatch: string,
        options: { electron: string; hardResetMethod: "exit"; ignored: RegExp }
      ) => void;
      electronReload(__dirname, {
        electron: electronBin,
        hardResetMethod: "exit",
        ignored: /node_modules|dist/,
      });
    } catch (error) {
      console.warn("electron-reload failed", error);
    }
  }
  createWindow();
  createTray();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
  else mainWindow?.show();
});

ipcMain.handle("perceive-state", async (_event, resolution: string) => {
  try {
    const response = await fetch(`${mcpServerUrl}/mcp/tools/screen.perceive_state`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        timestamp: new Date().toISOString(),
        resolution,
        debug: false,
      }),
    });

    if (!response.ok) {
      let backendError: BackendErrorPayload = {};
      try {
        backendError = (await response.json()) as BackendErrorPayload;
      } catch {
        // ignore parse failures
      }

      const errorCode = backendError.error ?? "";
      const message = backendError.message ?? `HTTP ${response.status}`;
      const isExpectedGameNotReadyError =
        response.status === 400 &&
        (errorCode === "WindowNotFoundError" || errorCode === "ResolutionMismatchError");

      if (isExpectedGameNotReadyError) {
        return {
          state: "IDLE",
          confidence: 0,
          timestamp: new Date().toISOString(),
        };
      }

      throw new Error(`${response.status} ${errorCode} ${message}`.trim());
    }

    const payload = (await response.json()) as {
      state: string;
      confidence: number;
      timestamp?: string;
      detected_at?: string;
    };

    return {
      state: payload.state ?? "IDLE",
      confidence: payload.confidence,
      timestamp: payload.timestamp ?? payload.detected_at ?? new Date().toISOString(),
    };
  } catch (error) {
    throw new Error(error instanceof Error ? error.message : "Unknown perceive_state failure");
  }
});

ipcMain.handle("test-notification", async () => {
  try {
    const response = await fetch(`${mcpServerUrl}/mcp/tools/notify.desktop`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: "Overwatch Queue Notifier",
        message: "This is a test notification from Sprint 2 UI.",
      }),
    });

    return { success: response.ok };
  } catch {
    return { success: false };
  }
});

ipcMain.handle("save-calibration-profile", async (_event, profile: CalibrationProfile) => {
  calibrationCache.set(profile.resolution, profile);
});

ipcMain.handle("get-screen-resolution", async () => {
  const { width, height } = screen.getPrimaryDisplay().size;
  return { width, height };
});

ipcMain.handle("minimize-window", async () => {
  mainWindow?.minimize();
});

ipcMain.handle("close-window", async () => {
  mainWindow?.hide();
});
