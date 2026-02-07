ALTER TABLE detection_history ADD COLUMN escalated INTEGER NOT NULL DEFAULT 0;
ALTER TABLE detection_history ADD COLUMN evidence_image_base64 TEXT;
ALTER TABLE detection_history ADD COLUMN window_resolution TEXT;

UPDATE detection_history
SET window_resolution = resolution
WHERE window_resolution IS NULL;
