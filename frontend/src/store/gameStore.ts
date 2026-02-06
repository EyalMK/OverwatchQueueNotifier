import { create } from "zustand";
import { persist } from "zustand/middleware";
import { Detection, GameState } from "../types/game";
import { perceiveState } from "../lib/ipc";

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
  setState: (state: GameState, confidence: number) => void;
  addDetection: (detection: Detection) => void;
  setDiscordUrl: (url: string | null) => void;
  setMonitoring: (enabled: boolean) => void;
  updatePerformance: (cpu: number, gpu: number, memory: number) => void;
  startPolling: (resolution: string) => void;
  stopPolling: () => void;
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
            set({
              currentState: detection.state,
              currentConfidence: detection.confidence,
            });
            set((store) => ({
              lastDetection: detection,
              detectionHistory: [detection, ...store.detectionHistory].slice(0, 100),
            }));
          } catch {
            // Backend unavailable; keep last state.
          }
        }, 500);
      },
      stopPolling: () => {
        if (pollingHandle) {
          window.clearInterval(pollingHandle);
          pollingHandle = null;
        }
      },
    }),
    {
      name: "ow-queue-notifier-store",
      partialize: (state) => ({
        discordWebhookUrl: state.discordWebhookUrl,
        notificationSoundEnabled: state.notificationSoundEnabled,
        autoStartEnabled: state.autoStartEnabled,
      }),
    }
  )
);

let pollingHandle: number | null = null;
