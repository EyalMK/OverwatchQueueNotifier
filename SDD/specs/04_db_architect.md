# Database Architect Specification
## Overwatch AI Queue Detection & Notification App

**Generated**: February 6, 2026  
**Version**: 1.0  
**Status**: Draft → Technical Foundation

---

## 1. Database Technology & Tooling

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Database Engine** | SQLite 3.45+ | Local-only, zero-setup, single-file portable, file-based backup |
| **ORM/Query Builder** | Python `sqlite3` (stdlib) | Lightweight, no dependency bloat, sufficient for simple schema |
| **Migrations** | `alembic` (lightweight alternative: custom migration runner) | Version schema changes, simple SQL scripts |
| **Connection Pooling** | Not needed (single app process, <5 concurrent queries) | SQLite handle per module |
| **Transactions** | SQLite ACID (deferred by default) | Atomic writes for notification log |

---

## 2. Entity-Relationship Diagram (ASCII)

```
┌─────────────────────────────────────┐
│    calibration_profiles             │
├─────────────────────────────────────┤
│ PK  id: INTEGER                     │
│     resolution: TEXT (UNIQUE)       │
│     profile_data: BLOB              │
│     created_at: TIMESTAMP           │
│     updated_at: TIMESTAMP           │
└──────────────┬──────────────────────┘
               │ (1:N)
               │
               ▼
┌─────────────────────────────────────┐
│    detection_history                │
├─────────────────────────────────────┤
│ PK  id: INTEGER                     │
│ FK  calibration_id: INTEGER (NULL)  │
│     state: TEXT                     │
│     confidence: REAL                │
│     resolution: TEXT                │
│     inference_latency_ms: INTEGER   │
│     evidence_json: TEXT (JSON)      │
│     timestamp: TIMESTAMP             │
│     
│ Index: (timestamp DESC)
│ Index: (resolution, timestamp)
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│    notification_log                 │
├─────────────────────────────────────┤
│ PK  id: INTEGER                     │
│ FK  detection_history_id: INTEGER   │
│     notification_type: TEXT         │
│     status: TEXT                    │
│     retry_count: INTEGER            │
│     error_message: TEXT (NULL)      │
│     timestamp: TIMESTAMP             │
│
│ Index: (status, timestamp)
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│    settings                         │
├─────────────────────────────────────┤
│ PK  key: TEXT                       │
│     value: TEXT                     │
│     updated_at: TIMESTAMP           │
│
│ Example rows:
│   ("discord_webhook_url", "https://...")
│   ("notification_sound_enabled", "true")
│   ("auto_start_enabled", "false")
└─────────────────────────────────────┘
```

---

## 3. Complete CREATE TABLE SQL

```sql
-- Enable foreign keys by default
PRAGMA foreign_keys = ON;

-- calibration_profiles table
-- Stores per-resolution UI calibration (which regions to crop, labels)
CREATE TABLE calibration_profiles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  resolution TEXT NOT NULL UNIQUE,
  -- profile_data is JSON:
  -- {
  --   "regions": [
  --     {"name": "queue_icon", "crop_normalized": [0.45, 0.25, 0.55, 0.35]},
  --     {"name": "match_found_button", "crop_normalized": [0.40, 0.40, 0.60, 0.60]}
  --   ],
  --   "confidence_thresholds": {"escalation": 0.85},
  --   "version": "1.0"
  -- }
  profile_data BLOB NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_calibration_profiles_resolution ON calibration_profiles(resolution);

-- detection_history table
-- Logs every state detection for audit trail + debugging
CREATE TABLE detection_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  calibration_id INTEGER,
  state TEXT NOT NULL CHECK(state IN ('IDLE', 'QUEUE', 'MATCH_FOUND', 'HERO_SELECT', 'LOADING', 'IN_GAME')),
  confidence REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
  resolution TEXT NOT NULL,
  inference_latency_ms INTEGER,
  evidence_json TEXT,
  -- evidence_json example:
  -- {
  --   "gate_triggered": true,
  --   "gate_signals": {"pixel_diff_pct": 15.3, "histogram_change": 0.78},
  --   "classifier_version": "tiny_v1.0",
  --   "cropped_regions": [
  --     {"name": "match_found_button", "confidence_per_region": 0.96}
  --   ],
  --   "escalation_used": false
  -- }
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (calibration_id) REFERENCES calibration_profiles(id) ON DELETE SET NULL
);

CREATE INDEX idx_detection_history_timestamp ON detection_history(timestamp DESC);
CREATE INDEX idx_detection_history_resolution_timestamp ON detection_history(resolution, timestamp DESC);
CREATE INDEX idx_detection_history_state ON detection_history(state);

-- notification_log table
-- Tracks which notifications were sent, retry attempts, failures
CREATE TABLE notification_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  detection_history_id INTEGER NOT NULL,
  notification_type TEXT NOT NULL CHECK(notification_type IN ('desktop', 'discord')),
  status TEXT NOT NULL CHECK(status IN ('queued', 'sent', 'failed', 'retry')),
  retry_count INTEGER DEFAULT 0,
  error_message TEXT,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (detection_history_id) REFERENCES detection_history(id) ON DELETE CASCADE
);

CREATE INDEX idx_notification_log_status_timestamp ON notification_log(status, timestamp DESC);
CREATE INDEX idx_notification_log_detection_id ON notification_log(detection_history_id);

-- settings table
-- Key-value store for application settings
CREATE TABLE settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed default settings
INSERT OR IGNORE INTO settings (key, value) VALUES
  ('notification_sound_enabled', 'true'),
  ('auto_start_enabled', 'false'),
  ('discord_webhook_url', NULL),
  ('app_version', '1.0.0');
```

---

## 4. Index Definitions & Query Optimization

| Index | Columns | Purpose | Expected Queries |
|-------|---------|---------|-----------------|
| `idx_calibration_profiles_resolution` | `resolution` | Lookup profile by resolution (primary access pattern) | `SELECT * FROM calibration_profiles WHERE resolution = ?` |
| `idx_detection_history_timestamp` | `timestamp DESC` | Recent detections (home page, stats) | `SELECT * FROM detection_history ORDER BY timestamp DESC LIMIT 100` |
| `idx_detection_history_resolution_timestamp` | `resolution, timestamp DESC` | Per-resolution detection history (dashboard filter) | `SELECT * FROM detection_history WHERE resolution = ? ORDER BY timestamp DESC` |
| `idx_detection_history_state` | `state` | Count by state (dashboard stats) | `SELECT COUNT(*) FROM detection_history WHERE state = 'MATCH_FOUND'` |
| `idx_notification_log_status_timestamp` | `status, timestamp DESC` | Failed notification retry (process retries) | `SELECT * FROM notification_log WHERE status = 'failed' ORDER BY timestamp DESC LIMIT 10` |
| `idx_notification_log_detection_id` | `detection_history_id` | Notifications for a detection (evidence view) | `SELECT * FROM notification_log WHERE detection_history_id = ?` |

---

## 5. Migration Strategy

### Naming Convention

```
YYYYMMDDHHMMSS_description.sql
202602060000_init_schema.sql
202602061200_add_settings_table.sql
202604151530_add_detection_evidence_json.sql
```

### Migration Runner (Python)

```python
# backend/src/db/migrations.py
import os
import sqlite3
from pathlib import Path

def run_migrations(db_path: str) -> None:
    """Apply all pending migrations in order"""
    migrations_dir = Path(__file__).parent / "migrations"
    
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS schema_version (version TEXT PRIMARY KEY, applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    
    applied = set(row[0] for row in conn.execute("SELECT version FROM schema_version"))
    
    for migration_file in sorted(migrations_dir.glob("*.sql")):
        version = migration_file.stem
        if version not in applied:
            print(f"Applying migration: {version}")
            migration_sql = migration_file.read_text()
            conn.executescript(migration_sql)
            conn.execute("INSERT INTO schema_version (version) VALUES (?)", (version,))
            conn.commit()
    
    conn.close()
```

---

## 6. Common Query Patterns

### Pattern 1: Get Current Calibration Profile

```python
# backend/src/db/queries.py
def get_calibration_profile(db: sqlite3.Connection, resolution: str) -> dict | None:
    """Fetch calibration profile for a given resolution"""
    cursor = db.execute(
        "SELECT id, profile_data FROM calibration_profiles WHERE resolution = ?",
        (resolution,)
    )
    row = cursor.fetchone()
    if row:
        return {"id": row[0], "profile_data": json.loads(row[1])}
    return None
```

**Index Hit**: `idx_calibration_profiles_resolution`  
**Expected Time**: <1ms

---

### Pattern 2: Recent Detection History (Paginated)

```python
def get_detection_history(db: sqlite3.Connection, limit: int = 100, offset: int = 0) -> list[dict]:
    """Fetch recent detections with pagination"""
    cursor = db.execute(
        """
        SELECT id, state, confidence, resolution, inference_latency_ms, 
               evidence_json, timestamp
        FROM detection_history
        ORDER BY timestamp DESC
        LIMIT ? OFFSET ?
        """,
        (limit, offset)
    )
    return [
        {
            "id": row[0],
            "state": row[1],
            "confidence": row[2],
            "resolution": row[3],
            "latency_ms": row[4],
            "evidence": json.loads(row[5]) if row[5] else None,
            "timestamp": row[6],
        }
        for row in cursor.fetchall()
    ]
```

**Index Hit**: `idx_detection_history_timestamp`  
**Expected Time**: <5ms for top 100 rows

---

### Pattern 3: Detection Stats Dashboard

```python
def get_detection_stats(db: sqlite3.Connection) -> dict:
    """Get dashboard statistics"""
    cursor = db.execute(
        """
        SELECT state, COUNT(*) as count
        FROM detection_history
        WHERE timestamp >= datetime('now', '-1 day')
        GROUP BY state
        """
    )
    stats = {row[0]: row[1] for row in cursor.fetchall()}
    return {
        "match_found_count_24h": stats.get("MATCH_FOUND", 0),
        "queue_detections_24h": stats.get("QUEUE", 0),
        "total_24h": sum(stats.values()),
    }
```

**Index Hit**: `idx_detection_history_state` (for GROUP BY optimization)  
**Expected Time**: <10ms

---

### Pattern 4: Deduplication Check (5-second window)

```python
def has_recent_notification(db: sqlite3.Connection, state: str, seconds: int = 5) -> bool:
    """Check if a notification was sent recently (dedup window)"""
    threshold_time = datetime.now() - timedelta(seconds=seconds)
    cursor = db.execute(
        """
        SELECT COUNT(*) FROM notification_log
        WHERE timestamp >= ?
        AND status IN ('sent', 'queued')
        """,
        (threshold_time,)
    )
    count = cursor.fetchone()[0]
    return count > 0
```

**Full Table Scan**: No index (small table, typically <10K rows)  
**Expected Time**: <2ms

---

### Pattern 5: Insert Detection + Notification (Transaction)

```python
def log_detection_and_notify(
    db: sqlite3.Connection,
    state: str,
    confidence: float,
    resolution: str,
    evidence_json: str
):
    """Atomically log detection and queue notifications"""
    try:
        cursor = db.execute(
            """
            INSERT INTO detection_history
            (state, confidence, resolution, evidence_json)
            VALUES (?, ?, ?, ?)
            """,
            (state, confidence, resolution, evidence_json)
        )
        detection_id = cursor.lastrowid
        
        # Queue desktop notification
        db.execute(
            """
            INSERT INTO notification_log
            (detection_history_id, notification_type, status)
            VALUES (?, 'desktop', 'queued')
            """,
            (detection_id,)
        )
        
        # Queue Discord notification if enabled
        webhook_url = get_setting(db, "discord_webhook_url")
        if webhook_url:
            db.execute(
                """
                INSERT INTO notification_log
                (detection_history_id, notification_type, status)
                VALUES (?, 'discord', 'queued')
                """,
                (detection_id,)
            )
        
        db.commit()
        return detection_id
    except Exception as e:
        db.rollback()
        raise
```

**Transaction Guarantee**: All-or-nothing (no orphaned detections without notifications)  
**Expected Time**: <5ms

---

## 7. Seed Data Plan

### Initialization (First Run)

```python
# backend/src/db/seeding.py
def seed_default_data(db: sqlite3.Connection) -> None:
    """Initialize default settings"""
    
    # Default settings
    defaults = {
        "notification_sound_enabled": "true",
        "auto_start_enabled": "false",
        "discord_webhook_url": None,
        "app_version": "1.0.0",
        "last_update_check": str(datetime.now()),
    }
    
    for key, value in defaults.items():
        if value is not None:
            db.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value)
            )
    
    db.commit()
```

### Test Data (E2E/QA)

```python
# tests/fixtures/seed_test_db.py
def seed_test_detections(db: sqlite3.Connection) -> None:
    """Populate test DB with sample data"""
    
    # Insert calibration for 1920x1080
    profile_data = json.dumps({
        "regions": [
            {"name": "queue_icon", "crop_normalized": [0.45, 0.25, 0.55, 0.35]},
            {"name": "match_found_button", "crop_normalized": [0.40, 0.40, 0.60, 0.60]},
        ],
        "version": "1.0"
    })
    
    cursor = db.execute(
        "INSERT INTO calibration_profiles (resolution, profile_data) VALUES (?, ?)",
        ("1920x1080", profile_data)
    )
    calibration_id = cursor.lastrowid
    
    # Insert 50 test detections over last 24h
    base_time = datetime.now() - timedelta(hours=24)
    states = ["IDLE", "QUEUE", "MATCH_FOUND", "HERO_SELECT", "LOADING", "IN_GAME"]
    
    for i in range(50):
        state = states[i % len(states)]
        timestamp = base_time + timedelta(minutes=i * 28.8)  # ~50 detections in 24h
        
        db.execute(
            """
            INSERT INTO detection_history
            (calibration_id, state, confidence, resolution, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (calibration_id, state, 0.85 + (i % 10) * 0.01, "1920x1080", timestamp)
        )
    
    db.commit()
```

---

## 8. Backup & Recovery Strategy

### File-Based Backup

```python
# backend/src/db/backup.py
def backup_database(db_path: str, backup_dir: str) -> str:
    """Create timestamped backup of SQLite database"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"local_{timestamp}.db")
    
    import shutil
    shutil.copy2(db_path, backup_path)
    
    # Keep only last 7 backups
    backups = sorted(os.listdir(backup_dir))
    for old_backup in backups[:-7]:
        os.remove(os.path.join(backup_dir, old_backup))
    
    return backup_path
```

### Restore Procedure

```python
def restore_database(db_path: str, backup_path: str) -> None:
    """Restore database from backup"""
    import shutil
    
    # Verify backup is valid
    test_conn = sqlite3.connect(backup_path)
    test_conn.execute("SELECT COUNT(*) FROM detection_history")
    test_conn.close()
    
    # Replace current DB
    shutil.copy2(backup_path, db_path)
    
    print(f"Restored database from {backup_path}")
```

**RTO** (Recovery Time Objective): <5 seconds (file copy)  
**RPO** (Recovery Point Objective): Hourly automated backups, user-initiated backups on demand

---

## 9. Soft Delete vs Hard Delete Policy

**Decision**: Hard delete for this app (all data is local, no compliance requirement)

```python
# Hard delete: immediately remove records
def clear_old_detections(db: sqlite3.Connection, older_than_days: int = 30) -> int:
    """Remove detections older than threshold"""
    threshold = datetime.now() - timedelta(days=older_than_days)
    
    # Cascade delete notifications
    cursor = db.execute(
        "DELETE FROM notification_log WHERE detection_history_id IN ("
        "  SELECT id FROM detection_history WHERE timestamp < ?"
        ")",
        (threshold,)
    )
    
    cursor = db.execute(
        "DELETE FROM detection_history WHERE timestamp < ?",
        (threshold,)
    )
    
    db.commit()
    return cursor.rowcount
```

---

## 10. Connection & Session Management

```python
# backend/src/db/connection.py
class DatabaseSession:
    """Single database connection for the app"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Open connection with pragmas"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Named tuple access
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging for concurrency
        return self.conn
    
    def disconnect(self):
        if self.conn:
            self.conn.close()

# Global session
_db_session = DatabaseSession("local.db")

def get_db():
    return _db_session.conn
```

---

## 11. Next Steps

1. ✅ **DB spec approved** → Generate migrations
2. ⏭️ **Create local.db** → Run initial migration (Sprint 0.1)
3. ⏭️ **Implement repository layer** → Queries + tests (Sprint 0.2)
4. ⏭️ **Add detection logging** → Log detections to DB (Sprint 1)
5. ⏭️ **Implement history API** → Expose detection history to frontend (Sprint 2)

**Owner**: Database Architect  
**Stakeholders**: Backend Lead, QA Lead, DevOps Lead
