#!/usr/bin/env python3
"""Evaluate figure-specific layout constraints from a TikZ source file.

This script is intentionally generic: each figure provides a JSON spec with
regex-extracted scalar variables and boolean checks built from those variables.
It is used as an objective gate for visual refinement loops.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def _safe_eval(expr: str, variables: dict[str, float]) -> Any:
    """Evaluate expressions with no builtins and only captured variables."""
    return eval(expr, {"__builtins__": {}}, variables)  # noqa: S307


def _extract_variables(source: str, spec: dict[str, Any]) -> tuple[dict[str, float], list[str]]:
    vars_out: dict[str, float] = {}
    errors: list[str] = []
    for name, cfg in spec.get("variables", {}).items():
        pattern = cfg["pattern"]
        cast = cfg.get("cast", "float")
        flags = 0
        for key in cfg.get("flags", []):
            if key == "MULTILINE":
                flags |= re.MULTILINE
            elif key == "DOTALL":
                flags |= re.DOTALL
            else:
                errors.append(f"unknown regex flag {key!r} for variable {name!r}")
        match = re.search(pattern, source, flags)
        if not match:
            errors.append(f"could not capture variable {name!r} with pattern {pattern!r}")
            continue
        raw = match.group(1)
        try:
            if cast == "float":
                vars_out[name] = float(raw)
            elif cast == "int":
                vars_out[name] = int(raw)
            else:
                errors.append(f"unknown cast {cast!r} for variable {name!r}")
        except ValueError as exc:
            errors.append(f"failed parsing variable {name!r} from value {raw!r}: {exc}")
    return vars_out, errors


def _run_checks(variables: dict[str, float], spec: dict[str, Any]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for check in spec.get("checks", []):
        cid = check["id"]
        expr = check["expr"]
        minimum = check.get("min")
        maximum = check.get("max")
        should_be_true = check.get("assert_true", False)
        rec: dict[str, Any] = {"id": cid, "expr": expr}
        try:
            value = _safe_eval(expr, variables)
            rec["value"] = value
            ok = True
            if minimum is not None:
                ok = ok and (value >= minimum)
                rec["min"] = minimum
            if maximum is not None:
                ok = ok and (value <= maximum)
                rec["max"] = maximum
            if should_be_true:
                ok = ok and bool(value) is True
                rec["assert_true"] = True
            rec["ok"] = bool(ok)
        except Exception as exc:  # noqa: BLE001
            rec["ok"] = False
            rec["error"] = str(exc)
        results.append(rec)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate TikZ layout constraints.")
    parser.add_argument("--source", required=True, help="Path to .tex figure source")
    parser.add_argument("--spec", required=True, help="Path to JSON constraints spec")
    parser.add_argument(
        "--output",
        default="",
        help="Optional JSON output path; defaults to docs/_build/figure_eval/<name>.json",
    )
    args = parser.parse_args()

    source_path = Path(args.source)
    spec_path = Path(args.spec)
    if not source_path.exists():
        print(f"missing source file: {source_path}", file=sys.stderr)
        return 2
    if not spec_path.exists():
        print(f"missing spec file: {spec_path}", file=sys.stderr)
        return 2

    source = source_path.read_text(encoding="utf-8")
    spec = json.loads(spec_path.read_text(encoding="utf-8"))

    variables, extraction_errors = _extract_variables(source, spec)
    checks = _run_checks(variables, spec)
    failed = [c for c in checks if not c.get("ok")]
    ok = not extraction_errors and not failed

    report = {
        "figure": spec.get("figure", source_path.stem),
        "source": str(source_path),
        "spec": str(spec_path),
        "ok": ok,
        "variables": variables,
        "extraction_errors": extraction_errors,
        "checks": checks,
        "summary": {
            "total_checks": len(checks),
            "failed_checks": len(failed),
            "extraction_errors": len(extraction_errors),
        },
    }

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = source_path.parents[2] / "_build" / "figure_eval" / f"{source_path.stem}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"layout report: {output_path}")
    if extraction_errors:
        print("extraction errors:")
        for err in extraction_errors:
            print(f"  - {err}")
    for chk in checks:
        status = "PASS" if chk.get("ok") else "FAIL"
        value = chk.get("value")
        print(f"[{status}] {chk['id']}: {value!r}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

