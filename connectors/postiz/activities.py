"""Postiz outbound Activity skeletons.

Activity names follow the canonical ``mcp__<server>__<tool>`` pattern.
Functions in this module are not yet wired to Temporal; they exist to
pin the contract surface so reviewers can ratify shapes before any
network code lands.
"""

from __future__ import annotations

from contracts.feedback import (
    ActivityName,
    PostizCreatePostInput,
    PostizCreatePostResult,
    PostizPostStatusInput,
    PostizPostStatusResult,
    is_valid_activity_name,
)

ACTIVITY_CREATE_POST: ActivityName = ActivityName("mcp__postiz__create_post")
ACTIVITY_GET_POST_STATUS: ActivityName = ActivityName("mcp__postiz__get_post_status")

assert is_valid_activity_name(ACTIVITY_CREATE_POST)
assert is_valid_activity_name(ACTIVITY_GET_POST_STATUS)


def create_post(_input: PostizCreatePostInput) -> PostizCreatePostResult:
    """Publish via Postiz (skeleton).

    Risky public write. The input contract requires an ``ApprovalToken``;
    that requirement is enforced by ``PostizCreatePostInput`` itself.
    Network I/O is intentionally not implemented here.
    """
    raise NotImplementedError("postiz outbound publishing is not implemented in this slice")


def get_post_status(_input: PostizPostStatusInput) -> PostizPostStatusResult:
    """Read post status via Postiz (skeleton)."""
    raise NotImplementedError("postiz status lookup is not implemented in this slice")
