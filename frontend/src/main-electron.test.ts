describe("electron preload bridge", () => {
  it("exposes expected API surface", () => {
    expect(typeof window.electronAPI).toBe("object");
    expect(typeof window.electronAPI?.perceiveState).toBe("function");
    expect(typeof window.electronAPI?.closeWindow).toBe("function");
  });
});
