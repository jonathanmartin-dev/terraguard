"""Markdown formatting for risk assessment results.

This module provides functionality to format risk assessment results
into markdown for display in logs or GitHub comments.
"""

from typing import Any, Dict


def format_summary_markdown(result: Dict[str, Any]) -> str:
    """Format a risk assessment result dictionary into markdown.

    Args:
        result: A dictionary containing:
            - level: Risk level string (LOW, MEDIUM, HIGH)
            - score: Numeric risk score
            - stats: Dictionary with change statistics
            - reasons: List of reason strings explaining the risk assessment

    Returns:
        A formatted markdown string suitable for display in logs or GitHub comments.
        Includes risk level, score, change summary, reasons, and a collapsible
        section for sensitive resource changes.
    """
    level = result["level"]
    stats = result["stats"]
    reasons = result["reasons"]

    lines = []
    lines.append("### Terraform Plan Risk Assessment")
    lines.append("")
    lines.append(f"**Risk Level:** `{level}` (score: {result['score']})")
    lines.append("")
    lines.append("**Change Summary:**")
    lines.append(f"- Total resources with changes: `{stats['total_resources']}`")
    lines.append(f"- Creates: `{stats['creates']}`")
    lines.append(f"- Updates: `{stats['updates']}`")
    lines.append(f"- Deletes: `{stats['deletes']}`")
    lines.append(f"- High risk changes: `{stats['high_risk_changes']}`")
    lines.append(f"- Critical changes: `{stats['critical_changes']}`")
    lines.append(f"- High risk deletes: `{stats['high_risk_deletes']}`")
    lines.append(f"- Critical deletes: `{stats['critical_deletes']}`")
    lines.append("")
    if reasons:
        lines.append("**Reasons / Signals:**")
        for r in reasons:
            lines.append(f"- {r}")
        lines.append("")
    sens_details = stats.get("sensitive_details", [])
    if sens_details:
        lines.append("<details>")
        lines.append("<summary>Sensitive resource changes</summary>")
        lines.append("")
        for rtype, address, risk_level, actions in sens_details:
            act_str = ",".join(actions)
            lines.append(f"- `{rtype}` `{address}` ({risk_level}) actions: `{act_str}`")
        lines.append("")
        lines.append("</details>")

    return "\n".join(lines)
