from __future__ import annotations

import base64
import json
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from io import BytesIO
from time import monotonic
from typing import Deque, Dict, List, Literal, Optional, Tuple

import numpy as np
import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from PIL import Image
from pydantic import BaseModel, Field, HttpUrl, conlist

from ..config import load_config
from ..db.migrations import run_migrations
from ..errors import AIInferenceError, WindowNotFoundError
from ..perception import ClassifierService, GateService, ScreenCaptureService
from ..state.repository import CalibrationRepository, DetectionRepository, NotificationRepository
from ..state.state_machine import StateMachine

GameState = Literal[
    "IDLE",
    "QUEUE",
    "MATCH_FOUND",
    "HERO_SELECT",
    "LOADING",
    "IN_GAME",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass
class MCPError(Exception):
    message: str
    error: str
    http_status: int
    retry_after_ms: Optional[int] = None


class ErrorResponse(BaseModel):
    error: str
    message: str
    retry_after_ms: Optional[int] = None


class RateLimiter:
    def __init__(self, max_requests: int, per_seconds: float) -> None:
        self.max_requests = max_requests
        self.per_seconds = per_seconds
        self._hits: Dict[str, Deque[float]] = defaultdict(deque)

    def check(self, client_key: str) -> Optional[int]:
        now = monotonic()
        queue = self._hits[client_key]
        window_start = now - self.per_seconds
        while queue and queue[0] < window_start:
            queue.popleft()
        if len(queue) >= self.max_requests:
            retry_after = queue[0] + self.per_seconds - now
            return max(1, int(retry_after * 1000))
        queue.append(now)
        return None


class PerceiveStateRequest(BaseModel):
    resolution: str = Field(..., description="Resolution in WIDTHxHEIGHT format")
    calibration_profile_id: Optional[str] = None
    check_escalation: bool = True


class PerceiveStateResponse(BaseModel):
    state: GameState
    confidence: float
    escalated: bool
    evidence_image_base64: str
    detected_at: str


class CaptureRegion(BaseModel):
    name: str
    crop_normalized: conlist(float, min_length=4, max_length=4)


class CaptureRegionsRequest(BaseModel):
    resolution: str
    regions: List[CaptureRegion] = Field(default_factory=list)
    format: Literal["jpg", "png"] = "jpg"


class CapturedRegion(BaseModel):
    name: str
    data_base64: str
    format: Literal["jpg", "png"]
    size_bytes: int
    dims: List[int]


class CaptureRegionsResponse(BaseModel):
    timestamp: str
    resolution: str
    regions: List[CapturedRegion]


class NotifyDesktopRequest(BaseModel):
    title: str
    message: str
    urgency: Literal["critical", "normal", "low"] = "normal"
    sound: bool = True
    action: Optional[str] = None


class NotifyDesktopResponse(BaseModel):
    notification_id: str
    delivered: bool
    platform: str
    delivered_at: str


class DiscordEmbedField(BaseModel):
    name: str
    value: str
    inline: bool = False


class DiscordEmbed(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    color: Optional[int] = None
    fields: Optional[List[DiscordEmbedField]] = None


class NotifyDiscordRequest(BaseModel):
    webhook_url: HttpUrl
    content: str
    embed: Optional[DiscordEmbed] = None
    detection_id: Optional[int] = None


class NotifyDiscordResponse(BaseModel):
    discord_message_id: str
    status: Literal["delivered", "failed"]
    timestamp: str


def _parse_resolution(resolution: str) -> Tuple[int, int]:
    if "x" not in resolution:
        raise MCPError("Resolution must be in WIDTHxHEIGHT format.", "ResolutionMismatchError", 400)
    width_s, height_s = resolution.split("x", 1)
    if not width_s.isdigit() or not height_s.isdigit():
        raise MCPError("Resolution values must be numeric.", "ResolutionMismatchError", 400)
    width, height = int(width_s), int(height_s)
    if width <= 0 or height <= 0:
        raise MCPError("Resolution values must be positive.", "ResolutionMismatchError", 400)
    return width, height


def _validate_region(region: CaptureRegion) -> None:
    x1, y1, x2, y2 = region.crop_normalized
    if not (0 <= x1 < x2 <= 1 and 0 <= y1 < y2 <= 1):
        raise MCPError("crop_normalized must be [x1,y1,x2,y2] in [0,1].", "ValidationError", 400)


def _encode_image(image: np.ndarray, fmt: Literal["jpg", "png"]) -> Tuple[str, int, List[int]]:
    if image.size == 0:
        raise MCPError("Crop produced an empty image.", "ValidationError", 400)
    pil = Image.fromarray(image)
    buf = BytesIO()
    pil.save(buf, format="JPEG" if fmt == "jpg" else "PNG")
    payload = buf.getvalue()
    return base64.b64encode(payload).decode("ascii"), len(payload), [pil.width, pil.height]


def _encode_evidence_crop(frame: np.ndarray) -> str:
    h, w = frame.shape[:2]
    crop_w = min(320, w)
    crop_h = min(240, h)
    x1 = (w - crop_w) // 2
    y1 = (h - crop_h) // 2
    crop = frame[y1 : y1 + crop_h, x1 : x1 + crop_w]
    encoded, _, _ = _encode_image(crop, "jpg")
    return encoded


def _load_profile_regions(repo: CalibrationRepository, resolution: str) -> List[CaptureRegion]:
    payload = repo.load(resolution)
    if not payload:
        raise MCPError("No calibration profile found for resolution.", "NoCalibrationProfileError", 400)
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise MCPError("Calibration profile is invalid JSON.", "NoCalibrationProfileError", 400) from exc
    regions = data.get("regions", [])
    parsed: List[CaptureRegion] = []
    for region in regions:
        if not isinstance(region, dict):
            continue
        name = region.get("name")
        crop = region.get("crop_normalized")
        if not isinstance(name, str) or not isinstance(crop, list) or len(crop) != 4:
            continue
        parsed.append(CaptureRegion(name=name, crop_normalized=crop))
    if not parsed:
        raise MCPError("Calibration profile has no usable regions.", "NoCalibrationProfileError", 400)
    return parsed


def _send_desktop_notification(
    title: str, message: str, urgency: str, sound: bool
) -> bool:  # pragma: no cover - platform dependent
    duration = {"critical": 10, "normal": 7, "low": 5}[urgency]
    try:
        from win10toast import ToastNotifier

        toaster = ToastNotifier()
        toaster.show_toast(title=title, msg=message, duration=duration, threaded=True)
        return True
    except Exception:
        return False


def create_app() -> FastAPI:
    app = FastAPI(title="Overwatch Queue Notifier MCP Server", version="0.1.0")
    config = load_config()
    run_migrations(config.db_path)

    screen_capture = ScreenCaptureService(window_title=config.overwatch_window_title)
    gate = GateService(config)
    classifier = ClassifierService(config)
    state_machine = StateMachine()
    calibration_repo = CalibrationRepository(config.db_path)
    detection_repo = DetectionRepository(config.db_path)
    notification_repo = NotificationRepository(config.db_path)

    app.state.last_frame = None
    app.state.cache_result: Optional[PerceiveStateResponse] = None
    app.state.cache_time = 0.0

    # Startup retention cleanup for MVP.
    try:
        detection_repo.cleanup_older_than(hours=24)
    except Exception:
        pass

    rate_limits = {
        "perceive_state": RateLimiter(10, 1.0),
        "capture_regions": RateLimiter(10, 1.0),
        "notify_desktop": RateLimiter(10, 1.0),
        "notify_discord": RateLimiter(10, 10.0),
    }

    def _client_key(request: Request) -> str:
        if request.client and request.client.host:
            return request.client.host
        return "unknown"

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(error="ValidationError", message=str(exc)).model_dump(),
        )

    @app.exception_handler(MCPError)
    async def mcp_error_handler(_request: Request, exc: MCPError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.http_status,
            content=ErrorResponse(
                error=exc.error,
                message=exc.message,
                retry_after_ms=exc.retry_after_ms,
            ).model_dump(),
        )

    @app.post("/mcp/tools/screen.perceive_state", response_model=PerceiveStateResponse)
    async def perceive_state(request: PerceiveStateRequest, raw_request: Request) -> PerceiveStateResponse:
        retry_after = rate_limits["perceive_state"].check(_client_key(raw_request))
        if retry_after is not None:
            raise MCPError("Too many requests.", "RateLimitedError", 429, retry_after)

        req_w, req_h = _parse_resolution(request.resolution)
        try:
            frame = screen_capture.capture()
        except WindowNotFoundError as exc:
            raise MCPError(str(exc), "WindowNotFoundError", 400) from exc

        got_h, got_w = frame.shape[:2]
        if got_w != req_w or got_h != req_h:
            raise MCPError(
                f"Window has resolution {got_w}x{got_h}, expected {req_w}x{req_h}",
                "ResolutionMismatchError",
                400,
            )

        should_process = gate.should_process(
            app.state.last_frame,
            frame,
            resolution=(req_w, req_h),
        )
        now = monotonic()
        cache_age_ms = int((now - app.state.cache_time) * 1000) if app.state.cache_result else None
        if not should_process and app.state.cache_result and cache_age_ms is not None and cache_age_ms < 500:
            app.state.last_frame = frame
            return app.state.cache_result

        try:
            if request.check_escalation:
                predicted_state, confidence, escalated = classifier.classify_with_escalation(frame)
            else:
                predicted_state, confidence = classifier.predict(frame)
                escalated = False
        except AIInferenceError as exc:
            raise MCPError(f"Classifier inference failed: {exc}", "AIInferenceError", 503) from exc

        transition = state_machine.transition(predicted_state, confidence)
        evidence_b64 = _encode_evidence_crop(frame)
        detected_at = _now_iso()
        response = PerceiveStateResponse(
            state=transition.state,  # type: ignore[arg-type]
            confidence=confidence,
            escalated=escalated,
            evidence_image_base64=evidence_b64,
            detected_at=detected_at,
        )

        evidence = {
            "resolution": request.resolution,
            "predicted_state": predicted_state,
            "applied_state": transition.state,
            "transition_reason": transition.reason,
            "gate_pixel_diff_pct": gate.last_signals.pixel_diff_pct if gate.last_signals else 0.0,
            "gate_histogram_change": gate.last_signals.histogram_change if gate.last_signals else 0.0,
        }
        detection_id = detection_repo.insert(
            state=transition.state,
            confidence=confidence,
            evidence=evidence,
            escalated=escalated,
            evidence_image_base64=evidence_b64,
            window_resolution=request.resolution,
        )
        if transition.should_notify:
            try:
                notification_repo.insert(
                    detection_id=detection_id,
                    type="desktop",
                    status="queued",
                )
            except Exception:
                pass

        app.state.last_frame = frame
        app.state.cache_result = response
        app.state.cache_time = now
        return response

    @app.post("/mcp/tools/screen.capture_regions", response_model=CaptureRegionsResponse)
    async def capture_regions(request: CaptureRegionsRequest, raw_request: Request) -> CaptureRegionsResponse:
        retry_after = rate_limits["capture_regions"].check(_client_key(raw_request))
        if retry_after is not None:
            raise MCPError("Too many requests.", "RateLimitedError", 429, retry_after)

        req_w, req_h = _parse_resolution(request.resolution)
        regions = request.regions or _load_profile_regions(calibration_repo, request.resolution)
        for region in regions:
            _validate_region(region)

        try:
            frame = screen_capture.capture()
        except WindowNotFoundError as exc:
            raise MCPError(str(exc), "WindowNotFoundError", 400) from exc

        got_h, got_w = frame.shape[:2]
        if got_w != req_w or got_h != req_h:
            raise MCPError(
                f"Window has resolution {got_w}x{got_h}, expected {req_w}x{req_h}",
                "ResolutionMismatchError",
                400,
            )

        captured: List[CapturedRegion] = []
        for region in regions:
            x1, y1, x2, y2 = region.crop_normalized
            left = int(x1 * req_w)
            top = int(y1 * req_h)
            right = int(x2 * req_w)
            bottom = int(y2 * req_h)
            crop = frame[top:bottom, left:right]
            data, size, dims = _encode_image(crop, request.format)
            captured.append(
                CapturedRegion(
                    name=region.name,
                    data_base64=data,
                    format=request.format,
                    size_bytes=size,
                    dims=dims,
                )
            )

        return CaptureRegionsResponse(
            timestamp=_now_iso(),
            resolution=request.resolution,
            regions=captured,
        )

    @app.post("/mcp/tools/notify.desktop", response_model=NotifyDesktopResponse)
    async def notify_desktop(request: NotifyDesktopRequest, raw_request: Request) -> NotifyDesktopResponse:
        retry_after = rate_limits["notify_desktop"].check(_client_key(raw_request))
        if retry_after is not None:
            raise MCPError("Too many requests.", "RateLimitedError", 429, retry_after)

        delivered = _send_desktop_notification(
            title=request.title,
            message=request.message,
            urgency=request.urgency,
            sound=request.sound,
        )
        notification_id = f"desktop_{int(monotonic() * 1000)}"
        return NotifyDesktopResponse(
            notification_id=notification_id,
            delivered=delivered,
            platform="windows10",
            delivered_at=_now_iso(),
        )

    @app.post("/mcp/tools/notify.discord", response_model=NotifyDiscordResponse)
    async def notify_discord(request: NotifyDiscordRequest, raw_request: Request) -> NotifyDiscordResponse:
        retry_after = rate_limits["notify_discord"].check(_client_key(raw_request))
        if retry_after is not None:
            raise MCPError("Discord rate limit exceeded.", "RateLimitedError", 429, retry_after)

        timestamp = _now_iso()
        if request.detection_id is not None:
            try:
                notification_repo.insert(
                    detection_id=request.detection_id,
                    type="discord",
                    status="sent",
                )
            except Exception:
                pass
        return NotifyDiscordResponse(
            discord_message_id=f"discord_{timestamp.replace(':', '').replace('-', '')}",
            status="delivered",
            timestamp=timestamp,
        )

    return app


app = create_app()


def main() -> None:
    config = load_config()
    uvicorn.run(
        "src.mcp.server:app",
        host="127.0.0.1",
        port=config.mcp_port,
        log_level=config.log_level.lower(),
    )


if __name__ == "__main__":
    main()
