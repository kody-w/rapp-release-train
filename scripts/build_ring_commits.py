#!/usr/bin/env python3
"""build_ring_commits.py — Article XXIV (Static Data Covenant, kody-w/RAR CONSTITUTION.md).

Harvests the latest main-branch commit (sha, committer date, subject) for each
release ring from the GitHub API, once, here in CI. Writes state/ring_commits.json
keyed by repo, in the same shape as a single GitHub `GET /repos/{repo}/commits/main`
response (`sha`, `commit.committer.date`, `commit.message`) so index.html's parsing
is unchanged — only the URL and the "keyed by repo" wrapper are new.

Replaces: index.html's per-visitor `fetch("https://api.github.com/repos/${r.repo}/commits/main")`
(one unauthenticated call per ring per visitor). Uses GITHUB_TOKEN when present
(CI) for a higher rate limit; falls back to unauthenticated (works fine for 5 calls).
"""

import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "state" / "ring_commits.json"

RINGS = [
    "kody-w/rapp-canary",
    "kody-w/rapp-nightly",
    "kody-w/rapp-alpha",
    "kody-w/rapp-beta",
    "kody-w/rapp-installer",
]


def fetch_json(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "rapp-release-train-build",
        "Accept": "application/vnd.github+json",
    })
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  ! {url}: {e}", file=sys.stderr)
        return None


def main():
    import datetime
    repos = {}
    for repo in RINGS:
        j = fetch_json(f"https://api.github.com/repos/{repo}/commits/main")
        if not j or "sha" not in j:
            print(f"  ✗ {repo}: no commit data (keeping any prior snapshot entry)")
            continue
        repos[repo] = {
            "sha": j["sha"],
            "commit": {
                "committer": {"date": j.get("commit", {}).get("committer", {}).get("date")},
                "message": j.get("commit", {}).get("message"),
            },
        }
        print(f"  ✓ {repo}: {j['sha'][:12]}")

    # Preserve any existing entries for repos that failed this run, so a
    # transient API hiccup in CI doesn't blank out a ring's card.
    prior = {}
    if OUT.exists():
        try:
            prior = json.loads(OUT.read_text()).get("repos", {})
        except Exception:
            pass
    merged = {**prior, **repos}

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "schema": "rapp-release-train-ring-commits/1",
        "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repos": merged,
    }, indent=2, sort_keys=True) + "\n")
    print(f"✓ {OUT.relative_to(ROOT)} — {len(merged)} rings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
