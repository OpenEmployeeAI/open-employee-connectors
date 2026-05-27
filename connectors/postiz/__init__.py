"""Postiz outbound connector skeleton.

Postiz is consumed as an external Gitroom-style publishing service. This
module declares the Activity name registry and a no-network skeleton; it
does not call the Postiz API. Production wiring is intentionally out of
scope for this slice.
"""

from connectors.postiz.activities import (
    ACTIVITY_CREATE_POST,
    ACTIVITY_GET_POST_STATUS,
    create_post,
    get_post_status,
)

__all__ = [
    "ACTIVITY_CREATE_POST",
    "ACTIVITY_GET_POST_STATUS",
    "create_post",
    "get_post_status",
]
