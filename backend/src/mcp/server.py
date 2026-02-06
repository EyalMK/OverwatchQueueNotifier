from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Literal, Optional

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, HttpUrl, conlist

from ..config import load_config

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


class NotifyDiscordResponse(BaseModel):
    discord_message_id: str
    status: Literal["delivered", "failed"]
    timestamp: str


def create_app() -> FastAPI:
    app = FastAPI(title="Overwatch Queue Notifier MCP Server", version="0.1.0")

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
        evidence = Evidence(
            gate_triggered=True,
            gate_signals=GateSignals(pixel_diff_pct=15.3, histogram_change=0.78),
            classifier_version="tiny_v1.0",
            model_name="TinyMobileNetV3",
            cropped_regions=[
                CroppedRegionEvidence(
                    name="match_found_button",
                    crop_coords=[960, 540, 1200, 600],
                    confidence_per_region=0.96,
                )
            ],
            escalation_used=False,
        )
        return PerceiveStateResponse(
            state="IDLE",
            confidence=0.92,
            timestamp=_now_iso(),
            inference_latency_ms=42,
            evidence=evidence,
        )

    @app.post(
        "/mcp/tools/screen.capture_regions",
        response_model=CaptureRegionsResponse,
    )
    async def capture_regions(
        request: CaptureRegionsRequest,
    ) -> CaptureRegionsResponse:
        captured = [
            CapturedRegion(
                name=region.name,
                data_base64="",
                format=request.format,
                size_bytes=0,
            )
            for region in request.regions
        ]
        return CaptureRegionsResponse(
            timestamp=_now_iso(),
            resolution=request.resolution,
            regions=captured,
            total_capture_time_ms=8,
        )

    @app.post(
        "/mcp/tools/notify.desktop",
        response_model=NotifyDesktopResponse,
    )
    async def notify_desktop(
        _request: NotifyDesktopRequest,
    ) -> NotifyDesktopResponse:
        timestamp = _now_iso()
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
        _request: NotifyDiscordRequest,
    ) -> NotifyDiscordResponse:
        timestamp = _now_iso()
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
