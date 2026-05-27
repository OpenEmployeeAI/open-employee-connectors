"""Inbound feedback collector Activity skeletons."""

from __future__ import annotations

from contracts.feedback import (
    ActivityName,
    InboundFetchInput,
    InboundFetchResult,
    InboundListInput,
    InboundListResult,
    is_valid_activity_name,
)

ACTIVITY_LIST_SIGNALS: ActivityName = ActivityName("mcp__feedback__list_signals")
ACTIVITY_FETCH_SIGNAL: ActivityName = ActivityName("mcp__feedback__fetch_signal")

assert is_valid_activity_name(ACTIVITY_LIST_SIGNALS)
assert is_valid_activity_name(ACTIVITY_FETCH_SIGNAL)


def list_signals(_input: InboundListInput) -> InboundListResult:
    """List normalized inbound feedback signals (skeleton)."""
    raise NotImplementedError("inbound list_signals is not implemented in this slice")


def fetch_signal(_input: InboundFetchInput) -> InboundFetchResult:
    """Fetch one normalized inbound feedback signal (skeleton)."""
    raise NotImplementedError("inbound fetch_signal is not implemented in this slice")
