import { GameState } from "../types/game";

interface StateIconProps {
  state: GameState;
  size?: "sm" | "md" | "lg";
}

const sizeMap = {
  sm: "h-4 w-4",
  md: "h-5 w-5",
  lg: "h-7 w-7",
};

export function StateIcon({ state, size = "md" }: StateIconProps) {
  const baseClass = `${sizeMap[size]} inline-flex items-center justify-center rounded-full border text-[10px]`;
  if (state === GameState.IDLE) return <span className={`${baseClass} border-slate-500 text-slate-300`}>ID</span>;
  if (state === GameState.QUEUE)
    return <span className={`${baseClass} border-amber-500 text-amber-300`}>Q</span>;
  if (state === GameState.MATCH_FOUND)
    return <span className={`${baseClass} border-emerald-500 text-emerald-300`}>OK</span>;
  if (state === GameState.HERO_SELECT)
    return <span className={`${baseClass} border-blue-500 text-blue-300`}>HS</span>;
  if (state === GameState.LOADING)
    return <span className={`${baseClass} border-indigo-500 text-indigo-300`}>L</span>;
  return <span className={`${baseClass} border-emerald-500 text-emerald-300`}>IG</span>;
}
