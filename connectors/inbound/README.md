# Inbound feedback collectors

Inbound collectors normalize provider-specific feedback (reactions,
replies, ratings, ticket comments) into typed ``FeedbackSignal`` values.

## Activity registry

| Activity name                 | Input               | Result               |
| ----------------------------- | ------------------- | -------------------- |
| `mcp__feedback__list_signals` | `InboundListInput`  | `InboundListResult`  |
| `mcp__feedback__fetch_signal` | `InboundFetchInput` | `InboundFetchResult` |

## Security boundaries

- Credentials use `AuthRef`; raw provider tokens never enter inputs.
- Inbound reads are not risky public writes and do not require
  `ApprovalToken`.
- Bodies longer than the 280-char preview budget must be returned via
  `ArtifactRef` so workflow history stays small.
