"""GitHub Actions integration for posting risk assessment comments.

This module handles posting risk assessment summaries as comments on
GitHub Pull Requests when running in GitHub Actions environments.
"""

import json
import os
import sys

import requests


def maybe_post_github_comment(summary_markdown: str) -> None:
    """
    If running in GitHub Actions on a PR event, post a comment to the PR.
    Uses GITHUB_TOKEN and GITHUB_EVENT_PATH.
    """
    gh_token = os.getenv("GITHUB_TOKEN")
    event_path = os.getenv("GITHUB_EVENT_PATH")

    if not gh_token or not event_path:
        # Not running in GitHub Actions, or no token.
        return

    try:
        with open(event_path, encoding="utf-8") as f:
            event = json.load(f)
    except Exception:
        return

    # Support pull_request and pull_request_target events
    pr = event.get("pull_request")
    if not pr:
        # Not a PR event; nothing to comment on
        return

    repo = event.get("repository", {})
    full_name = repo.get("full_name")  # e.g. "owner/repo"
    if not full_name:
        return

    pr_number = pr.get("number")
    if not pr_number:
        return

    url = f"https://api.github.com/repos/{full_name}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {gh_token}",
        "Accept": "application/vnd.github+json",
    }
    payload = {"body": summary_markdown}

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if resp.status_code >= 300:
            print(
                f"WARNING: Failed to post GitHub comment "
                f"(status={resp.status_code}): {resp.text}",
                file=sys.stderr,
            )
    except Exception as e:
        print(f"WARNING: Exception posting GitHub comment: {e}", file=sys.stderr)
