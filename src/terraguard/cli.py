"""Command-line interface for the dynamic approvals bot.

This module provides the main entry point for assessing Terraform plan risk
and optionally gating CI/CD approvals based on the assessed risk level.
"""

import argparse
import os
import sys

from terraguard.config import RISK_LEVEL_ORDER, get_settings
from terraguard.outputs import format_summary_markdown, maybe_post_github_comment
from terraguard.risk import assess_risk, load_risk_config
from terraguard.terraform_plan import load_plan_json, summarize_changes


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        An argparse.Namespace object containing the parsed arguments:
        - plan_json: Path to Terraform plan JSON file
        - risk_config_path: Optional path to risk configuration JSON file
        - fail_on: Optional risk level threshold for failing the build
        - no_github_comment: Flag to disable GitHub comment posting
    """
    parser = argparse.ArgumentParser(
        description="Assess risk level of a Terraform plan JSON and optionally gate approvals."
    )
    parser.add_argument(
        "plan_json",
        help="Path to Terraform plan JSON (from `terraform show -json plan.out > plan.json`).",
    )
    parser.add_argument(
        "--risk-config-path",
        default=os.getenv("RISK_CONFIG_PATH"),
        help="Path to the risk configuration JSON file. Overrides RISK_CONFIG_PATH env var.",
    )
    parser.add_argument(
        "--fail-on",
        choices=RISK_LEVEL_ORDER,
        default=None,
        help=(
            "Fail (exit code 1) if risk level is at or above this. "
            "Default: env FAIL_ON_RISK_LEVEL or HIGH."
        ),
    )
    parser.add_argument(
        "--no-github-comment",
        action="store_true",
        help="Do not attempt to post a comment to GitHub, even if running in Actions.",
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point for the dynamic approvals bot.

    Loads and analyzes a Terraform plan, assesses risk, formats output,
    optionally posts to GitHub, and exits with appropriate code based on
    the risk level threshold.

    Exits with code 1 if risk level meets or exceeds the fail-on threshold,
    otherwise exits with code 0.
    """
    args = parse_args()
    DEFAULT_RISK_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "risk", "risk_config.json")
    risk_config_path = args.risk_config_path or DEFAULT_RISK_CONFIG_PATH
    settings = get_settings(
        arg_fail_on=args.fail_on,
        arg_no_github_comment=args.no_github_comment,
    )

    try:
        plan = load_plan_json(args.plan_json)
    except Exception as e:
        print(f"ERROR: Failed to load plan JSON from {args.plan_json}: {e}", file=sys.stderr)
        sys.exit(1)

    risk_config = load_risk_config(risk_config_path)

    stats = summarize_changes(plan, risk_config)
    result = assess_risk(stats)
    summary_md = format_summary_markdown(result)

    # Always print markdown summary to stdout so logs show it.
    print(summary_md)

    # Optionally post to GitHub
    maybe_post_github_comment(summary_md)

    # Decide exit code based on risk vs threshold
    current_level = result["level"]
    fail_on = settings.fail_on_risk_level

    if RISK_LEVEL_ORDER.index(current_level) >= RISK_LEVEL_ORDER.index(fail_on):
        print(
            f"\nRisk level `{current_level}` is >= fail-on threshold `{fail_on}`. "
            f"Failing for manual review.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(
        f"\nRisk level `{current_level}` is below fail-on threshold `{fail_on}`. " f"Continuing.",
        file=sys.stderr,
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
