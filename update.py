#!/usr/bin/env python3
"""Discover and pin the latest Antigravity Hub Linux downloads."""

from __future__ import annotations

import argparse
import gzip
import html
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urljoin


ROOT = Path(__file__).resolve().parent
SOURCES_FILE = ROOT / "sources.json"
DOWNLOAD_PAGE = "https://antigravity.google/download"
URL_PATTERN = re.compile(
    r"https?://[^\"'\s<>)]*/linux-x64/Antigravity\.tar\.gz"
)
VERSION_PATTERN = re.compile(
    r"/antigravity-hub/(?P<version>\d+(?:\.\d+)+)-(?P<build_id>\d+)/"
)
ARCH_URLS = {
    "x86_64-linux": "x64",
    "aarch64-linux": "arm",
}


def fetch_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "antigravity-hub-nix updater (personal Nix package)"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read()
            if body.startswith(b"\x1f\x8b"):
                body = gzip.decompress(body)
            return body.decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError) as error:
        raise RuntimeError(f"Could not fetch {url}: {error}") from error


def latest_download() -> tuple[str, str, str]:
    page = fetch_text(DOWNLOAD_PAGE)
    normalized_page = html.unescape(page).replace("\\/", "/")
    urls = URL_PATTERN.findall(normalized_page)
    if not urls:
        bundle_links = re.findall(
            r"(?:src|href)=[\"']([^\"']*main-[^\"']+\.js)[\"']", page, re.I
        )
        if not bundle_links:
            bundle_links = re.findall(r"(?:src|href)=[\"']([^\"']+\.js)[\"']", page, re.I)
        if not bundle_links:
            raise RuntimeError("Could not find the official download page JavaScript bundle.")
        bundle_url = urljoin(DOWNLOAD_PAGE, bundle_links[-1])
        normalized_bundle = html.unescape(fetch_text(bundle_url)).replace("\\/", "/")
        urls = URL_PATTERN.findall(normalized_bundle)
    if not urls:
        raise RuntimeError(
            "No Linux x64 Hub download URL found on Google's download page or bundle. "
            "The page format may have changed."
        )

    candidates = []
    for url in urls:
        version_match = VERSION_PATTERN.search(url)
        if version_match:
            version = version_match.group("version")
            candidates.append((tuple(int(part) for part in version.split(".")), version_match, url))
    if not candidates:
        raise RuntimeError("Could not read version/build ID from the official download URL.")

    _, version_match, url = max(candidates, key=lambda item: item[0])
    return version_match.group("version"), version_match.group("build_id"), url


def load_sources() -> dict:
    return json.loads(SOURCES_FILE.read_text(encoding="utf-8"))


def prefetch_hash(url: str) -> str:
    result = subprocess.run(
        ["nix", "store", "prefetch-file", "--json", url],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)["hash"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report whether an update exists without changing files or fetching hashes.",
    )
    parser.add_argument(
        "--github-output",
        help="Write update=true/false to a GitHub Actions output file.",
    )
    args = parser.parse_args()

    try:
        latest_version, latest_build_id, latest_x64_url = latest_download()
        current = load_sources()
    except (OSError, RuntimeError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    has_update = (current["version"], current["buildId"]) != (
        latest_version,
        latest_build_id,
    )
    print(f"Pinned version: {current['version']} (build {current['buildId']})")
    print(f"Official latest: {latest_version} (build {latest_build_id})")
    if not has_update:
        print("Antigravity Hub is up to date.")
    elif args.check:
        print("Update available; sources.json was left unchanged.")

    if args.github_output:
        with Path(args.github_output).open("a", encoding="utf-8") as output:
            output.write(f"update={str(has_update).lower()}\n")

    if not has_update or args.check:
        return 0

    current["version"] = latest_version
    current["buildId"] = latest_build_id
    current["hashes"] = dict(current["hashes"])

    for system, arch in ARCH_URLS.items():
        url = latest_x64_url.replace("linux-x64/", f"linux-{arch}/")
        print(f"Fetching fixed-output hash for {system}: {url}")
        current["hashes"][system] = prefetch_hash(url)

    SOURCES_FILE.write_text(
        json.dumps(current, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Updated sources.json to Antigravity Hub {latest_version}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
