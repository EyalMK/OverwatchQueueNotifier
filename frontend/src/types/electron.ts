import type { CalibrationProfile, Detection } from "./game";

export interface ElectronAPI {
  perceiveState: (resolution: string) => Promise<Detection>;
  testNotification: () => Promise<{ success: boolean }>;
  saveCalibrationProfile: (profile: CalibrationProfile) => Promise<void>;
  getScreenResolution: () => Promise<{ width: number; height: number }>;
  minimizeWindow: () => Promise<void>;
  closeWindow: () => Promise<void>;
  onOpenSettings: (callback: () => void) => () => void;
}

declare global {
  interface Window {
    electronAPI?: ElectronAPI;
  }
}
