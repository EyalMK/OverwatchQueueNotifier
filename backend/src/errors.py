from __future__ import annotations


class OverwatchQueueError(Exception):
    """Base error for backend domain exceptions."""


class WindowNotFoundError(OverwatchQueueError):
    """Raised when the Overwatch window cannot be located."""

