"""Typed contracts for feedback provider boundaries.

This package defines the minimal data shapes used by outbound publishing
(Postiz) and inbound provider collectors. Implementations live in
``connectors/`` and are wired to Temporal Activities elsewhere.
"""

from contracts.feedback.types import (
    ActivityName,
    ApprovalToken,
    AuthRef,
    ArtifactRef,
    FeedbackSignal,
    InboundFetchInput,
    InboundFetchResult,
    InboundListInput,
    InboundListResult,
    MCPToolError,
    PostizCreatePostInput,
    PostizCreatePostResult,
    PostizPostStatusInput,
    PostizPostStatusResult,
    is_valid_activity_name,
)

__all__ = [
    "ActivityName",
    "ApprovalToken",
    "AuthRef",
    "ArtifactRef",
    "FeedbackSignal",
    "InboundFetchInput",
    "InboundFetchResult",
    "InboundListInput",
    "InboundListResult",
    "MCPToolError",
    "PostizCreatePostInput",
    "PostizCreatePostResult",
    "PostizPostStatusInput",
    "PostizPostStatusResult",
    "is_valid_activity_name",
]
