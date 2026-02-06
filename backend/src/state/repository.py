from __future__ import annotations

import json
import sqlite3
from typing import Any, Optional


class DatabaseError(Exception):
    """Base error for database operations."""


class IntegrityError(DatabaseError):
    """Raised when a database integrity constraint fails."""


_ALLOWED_STATES = {
    "IDLE",
    "QUEUE",
    "MATCH_FOUND",
    "HERO_SELECT",
    "LOADING",
    "IN_GAME",
}

_ALLOWED_NOTIFICATION_TYPES = {"desktop", "discord"}
_ALLOWED_NOTIFICATION_STATUS = {"queued", "sent", "failed", "retry"}


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _normalize_evidence(evidence: Any) -> tuple[str, str]:
    if evidence is None:
        raise DatabaseError("Evidence is required and must include resolution.")

    resolution: Optional[str] = None
    evidence_json: Optional[str] = None

    if isinstance(evidence, dict):
        resolution = evidence.get("resolution")
        evidence_json = json.dumps(evidence, separators=(",", ":"), ensure_ascii=False)
    elif isinstance(evidence, str):
        evidence_json = evidence
        try:
            parsed = json.loads(evidence)
            if isinstance(parsed, dict):
                resolution = parsed.get("resolution")
        except json.JSONDecodeError:
            resolution = None
    else:
        raise DatabaseError("Evidence must be a dict or JSON string.")

    if not resolution:
        raise DatabaseError("Evidence must include resolution.")

    return resolution, evidence_json


class CalibrationRepository:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def load(self, resolution: str) -> Optional[str]:
        conn = _connect(self.db_path)
        try:
            row = conn.execute(
                "SELECT profile_data FROM calibration_profiles WHERE resolution = ?",
                (resolution,),
            ).fetchone()
            return row["profile_data"] if row else None
        finally:
            conn.close()


class DetectionRepository:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def insert(self, state: str, confidence: float, evidence: Any) -> int:
        if state not in _ALLOWED_STATES:
            raise DatabaseError(f"Invalid state: {state}")
        if not 0.0 <= confidence <= 1.0:
            raise DatabaseError("Confidence must be between 0.0 and 1.0.")

        resolution, evidence_json = _normalize_evidence(evidence)

        conn = _connect(self.db_path)
        try:
            cursor = conn.execute(
                """
                INSERT INTO detection_history (state, confidence, resolution, evidence_json)
                VALUES (?, ?, ?, ?)
                """,
                (state, confidence, resolution, evidence_json),
            )
            conn.commit()
            return int(cursor.lastrowid)
        except sqlite3.IntegrityError as exc:
            conn.rollback()
            raise IntegrityError(str(exc)) from exc
        except sqlite3.Error as exc:
            conn.rollback()
            raise DatabaseError(str(exc)) from exc
        finally:
            conn.close()


class NotificationRepository:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def insert(self, detection_id: int, type: str, status: str) -> int:
        if type not in _ALLOWED_NOTIFICATION_TYPES:
            raise DatabaseError(f"Invalid notification type: {type}")
        if status not in _ALLOWED_NOTIFICATION_STATUS:
            raise DatabaseError(f"Invalid notification status: {status}")

        conn = _connect(self.db_path)
        try:
            cursor = conn.execute(
                """
                INSERT INTO notification_log (detection_history_id, notification_type, status)
                VALUES (?, ?, ?)
                """,
                (detection_id, type, status),
            )
            conn.commit()
            return int(cursor.lastrowid)
        except sqlite3.IntegrityError as exc:
            conn.rollback()
            raise IntegrityError(str(exc)) from exc
        except sqlite3.Error as exc:
            conn.rollback()
            raise DatabaseError(str(exc)) from exc
        finally:
            conn.close()


class SettingsRepository:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def get(self, key: str) -> Optional[str]:
        conn = _connect(self.db_path)
        try:
            row = conn.execute(
                "SELECT value FROM settings WHERE key = ?",
                (key,),
            ).fetchone()
            return row["value"] if row else None
        finally:
            conn.close()
