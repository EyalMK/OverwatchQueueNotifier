import { render, screen } from "@testing-library/react";
import { ConfidenceBar } from "./ConfidenceBar";
import { GameState } from "../types/game";

describe("ConfidenceBar", () => {
  it("renders confidence percentage and progressbar value", () => {
    render(<ConfidenceBar confidence={0.82} state={GameState.QUEUE} />);
    expect(screen.getByText("82%")).toBeInTheDocument();
    expect(screen.getByRole("progressbar")).toHaveAttribute("aria-valuenow", "82");
  });
});
