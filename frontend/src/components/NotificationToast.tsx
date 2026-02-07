import { useEffect } from "react";

interface NotificationToastProps {
  message: string;
  type: "success" | "error" | "info";
  duration?: number;
  onClose?: () => void;
}

const iconMap = {
  success: <span className="text-emerald-300" aria-hidden>OK</span>,
  error: <span className="text-rose-300" aria-hidden>!</span>,
  info: <span className="text-blue-300" aria-hidden>i</span>,
};

const bgMap = {
  success: "border-emerald-800 bg-emerald-950/95",
  error: "border-rose-800 bg-rose-950/95",
  info: "border-blue-800 bg-blue-950/95",
};

export function NotificationToast({
  message,
  type,
  duration = 3000,
  onClose,
}: NotificationToastProps) {
  useEffect(() => {
    const timer = window.setTimeout(() => onClose?.(), duration);
    return () => window.clearTimeout(timer);
  }, [duration, onClose]);

  return (
    <div
      className={`fixed right-4 top-4 z-50 flex w-[320px] items-center gap-2 rounded-lg border px-3 py-2 text-sm text-slate-100 shadow-xl animate-slide-in ${bgMap[type]}`}
      role="alert"
      aria-live="polite"
    >
      {iconMap[type]}
      <span className="flex-1">{message}</span>
      <button
        type="button"
        className="rounded p-1 text-slate-300 hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-400"
        onClick={onClose}
        aria-label="Close notification"
      >
        x
      </button>
    </div>
  );
}
