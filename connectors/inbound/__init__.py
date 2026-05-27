"""Inbound feedback provider collector skeleton.

Provider collectors pull or receive feedback signals from external
systems and normalize them into ``FeedbackSignal`` values. This module
declares the Activity name registry and a no-network skeleton.
"""

from connectors.inbound.activities import (
    ACTIVITY_FETCH_SIGNAL,
    ACTIVITY_LIST_SIGNALS,
    fetch_signal,
    list_signals,
)

__all__ = [
    "ACTIVITY_FETCH_SIGNAL",
    "ACTIVITY_LIST_SIGNALS",
    "fetch_signal",
    "list_signals",
]
