import React, { useEffect, useState } from "react";
import { SettingsModal } from "./components/SettingsModal";
import { TrayWindow } from "./pages/TrayWindow";
import { useGameStore } from "./store/gameStore";

export default function App() {
  const [settingsOpen, setSettingsOpen] = useState(false);
  const startPolling = useGameStore((state) => state.startPolling);
  const stopPolling = useGameStore((state) => state.stopPolling);

  useEffect(() => {
    startPolling("1920x1080");
    return () => stopPolling();
  }, [startPolling, stopPolling]);

  return (
    <div className="min-h-screen px-6 py-8">
      <TrayWindow onOpenSettings={() => setSettingsOpen(true)} />
      <SettingsModal open={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </div>
  );
}
