#!/usr/bin/env python3
"""Resolve draw.io light-dark() exports into paired SVGs for Sphinx."""

from __future__ import annotations

import argparse
from pathlib import Path


def split_light_dark(svg_text: str, mode: str) -> str:
    """Replace CSS light-dark(light, dark) with the chosen theme color."""
    result: list[str] = []
    i = 0
    needle = "light-dark("
    pick = 0 if mode == "light" else 1
    while i < len(svg_text):
        j = svg_text.find(needle, i)
        if j == -1:
            result.append(svg_text[i:])
            break
        result.append(svg_text[i:j])
        k = j + len(needle)
        depth = 1
        while k < len(svg_text) and depth:
            if svg_text[k] == "(":
                depth += 1
            elif svg_text[k] == ")":
                depth -= 1
            k += 1
        inner = svg_text[j + len(needle) : k - 1]
        parts: list[str] = []
        buf = ""
        d = 0
        for ch in inner:
            if ch == "(":
                d += 1
            elif ch == ")":
                d -= 1
            elif ch == "," and d == 0:
                parts.append(buf.strip())
                buf = ""
                continue
            buf += ch
        parts.append(buf.strip())
        result.append(parts[pick] if len(parts) > pick else inner)
        i = k
    return "".join(result)


def build_drawio_figures(src_dir: Path, out_dir: Path) -> int:
    sources = sorted(src_dir.glob("*.drawio.svg"))
    if not sources:
        print(f"No draw.io sources in {src_dir}")
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    for src in sources:
        base = src.name.removesuffix(".drawio.svg")
        text = src.read_text(encoding="utf-8")
        light_path = out_dir / f"{base}.svg"
        dark_path = out_dir / f"{base}-dark.svg"
        light_path.write_text(split_light_dark(text, "light"), encoding="utf-8")
        dark_path.write_text(split_light_dark(text, "dark"), encoding="utf-8")
        print(f"Built draw.io: {src.name} -> {light_path.name}, {dark_path.name}")
    return len(sources)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--src-dir",
        type=Path,
        default=root / "docs" / "_figures_src" / "drawio",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=root / "docs" / "_static",
    )
    args = parser.parse_args()
    count = build_drawio_figures(args.src_dir, args.out_dir)
    if count:
        print(f"Figure build completed successfully ({count} source(s)).")


if __name__ == "__main__":
    main()
