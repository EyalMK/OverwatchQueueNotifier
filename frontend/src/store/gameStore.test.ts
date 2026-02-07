import { describe, expect, it } from "vitest";
import { useGameStore } from "./gameStore";
import { GameState } from "../types/game";

describe("gameStore", () => {
  it("saves and loads calibration profiles", async () => {
    const store = useGameStore.getState();
    await store.saveCalibrationProfile({
      resolution: "1920x1080",
      regions: {
        queue_button: { x: 1, y: 2, width: 3, height: 4 },
      },
    });

    expect(localStorage.getItem("calibration_1920x1080")).toBeTruthy();

    await store.loadCalibrationProfiles();
    expect(useGameStore.getState().calibrationProfiles["1920x1080"]).toBeTruthy();
  });

  it("updates current state and confidence", () => {
    const store = useGameStore.getState();
    store.setState(GameState.QUEUE, 0.84);

    const updated = useGameStore.getState();
    expect(updated.currentState).toBe(GameState.QUEUE);
    expect(updated.currentConfidence).toBe(0.84);
  });

  it("adds detections to history", () => {
    const store = useGameStore.getState();
    store.addDetection({
      state: GameState.MATCH_FOUND,
      confidence: 0.95,
      timestamp: "2026-02-06T12:00:00Z",
    });

    const updated = useGameStore.getState();
    expect(updated.lastDetection?.state).toBe(GameState.MATCH_FOUND);
    expect(updated.detectionHistory.length).toBeGreaterThan(0);
  });

  it("adds and removes toast messages", () => {
    const store = useGameStore.getState();
    store.showToast("hello", "info", 500);
    const toastId = useGameStore.getState().toasts[0]?.id;
    expect(toastId).toBeTruthy();
    if (toastId) {
      store.removeToast(toastId);
      expect(useGameStore.getState().toasts).toHaveLength(0);
    }
  });
});
