"""
Developer activity from GitHub: the only module that calls the GitHub API.

Reads one main client repository per featured chain. One repository is a
partial view (many chains develop across several, some partly in private),
and the report says so. Works without a token at GitHub's public rate
limit; set GITHUB_TOKEN to raise it. Never raises: a failure comes back as
a labelled error and shows as "No data".
"""
import datetime
import os
import time

import requests

API = "https://api.github.com"
TIMEOUT = 12


def _get(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "blockchain-research-platform"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.get(f"{API}{path}", headers=headers, timeout=TIMEOUT)


def fetch_github_activity(repo):
    """Stars, last push, and commits in the last four weeks for owner/name."""
    if not repo:
        return None
    try:
        info = _get(f"/repos/{repo}")
        info.raise_for_status()
        data = info.json()
        # GitHub computes participation statistics on demand and answers 202 until ready
        commits = None
        for _attempt in range(3):
            stats = _get(f"/repos/{repo}/stats/participation")
            if stats.status_code == 200:
                commits = sum((stats.json().get("all") or [])[-4:])
                break
            time.sleep(2)
        pushed = datetime.datetime.fromisoformat(data["pushed_at"].replace("Z", "+00:00"))
        return {
            "repo": repo,
            "url": data.get("html_url"),
            "stars": data.get("stargazers_count"),
            "commits_4_weeks": commits,
            "last_push": pushed.strftime("%d %B %Y"),
            "archived": data.get("archived"),
        }
    except Exception as e:
        return {"repo": repo, "error": f"{type(e).__name__}: {e}"[:200]}
