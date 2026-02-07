import "@testing-library/jest-dom";
import { afterEach, vi } from "vitest";
import { cleanup } from "@testing-library/react";

Object.defineProperty(window, "electronAPI", {
  value: {
    perceiveState: vi.fn(async () => ({
      state: "IDLE",
      confidence: 0.95,
      timestamp: new Date().toISOString(),
    })),
    testNotification: vi.fn(async () => ({ success: true })),
    saveCalibrationProfile: vi.fn(async () => undefined),
    getScreenResolution: vi.fn(async () => ({ width: 1920, height: 1080 })),
    minimizeWindow: vi.fn(async () => undefined),
    closeWindow: vi.fn(async () => undefined),
    onOpenSettings: vi.fn(() => () => undefined),
  },
  writable: true,
});

if (!globalThis.crypto?.randomUUID) {
  Object.defineProperty(globalThis, "crypto", {
    value: {
      randomUUID: () => "test-uuid",
    },
    configurable: true,
  });
}

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
  localStorage.clear();
});
