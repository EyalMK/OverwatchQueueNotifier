# Database Architecture
## Overwatch AI Queue Detection & Notification App

**Generated**: February 6, 2026  
**Version**: 1.0

---

## Database Technology & ORM

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Engine** | SQLite 3.45+ | Local-only, zero setup, file-based, fully ACID, suitable for single-user desktop app |
| **Query Layer** | Python `sqlite3` (stdlib) | Lightweight, no ORM overhead, sufficient for simple schemas, no dependency bloat |
| **Connection Pool** | Single handle per module | Single-threaded app, <5 concurrent queries, no pooling needed |
| **Transactions** | SQLite ACID (deferred mode) | Serializable isolation, atomic writes for critical operations |

---

## Entity-Relationship Diagram (ERD)

```
┌────────────────────────────────────────────┐
│       calibration_profiles                 │ 1
├────────────────────────────────────────────┤
│ PK  id: INTEGER                            │
│ UQ  resolution: TEXT (e.g., "1920x1080")  │
│     profile_data: BLOB (JSON)              │
│     created_at: TIMESTAMP                  │
│     updated_at: TIMESTAMP                  │
└────────┬─────────────────────────────────-─┘
         │ (1:N) has_many
         │ calibration_id
         ▼
┌────────────────────────────────────────────┐
│       detection_history                    │ N
├────────────────────────────────────────────┤
│ PK  id: INTEGER                            │
│ FK  calibration_id: INTEGER (NULL)         │
│     state: TEXT (enum)                     │
│     confidence: REAL [0.0–1.0]             │
│     resolution: TEXT (cached)              │
│     inference_latency_ms: INTEGER          │
│     evidence_json: TEXT (JSON)             │
│     timestamp: TIMESTAMP                   │
│                                            │
│ Indices:                                   │
│  - (timestamp DESC) — recent detections   │
│  - (resolution, timestamp DESC)            │
│  - (state) — state aggregations           │
└────────┬─────────────────────────────────-─┘
         │ (1:N) has_many
         │ detection_history_id
         ▼
┌────────────────────────────────────────────┐
│       notification_log                     │ N
├────────────────────────────────────────────┤
│ PK  id: INTEGER                            │
│ FK  detection_history_id: INTEGER (FK)     │
│     notification_type: TEXT (enum)         │
│     status: TEXT (enum)                    │
│     retry_count: INTEGER                   │
│     error_message: TEXT (NULL)             │
│     timestamp: TIMESTAMP                   │
│                                            │
│ Indices:                                   │
│  - (status, timestamp DESC) — retry queue │
│  - (detection_history_id) — notification lookup
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│       settings                             │ K-V
├────────────────────────────────────────────┤
│ PK  key: TEXT                              │
│     value: TEXT (JSON-stringified)         │
│     updated_at: TIMESTAMP                  │
│                                            │
│ Examples:                                  │
│  - "discord_webhook_url": "https://..."   │
│  - "notification_sound_enabled": "true"   │
│  - "auto_start_enabled": "false"          │
└────────────────────────────────────────────┘
```

---

## Complete CREATE TABLE SQL

```sql
-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- calibration_profiles
-- Stores per-resolution calibration metadata (crop regions, labels, thresholds)
CREATE TABLE calibration_profiles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  resolution TEXT NOT NULL UNIQUE,
  -- profile_data is JSON string:
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

CREATE INDEX idx_calibration_profiles_resolution 
  ON calibration_profiles(resolution);

-- detection_history
-- Audit trail of every state detection for debugging + dashboard
CREATE TABLE detection_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  calibration_id INTEGER,
  state TEXT NOT NULL CHECK(state IN ('IDLE', 'QUEUE', 'MATCH_FOUND', 'HERO_SELECT', 'LOADING', 'IN_GAME')),
  confidence REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
  resolution TEXT NOT NULL,  -- e.g., "1920x1080"
  inference_latency_ms INTEGER,  -- Time spent in AI inference
  -- evidence_json is JSON string:
  -- {
  --   "gate_triggered": true,
  --   "gate_signals": {"pixel_diff_pct": 15.3, "histogram_change": 0.78},
  --   "classifier_version": "tiny_v1.0",
  --   "cropped_regions": [
  --     {"name": "match_found_button", "crop_coords": [960, 540, 1200, 600], "confidence_per_region": 0.96}
  --   ],
  --   "escalation_used": false
  -- }
  evidence_json TEXT,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (calibration_id) REFERENCES calibration_profiles(id) ON DELETE SET NULL
);

CREATE INDEX idx_detection_history_timestamp 
  ON detection_history(timestamp DESC);
CREATE INDEX idx_detection_history_resolution_timestamp 
  ON detection_history(resolution, timestamp DESC);
CREATE INDEX idx_detection_history_state 
  ON detection_history(state);

-- notification_log
-- Tracks which notifications were sent, retry attempts, failures
CREATE TABLE notification_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  detection_history_id INTEGER NOT NULL,
  notification_type TEXT NOT NULL CHECK(notification_type IN ('desktop', 'discord')),
  status TEXT NOT NULL CHECK(status IN ('queued', 'sent', 'failed', 'retry')),
  retry_count INTEGER DEFAULT 0,
  error_message TEXT,  -- NULL on success, populated on failure
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (detection_history_id) REFERENCES detection_history(id) ON DELETE CASCADE
);

CREATE INDEX idx_notification_log_status_timestamp 
  ON notification_log(status, timestamp DESC);
CREATE INDEX idx_notification_log_detection_id 
  ON notification_log(detection_history_id);

-- settings
-- Key-value application settings (persisted across restarts)
CREATE TABLE settings (
  key TEXT PRIMARY KEY,
  -- value is TEXT; use JSON for complex types
  value TEXT NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed default settings
INSERT OR IGNORE INTO settings (key, value) VALUES
  ('notification_sound_enabled', 'true'),
  ('auto_start_enabled', 'false'),
  ('discord_webhook_url', NULL),
  ('app_version', '1.0.0'),
  ('last_calibration_timestamp', NULL),
  ('theme_preference', 'system');
```

---

## Index Definitions & Query Optimization

| Index | Columns | Purpose | Primary Query Pattern |
|-------|---------|---------|----------------------|
| `idx_calibration_profiles_resolution` | `resolution` | Fast profile lookup by screen resolution | `SELECT * FROM calibration_profiles WHERE resolution = '1920x1080'` |
| `idx_detection_history_timestamp` | `timestamp DESC` | Recent detections for dashboard, logs | `SELECT * FROM detection_history ORDER BY timestamp DESC LIMIT 100` |
| `idx_detection_history_resolution_timestamp` | `resolution, timestamp DESC` | Per-resolution history (filter + sort) | `SELECT * FROM detection_history WHERE resolution = '1920x1080' ORDER BY timestamp DESC` |
| `idx_detection_history_state` | `state` | State aggregations (count by state) | `SELECT COUNT(*) FROM detection_history WHERE state = 'MATCH_FOUND'` |
| `idx_notification_log_status_timestamp` | `status, timestamp DESC` | Find failed notifications for retry | `SELECT * FROM notification_log WHERE status IN ('failed', 'retry') ORDER BY timestamp DESC LIMIT 10` |
| `idx_notification_log_detection_id` | `detection_history_id` | Fetch notifications for a detection (evidence view) | `SELECT * FROM notification_log WHERE detection_history_id = 123` |

---

## Migration Strategy

### Naming Convention

```
YYYYMMDDHHMMSS_description.sql

Examples:
  202602060000_init_schema.sql          — Initial schema
  202602061200_add_settings_table.sql   — Add new table
  202604151530_add_detection_evidence_json.sql  — Schema evolution
```

### Migration Execution (Python)

```python
# backend/src/db/migrations.py
import os
import sqlite3
from pathlib import Path

def run_migrations(db_path: str):
    """Execute all pending migrations in order"""
    
    migrations_dir = Path(__file__).parent / "migrations"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create migrations table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # List all migration files
    migrations = sorted(migrations_dir.glob("*.sql"))
    
    for migration_file in migrations:
        version = migration_file.stem  # e.g., "202602060000_init_schema"
        
        # Check if already executed
        cursor.execute("SELECT 1 FROM schema_migrations WHERE version = ?", (version,))
        if cursor.fetchone():
            print(f"Migration {version} already executed")
            continue
        
        # Execute migration
        with open(migration_file) as f:
            sql = f.read()
        
        try:
            cursor.executescript(sql)
            cursor.execute("INSERT INTO schema_migrations (version) VALUES (?)", (version,))
            conn.commit()
            print(f"✓ Executed {version}")
        except Exception as e:
            conn.rollback()
            print(f"✗ Failed {version}: {e}")
            raise
    
    conn.close()
```

---

## Common Query Patterns

### 1. Recent Detections (Dashboard)
```sql
SELECT id, state, confidence, timestamp, resolution
FROM detection_history
ORDER BY timestamp DESC
LIMIT 100;
```

### 2. State Aggregation (Stats)
```sql
SELECT state, COUNT(*) as count
FROM detection_history
WHERE timestamp > datetime('now', '-1 day')
GROUP BY state;
```

### 3. Failed Notifications (Retry Queue)
```sql
SELECT nl.id, dl.state, nl.error_message, nl.retry_count, nl.timestamp
FROM notification_log nl
JOIN detection_history dl ON nl.detection_history_id = dl.id
WHERE nl.status IN ('failed', 'retry')
  AND nl.retry_count < 5
ORDER BY nl.timestamp ASC
LIMIT 10;
```

### 4. Per-Resolution Performance
```sql
SELECT resolution, AVG(inference_latency_ms) as avg_latency_ms
FROM detection_history
WHERE timestamp > datetime('now', '-1 hour')
GROUP BY resolution;
```

### 5. Deduplication Check (Before Notification)
```sql
SELECT 1 FROM detection_history
WHERE state = ? AND timestamp > datetime('now', '-5 seconds')
LIMIT 1;
```

---

## Soft Delete Policy

**Decision**: Hard delete only; no soft delete needed.

**Rationale**:
- Settings table: updates only, never deleted (at rest)
- Detection history: append-only; deletions manual (user export → local backup → clear)
- No compliance-driven retention (not health/financial data)
- Simplifies queries (no `WHERE deleted_at IS NULL`)

**Manual Cleanup** (optional):
```sql
DELETE FROM detection_history WHERE timestamp < datetime('now', '-30 days');
```

---

## Summary

**Database design** for Overwatch Queue Notifier:
- **SQLite**: Zero-setup, fully local, ACID-compliant
- **4 tables**: Calibration profiles, detection history, notification log, settings
- **Optimized indices**: Fast queries for dashboard, logs, retry queue
- **Migrations**: SQL scripts with version tracking
- **Simple patterns**: Append-only logs, k-v settings, minimal joins

This design supports **fast queries**, **easy maintenance**, and **no external dependencies**.
