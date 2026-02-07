import { fireEvent, render, screen } from "@testing-library/react";
import { vi } from "vitest";
import { SettingsModal } from "./SettingsModal";

describe("SettingsModal", () => {
  it("renders five tabs and closes on escape", () => {
    const onClose = vi.fn();
    render(<SettingsModal open onClose={onClose} onOpenCalibration={vi.fn()} />);
    expect(screen.getByRole("tab", { name: "General" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Discord" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Calibration" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Stats" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Logs" })).toBeInTheDocument();
    fireEvent.keyDown(screen.getByRole("dialog"), { key: "Escape" });
    expect(onClose).toHaveBeenCalled();
  });

  it("switches tabs with arrow keys", () => {
    render(<SettingsModal open onClose={vi.fn()} onOpenCalibration={vi.fn()} />);
    const dialog = screen.getByRole("dialog");
    fireEvent.keyDown(dialog, { key: "ArrowRight" });
    expect(screen.getByRole("tab", { name: "Discord" })).toHaveAttribute("aria-selected", "true");
  });
});
