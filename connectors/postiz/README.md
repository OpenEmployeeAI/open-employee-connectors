# Postiz outbound connector

Postiz is treated as an external [Gitroom](https://github.com/gitroomhq)-style
publishing service. This repo does **not** vendor, fork, or re-implement
Postiz; we call it as a remote MCP server.

## Activity registry

| Activity name                  | Input                     | Result                      |
| ------------------------------ | ------------------------- | --------------------------- |
| `mcp__postiz__create_post`     | `PostizCreatePostInput`   | `PostizCreatePostResult`    |
| `mcp__postiz__get_post_status` | `PostizPostStatusInput`   | `PostizPostStatusResult`    |

## Security boundaries

- Credentials are passed as `AuthRef(provider="postiz", ref=...)`. Raw API
  keys must not appear in inputs, results, logs, or workflow history.
- `create_post` is a risky public write. `PostizCreatePostInput` requires
  an `ApprovalToken`; constructing the input without one raises
  `ValueError`, so the Activity cannot be scheduled without prior human
  approval.
- Status reads are not risky writes and do not require an `ApprovalToken`.

## What this slice intentionally omits

- No HTTP client, retry policy, or rate limit handling.
- No Postiz-specific channel validation. The contract accepts opaque
  channel identifiers; resolution lives behind the Postiz API.
- No persistence; ApprovalToken verification is delegated to the policy
  layer.
