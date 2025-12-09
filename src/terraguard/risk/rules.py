"""Risk assessment rules and scoring logic.

This module implements the core risk assessment algorithm that evaluates
Terraform plan statistics and determines an overall risk level and score.
"""

from typing import Any, Dict, List

from terraguard.config import RISK_LEVEL_ORDER


def assess_risk(stats: Dict[str, Any]) -> Dict[str, Any]:
    """Assess overall risk level based on Terraform plan statistics.

    Evaluates various risk signals including critical/high risk changes,
    deletions, and blast radius (total change count) to determine an
    overall risk level.

    Args:
        stats: Dictionary containing plan statistics:
            - total_resources: Total number of resources with changes
            - creates: Number of resources being created
            - updates: Number of resources being updated
            - deletes: Number of resources being deleted
            - high_risk_changes: Number of HIGH risk resources changing
            - critical_changes: Number of CRITICAL risk resources changing
            - high_risk_deletes: Number of HIGH risk resources being deleted
            - critical_deletes: Number of CRITICAL risk resources being deleted

    Returns:
        A dictionary containing:
            - level: Risk level string (LOW, MEDIUM, HIGH)
            - score: Numeric risk score (10, 50, or 90)
            - reasons: List of reason strings explaining the assessment
            - stats: The original stats dictionary
    """
    level = "LOW"
    reasons: List[str] = []
    deletes = stats["deletes"]
    total = stats["total_resources"]

    # 💥 USE NEW STATS 💥
    high_changes = stats["high_risk_changes"]
    crit_changes = stats["critical_changes"]
    high_deletes = stats["high_risk_deletes"]
    crit_deletes = stats["critical_deletes"]

    # 1. Base Signals (for informational purposes)
    if total > 0:
        reasons.append(f"{total} resource(s) will be changed (create/update/delete).")
    if deletes > 0:
        reasons.append(f"{deletes} resource(s) will be deleted.")

    # 2. Risk Rules (Tuned to prioritize CRITICAL changes)

    # A. No changes at all
    if total == 0:
        level = "LOW"
        reasons = ["No resource changes detected in plan."]
        return {
            "level": level,
            "score": score_from_level(level),
            "reasons": reasons,
            "stats": stats,
        }

    # B. CRITICAL Resource Rules (Highest Priority)
    if crit_deletes > 0:
        level = max_level(level, "HIGH")
        reasons.append(f"{crit_deletes} CRITICAL resource(s) will be **deleted**.")
    if crit_changes > 0:
        level = max_level(level, "MEDIUM")
        reasons.append(f"{crit_changes} CRITICAL resource(s) will be changed.")

    # C. HIGH Resource Rules
    if high_deletes > 0:
        level = max_level(level, "MEDIUM")
        reasons.append(f"{high_deletes} HIGH risk resource(s) will be deleted.")
    if high_changes > 0:
        level = max_level(level, "LOW")  # Bump to MEDIUM if LOW, but keep it if already MEDIUM/HIGH
        reasons.append(f"{high_changes} HIGH risk resource(s) will be changed.")

    # D. Blast Radius Rules (Optional, remains similar)
    if total > 20 or deletes > 5:
        level = max_level(level, "HIGH")
        reasons.append("High count of changes or deletions (Blast Radius).")
    elif total > 5:
        level = max_level(level, "MEDIUM")

    score = score_from_level(level)

    return {
        "level": level,
        "score": score,
        "reasons": reasons,
        "stats": stats,
    }


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


def score_from_level(level: str) -> int:
    """Convert a risk level string to a numeric score.

    Args:
        level: Risk level string (LOW, MEDIUM, or HIGH).

    Returns:
        Numeric score: 10 for LOW, 50 for MEDIUM, 90 for HIGH, 0 for unknown.
    """
    if level == "LOW":
        return 10
    if level == "MEDIUM":
        return 50
    if level == "HIGH":
        return 90
    return 0
