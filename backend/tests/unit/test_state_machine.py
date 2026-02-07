from __future__ import annotations

from src.state.state_machine import StateMachine


def test_valid_transitions_flow() -> None:
    sm = StateMachine()
    assert sm.transition("QUEUE", 0.95).transitioned is True
    assert sm.transition("MATCH_FOUND", 0.95).transitioned is True
    assert sm.transition("IN_GAME", 0.95).transitioned is True


def test_invalid_transition_is_rejected() -> None:
    sm = StateMachine()
    result = sm.transition("MATCH_FOUND", 0.95)
    assert result.transitioned is False
    assert result.reason == "invalid_transition"


def test_idempotent_state_no_transition() -> None:
    sm = StateMachine()
    sm.transition("QUEUE", 0.95)
    result = sm.transition("QUEUE", 0.95)
    assert result.transitioned is False
    assert result.reason == "idempotent"


def test_match_found_notifies_once() -> None:
    sm = StateMachine()
    sm.transition("QUEUE", 0.95)
    first = sm.transition("MATCH_FOUND", 0.95)
    second = sm.transition("MATCH_FOUND", 0.95)
    assert first.should_notify is True
    assert second.should_notify is False


def test_debounce_requires_two_confirmations() -> None:
    sm = StateMachine(debounce_confidence_threshold=0.85, min_confirmations=2)
    sm.transition("QUEUE", 0.95)
    first = sm.transition("MATCH_FOUND", 0.75)
    second = sm.transition("MATCH_FOUND", 0.75)
    assert first.transitioned is False
    assert first.reason == "debounced_waiting_confirmation"
    assert second.transitioned is True
