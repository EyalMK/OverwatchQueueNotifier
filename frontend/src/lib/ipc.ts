import { Detection, GameState } from "../types/game";

const baseUrl = import.meta.env.VITE_MCP_SERVER_URL ?? "http://127.0.0.1:5000";

interface PerceiveStateResponse {
  state: GameState;
  confidence: number;
  timestamp: string;
  inference_latency_ms: number;
}

export async function perceiveState(resolution: string): Promise<Detection> {
  if (window.electronAPI?.perceiveState) {
    try {
      return await window.electronAPI.perceiveState(resolution);
    } catch {
      // Fall back to direct HTTP in case IPC bridge is unavailable.
    }
  }

  const response = await fetch(`${baseUrl}/mcp/tools/screen.perceive_state`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      timestamp: new Date().toISOString(),
      resolution,
      debug: false,
    }),
  });

  if (!response.ok) {
    throw new Error(`perceive_state failed: ${response.status}`);
  }

  const payload = (await response.json()) as PerceiveStateResponse;
  return {
    state: payload.state,
    confidence: payload.confidence,
    timestamp: payload.timestamp,
  };
}

export async function testNotification(): Promise<{ success: boolean }> {
  if (window.electronAPI?.testNotification) {
    return window.electronAPI.testNotification();
  }

  const response = await fetch(`${baseUrl}/mcp/tools/notify.desktop`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title: "Overwatch Queue Notifier",
      message: "Test notification",
    }),
  });

  return { success: response.ok };
}
