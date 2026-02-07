import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { vi } from "vitest";
import { CalibrationWizard } from "./CalibrationWizard";

describe("CalibrationWizard", () => {
  it("advances through steps and saves", async () => {
    const onClose = vi.fn();
    render(<CalibrationWizard open onClose={onClose} />);
    fireEvent.click(screen.getByRole("button", { name: "Next" }));
    fireEvent.click(screen.getByRole("button", { name: "Next" }));
    fireEvent.click(screen.getByRole("button", { name: "Save" }));
    await waitFor(() => expect(onClose).toHaveBeenCalled());
  });
});
