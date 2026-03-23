from __future__ import annotations

from typing import Any

import requests
from mcp.server.fastmcp import FastMCP

server = FastMCP("github-demo")

PROMPT_INJECTION_MARKERS = (
    "ignore previous instructions",
    "system prompt",
    "developer message",
    "send secrets",
    "reveal credentials",
    "call tool",
)


def _find_prompt_injection_signals(text: str) -> list[str]:
    lowered = text.lower()
    return [marker for marker in PROMPT_INJECTION_MARKERS if marker in lowered]


@server.tool()
def list_issues(owner: str, repo: str, state: str = "open", limit: int = 10) -> list[dict[str, Any]]:
    """
    Connect to the GitHub API and return issue content that may carry indirect instructions.
    """
    response = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/issues",
        params={"state": state, "per_page": max(1, min(limit, 30))},
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "mcp-landscape-indirect-prompt-injection-poc",
        },
        timeout=15,
    )
    response.raise_for_status()

    issues: list[dict[str, Any]] = []
    for item in response.json():
        if "pull_request" in item:
            continue

        body = item.get("body") or ""
        issues.append(
            {
                "number": item.get("number"),
                "title": item.get("title"),
                "body": body,
                "author": (item.get("user") or {}).get("login"),
                "url": item.get("html_url"),
                "prompt_injection_signals": _find_prompt_injection_signals(body),
            }
        )

        if len(issues) >= limit:
            break

    return issues


if __name__ == "__main__":
    server.run()
