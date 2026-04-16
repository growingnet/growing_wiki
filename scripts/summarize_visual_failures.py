#!/usr/bin/env python3
"""Summarize repeated visual check failures for skill/workflow tuning."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize visual QA failures.")
    parser.add_argument(
        "--reports-dir",
        default="docs/_build/figure_eval",
        help="Directory containing JSON reports from eval_tikz_constraints.py",
    )
    parser.add_argument(
        "--min-repeat",
        type=int,
        default=2,
        help="Minimum repeated count to flag as recurring failure mode",
    )
    args = parser.parse_args()

    reports_dir = Path(args.reports_dir)
    if not reports_dir.exists():
        print(f"reports directory not found: {reports_dir}")
        return 1

    failure_counter: Counter[str] = Counter()
    report_count = 0
    for report_file in sorted(reports_dir.glob("*.json")):
        report_count += 1
        payload = json.loads(report_file.read_text(encoding="utf-8"))
        for err in payload.get("extraction_errors", []):
            failure_counter[f"extraction:{err}"] += 1
        for check in payload.get("checks", []):
            if not check.get("ok", False):
                failure_counter[f"check:{check.get('id', 'unknown')}"] += 1

    print(f"reports scanned: {report_count}")
    if not failure_counter:
        print("no failures found")
        return 0

    print("failure counts:")
    for key, count in failure_counter.most_common():
        print(f"- {key}: {count}")

    recurring = [(k, c) for k, c in failure_counter.items() if c >= args.min_repeat]
    if recurring:
        print("\nrecurring failure modes (candidate skill updates):")
        for key, count in sorted(recurring, key=lambda item: (-item[1], item[0])):
            print(f"- {key} ({count}x)")
    else:
        print("\nno recurring failures at selected threshold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

