from __future__ import annotations


class OverwatchQueueError(Exception):
    """Base error for backend domain exceptions."""


class WindowNotFoundError(OverwatchQueueError):
    """Raised when the Overwatch window cannot be located."""


class ResolutionMismatchError(OverwatchQueueError):
    """Raised when captured frame resolution does not match the expected value."""


class AIInferenceError(OverwatchQueueError):
    """Raised when model loading or inference fails."""
