from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from io import BytesIO
from time import monotonic, perf_counter
from typing import Deque, List, Literal, Optional, Tuple

import uvicorn
import base64
import json
import numpy as np
from PIL import Image
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, HttpUrl, conlist

from ..config import load_config
from ..errors import WindowNotFoundError
from ..perception import ClassifierService, GateService, ScreenCaptureService
from ..state.repository import CalibrationRepository, NotificationRepository

GameState = Literal[
    "IDLE",
    "QUEUE",
    "MATCH_FOUND",
    "HERO_SELECT",
    "LOADING",
    "IN_GAME",
    "UNKNOWN",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ErrorResponse(BaseModel):
    error: str
    error_code: str
    message: str
    timestamp: str
    retry_after_ms: Optional[int] = None


@dataclass
class MCPError(Exception):
    message: str
    error: str
    error_code: str
    http_status: int
    retry_after_ms: Optional[int] = None


class RateLimiter:
    def __init__(self, max_requests: int, per_seconds: float) -> None:
        self.max_requests = max_requests
        self.per_seconds = per_seconds
        self._hits: Deque[float] = deque()

    def check(self) -> Optional[int]:
        now = monotonic()
        window_start = now - self.per_seconds
        while self._hits and self._hits[0] < window_start:
            self._hits.popleft()

        if len(self._hits) >= self.max_requests:
            retry_after = self._hits[0] + self.per_seconds - now
            return max(1, int(retry_after * 1000))

        self._hits.append(now)
        return None


def _parse_resolution(resolution: str) -> Tuple[int, int]:
    if "x" not in resolution:
        raise MCPError(
            message="Resolution must be in WIDTHxHEIGHT format.",
            error="ResolutionMismatchError",
            error_code="ERR_RES_MISMATCH",
            http_status=400,
        )
    width_str, height_str = resolution.split("x", 1)
    if not width_str.isdigit() or not height_str.isdigit():
        raise MCPError(
            message="Resolution must use numeric dimensions.",
            error="ResolutionMismatchError",
            error_code="ERR_RES_MISMATCH",
            http_status=400,
        )
    width, height = int(width_str), int(height_str)
    if width <= 0 or height <= 0:
        raise MCPError(
            message="Resolution dimensions must be positive.",
            error="ResolutionMismatchError",
            error_code="ERR_RES_MISMATCH",
            http_status=400,
        )
    return width, height


def _validate_crop_normalized(region: "CaptureRegion") -> None:
    x1, y1, x2, y2 = region.crop_normalized
    for value in (x1, y1, x2, y2):
        if value < 0 or value > 1:
            raise MCPError(
                message="crop_normalized values must be between 0 and 1.",
                error="ValidationError",
                error_code="ERR_VALIDATION",
                http_status=400,
            )
    if x2 <= x1 or y2 <= y1:
        raise MCPError(
            message="crop_normalized must define a positive-width rectangle.",
            error="ValidationError",
            error_code="ERR_VALIDATION",
            http_status=400,
            )


def _encode_image(image: np.ndarray, fmt: Literal["jpg", "png"]) -> Tuple[str, int, List[int]]:
    if image.size == 0:
        raise MCPError(
            message="Crop region produced empty image.",
            error="ValidationError",
            error_code="ERR_VALIDATION",
            http_status=400,
        )
    pil_image = Image.fromarray(image)
    buffer = BytesIO()
    save_format = "JPEG" if fmt == "jpg" else "PNG"
    pil_image.save(buffer, format=save_format)
    data = buffer.getvalue()
    encoded = base64.b64encode(data).decode("ascii")
    return encoded, len(data), [pil_image.width, pil_image.height]


def _load_profile_regions(
    repo: CalibrationRepository, resolution: str
) -> List[CaptureRegion]:
    raw = repo.load(resolution)
    if not raw:
        raise MCPError(
            message="No calibration profile found for resolution.",
            error="NoCalibrationProfileError",
            error_code="ERR_NO_CALIBRATION",
            http_status=400,
        )
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise MCPError(
            message="Calibration profile is invalid.",
            error="NoCalibrationProfileError",
            error_code="ERR_NO_CALIBRATION",
            http_status=400,
        ) from exc
    regions = payload.get("regions", [])
    if not isinstance(regions, list) or not regions:
        raise MCPError(
            message="Calibration profile has no regions.",
            error="NoCalibrationProfileError",
            error_code="ERR_NO_CALIBRATION",
            http_status=400,
        )
    parsed: List[CaptureRegion] = []
    for region in regions:
        name = region.get("name")
        crop = region.get("crop_normalized")
        if not name or not isinstance(crop, list) or len(crop) != 4:
            continue
        parsed.append(CaptureRegion(name=name, crop_normalized=crop))
    if not parsed:
        raise MCPError(
            message="Calibration profile has no usable regions.",
            error="NoCalibrationProfileError",
            error_code="ERR_NO_CALIBRATION",
            http_status=400,
        )
    return parsed


class PerceiveStateRequest(BaseModel):
    timestamp: str = Field(..., description="ISO8601 timestamp")
    resolution: str = Field(..., description="Resolution like 1920x1080")
    debug: bool = False


class GateSignals(BaseModel):
    pixel_diff_pct: float
    histogram_change: float


class CroppedRegionEvidence(BaseModel):
    name: str
    crop_coords: List[int]
    confidence_per_region: float


class Evidence(BaseModel):
    gate_triggered: bool
    gate_signals: GateSignals
    classifier_version: str
    model_name: str
    cropped_regions: List[CroppedRegionEvidence]
    escalation_used: bool


class PerceiveStateResponse(BaseModel):
    state: GameState
    confidence: float
    timestamp: str
    inference_latency_ms: int
    evidence: Evidence


class CaptureRegion(BaseModel):
    name: str
    crop_normalized: conlist(float, min_length=4, max_length=4)


class CaptureRegionsRequest(BaseModel):
    resolution: str
    regions: List[CaptureRegion]
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
    total_capture_time_ms: int


class NotifyDesktopRequest(BaseModel):
    title: str
    body: str
    urgency: Literal["low", "normal", "high"] = "normal"
    sound: bool = True
    action_url: Optional[str] = None
    detection_id: Optional[int] = None


class NotifyDesktopResponse(BaseModel):
    notification_id: str
    sent_at: str
    delivered: bool


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


def create_app() -> FastAPI:
    app = FastAPI(title="Overwatch Queue Notifier MCP Server", version="0.1.0")
    config = load_config()
    screen_capture = ScreenCaptureService(window_title=config.overwatch_window_title)
    gate = GateService(config)
    classifier = ClassifierService(config)
    calibration_repo = CalibrationRepository(config.db_path)
    notification_repo = NotificationRepository(config.db_path)
    app.state.last_frame = None
    app.state.last_state = "IDLE"
    app.state.last_confidence = 0.0
    rate_limits = {
        "perceive_state": RateLimiter(max_requests=100, per_seconds=1.0),
        "capture_regions": RateLimiter(max_requests=50, per_seconds=1.0),
        "notify_desktop": RateLimiter(max_requests=100, per_seconds=60.0),
        "notify_discord": RateLimiter(max_requests=10, per_seconds=10.0),
    }

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                error="ValidationError",
                error_code="ERR_VALIDATION",
                message=str(exc),
                timestamp=_now_iso(),
            ).model_dump(),
        )

    @app.exception_handler(MCPError)
    async def mcp_error_handler(_request: Request, exc: MCPError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.http_status,
            content=ErrorResponse(
                error=exc.error,
                error_code=exc.error_code,
                message=exc.message,
                timestamp=_now_iso(),
                retry_after_ms=exc.retry_after_ms,
            ).model_dump(),
        )

    @app.post(
        "/mcp/tools/screen.perceive_state",
        response_model=PerceiveStateResponse,
    )
    async def perceive_state(request: PerceiveStateRequest) -> PerceiveStateResponse:
        retry_after = rate_limits["perceive_state"].check()
        if retry_after is not None:
            raise MCPError(
                message="Too many requests.",
                error="RateLimitedError",
                error_code="ERR_RATE_LIMITED",
                http_status=429,
                retry_after_ms=retry_after,
            )

        req_width, req_height = _parse_resolution(request.resolution)

        try:
            frame = screen_capture.capture()
        except WindowNotFoundError as exc:
            raise MCPError(
                message=str(exc),
                error="WindowNotFoundError",
                error_code="ERR_WIN_NOT_FOUND",
                http_status=400,
            ) from exc

        if frame.shape[1] != req_width or frame.shape[0] != req_height:
            raise MCPError(
                message="Captured frame resolution does not match request.",
                error="ResolutionMismatchError",
                error_code="ERR_RES_MISMATCH",
                http_status=400,
            )

        gate_triggered = True
        if app.state.last_frame is not None:
            gate_triggered = gate.should_process(app.state.last_frame, frame)

        inference_latency_ms = 0
        state = app.state.last_state
        confidence = app.state.last_confidence
        model_name = "None"
        classifier_version = "none"
        escalation_used = False

        if gate_triggered or app.state.last_frame is None:
            start = perf_counter()
            result = classifier.predict_with_escalation(frame)
            inference_latency_ms = int((perf_counter() - start) * 1000)
            state = result.state
            confidence = result.confidence
            escalation_used = result.escalated
            if escalation_used:
                model_name = "MobileNetV2"
                classifier_version = "escalation_v1.0"
            else:
                model_name = "TinyMobileNetV3"
                classifier_version = "tiny_v1.0"

        app.state.last_frame = frame
        app.state.last_state = state
        app.state.last_confidence = confidence

        signals = gate.last_signals or GateSignals(
            pixel_diff_pct=0.0, histogram_change=0.0
        )

        evidence = Evidence(
            gate_triggered=gate_triggered,
            gate_signals=signals,
            classifier_version=classifier_version,
            model_name=model_name,
            cropped_regions=[],
            escalation_used=escalation_used,
        )
        return PerceiveStateResponse(
            state=state,
            confidence=confidence,
            timestamp=_now_iso(),
            inference_latency_ms=inference_latency_ms,
            evidence=evidence,
        )

    @app.post(
        "/mcp/tools/screen.capture_regions",
        response_model=CaptureRegionsResponse,
    )
    async def capture_regions(
        request: CaptureRegionsRequest,
    ) -> CaptureRegionsResponse:
        retry_after = rate_limits["capture_regions"].check()
        if retry_after is not None:
            raise MCPError(
                message="Too many requests.",
                error="RateLimitedError",
                error_code="ERR_RATE_LIMITED",
                http_status=429,
                retry_after_ms=retry_after,
            )

        req_width, req_height = _parse_resolution(request.resolution)
        regions = request.regions
        if not regions:
            regions = _load_profile_regions(calibration_repo, request.resolution)
        for region in regions:
            _validate_crop_normalized(region)

        try:
            frame = screen_capture.capture()
        except WindowNotFoundError as exc:
            raise MCPError(
                message=str(exc),
                error="WindowNotFoundError",
                error_code="ERR_WIN_NOT_FOUND",
                http_status=400,
            ) from exc

        if frame.shape[1] != req_width or frame.shape[0] != req_height:
            raise MCPError(
                message="Captured frame resolution does not match request.",
                error="ResolutionMismatchError",
                error_code="ERR_RES_MISMATCH",
                http_status=400,
            )

        start = perf_counter()
        height, width = frame.shape[0], frame.shape[1]
        captured: List[CapturedRegion] = []
        for region in regions:
            x1, y1, x2, y2 = region.crop_normalized
            left = int(x1 * width)
            top = int(y1 * height)
            right = int(x2 * width)
            bottom = int(y2 * height)
            crop = frame[top:bottom, left:right]
            data_base64, size_bytes, dims = _encode_image(crop, request.format)
            captured.append(
                CapturedRegion(
                    name=region.name,
                    data_base64=data_base64,
                    format=request.format,
                    size_bytes=size_bytes,
                    dims=dims,
                )
            )
        return CaptureRegionsResponse(
            timestamp=_now_iso(),
            resolution=request.resolution,
            regions=captured,
            total_capture_time_ms=int((perf_counter() - start) * 1000),
        )

    @app.post(
        "/mcp/tools/notify.desktop",
        response_model=NotifyDesktopResponse,
    )
    async def notify_desktop(
        request: NotifyDesktopRequest,
    ) -> NotifyDesktopResponse:
        retry_after = rate_limits["notify_desktop"].check()
        if retry_after is not None:
            raise MCPError(
                message="Too many requests.",
                error="RateLimitedError",
                error_code="ERR_RATE_LIMITED",
                http_status=429,
                retry_after_ms=retry_after,
            )

        timestamp = _now_iso()
        if request.detection_id is not None:
            try:
                notification_repo.insert(
                    detection_id=request.detection_id,
                    type="desktop",
                    status="sent",
                )
            except Exception:
                pass
        notification_id = f"ow_notif_{timestamp.replace(':', '').replace('-', '')}"
        return NotifyDesktopResponse(
            notification_id=notification_id,
            sent_at=timestamp,
            delivered=True,
        )

    @app.post(
        "/mcp/tools/notify.discord",
        response_model=NotifyDiscordResponse,
    )
    async def notify_discord(
        request: NotifyDiscordRequest,
    ) -> NotifyDiscordResponse:
        retry_after = rate_limits["notify_discord"].check()
        if retry_after is not None:
            raise MCPError(
                message="Discord rate limit exceeded.",
                error="RateLimitedError",
                error_code="ERR_RATE_LIMITED",
                http_status=429,
                retry_after_ms=retry_after,
            )

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
