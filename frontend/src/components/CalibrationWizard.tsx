import { useEffect, useMemo, useState } from "react";
import { RegionEditor } from "./RegionEditor";
import type { CalibrationProfile } from "../types/game";
import { useGameStore } from "../store/gameStore";

const steps = ["Intro", "Queue Region", "Review"] as const;

const defaultProfile: CalibrationProfile = {
  resolution: "1920x1080",
  regions: {
    queue_button: { x: 690, y: 780, width: 550, height: 120 },
  },
};

export function CalibrationWizard({
  open,
  onClose,
  resolution = "1920x1080",
}: {
  open: boolean;
  onClose: () => void;
  resolution?: string;
}) {
  const [step, setStep] = useState(0);
  const [draft, setDraft] = useState<CalibrationProfile>({
    ...defaultProfile,
    resolution,
  });
  const saveCalibrationProfile = useGameStore((state) => state.saveCalibrationProfile);
  const showToast = useGameStore((state) => state.showToast);

  useEffect(() => {
    setDraft((current) => ({ ...current, resolution }));
  }, [resolution]);

  const canNext = useMemo(() => {
    if (step === 1) return draft.regions.queue_button.width > 0 && draft.regions.queue_button.height > 0;
    return true;
  }, [draft, step]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-20 flex items-center justify-center bg-black/70">
      <div className="w-[760px] rounded-2xl border border-slate-700 bg-slate-950 p-5">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-slate-100">Calibration Wizard</h3>
          <button
            type="button"
            onClick={onClose}
            className="rounded border border-slate-700 px-2 py-1 text-xs text-slate-300"
            aria-label="Close calibration wizard"
          >
            Close
          </button>
        </div>

        <div className="mt-3 flex gap-2">
          {steps.map((label, index) => (
            <div
              key={label}
              className={`rounded-full px-3 py-1 text-xs ${
                index === step ? "bg-blue-600 text-white" : "bg-slate-800 text-slate-300"
              }`}
            >
              {index + 1}. {label}
            </div>
          ))}
        </div>

        <div className="mt-4 min-h-72 rounded-lg border border-slate-800 bg-slate-900/50 p-4">
          {step === 0 && (
            <div className="space-y-3 text-sm text-slate-300">
              <p>
                Select the queue UI region used for detection. Use click-and-drag to define an
                accurate region.
              </p>
              <p>Current resolution profile: {draft.resolution}</p>
            </div>
          )}
          {step === 1 && (
            <RegionEditor
              value={draft.regions.queue_button}
              onChange={(region) =>
                setDraft((current) => ({
                  ...current,
                  regions: { ...current.regions, queue_button: region },
                }))
              }
            />
          )}
          {step === 2 && (
            <div className="space-y-3 text-sm text-slate-300">
              <p>Queue region: {JSON.stringify(draft.regions.queue_button)}</p>
              <p>Save to apply this profile for {draft.resolution}.</p>
            </div>
          )}
        </div>

        <div className="mt-4 flex items-center justify-between">
          <button
            type="button"
            disabled={step === 0}
            onClick={() => setStep((current) => Math.max(current - 1, 0))}
            className="rounded border border-slate-700 px-3 py-2 text-sm text-slate-200 disabled:opacity-50"
          >
            Back
          </button>

          {step < steps.length - 1 ? (
            <button
              type="button"
              disabled={!canNext}
              onClick={() => setStep((current) => Math.min(current + 1, steps.length - 1))}
              className="rounded bg-blue-600 px-3 py-2 text-sm text-white disabled:opacity-50"
            >
              Next
            </button>
          ) : (
            <button
              type="button"
              onClick={async () => {
                await saveCalibrationProfile(draft);
                showToast("Calibration profile saved.", "success");
                onClose();
              }}
              className="rounded bg-emerald-600 px-3 py-2 text-sm text-white"
            >
              Save
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
