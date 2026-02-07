from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Set


@dataclass
class TransitionResult:
    previous_state: str
    state: str
    transitioned: bool
    should_notify: bool
    reason: str


class StateMachine:
    def __init__(
        self,
        initial_state: str = "IDLE",
        debounce_confidence_threshold: float = 0.8,
        min_confirmations: int = 2,
    ) -> None:
        self.current_state = initial_state
        self._debounce_threshold = debounce_confidence_threshold
        self._min_confirmations = min_confirmations
        self._pending_state: str | None = None
        self._pending_count = 0
        self._last_notified_match = False

        self._transitions: Dict[str, Set[str]] = {
            "IDLE": {"QUEUE"},
            "QUEUE": {"MATCH_FOUND", "IDLE"},
            "MATCH_FOUND": {"IN_GAME", "QUEUE"},
            "IN_GAME": {"IDLE", "QUEUE"},
            "LOADING": {"IN_GAME", "IDLE"},
            "HERO_SELECT": {"QUEUE", "MATCH_FOUND", "IN_GAME"},
        }

    def _is_valid_transition(self, target_state: str) -> bool:
        if target_state == self.current_state:
            return True
        valid_targets = self._transitions.get(self.current_state, set())
        return target_state in valid_targets

    def transition(self, target_state: str, confidence: float) -> TransitionResult:
        prev = self.current_state
        if target_state == self.current_state:
            self._pending_state = None
            self._pending_count = 0
            return TransitionResult(
                previous_state=prev,
                state=self.current_state,
                transitioned=False,
                should_notify=False,
                reason="idempotent",
            )

        if confidence < self._debounce_threshold:
            if self._pending_state == target_state:
                self._pending_count += 1
            else:
                self._pending_state = target_state
                self._pending_count = 1
            if self._pending_count < self._min_confirmations:
                return TransitionResult(
                    previous_state=prev,
                    state=self.current_state,
                    transitioned=False,
                    should_notify=False,
                    reason="debounced_waiting_confirmation",
                )

        self._pending_state = None
        self._pending_count = 0
        if not self._is_valid_transition(target_state):
            return TransitionResult(
                previous_state=prev,
                state=self.current_state,
                transitioned=False,
                should_notify=False,
                reason="invalid_transition",
            )

        self.current_state = target_state
        should_notify = target_state == "MATCH_FOUND" and not self._last_notified_match
        if target_state == "MATCH_FOUND":
            self._last_notified_match = True
        elif target_state != "MATCH_FOUND":
            self._last_notified_match = False

        return TransitionResult(
            previous_state=prev,
            state=self.current_state,
            transitioned=True,
            should_notify=should_notify,
            reason="ok",
        )
