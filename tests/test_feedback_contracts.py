"""Contract tests for the feedback provider boundary slice.

These tests pin the invariants from ``docs/feedback/README.md``:

1. Activity names match ``mcp__<server>__<tool>``.
2. ``AuthRef`` rejects payloads that look like raw secrets.
3. Postiz ``create_post`` cannot be called without an ``ApprovalToken``.
4. Inbound previews are bounded so workflow history stays small.
"""

from __future__ import annotations

import unittest

from connectors.inbound.activities import (
    ACTIVITY_FETCH_SIGNAL,
    ACTIVITY_LIST_SIGNALS,
)
from connectors.postiz.activities import (
    ACTIVITY_CREATE_POST,
    ACTIVITY_GET_POST_STATUS,
)
from contracts.feedback import (
    ApprovalToken,
    ArtifactRef,
    AuthRef,
    FeedbackSignal,
    InboundListInput,
    PostizCreatePostInput,
    is_valid_activity_name,
)


class ActivityNameTests(unittest.TestCase):
    def test_postiz_activity_names_match_pattern(self) -> None:
        self.assertTrue(is_valid_activity_name(ACTIVITY_CREATE_POST))
        self.assertTrue(is_valid_activity_name(ACTIVITY_GET_POST_STATUS))
        self.assertEqual(ACTIVITY_CREATE_POST, "mcp__postiz__create_post")
        self.assertEqual(ACTIVITY_GET_POST_STATUS, "mcp__postiz__get_post_status")

    def test_inbound_activity_names_match_pattern(self) -> None:
        self.assertTrue(is_valid_activity_name(ACTIVITY_LIST_SIGNALS))
        self.assertTrue(is_valid_activity_name(ACTIVITY_FETCH_SIGNAL))
        self.assertEqual(ACTIVITY_LIST_SIGNALS, "mcp__feedback__list_signals")
        self.assertEqual(ACTIVITY_FETCH_SIGNAL, "mcp__feedback__fetch_signal")

    def test_invalid_activity_names_are_rejected(self) -> None:
        for bad in [
            "postiz_create_post",
            "mcp_postiz_create_post",
            "mcp__Postiz__create_post",
            "mcp__postiz__create-post",
            "mcp__postiz",
            "mcp____create_post",
        ]:
            self.assertFalse(is_valid_activity_name(bad), bad)


class AuthRefTests(unittest.TestCase):
    def test_valid_ref(self) -> None:
        ref = AuthRef(ref="postiz/default", provider="postiz")
        self.assertEqual(ref.provider, "postiz")

    def test_rejects_raw_secret_markers(self) -> None:
        for bad in ["sk-12345", "Bearer abcdef", "password=hunter2"]:
            with self.assertRaises(ValueError):
                AuthRef(ref=bad, provider="postiz")

    def test_requires_ref_and_provider(self) -> None:
        with self.assertRaises(ValueError):
            AuthRef(ref="", provider="postiz")
        with self.assertRaises(ValueError):
            AuthRef(ref="x", provider="")


class PostizApprovalTests(unittest.TestCase):
    def _ref(self) -> AuthRef:
        return AuthRef(ref="postiz/default", provider="postiz")

    def test_create_post_requires_approval(self) -> None:
        with self.assertRaises(ValueError):
            PostizCreatePostInput(
                auth_ref=self._ref(),
                channels=("twitter",),
                body="hello",
            )

    def test_create_post_with_approval_constructs(self) -> None:
        approval = ApprovalToken(
            token="tok-1",
            approver="alice@example.com",
            granted_at="2026-01-01T00:00:00Z",
        )
        post = PostizCreatePostInput(
            auth_ref=self._ref(),
            channels=("twitter",),
            body="hello",
            approval=approval,
        )
        self.assertEqual(post.approval, approval)

    def test_create_post_rejects_non_postiz_authref(self) -> None:
        with self.assertRaises(ValueError):
            PostizCreatePostInput(
                auth_ref=AuthRef(ref="x", provider="zendesk"),
                channels=("twitter",),
                body="hello",
                approval=ApprovalToken("tok", "a", "2026-01-01T00:00:00Z"),
            )

    def test_create_post_rejects_empty_channels_or_body(self) -> None:
        approval = ApprovalToken("tok", "a", "2026-01-01T00:00:00Z")
        with self.assertRaises(ValueError):
            PostizCreatePostInput(
                auth_ref=self._ref(),
                channels=(),
                body="x",
                approval=approval,
            )
        with self.assertRaises(ValueError):
            PostizCreatePostInput(
                auth_ref=self._ref(),
                channels=("twitter",),
                body="   ",
                approval=approval,
            )


class InboundContractTests(unittest.TestCase):
    def test_preview_length_is_bounded(self) -> None:
        with self.assertRaises(ValueError):
            FeedbackSignal(
                signal_id="s1",
                provider="zendesk",
                kind="ticket_comment",
                subject_ref="ticket/42",
                received_at="2026-01-01T00:00:00Z",
                preview="x" * 281,
            )

    def test_artifact_ref_carries_large_payload(self) -> None:
        signal = FeedbackSignal(
            signal_id="s1",
            provider="zendesk",
            kind="ticket_comment",
            subject_ref="ticket/42",
            received_at="2026-01-01T00:00:00Z",
            preview="short summary",
            artifact=ArtifactRef(
                uri="claimcheck://blob/abc",
                size_bytes=10_000,
                content_type="text/html",
            ),
        )
        self.assertIsNotNone(signal.artifact)

    def test_list_limit_bounds(self) -> None:
        ref = AuthRef(ref="zendesk/default", provider="zendesk")
        with self.assertRaises(ValueError):
            InboundListInput(auth_ref=ref, limit=0)
        with self.assertRaises(ValueError):
            InboundListInput(auth_ref=ref, limit=501)
        ok = InboundListInput(auth_ref=ref, limit=50)
        self.assertEqual(ok.limit, 50)


class SkeletonSafetyTests(unittest.TestCase):
    """Skeletons must not silently execute; they should raise NotImplementedError."""

    def test_postiz_skeletons_raise(self) -> None:
        from connectors.postiz import create_post, get_post_status

        approval = ApprovalToken("tok", "a", "2026-01-01T00:00:00Z")
        ref = AuthRef(ref="postiz/default", provider="postiz")
        post = PostizCreatePostInput(
            auth_ref=ref, channels=("twitter",), body="hi", approval=approval
        )
        with self.assertRaises(NotImplementedError):
            create_post(post)
        from contracts.feedback import PostizPostStatusInput

        with self.assertRaises(NotImplementedError):
            get_post_status(PostizPostStatusInput(auth_ref=ref, post_id="p"))

    def test_inbound_skeletons_raise(self) -> None:
        from connectors.inbound import fetch_signal, list_signals
        from contracts.feedback import InboundFetchInput

        ref = AuthRef(ref="zendesk/default", provider="zendesk")
        with self.assertRaises(NotImplementedError):
            list_signals(InboundListInput(auth_ref=ref))
        with self.assertRaises(NotImplementedError):
            fetch_signal(InboundFetchInput(auth_ref=ref, signal_id="s1"))


if __name__ == "__main__":
    unittest.main()
