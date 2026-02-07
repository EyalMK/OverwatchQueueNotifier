import { ConfidenceBar } from "../components/ConfidenceBar";
import { StateIcon } from "../components/StateIcon";
import { useGameStore } from "../store/gameStore";
import { GameState } from "../types/game";

const stateColors: Record<GameState, string> = {
  [GameState.IDLE]: "bg-slate-500/20 text-slate-200",
  [GameState.QUEUE]: "bg-amber-500/20 text-amber-200",
  [GameState.MATCH_FOUND]: "bg-emerald-500/20 text-emerald-200",
  [GameState.HERO_SELECT]: "bg-blue-500/20 text-blue-200",
  [GameState.LOADING]: "bg-indigo-500/20 text-indigo-200",
  [GameState.IN_GAME]: "bg-emerald-500/20 text-emerald-200",
};

const stateLabel: Record<GameState, string> = {
  [GameState.IDLE]: "IDLE",
  [GameState.QUEUE]: "QUEUE",
  [GameState.MATCH_FOUND]: "MATCH FOUND",
  [GameState.HERO_SELECT]: "HERO SELECT",
  [GameState.LOADING]: "LOADING",
  [GameState.IN_GAME]: "IN GAME",
};

export function TrayWindow({
  onOpenSettings,
  onOpenCalibration,
}: {
  onOpenSettings: () => void;
  onOpenCalibration: () => void;
}) {
  const {
    currentState,
    currentConfidence,
    lastDetection,
    isMonitoring,
    cpuUsage,
    gpuUsage,
    memoryUsage,
    triggerTestNotification,
  } = useGameStore();

  return (
    <div className="mx-auto w-[400px] rounded-2xl border border-white/10 bg-slate-900/70 p-4 shadow-xl">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm font-semibold text-slate-100">
          <StateIcon state={currentState} />
          <span>Overwatch Queue</span>
        </div>
        <div className="flex gap-2">
          <button
            className="h-6 w-6 rounded-md bg-white/5 text-xs text-slate-200"
            onClick={() => void window.electronAPI?.minimizeWindow?.()}
            aria-label="Minimize"
          >
            -
          </button>
          <button
            className="h-6 w-6 rounded-md bg-white/5 text-xs text-slate-200"
            onClick={() => void window.electronAPI?.closeWindow?.()}
            aria-label="Close"
          >
            x
          </button>
        </div>
      </div>

      <div className="mt-4 rounded-xl border border-white/10 bg-slate-900/60 p-3">
        <div className="flex items-center justify-between">
          <span className={`rounded-full px-3 py-1 text-xs ${stateColors[currentState]}`}>
            {stateLabel[currentState]}
          </span>
          <span className="text-xs text-slate-300">{Math.round(currentConfidence * 100)}%</span>
        </div>
        <div className="mt-3">
          <ConfidenceBar confidence={currentConfidence} state={currentState} />
        </div>
      </div>

      <div className="mt-4 rounded-xl border border-white/10 bg-slate-900/60 p-3 text-xs text-slate-300">
        <div className="text-[11px] uppercase tracking-wide text-slate-500">Last Event</div>
        <div className="mt-2 flex justify-between">
          <span>{lastDetection?.timestamp ?? "-"}</span>
          <span>{lastDetection ? stateLabel[lastDetection.state] : "No data"}</span>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-3 gap-2 text-xs">
        <button
          className="rounded-lg border border-white/10 bg-white/5 py-2 text-slate-200"
          onClick={() => void triggerTestNotification()}
        >
          Test Notif
        </button>
        <button
          className="rounded-lg border border-white/10 bg-white/5 py-2 text-slate-200"
          onClick={onOpenCalibration}
        >
          Calibrate
        </button>
        <button
          className="rounded-lg border border-white/10 bg-white/5 py-2 text-slate-200"
          onClick={onOpenSettings}
        >
          Settings
        </button>
      </div>

      <div className="mt-4 rounded-xl border border-white/10 bg-slate-900/60 p-3 text-xs text-slate-300">
        <div className="flex justify-between">
          <span>CPU</span>
          <span>{cpuUsage.toFixed(0)}%</span>
        </div>
        <div className="mt-1 flex justify-between">
          <span>GPU</span>
          <span>{gpuUsage.toFixed(0)}%</span>
        </div>
        <div className="mt-1 flex justify-between">
          <span>Memory</span>
          <span>{memoryUsage.toFixed(0)} MB</span>
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between text-xs text-slate-400">
        <span>Status: {isMonitoring ? "Monitoring" : "Paused"}</span>
        <button
          className="rounded-md border border-white/10 px-2 py-1"
          onClick={() => void window.electronAPI?.closeWindow?.()}
        >
          Exit
        </button>
      </div>
    </div>
  );
}
