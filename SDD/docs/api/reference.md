# API Reference
## Overwatch AI Queue Detection & Notification App

**Generated**: February 6, 2026  
**Version**: 1.0

---

## Base URL

```
http://127.0.0.1:5000
```

All requests are JSON. All tools are behind `/mcp/tools/`.

---

## Tools / Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/mcp/tools/screen.perceive_state` | Classify game state from screen |
| POST | `/mcp/tools/screen.capture_regions` | Capture cropped UI regions |
| POST | `/mcp/tools/notify.desktop` | Send Windows desktop notification |
| POST | `/mcp/tools/notify.discord` | Send Discord webhook notification |

---

## Tool 1: screen.perceive_state

**Purpose**: Classify current Overwatch game state

**Request**:
```json
{
  "timestamp": "2026-02-06T14:30:45.123Z",
  "resolution": "1920x1080",
  "debug": false
}
```

**Response (200 - Success)**:
```json
{
  "state": "MATCH_FOUND",
  "confidence": 0.94,
  "timestamp": "2026-02-06T14:30:45.500Z",
  "inference_latency_ms": 42,
  "evidence": {
    "gate_triggered": true,
    "gate_signals": {
      "pixel_diff_pct": 15.3,
      "histogram_divergence": 0.78
    },
    "classifier": "tiny_v1.0",
    "escalation_used": false,
    "crop_regions": [
      {
        "name": "match_found_button",
        "crop_coords": [960, 540, 1200, 600],
        "confidence_per_region": 0.96
      }
    ]
  }
}
```

**Response (400 - Error)**:
```json
{
  "error": "WindowNotFoundError",
  "error_code": "ERR_WINDOW_NOT_FOUND",
  "message": "Overwatch window not found. Is the game running?",
  "timestamp": "2026-02-06T14:30:45.500Z"
}
```

**Status Codes**:
- `200`: Success
- `400`: Bad request (invalid resolution, window not found)
- `503`: AI inference error (model initialization failed)
- `429`: Rate limited (too many requests)

---

## Tool 2: screen.capture_regions

**Purpose**: Capture and return cropped screen regions

**Request**:
```json
{
  "resolution": "1920x1080",
  "regions": [
    {
      "name": "queue_icon",
      "crop_normalized": [0.45, 0.25, 0.55, 0.35]
    },
    {
      "name": "match_found_popup",
      "crop_normalized": [0.40, 0.40, 0.60, 0.60]
    }
  ],
  "format": "jpg"
}
```

**Response (200)**:
```json
{
  "timestamp": "2026-02-06T14:30:45.123Z",
  "resolution": "1920x1080",
  "regions": [
    {
      "name": "queue_icon",
      "data_base64": "iVBORw0KGgoAAAANSUhEUgAAAA...",
      "format": "jpg",
      "size_bytes": 1240,
      "dims": [96, 96]
    },
    {
      "name": "match_found_popup",
      "data_base64": "iVBORw0KGgoAAAANSUhEUgAAAA...",
      "format": "jpg",
      "size_bytes": 3560,
      "dims": [192, 192]
    }
  ],
  "total_capture_time_ms": 12
}
```

---

## Tool 3: notify.desktop

**Purpose**: Send Windows Toast notification

**Request**:
```json
{
  "title": "MATCH FOUND!",
  "body": "Your team has found a match! Confidence: 94%",
  "urgency": "high",
  "sound": true,
  "action_url": null
}
```

**Response (200)**:
```json
{
  "notification_id": "ow_20260206_143045_abc123",
  "delivered": true,
  "timestamp": "2026-02-06T14:30:45.600Z"
}
```

---

## Tool 4: notify.discord

**Purpose**: Send Discord webhook notification

**Request**:
```json
{
  "webhook_url": "https://discord.com/api/webhooks/12345/abcdef",
  "content": "MATCH FOUND! 🎮",
  "embed": {
    "title": "Overwatch Match Detection",
    "description": "Your team found a match!",
    "color": 16711680,
    "fields": [
      {
        "name": "Confidence",
        "value": "94%"
      },
      {
        "name": "Detection Time",
        "value": "14:30:45"
      }
    ]
  }
}
```

**Response (200)**:
```json
{
  "webhook_id": "12345",
  "message_id": "109876543210",
  "delivered": true,
  "timestamp": "2026-02-06T14:30:46.200Z"
}
```

**Response (429 - Rate Limited)**:
```json
{
  "error": "RateLimited",
  "message": "Discord rate limit hit",
  "retry_after_ms": 5000,
  "timestamp": "2026-02-06T14:30:46.200Z"
}
```

---

## Error Codes

| Code | HTTP | Meaning | Recovery |
|------|------|---------|----------|
| `ERR_WINDOW_NOT_FOUND` | 400 | Overwatch game window not detected | Wait for user to launch game |
| `ERR_RESOLUTION_MISMATCH` | 400 | Screen resolution not in calibration profile | Run calibration wizard |
| `ERR_AI_INFERENCE` | 503 | ONNX model loading/inference failed | Check model file integrity |
| `ERR_RATE_LIMITED` | 429 | Too many requests (Discord webhook) | Retry with exponential backoff |
| `ERR_DISCORD_WEBHOOK_INVALID` | 400 | Webhook URL malformed or invalid | Re-enter webhook URL in settings |
| `ERR_INTERNAL_SERVER_ERROR` | 500 | Unexpected error in backend | Check logs; report issue |

---

## Retry Strategy

**For transient failures (429, 503)**:
```
Attempt 1: Wait 1s → Retry
Attempt 2: Wait 2s → Retry
Attempt 3: Wait 4s → Retry
Attempt 4: Wait 8s → Retry
Attempt 5: Wait 16s → Retry
Attempt 6: Wait 30s → Give up
```

---

## Example Workflow

```
1. POST /mcp/tools/screen.perceive_state
   ← { state: "QUEUE", confidence: 0.87 }

2. Wait 500ms (perception cycle)

3. POST /mcp/tools/screen.perceive_state
   ← { state: "MATCH_FOUND", confidence: 0.94 }

4. POST /mcp/tools/notify.desktop
   ← { delivered: true }

5. POST /mcp/tools/notify.discord
   ← { delivered: true }
```

---

## Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| `screen.perceive_state` | 100 req/s | Per second |
| `screen.capture_regions` | 50 req/s | Per second |
| `notify.discord` | 10 req/10s | Global (Discord limit) |
| `notify.desktop` | 100 req/min | Per minute |

---

## Summary

MCP tools provide a **clean, RESTful interface** for:
- **Perception**: Get current game state
- **Capture**: Get cropped region images
- **Notification**: Send alerts to user

All responses include **timestamp + error handling** for reliable orchestration by Strands agents.
