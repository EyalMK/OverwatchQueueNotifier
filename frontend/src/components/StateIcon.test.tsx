import { render } from "@testing-library/react";
import { StateIcon } from "./StateIcon";
import { GameState } from "../types/game";

describe("StateIcon", () => {
  it("renders for each game state", () => {
    const states = Object.values(GameState);
    states.forEach((state) => {
      const { container, unmount } = render(<StateIcon state={state} />);
      expect(container.textContent).toBeTruthy();
      unmount();
    });
  });
});
