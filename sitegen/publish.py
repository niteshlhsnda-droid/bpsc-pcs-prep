#!/usr/bin/env python3
"""
sitegen/publish.py -- publish the BPSC PCS Prep repo to GitHub via the API.

Creates ONE atomic commit with all new/changed files using the Git Data API
(blobs -> tree -> commit -> update ref), using the stored custom.github
credential. The local workspace is not a git clone, so everything goes
through the API.

Usage:
    python3 sitegen/build.py && python3 sitegen/publish.py

Publishes: generated HTML (.nojekyll + all pages), updated Markdown sources
(booklist.md, README.md), and the sitegen/ tooling itself.
"""

from __future__ import annotations

import base64
import json
import os
import sys
import urllib.request

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import (  # noqa: E402
    add_surrogate_to_request,
    ensure_allowed_url,
    read_response_body,
)

CREDENTIAL = "custom.github"
API = "https://api.github.com"
OWNER = "niteshlhsnda-droid"
REPO_NAME = "bpsc-pcs-prep"
BRANCH = "main"

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Generated site files (relative to repo root) + sources + tooling.
GENERATED = [
    ".nojekyll",
    "index.html",
    "books/index.html",
    "syllabus/index.html",
    "syllabus/prelims/index.html",
    "syllabus/mains/index.html",
    "notes/index.html",
    "notes/bihar-history/index.html",
    "notes/bihar-geography/index.html",
    "notes/bihar-polity/index.html",
    "notes/bihar-economy/index.html",
    "notes/modern-history/index.html",
    "notes/polity/index.html",
    "notes/geography/index.html",
    "notes/economy/index.html",
    "notes/environment/index.html",
    "notes/science-tech/index.html",
    "bihar-gk-rapid-fire/index.html",
    "pyq/index.html",
    "pyq/strategy/index.html",
    "pyq-analysis/index.html",
    "strategy/index.html",
    "strategy/one-attempt-plan/index.html",
    "strategy/memorization/index.html",
]
SOURCES = ["booklist.md", "README.md"]
TOOLING = [
    "sitegen/build.py",
    "sitegen/publish.py",
    "sitegen/README.md",
    "sitegen/templates/base.html",
]


def api(method: str, path: str, data: dict | None = None):
    url = API + path
    ensure_allowed_url(url, ["api.github.com"])
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, method=method.upper())
    req.add_header("User-Agent", "muse-github-skill")
    req.add_header("Accept", "application/vnd.github+json")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    add_surrogate_to_request(req, CREDENTIAL, allowed_hosts=["api.github.com"])
    try:
        with urllib.request.urlopen(req, data=body, timeout=60) as resp:
            return json.loads(read_response_body(resp).decode("utf-8") or "null")
    except urllib.error.HTTPError as exc:  # noqa: F821
        raw = read_response_body(exc).decode("utf-8", "replace")
        raise RuntimeError(f"GitHub API {method} {path} -> HTTP {exc.code}: {raw[:500]}")


def main() -> int:
    files = GENERATED + SOURCES + TOOLING
    missing = [f for f in files if not os.path.exists(os.path.join(REPO, f))]
    if missing:
        print("Missing files (run sitegen/build.py first):", missing)
        return 1

    base = f"/repos/{OWNER}/{REPO_NAME}"
    ref = api("get", f"{base}/git/ref/heads/{BRANCH}")
    head_sha = ref["object"]["sha"]
    head_commit = api("get", f"{base}/git/commits/{head_sha}")
    base_tree = head_commit["tree"]["sha"]
    print(f"HEAD {head_sha[:7]} tree {base_tree[:7]}")

    tree_entries = []
    for rel in files:
        with open(os.path.join(REPO, rel), "rb") as fh:
            content = base64.b64encode(fh.read()).decode("ascii")
        blob = api("post", f"{base}/git/blobs",
                   {"content": content, "encoding": "base64"})
        tree_entries.append({"path": rel, "mode": "100644",
                             "type": "blob", "sha": blob["sha"]})
        print(f"  blob {rel}")
    # Deterministic tree order
    tree_entries.sort(key=lambda e: e["path"])

    tree = api("post", f"{base}/git/trees",
               {"base_tree": base_tree, "tree": tree_entries})
    print(f"tree {tree['sha'][:7]}")

    commit = api("post", f"{base}/git/commits", {
        "message": ("Books & question banks added; site rebuilt with Python "
                    "sitegen generator (build.py + templates, .nojekyll)"),
        "tree": tree["sha"],
        "parents": [head_sha],
    })
    print(f"commit {commit['sha']}")

    api("patch", f"{base}/git/refs/heads/{BRANCH}", {"sha": commit["sha"]})
    print(f"Updated {BRANCH} -> {commit['sha'][:7]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
