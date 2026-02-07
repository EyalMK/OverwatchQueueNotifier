import { fireEvent, render, screen } from "@testing-library/react";
import { vi } from "vitest";
import { TrayWindow } from "./TrayWindow";

describe("TrayWindow", () => {
  it("calls window controls and opens settings", () => {
    const onOpenSettings = vi.fn();
    render(<TrayWindow onOpenSettings={onOpenSettings} onOpenCalibration={vi.fn()} />);
    fireEvent.click(screen.getByLabelText("Minimize"));
    expect(window.electronAPI?.minimizeWindow).toHaveBeenCalled();
    fireEvent.click(screen.getByText("Settings"));
    expect(onOpenSettings).toHaveBeenCalled();
  });
});
