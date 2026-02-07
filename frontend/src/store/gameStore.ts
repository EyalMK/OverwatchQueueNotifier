import { create } from "zustand";
import { persist } from "zustand/middleware";
import { CalibrationProfile, Detection, GameState, Toast } from "../types/game";
import { perceiveState, testNotification } from "../lib/ipc";

interface GameStore {
  currentState: GameState;
  currentConfidence: number;
  lastDetection: Detection | null;
  isMonitoring: boolean;
  detectionHistory: Detection[];
  discordWebhookUrl: string | null;
  notificationSoundEnabled: boolean;
  autoStartEnabled: boolean;
  cpuUsage: number;
  gpuUsage: number;
  memoryUsage: number;
  calibrationProfiles: Record<string, CalibrationProfile>;
  toasts: Toast[];
  setState: (state: GameState, confidence: number) => void;
  addDetection: (detection: Detection) => void;
  setDiscordUrl: (url: string | null) => void;
  setMonitoring: (enabled: boolean) => void;
  updatePerformance: (cpu: number, gpu: number, memory: number) => void;
  startPolling: (resolution: string) => void;
  stopPolling: () => void;
  showToast: (message: string, type: Toast["type"], duration?: number) => void;
  removeToast: (id: string) => void;
  triggerTestNotification: () => Promise<void>;
  saveCalibrationProfile: (profile: CalibrationProfile) => Promise<void>;
  loadCalibrationProfiles: () => Promise<void>;
  deleteCalibrationProfile: (resolution: string) => Promise<void>;
}

export const useGameStore = create<GameStore>()(
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
      cpuUsage: 0,
      gpuUsage: 0,
      memoryUsage: 0,
      calibrationProfiles: {},
      toasts: [],
      setState: (state, confidence) =>
        set({
          currentState: state,
          currentConfidence: confidence,
        }),
      addDetection: (detection) =>
        set((store) => ({
          lastDetection: detection,
          detectionHistory: [detection, ...store.detectionHistory].slice(0, 100),
        })),
      setDiscordUrl: (url) => set({ discordWebhookUrl: url }),
      setMonitoring: (enabled) => set({ isMonitoring: enabled }),
      updatePerformance: (cpu, gpu, memory) =>
        set({ cpuUsage: cpu, gpuUsage: gpu, memoryUsage: memory }),
      startPolling: (resolution) => {
        if (pollingHandle) return;
        pollingHandle = window.setInterval(async () => {
          try {
            const detection = await perceiveState(resolution);
            pollingErrorLogged = false;
            set({
              currentState: detection.state,
              currentConfidence: detection.confidence,
            });
            set((store) => ({
              lastDetection: detection,
              detectionHistory: [detection, ...store.detectionHistory].slice(0, 100),
            }));
          } catch (error) {
            // Keep last state, but log once per failure burst for debugging.
            if (!pollingErrorLogged) {
              pollingErrorLogged = true;
              console.warn("Polling failed:", error);
            }
          }
        }, 500);
      },
      stopPolling: () => {
        if (pollingHandle) {
          window.clearInterval(pollingHandle);
          pollingHandle = null;
          pollingErrorLogged = false;
        }
      },
      showToast: (message, type, duration = 3000) =>
        set((store) => ({
          toasts: [
            ...store.toasts,
            {
              id: crypto.randomUUID(),
              message,
              type,
              duration,
            },
          ],
        })),
      removeToast: (id) => set((store) => ({ toasts: store.toasts.filter((toast) => toast.id !== id) })),
      triggerTestNotification: async () => {
        try {
          const response = await testNotification();
          if (response.success) {
            set((store) => ({
              toasts: [
                ...store.toasts,
                {
                  id: crypto.randomUUID(),
                  message: "Test notification sent.",
                  type: "success",
                  duration: 3000,
                },
              ],
            }));
            return;
          }
        } catch {
          // handled below
        }
        set((store) => ({
          toasts: [
            ...store.toasts,
            {
              id: crypto.randomUUID(),
              message: "Failed to send test notification.",
              type: "error",
              duration: 3000,
            },
          ],
        }));
      },
      saveCalibrationProfile: async (profile) => {
        localStorage.setItem(`calibration_${profile.resolution}`, JSON.stringify(profile));
        if (window.electronAPI?.saveCalibrationProfile) {
          await window.electronAPI.saveCalibrationProfile(profile);
        }
        set((store) => ({
          calibrationProfiles: {
            ...store.calibrationProfiles,
            [profile.resolution]: profile,
          },
        }));
      },
      loadCalibrationProfiles: async () => {
        const profiles: Record<string, CalibrationProfile> = {};
        for (let i = 0; i < localStorage.length; i += 1) {
          const key = localStorage.key(i);
          if (key?.startsWith("calibration_")) {
            const resolution = key.replace("calibration_", "");
            const raw = localStorage.getItem(key);
            if (!raw) continue;
            try {
              profiles[resolution] = JSON.parse(raw) as CalibrationProfile;
            } catch {
              // ignore malformed profile
            }
          }
        }
        set({ calibrationProfiles: profiles });
      },
      deleteCalibrationProfile: async (resolution) => {
        localStorage.removeItem(`calibration_${resolution}`);
        set((store) => {
          const next = { ...store.calibrationProfiles };
          delete next[resolution];
          return { calibrationProfiles: next };
        });
      },
    }),
    {
      name: "ow-queue-notifier-store",
      partialize: (state) => ({
        discordWebhookUrl: state.discordWebhookUrl,
        notificationSoundEnabled: state.notificationSoundEnabled,
        autoStartEnabled: state.autoStartEnabled,
        calibrationProfiles: state.calibrationProfiles,
      }),
    }
  )
);

let pollingHandle: number | null = null;
let pollingErrorLogged = false;
