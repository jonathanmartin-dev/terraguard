"""Configuration and settings management for the dynamic approvals bot.

This module defines risk level constants and provides functionality to
derive runtime settings from command-line arguments and environment variables.
"""

import os
from dataclasses import dataclass
from typing import Optional, Tuple

# Single source of truth for risk levels
RISK_LEVEL_ORDER: Tuple[str, ...] = ("LOW", "MEDIUM", "HIGH")


@dataclass(frozen=True)
class Settings:
    """Runtime settings derived from CLI args and environment."""

    # Which risk level (inclusive) should cause a non-zero exit code.
    fail_on_risk_level: str

    # Whether the script should attempt to post a comment to GitHub.
    post_github_comment: bool


def get_settings(
    arg_fail_on: Optional[str],
    arg_no_github_comment: bool,
) -> Settings:
    """Derive runtime settings from CLI arguments and environment variables.

    Args:
        arg_fail_on: Risk level threshold from CLI argument, or None.
        arg_no_github_comment: Flag indicating GitHub comments should be disabled.

    Returns:
        A Settings object with fail_on_risk_level and post_github_comment values.

    Raises:
        ValueError: If an invalid risk level is provided (not in RISK_LEVEL_ORDER).

    Note:
        The fail_on_risk_level is determined in priority order:
        1. CLI argument (arg_fail_on)
        2. Environment variable (FAIL_ON_RISK_LEVEL)
        3. Default value ("HIGH")
    """
    # 1. Determine the source of the risk level
    env_fail_on = os.getenv("FAIL_ON_RISK_LEVEL")
    fail_on = arg_fail_on or env_fail_on

    # 2. Validate or set the default
    if fail_on is not None and fail_on not in RISK_LEVEL_ORDER:
        # ⚠️ Raise an error if an explicit, but invalid, value was provided
        raise ValueError(f"Invalid risk level '{fail_on}'. Must be one of {RISK_LEVEL_ORDER}.")

    # 3. Set the final value (defaulting only if no value was provided)
    final_fail_on = fail_on if fail_on is not None else "HIGH"

    post_github_comment = not arg_no_github_comment

    return Settings(
        fail_on_risk_level=final_fail_on,
        post_github_comment=post_github_comment,
    )
