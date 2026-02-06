from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    mcp_port: int
    log_level: str
    db_path: str
    overwatch_window_title: str
    gate_pixel_diff_threshold_pct: float
    gate_histogram_threshold: float
    escalation_confidence_threshold: float
    screen_capture_interval_ms: int
    discord_webhook_url: Optional[str]


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value is not None else default


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name)
    return float(value) if value is not None else default


def load_config(env_path: Optional[str] = None) -> AppConfig:
    # Load .env if present (local dev)
    if env_path:
        load_dotenv(env_path)
    else:
        load_dotenv()

    db_path = os.getenv("DB_PATH")
    if not db_path:
        # Default to backend/local.db
        repo_root = Path(__file__).resolve().parents[2]
        db_path = str(repo_root / "local.db")

    return AppConfig(
        mcp_port=_get_int("MCP_PORT", 5000),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        db_path=db_path,
        overwatch_window_title=os.getenv("OVERWATCH_WINDOW_TITLE", "Overwatch 2"),
        gate_pixel_diff_threshold_pct=_get_float("GATE_PIXEL_DIFF_THRESHOLD_PCT", 15.0),
        gate_histogram_threshold=_get_float("GATE_HISTOGRAM_THRESHOLD", 0.5),
        escalation_confidence_threshold=_get_float("ESCALATION_CONFIDENCE_THRESHOLD", 0.85),
        screen_capture_interval_ms=_get_int("SCREEN_CAPTURE_INTERVAL_MS", 500),
        discord_webhook_url=os.getenv("DISCORD_WEBHOOK_URL") or None,
    )
