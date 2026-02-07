import { useRef, useState } from "react";
import type { Region } from "../types/game";

interface RegionEditorProps {
  value: Region;
  onChange: (region: Region) => void;
}

export function RegionEditor({ value, onChange }: RegionEditorProps) {
  const boxRef = useRef<HTMLDivElement | null>(null);
  const [dragging, setDragging] = useState(false);
  const [start, setStart] = useState<{ x: number; y: number } | null>(null);

  function calculateRegion(clientX: number, clientY: number) {
    if (!boxRef.current || !start) return value;
    const rect = boxRef.current.getBoundingClientRect();
    const x1 = Math.max(0, Math.min(start.x, clientX - rect.left));
    const y1 = Math.max(0, Math.min(start.y, clientY - rect.top));
    const x2 = Math.max(0, Math.max(start.x, clientX - rect.left));
    const y2 = Math.max(0, Math.max(start.y, clientY - rect.top));
    return {
      x: Math.round((x1 / rect.width) * 1920),
      y: Math.round((y1 / rect.height) * 1080),
      width: Math.round(((x2 - x1) / rect.width) * 1920),
      height: Math.round(((y2 - y1) / rect.height) * 1080),
    };
  }

  return (
    <div className="space-y-2">
      <div
        ref={boxRef}
        className="relative h-52 w-full rounded-lg border border-slate-700 bg-gradient-to-br from-slate-900 to-slate-800"
        onMouseDown={(event) => {
          if (!boxRef.current) return;
          const rect = boxRef.current.getBoundingClientRect();
          setStart({ x: event.clientX - rect.left, y: event.clientY - rect.top });
          setDragging(true);
        }}
        onMouseMove={(event) => {
          if (!dragging) return;
          onChange(calculateRegion(event.clientX, event.clientY));
        }}
        onMouseUp={() => {
          setDragging(false);
          setStart(null);
        }}
      >
        <div
          className="absolute border-2 border-blue-400 bg-blue-400/20"
          style={{
            left: `${(value.x / 1920) * 100}%`,
            top: `${(value.y / 1080) * 100}%`,
            width: `${(value.width / 1920) * 100}%`,
            height: `${(value.height / 1080) * 100}%`,
          }}
        />
      </div>
      <div className="grid grid-cols-2 gap-2 text-xs text-slate-300">
        <label>
          X
          <input
            value={value.x}
            onChange={(event) => onChange({ ...value, x: Number(event.target.value) || 0 })}
            className="mt-1 w-full rounded border border-slate-700 bg-slate-900 px-2 py-1"
          />
        </label>
        <label>
          Y
          <input
            value={value.y}
            onChange={(event) => onChange({ ...value, y: Number(event.target.value) || 0 })}
            className="mt-1 w-full rounded border border-slate-700 bg-slate-900 px-2 py-1"
          />
        </label>
        <label>
          Width
          <input
            value={value.width}
            onChange={(event) => onChange({ ...value, width: Number(event.target.value) || 0 })}
            className="mt-1 w-full rounded border border-slate-700 bg-slate-900 px-2 py-1"
          />
        </label>
        <label>
          Height
          <input
            value={value.height}
            onChange={(event) => onChange({ ...value, height: Number(event.target.value) || 0 })}
            className="mt-1 w-full rounded border border-slate-700 bg-slate-900 px-2 py-1"
          />
        </label>
      </div>
    </div>
  );
}
