"""Risk configuration loading and resource type risk mapping.

This module provides functionality to load risk configuration from JSON files
and map Terraform resource types to risk levels using regex patterns.
"""

import json
import os
import re
import sys
from typing import Any, Dict, Tuple, cast

from terraguard.config import RISK_LEVEL_ORDER


def load_risk_config(path: str) -> Dict[str, Any]:
    """
    Loads risk configuration data from a JSON file, handling path and parsing errors.

    Args:
        path: The file system path to the risk_config.json file.

    Returns:
        The configuration data as a dictionary.

    Raises:
        SystemExit: If the file cannot be found or the JSON is invalid.
    """
    if not os.path.exists(path):
        print(f"ERROR: Risk configuration file not found at path: {path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(path, encoding="utf-8") as f:
            data = f.read()
        return cast(Dict[str, Any], json.loads(data))

    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse risk configuration JSON from {path}.", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while reading {path}: {e}", file=sys.stderr)
        sys.exit(1)


def max_level(current: str, new: str) -> str:
    """Return the higher risk level between two risk levels.

    Args:
        current: Current risk level string.
        new: New risk level string to compare.

    Returns:
        The risk level string with higher severity (new if it's higher,
        current otherwise).

    Note:
        Risk levels are compared using their order in RISK_LEVEL_ORDER.
    """
    if RISK_LEVEL_ORDER.index(new) > RISK_LEVEL_ORDER.index(current):
        return new
    return current


def map_risk_level(rtype: str, config: Dict[str, Any]) -> Tuple[str, str]:
    """Map a Terraform resource type to its risk level using regex patterns.

    Evaluates the resource type against all patterns in the configuration
    and returns the highest risk level that matches, along with the reason.

    Args:
        rtype: Terraform resource type string (e.g., "aws_s3_bucket").
        config: Risk configuration dictionary containing:
            - default_risk_level: Default level if no patterns match
            - resource_risk_patterns: List of pattern dictionaries with:
                - pattern: Regex pattern to match against rtype
                - risk_level: Risk level if pattern matches
                - reason: Explanation for the risk level

    Returns:
        A tuple of (risk_level, reason) where:
        - risk_level: The highest matching risk level string
        - reason: The reason string for the matched pattern, or default message
    """

    # Default to LOW if no match is found
    highest_level = config.get("default_risk_level", "LOW")
    highest_reason = "No specific pattern matched."

    # Iterate through patterns defined in the configuration
    for item in config.get("resource_risk_patterns", []):
        pattern = item.get("pattern")
        level = item.get("risk_level", "LOW")
        reason = item.get("reason", "Pattern matched.")

        if re.match(pattern, rtype):
            # Use the max_level helper function to find the most severe match
            if max_level(highest_level, level) == level:
                highest_level = level
                highest_reason = reason

    return highest_level, highest_reason
