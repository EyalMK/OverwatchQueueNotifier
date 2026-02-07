import { useEffect, useMemo, useRef, useState } from "react";
import { useGameStore } from "../store/gameStore";

type TabKey = "general" | "discord" | "calibration" | "stats" | "logs";

const tabs: { key: TabKey; label: string }[] = [
  { key: "general", label: "General" },
  { key: "discord", label: "Discord" },
  { key: "calibration", label: "Calibration" },
  { key: "stats", label: "Stats" },
  { key: "logs", label: "Logs" },
];

function isValidWebhook(url: string) {
  return /^https:\/\/(discord\.com|discordapp\.com)\/api\/webhooks\/.+/i.test(url);
}

export function SettingsModal({
  open,
  onClose,
  onOpenCalibration,
  detectedResolution = "Unknown",
}: {
  open: boolean;
  onClose: () => void;
  onOpenCalibration: () => void;
  detectedResolution?: string;
}) {
  const [activeTab, setActiveTab] = useState<TabKey>("general");
  const { discordWebhookUrl, setDiscordUrl, calibrationProfiles } = useGameStore();
  const [inputUrl, setInputUrl] = useState(discordWebhookUrl ?? "");
  const inputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    if (open) {
      setInputUrl(discordWebhookUrl ?? "");
      inputRef.current?.focus();
    }
  }, [discordWebhookUrl, open]);

  const webhookStatus = useMemo(() => {
    if (!inputUrl) return { label: "Not set", color: "text-slate-400" };
    return isValidWebhook(inputUrl)
      ? { label: "Valid", color: "text-emerald-300" }
      : { label: "Invalid", color: "text-rose-300" };
  }, [inputUrl]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-10 flex items-center justify-center bg-black/60">
      <div
        className="w-[680px] rounded-2xl border border-white/10 bg-slate-900/95 p-6 shadow-2xl"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        onKeyDown={(event) => {
          if (event.key === "Escape") onClose();
          if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
            const current = tabs.findIndex((tab) => tab.key === activeTab);
            const delta = event.key === "ArrowRight" ? 1 : -1;
            const next = (current + delta + tabs.length) % tabs.length;
            setActiveTab(tabs[next].key);
          }
        }}
      >
        <div className="flex items-center justify-between">
          <h2 id="modal-title" className="text-lg font-semibold text-slate-100">
            Settings
          </h2>
          <button
            className="rounded-md border border-white/10 px-2 py-1 text-xs text-slate-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-400"
            onClick={onClose}
            aria-label="Close settings"
          >
            Close
          </button>
        </div>

        <div className="mt-4 flex gap-2" role="tablist" aria-label="Settings tabs">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              role="tab"
              aria-selected={activeTab === tab.key}
              aria-controls={`settings-tab-${tab.key}`}
              className={`rounded-full px-3 py-1 text-xs ${
                activeTab === tab.key ? "bg-blue-500/30 text-blue-100" : "bg-white/5 text-slate-300"
              }`}
              onClick={() => setActiveTab(tab.key)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="mt-6 text-sm text-slate-200">
          {activeTab === "general" && (
            <div id="settings-tab-general" className="space-y-3">
              <div className="flex items-center justify-between">
                <span>Auto-start with Windows</span>
                <button className="rounded-full border border-white/10 px-3 py-1 text-xs">Toggle</button>
              </div>
              <div className="flex items-center justify-between">
                <span>Notification sound</span>
                <button className="rounded-full border border-white/10 px-3 py-1 text-xs">Toggle</button>
              </div>
              <div className="flex items-center justify-between">
                <span>Theme</span>
                <select className="rounded-md border border-white/10 bg-slate-900 px-2 py-1 text-xs">
                  <option>System</option>
                  <option>Dark</option>
                  <option>Light</option>
                </select>
              </div>
            </div>
          )}

          {activeTab === "discord" && (
            <div id="settings-tab-discord" className="space-y-3">
              <label
                htmlFor="discord-webhook"
                className="block text-xs uppercase tracking-wide text-slate-400"
              >
                Discord Webhook URL
              </label>
              <input
                id="discord-webhook"
                ref={inputRef}
                type="password"
                className="w-full rounded-md border border-white/10 bg-slate-900 px-3 py-2 text-sm text-slate-100"
                value={inputUrl}
                placeholder="https://discord.com/api/webhooks/..."
                onChange={(event) => setInputUrl(event.target.value)}
              />
              <div className="flex items-center justify-between text-xs">
                <span className={webhookStatus.color}>{webhookStatus.label}</span>
                <button
                  className="rounded-md border border-white/10 px-2 py-1"
                  onClick={() => setDiscordUrl(inputUrl || null)}
                >
                  Save
                </button>
              </div>
            </div>
          )}

          {activeTab === "calibration" && (
            <div id="settings-tab-calibration" className="space-y-3 text-sm">
              <div>Detected Resolution: {detectedResolution}</div>
              <div>Profiles: {Object.keys(calibrationProfiles).length}</div>
              <button
                className="rounded-md border border-white/10 px-3 py-2"
                onClick={onOpenCalibration}
              >
                Start Calibration Wizard
              </button>
            </div>
          )}

          {activeTab === "stats" && (
            <div id="settings-tab-stats" className="space-y-2 text-sm text-slate-300">
              <div>CPU Usage: 0%</div>
              <div>GPU Usage: 0%</div>
              <div>Memory: 0 MB</div>
            </div>
          )}

          {activeTab === "logs" && (
            <div id="settings-tab-logs" className="space-y-3 text-sm">
              <div className="text-xs text-slate-400">Latest 100 detections</div>
              <div className="rounded-md border border-white/10 p-3 text-xs text-slate-400">
                No detections yet.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
