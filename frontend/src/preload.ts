import { contextBridge, ipcRenderer, IpcRendererEvent } from "electron";
import type { CalibrationProfile, Detection } from "./types/game";

const electronAPI = {
  perceiveState: (resolution: string): Promise<Detection> =>
    ipcRenderer.invoke("perceive-state", resolution),
  testNotification: (): Promise<{ success: boolean }> => ipcRenderer.invoke("test-notification"),
  saveCalibrationProfile: (profile: CalibrationProfile): Promise<void> =>
    ipcRenderer.invoke("save-calibration-profile", profile),
  getScreenResolution: (): Promise<{ width: number; height: number }> =>
    ipcRenderer.invoke("get-screen-resolution"),
  minimizeWindow: (): Promise<void> => ipcRenderer.invoke("minimize-window"),
  closeWindow: (): Promise<void> => ipcRenderer.invoke("close-window"),
  onOpenSettings: (callback: () => void) => {
    const listener = (_event: IpcRendererEvent) => callback();
    ipcRenderer.on("open-settings", listener);
    return () => ipcRenderer.removeListener("open-settings", listener);
  },
};

contextBridge.exposeInMainWorld("electronAPI", electronAPI);
