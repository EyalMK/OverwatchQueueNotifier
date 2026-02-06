import { describe, expect, it } from "vitest";
import { useGameStore } from "./gameStore";
import { GameState } from "../types/game";

describe("gameStore", () => {
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
});
