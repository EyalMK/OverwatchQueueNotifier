import React, { useMemo, useState } from "react";
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
}: {
  open: boolean;
  onClose: () => void;
}) {
  const [activeTab, setActiveTab] = useState<TabKey>("general");
  const { discordWebhookUrl, setDiscordUrl } = useGameStore();
  const [inputUrl, setInputUrl] = useState(discordWebhookUrl ?? "");

  const webhookStatus = useMemo(() => {
    if (!inputUrl) return { label: "Not set", color: "text-slate-400" };
    return isValidWebhook(inputUrl)
      ? { label: "Valid", color: "text-emerald-300" }
      : { label: "Invalid", color: "text-rose-300" };
  }, [inputUrl]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-10 flex items-center justify-center bg-black/60">
      <div className="w-[640px] rounded-2xl border border-white/10 bg-slate-900/95 p-6 shadow-2xl">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-100">Settings</h2>
          <button
            className="rounded-md border border-white/10 px-2 py-1 text-xs text-slate-200"
            onClick={onClose}
          >
            Close
          </button>
        </div>

        <div className="mt-4 flex gap-2">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              className={`rounded-full px-3 py-1 text-xs ${
                activeTab === tab.key
                  ? "bg-blue-500/30 text-blue-100"
                  : "bg-white/5 text-slate-300"
              }`}
              onClick={() => setActiveTab(tab.key)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="mt-6 text-sm text-slate-200">
          {activeTab === "general" && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span>Auto-start with Windows</span>
                <button className="rounded-full border border-white/10 px-3 py-1 text-xs">
                  Toggle
                </button>
              </div>
              <div className="flex items-center justify-between">
                <span>Notification sound</span>
                <button className="rounded-full border border-white/10 px-3 py-1 text-xs">
                  Toggle
                </button>
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
            <div className="space-y-3">
              <label className="text-xs uppercase tracking-wide text-slate-400">
                Discord Webhook URL
              </label>
              <input
                type="password"
                className="w-full rounded-md border border-white/10 bg-slate-900 px-3 py-2 text-sm text-slate-100"
                value={inputUrl}
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
            <div className="space-y-3 text-sm">
              <div>Detected Resolution: 1920×1080</div>
              <button className="rounded-md border border-white/10 px-3 py-2">
                Start Calibration Wizard
              </button>
            </div>
          )}

          {activeTab === "stats" && (
            <div className="space-y-2 text-sm text-slate-300">
              <div>CPU Usage: 0%</div>
              <div>GPU Usage: 0%</div>
              <div>Memory: 0 MB</div>
            </div>
          )}

          {activeTab === "logs" && (
            <div className="space-y-3 text-sm">
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
