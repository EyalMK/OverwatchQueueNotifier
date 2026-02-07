import { useEffect, useState } from "react";
import { CalibrationWizard } from "./components/CalibrationWizard";
import { NotificationToast } from "./components/NotificationToast";
import { SettingsModal } from "./components/SettingsModal";
import { TrayWindow } from "./pages/TrayWindow";
import { useGameStore } from "./store/gameStore";

export default function App() {
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [wizardOpen, setWizardOpen] = useState(false);
  const [detectedResolution, setDetectedResolution] = useState(
    `${window.screen.width}x${window.screen.height}`
  );
  const startPolling = useGameStore((state) => state.startPolling);
  const stopPolling = useGameStore((state) => state.stopPolling);
  const loadCalibrationProfiles = useGameStore((state) => state.loadCalibrationProfiles);
  const toasts = useGameStore((state) => state.toasts);
  const removeToast = useGameStore((state) => state.removeToast);

  useEffect(() => {
    let cancelled = false;
    const defaultResolution = `${window.screen.width}x${window.screen.height}`;
    startPolling(defaultResolution);

    const bootPolling = async () => {
      let resolution = defaultResolution;
      if (window.electronAPI?.getScreenResolution) {
        try {
          const screen = await window.electronAPI.getScreenResolution();
          resolution = `${screen.width}x${screen.height}`;
          setDetectedResolution(resolution);
        } catch {
          setDetectedResolution(defaultResolution);
        }
      } else {
        setDetectedResolution(defaultResolution);
      }
      if (!cancelled) {
        if (resolution !== defaultResolution) {
          stopPolling();
          startPolling(resolution);
        }
      }
    };
    void bootPolling();
    return () => {
      cancelled = true;
      stopPolling();
    };
  }, [startPolling, stopPolling]);

  useEffect(() => {
    void loadCalibrationProfiles();
  }, [loadCalibrationProfiles]);

  useEffect(() => {
    if (!window.electronAPI?.onOpenSettings) return undefined;
    return window.electronAPI.onOpenSettings(() => setSettingsOpen(true));
  }, []);

  return (
    <div className="min-h-screen px-6 py-8">
      <TrayWindow
        onOpenSettings={() => setSettingsOpen(true)}
        onOpenCalibration={() => setWizardOpen(true)}
      />
      <SettingsModal
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        detectedResolution={detectedResolution}
        onOpenCalibration={() => {
          setSettingsOpen(false);
          setWizardOpen(true);
        }}
      />
      <CalibrationWizard
        open={wizardOpen}
        onClose={() => setWizardOpen(false)}
        resolution={detectedResolution}
      />
      {toasts.map((toast) => (
        <NotificationToast
          key={toast.id}
          message={toast.message}
          type={toast.type}
          duration={toast.duration}
          onClose={() => removeToast(toast.id)}
        />
      ))}
    </div>
  );
}
