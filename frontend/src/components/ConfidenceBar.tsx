import { GameState } from "../types/game";

interface ConfidenceBarProps {
  confidence: number;
  state: GameState;
}

const stateColorMap: Record<GameState, string> = {
  [GameState.IDLE]: "bg-slate-400",
  [GameState.QUEUE]: "bg-amber-500",
  [GameState.MATCH_FOUND]: "bg-emerald-500",
  [GameState.HERO_SELECT]: "bg-blue-500",
  [GameState.LOADING]: "bg-indigo-400",
  [GameState.IN_GAME]: "bg-emerald-500",
};

export function ConfidenceBar({ confidence, state }: ConfidenceBarProps) {
  const percentage = Math.max(0, Math.min(100, Math.round(confidence * 100)));

  return (
    <div className="w-full">
      <div className="mb-1 flex items-center justify-between text-xs text-slate-300">
        <span>Confidence</span>
        <span className="font-semibold text-slate-100">{percentage}%</span>
      </div>
      <div className="h-2 w-full rounded-full bg-slate-800">
        <div
          className={`h-2 rounded-full transition-all duration-300 ${stateColorMap[state]}`}
          style={{ width: `${percentage}%` }}
          role="progressbar"
          aria-label="Detection confidence"
          aria-valuenow={percentage}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
    </div>
  );
}
