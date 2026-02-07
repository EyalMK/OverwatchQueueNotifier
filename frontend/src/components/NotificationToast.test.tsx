import { render } from "@testing-library/react";
import { vi } from "vitest";
import { NotificationToast } from "./NotificationToast";

describe("NotificationToast", () => {
  it("auto-dismisses on timer", () => {
    vi.useFakeTimers();
    const onClose = vi.fn();
    render(<NotificationToast message="Saved" type="success" duration={100} onClose={onClose} />);
    vi.advanceTimersByTime(120);
    expect(onClose).toHaveBeenCalled();
    vi.useRealTimers();
  });
});
