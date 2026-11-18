"""Shared, default-deny policy for billable provider access."""
import os


def require_paid_opt_in(allowed=False):
    if os.environ.get("VIDEO_WORKBENCH_ZERO_SPEND", "1") != "0" or not allowed:
        raise ValueError("Zero-spend policy blocks remote APIs. For an explicitly paid workflow, "
                         "set VIDEO_WORKBENCH_ZERO_SPEND=0 and pass --allow-remote.")
