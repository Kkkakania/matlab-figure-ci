#!/usr/bin/env python3
"""Check whether a PyPI project name appears to be available."""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request


def classify_status(status_code: int) -> str:
    if status_code == 404:
        return "available"
    if status_code == 200:
        return "taken"
    return "unknown"


def check_name(name: str, timeout: float = 10.0) -> tuple[str, str]:
    url = f"https://pypi.org/pypi/{name}/json"
    request = urllib.request.Request(url, headers={"User-Agent": "matlab-figure-ci-release-check"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = classify_status(response.status)
    except urllib.error.HTTPError as exc:
        status = classify_status(exc.code)
    except urllib.error.URLError as exc:
        return "unknown", f"{url} could not be checked: {exc.reason}"
    return status, url


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="PyPI project name to check.")
    args = parser.parse_args()

    status, detail = check_name(args.name)
    if status == "available":
        print(f"available: {detail} returned 404")
        return 0
    if status == "taken":
        print(f"taken: {detail} returned 200")
        return 1
    print(f"unknown: {detail}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
