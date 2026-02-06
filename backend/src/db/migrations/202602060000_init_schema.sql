PRAGMA foreign_keys = ON;

CREATE TABLE calibration_profiles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  resolution TEXT NOT NULL UNIQUE,
  profile_data BLOB NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_calibration_profiles_resolution ON calibration_profiles(resolution);

CREATE TABLE detection_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  calibration_id INTEGER,
  state TEXT NOT NULL CHECK(state IN ('IDLE', 'QUEUE', 'MATCH_FOUND', 'HERO_SELECT', 'LOADING', 'IN_GAME')),
  confidence REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
  resolution TEXT NOT NULL,
  inference_latency_ms INTEGER,
  evidence_json TEXT,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (calibration_id) REFERENCES calibration_profiles(id) ON DELETE SET NULL
);

CREATE INDEX idx_detection_history_timestamp ON detection_history(timestamp DESC);
CREATE INDEX idx_detection_history_resolution_timestamp ON detection_history(resolution, timestamp DESC);
CREATE INDEX idx_detection_history_state ON detection_history(state);

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

CREATE TABLE settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO settings (key, value) VALUES
  ('notification_sound_enabled', 'true'),
  ('auto_start_enabled', 'false'),
  ('discord_webhook_url', NULL),
  ('app_version', '1.0.0');
