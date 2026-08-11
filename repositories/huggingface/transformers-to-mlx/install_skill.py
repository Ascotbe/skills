#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
"""Install the transformers-to-mlx skill into the current project.

Downloads the skill into `.agents/skills/transformers-to-mlx/` (Agent Skills
open-standard location), symlinks `.claude/skills/transformers-to-mlx/` to it.

Usage:
    uv run https://raw.githubusercontent.com/huggingface/transformers-to-mlx/main/install_skill.py
"""

import json
import os
import shutil
import sys
import urllib.request
from pathlib import Path

OWNER = "huggingface"
REPO = "transformers-to-mlx"
BRANCH = "main"
SKILL_NAME = "transformers-to-mlx"
SKILL_PATH = f"skills/{SKILL_NAME}"

RAW_BASE = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}"
TREE_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/git/trees/{BRANCH}?recursive=1"

CANONICAL = Path(".agents/skills")
SYMLINK_FROM = Path(".claude/skills")

def fetch(url):
    with urllib.request.urlopen(url) as r:
        return r.read()

def remove(path: Path):
    if path.is_symlink() or path.exists():
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        else:
            path.unlink()

def main():
    skill_dir = (CANONICAL / SKILL_NAME).resolve()
    link_dir = (SYMLINK_FROM / SKILL_NAME).resolve()

    skill_dir.parent.mkdir(parents=True, exist_ok=True)
    link_dir.parent.mkdir(parents=True, exist_ok=True)

    remove(skill_dir)
    remove(link_dir)

    print(f"Fetching file list from {OWNER}/{REPO}@{BRANCH}...", end=" ", flush=True)
    tree = json.loads(fetch(TREE_URL))
    prefix = SKILL_PATH + "/"
    files = [item["path"] for item in tree["tree"]
             if item["type"] == "blob" and item["path"].startswith(prefix)]
    print(f"{len(files)} files")

    if not files:
        sys.exit(f"Error: no files found under {SKILL_PATH}")

    for path in files:
        relative = path[len(prefix):]
        dest = skill_dir / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        print(f"  {relative}", flush=True)
        dest.write_bytes(fetch(f"{RAW_BASE}/{path}"))

    link_dir.symlink_to(os.path.relpath(skill_dir, link_dir.parent))
    print(f"\nInstalled to {skill_dir}")
    print(f"Symlinked   {link_dir} -> {os.readlink(link_dir)}")
    print("\nRestart your AI assistant to activate the skill.")

if __name__ == "__main__":
    main()
