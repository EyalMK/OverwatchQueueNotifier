from __future__ import annotations

import sqlite3

import pytest

from src.db.migrations import run_migrations
from src.state.repository import (
    CalibrationRepository,
    DatabaseError,
    DetectionRepository,
    NotificationRepository,
    SettingsRepository,
)


def _fetchone(conn: sqlite3.Connection, query: str, params: tuple) -> sqlite3.Row | None:
    conn.row_factory = sqlite3.Row
    return conn.execute(query, params).fetchone()


def test_calibration_repository_loads_profile(temp_db: str) -> None:
    run_migrations(temp_db)

    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    conn.execute(
        "INSERT INTO calibration_profiles (resolution, profile_data) VALUES (?, ?)",
        ("1920x1080", '{"regions": []}'),
    )
    conn.commit()
    conn.close()

    repo = CalibrationRepository(temp_db)
    profile = repo.load("1920x1080")

    assert profile == '{"regions": []}'


def test_calibration_repository_missing_returns_none(temp_db: str) -> None:
    run_migrations(temp_db)

    repo = CalibrationRepository(temp_db)
    assert repo.load("2560x1440") is None


def test_detection_repository_inserts_detection(temp_db: str) -> None:
    run_migrations(temp_db)

    repo = DetectionRepository(temp_db)
    detection_id = repo.insert(
        "QUEUE",
        0.87,
        {"resolution": "1920x1080", "gate_triggered": True},
        escalated=True,
        evidence_image_base64="abc123",
        window_resolution="1920x1080",
    )

    conn = sqlite3.connect(temp_db)
    conn.row_factory = sqlite3.Row
    row = _fetchone(
        conn,
        "SELECT id, state, confidence, resolution, escalated, window_resolution FROM detection_history WHERE id = ?",
        (detection_id,),
    )
    conn.close()

    assert row is not None
    assert row["state"] == "QUEUE"
    assert row["resolution"] == "1920x1080"
    assert row["escalated"] == 1
    assert row["window_resolution"] == "1920x1080"
    assert pytest.approx(row["confidence"], rel=1e-6) == 0.87


def test_detection_repository_requires_resolution(temp_db: str) -> None:
    run_migrations(temp_db)

    repo = DetectionRepository(temp_db)
    with pytest.raises(DatabaseError):
        repo.insert("IDLE", 0.9, {"gate_triggered": True})


def test_notification_repository_inserts_notification(temp_db: str) -> None:
    run_migrations(temp_db)

    detection_repo = DetectionRepository(temp_db)
    detection_id = detection_repo.insert(
        "MATCH_FOUND",
        0.94,
        {"resolution": "1920x1080", "classifier": "tiny_v1"},
    )

    notif_repo = NotificationRepository(temp_db)
    notif_id = notif_repo.insert(detection_id, "desktop", "queued")

    conn = sqlite3.connect(temp_db)
    row = _fetchone(
        conn,
        "SELECT id, notification_type, status FROM notification_log WHERE id = ?",
        (notif_id,),
    )
    conn.close()

    assert row is not None
    assert row["notification_type"] == "desktop"
    assert row["status"] == "queued"


def test_settings_repository_reads_value(temp_db: str) -> None:
    run_migrations(temp_db)

    repo = SettingsRepository(temp_db)
    assert repo.get("notification_sound_enabled") == "true"


def test_detection_cleanup_removes_old_records(temp_db: str) -> None:
    run_migrations(temp_db)
    repo = DetectionRepository(temp_db)
    detection_id = repo.insert("IDLE", 0.99, {"resolution": "1920x1080"})

    conn = sqlite3.connect(temp_db)
    conn.execute(
        "UPDATE detection_history SET timestamp = datetime('now', '-2 days') WHERE id = ?",
        (detection_id,),
    )
    conn.commit()
    conn.close()

    removed = repo.cleanup_older_than(hours=24)
    assert removed >= 1
