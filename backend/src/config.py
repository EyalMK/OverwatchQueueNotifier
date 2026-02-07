from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv

CLASSIFIER_CONFIG = {
    "tiny_model_path": "backend/models/Shufflenet-v2.onnx",
    "escalation_model_path": "backend/models/efficientnet-lite4-11.onnx",
    "input_dim": (224, 224),
    "escalation_threshold": 0.85,
    "class_names": [
        "IDLE",
        "QUEUE",
        "MATCH_FOUND",
        "IN_GAME",
        "LOADING",
        "HERO_SELECT",
    ],
}

GATE_THRESHOLDS = {
    (1920, 1080): (5.0, 0.30),
    (2560, 1440): (3.0, 0.30),
    (3440, 1440): (2.0, 0.30),
}


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
    cors_allowed_origins: List[str] = field(default_factory=list)


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value is not None else default


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name)
    return float(value) if value is not None else default


def _get_csv(name: str, default: str) -> List[str]:
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


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
        escalation_confidence_threshold=_get_float(
            "ESCALATION_CONFIDENCE_THRESHOLD",
            float(CLASSIFIER_CONFIG["escalation_threshold"]),
        ),
        screen_capture_interval_ms=_get_int("SCREEN_CAPTURE_INTERVAL_MS", 500),
        discord_webhook_url=os.getenv("DISCORD_WEBHOOK_URL") or None,
        cors_allowed_origins=_get_csv(
            "CORS_ALLOWED_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174,null",
        ),
    )
