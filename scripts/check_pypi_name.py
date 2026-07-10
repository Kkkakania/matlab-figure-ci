#!/usr/bin/env python3
"""Check whether a PyPI project name appears to be available."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


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


def exit_code_for_status(status: str) -> int:
    if status == "available":
        return 0
    if status == "taken":
        return 1
    return 2


def name_check_payload(name: str, status: str, detail: str) -> dict[str, str | int]:
    return {
        "name": name,
        "status": status,
        "detail": detail,
        "exitCode": exit_code_for_status(status),
    }


def write_json_payload(path: Path, payload: dict[str, str | int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="PyPI project name to check.")
    parser.add_argument("--json-out", help="Write a machine-readable check result to this file.")
    args = parser.parse_args()

    status, detail = check_name(args.name)
    payload = name_check_payload(args.name, status, detail)
    if args.json_out:
        path = Path(args.json_out)
        write_json_payload(path, payload)

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
