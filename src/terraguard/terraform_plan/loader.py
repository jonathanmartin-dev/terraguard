"""Terraform plan JSON file loading.

This module provides functionality to load and parse Terraform plan JSON files
generated from `terraform show -json`.
"""

import json
from typing import Any, Dict, cast


def load_plan_json(path: str) -> Dict[str, Any]:
    """Load and parse a Terraform plan JSON file.

    Args:
        path: File system path to the Terraform plan JSON file.

    Returns:
        A dictionary containing the parsed Terraform plan data.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
        OSError: If the file cannot be read.
    """
    with open(path, encoding="utf-8") as f:
        return cast(Dict[str, Any], json.load(f))
