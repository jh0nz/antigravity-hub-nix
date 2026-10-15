#!/usr/bin/env python3
"""Pin official Antigravity CLI Linux manifests and their SHA-512 hashes."""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from pathlib import Path

from update import fetch_text


ROOT = Path(__file__).resolve().parent
SOURCES_FILE = ROOT / "cli-sources.json"
BASE_URL = "https://antigravity-cli-auto-updater-974169037036.us-central1.run.app"
PLATFORMS = {"x86_64-linux": "linux_amd64", "aarch64-linux": "linux_arm64"}


def latest_sources() -> dict:
    sources = {}
    versions = set()
    for system, platform in PLATFORMS.items():
        manifest = json.loads(fetch_text(f"{BASE_URL}/manifests/{platform}.json"))
        version, url, digest = (manifest[key] for key in ("version", "url", "sha512"))
        if not re.fullmatch(r"\d+(?:\.\d+)+", version):
            raise ValueError(f"Invalid CLI version for {system}: {version}")
        if not url.startswith("https://storage.googleapis.com/antigravity-public/antigravity-cli/") or not url.endswith(".tar.gz"):
            raise ValueError(f"Unexpected CLI download URL: {url}")
        if not re.fullmatch(r"[0-9a-fA-F]{128}", digest):
            raise ValueError(f"Invalid SHA-512 checksum for {system}")
        versions.add(version)
        sources[system] = {
            "url": url,
            "hash": "sha512-" + base64.b64encode(bytes.fromhex(digest)).decode("ascii"),
        }
    if len(versions) != 1:
        raise ValueError("CLI releases differ across architectures; retry after the rollout.")
    return {"version": versions.pop(), "sources": sources}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check without modifying the pin.")
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()
    try:
        current = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
        latest = latest_sources()
        has_update = current != latest
        print(f"Pinned CLI: {current['version']}; official latest: {latest['version']}")
        if args.github_output:
            with args.github_output.open("a", encoding="utf-8") as output:
                output.write(f"update={str(has_update).lower()}\n")
        if has_update and not args.check:
            SOURCES_FILE.write_text(json.dumps(latest, indent=2) + "\n", encoding="utf-8")
            print("Updated cli-sources.json.")
        else:
            print("Update available." if has_update else "Antigravity CLI is up to date.")
    except (OSError, RuntimeError, ValueError, KeyError, TypeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
