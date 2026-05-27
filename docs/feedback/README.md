# Feedback Provider Boundaries

OpenEmployee separates feedback flow into two directional boundaries, each
crossing a dedicated Temporal Activity. This document defines the first
reviewable slice; production wiring is intentionally out of scope.

## Directions

- **Outbound publishing**: agent-produced content is published to external
  reach surfaces (e.g. social channels). Postiz is the reference outbound
  service. Posting is treated as a risky public write.
- **Inbound collection**: provider collectors pull or receive feedback
  signals (reactions, replies, ratings, ticket comments) from external
  systems and normalize them into typed Activity results.

## Invariants

1. Every selected MCP tool executes as a dedicated Temporal Activity named
   `mcp__<server>__<tool>`.
2. Provider credentials are referenced through `auth_ref` only. Raw API
   keys, bearer tokens, or cookies must never appear in Activity inputs,
   workflow history, or repo files.
3. Risky public writes (anything that produces a visible artifact on a
   third-party platform) require human approval before the Activity is
   scheduled. Approval is recorded as a typed `ApprovalToken`.
4. Postiz is consumed as a Gitroom-style external publishing service. It
   is not vendored, forked, or re-implemented inside this repo.
5. Large provider payloads (raw HTML, long threads) must be returned via
   claim-check artifact references, not inlined into Activity results.

## Activity name registry (this slice)

| Direction | Activity name                      | Purpose                                |
| --------- | ---------------------------------- | -------------------------------------- |
| outbound  | `mcp__postiz__create_post`         | Schedule or send a post via Postiz.    |
| outbound  | `mcp__postiz__get_post_status`     | Read status of a previously created post. |
| inbound   | `mcp__feedback__list_signals`      | List normalized feedback signals.      |
| inbound   | `mcp__feedback__fetch_signal`      | Fetch one normalized feedback signal.  |

All four names match the canonical `mcp__<server>__<tool>` pattern from
the repo `README.md` and `SECURITY.md`.

## Out of scope for this slice

- Network I/O, retries, and rate-limit handling.
- Concrete provider adapters (Twitter/X, LinkedIn, Zendesk, etc.).
- Policy engine implementation; the contract only declares the approval
  requirement.
- Persistence of `ApprovalToken` and `auth_ref` resolution backends.
