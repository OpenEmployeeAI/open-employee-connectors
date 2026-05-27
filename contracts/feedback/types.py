"""Typed contracts for feedback provider boundaries.

Stdlib-only on purpose: this slice ships contracts, not runtime. The
shapes here are intended to be the Activity input/result types once
Temporal wiring lands.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal, NewType

# Deterministic Temporal Activity name. The pattern is enforced by
# ``is_valid_activity_name`` and exercised by the tests in this slice.
ActivityName = NewType("ActivityName", str)

_ACTIVITY_NAME_RE = re.compile(r"^mcp__[a-z0-9][a-z0-9_]*__[a-z0-9][a-z0-9_]*$")


def is_valid_activity_name(name: str) -> bool:
    """Return True iff ``name`` matches ``mcp__<server>__<tool>``."""
    return bool(_ACTIVITY_NAME_RE.match(name))


@dataclass(frozen=True)
class AuthRef:
    """Opaque reference to a credential resolved outside workflow history.

    The ``ref`` value must be a logical pointer (e.g. ``postiz/default``)
    that an out-of-workflow resolver can exchange for live credentials.
    Raw secrets must never be placed in this structure.
    """

    ref: str
    provider: str

    def __post_init__(self) -> None:
        if not self.ref or not self.provider:
            raise ValueError("AuthRef.ref and AuthRef.provider are required")
        if any(token in self.ref.lower() for token in ("sk-", "bearer ", "password=")):
            raise ValueError("AuthRef.ref must not contain raw secret material")


@dataclass(frozen=True)
class ApprovalToken:
    """Proof that a risky public write was approved by a human.

    The token is opaque to connectors; verification belongs to the policy
    layer. Connectors only check presence and surface ``approver`` for
    audit trails.
    """

    token: str
    approver: str
    granted_at: str  # ISO-8601 UTC; not parsed in this slice


@dataclass(frozen=True)
class ArtifactRef:
    """Claim-check pointer for large payloads kept out of workflow history."""

    uri: str
    size_bytes: int
    content_type: str


@dataclass(frozen=True)
class MCPToolError:
    """Structured error returned from an MCP Activity."""

    code: str
    message: str
    retryable: bool = False


# ---------------------------------------------------------------------------
# Outbound: Postiz (Gitroom-style external publishing service)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PostizCreatePostInput:
    """Input for ``mcp__postiz__create_post``.

    Postiz is treated as an external Gitroom-style service. We pass an
    ``auth_ref`` and the post payload; we never embed Postiz credentials.
    """

    auth_ref: AuthRef
    channels: tuple[str, ...]
    body: str
    scheduled_at: str | None = None
    approval: ApprovalToken | None = None

    def __post_init__(self) -> None:
        if self.auth_ref.provider != "postiz":
            raise ValueError("PostizCreatePostInput requires a postiz AuthRef")
        if not self.channels:
            raise ValueError("at least one channel is required")
        if not self.body.strip():
            raise ValueError("post body must not be empty")
        if self.approval is None:
            # Posting is a risky public write. The contract requires an
            # ApprovalToken to be present before the Activity is scheduled.
            raise ValueError("PostizCreatePostInput requires an ApprovalToken")


@dataclass(frozen=True)
class PostizCreatePostResult:
    post_id: str
    status: Literal["scheduled", "published", "queued"]
    channels: tuple[str, ...]


@dataclass(frozen=True)
class PostizPostStatusInput:
    auth_ref: AuthRef
    post_id: str

    def __post_init__(self) -> None:
        if self.auth_ref.provider != "postiz":
            raise ValueError("PostizPostStatusInput requires a postiz AuthRef")
        if not self.post_id:
            raise ValueError("post_id is required")


@dataclass(frozen=True)
class PostizPostStatusResult:
    post_id: str
    status: Literal["scheduled", "published", "queued", "failed"]
    detail: str | None = None


# ---------------------------------------------------------------------------
# Inbound: provider collectors
# ---------------------------------------------------------------------------


SignalKind = Literal["reaction", "reply", "rating", "ticket_comment"]


@dataclass(frozen=True)
class FeedbackSignal:
    """Normalized inbound feedback signal.

    Large bodies must be returned via ``artifact`` rather than ``preview``.
    ``preview`` is bounded to a short summary suitable for workflow history.
    """

    signal_id: str
    provider: str
    kind: SignalKind
    subject_ref: str
    received_at: str  # ISO-8601 UTC
    preview: str
    artifact: ArtifactRef | None = None

    def __post_init__(self) -> None:
        if len(self.preview) > 280:
            raise ValueError("preview exceeds 280 chars; use ArtifactRef instead")


@dataclass(frozen=True)
class InboundListInput:
    auth_ref: AuthRef
    since: str | None = None
    limit: int = 50

    def __post_init__(self) -> None:
        if self.limit <= 0 or self.limit > 500:
            raise ValueError("limit must be in (0, 500]")


@dataclass(frozen=True)
class InboundListResult:
    signals: tuple[FeedbackSignal, ...] = field(default_factory=tuple)
    next_cursor: str | None = None


@dataclass(frozen=True)
class InboundFetchInput:
    auth_ref: AuthRef
    signal_id: str

    def __post_init__(self) -> None:
        if not self.signal_id:
            raise ValueError("signal_id is required")


@dataclass(frozen=True)
class InboundFetchResult:
    signal: FeedbackSignal
