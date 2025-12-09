"""Terraform plan change summarization.

This module analyzes Terraform plan data and produces statistics about
resource changes, categorizing them by risk level and action type.
"""

from typing import Any, Dict, List, Tuple

from terraguard.risk.risk import map_risk_level


def summarize_changes(plan: Dict[str, Any], risk_config: Dict[str, Any]) -> Dict[str, Any]:
    """Summarize changes in a Terraform plan and categorize by risk level.

    Analyzes resource changes in the plan, counts actions (create/update/delete),
    and maps each resource to its risk level using the provided configuration.

    Args:
        plan: Terraform plan dictionary containing a "resource_changes" list.
        risk_config: Risk configuration dictionary used to map resource types
            to risk levels.

    Returns:
        A dictionary containing statistics:
            - total_resources: Total number of resources with changes
            - creates: Number of create actions
            - updates: Number of update actions
            - deletes: Number of delete actions
            - high_risk_changes: Number of HIGH risk resources changing
            - critical_changes: Number of CRITICAL risk resources changing
            - high_risk_deletes: Number of HIGH risk resources being deleted
            - critical_deletes: Number of CRITICAL risk resources being deleted
            - sensitive_details: List of tuples (rtype, address, risk_level, actions)
                for HIGH and CRITICAL risk resources
    """
    resource_changes = plan.get("resource_changes", [])
    stats: Dict[str, Any] = {
        "total_resources": len(resource_changes),
        "creates": 0,
        "updates": 0,
        "deletes": 0,
        "high_risk_changes": 0,  # New stat
        "critical_changes": 0,  # New stat
        "high_risk_deletes": 0,  # New stat
        "critical_deletes": 0,  # New stat
        "sensitive_details": [],
    }
    # sensitive_details will now track HIGH/CRITICAL resources
    high_critical_details: List[Tuple[str, str, str, List[str]]] = []

    for rc in resource_changes:
        rtype = rc.get("type", "")
        address = rc.get("address", f"{rtype}.{rc.get('name', 'unknown')}")
        change = rc.get("change", {})
        actions: List[str] = change.get("actions", [])

        # 1. Count basic stats
        if "create" in actions:
            stats["creates"] = stats.get("creates", 0) + 1
        if "update" in actions:
            stats["updates"] = stats.get("updates", 0) + 1
        if "delete" in actions:
            stats["deletes"] = stats.get("deletes", 0) + 1

        # 2. Map resource risk using the new configuration
        risk_level, _ = map_risk_level(
            rtype, risk_config
        )  # Assuming map_risk_level returns (level, reason)

        # 3. Count changes based on mapped risk level
        if risk_level == "HIGH" and any(a in actions for a in ("create", "update", "delete")):
            stats["high_risk_changes"] = stats.get("high_risk_changes", 0) + 1
            if "delete" in actions:
                stats["high_risk_deletes"] = stats.get("high_risk_deletes", 0) + 1
            high_critical_details.append((rtype, address, risk_level, actions))

        elif risk_level == "CRITICAL" and any(a in actions for a in ("create", "update", "delete")):
            stats["critical_changes"] = stats.get("critical_changes", 0) + 1
            if "delete" in actions:
                stats["critical_deletes"] = stats.get("critical_deletes", 0) + 1
            high_critical_details.append((rtype, address, risk_level, actions))

    stats["sensitive_details"] = high_critical_details
    return stats
