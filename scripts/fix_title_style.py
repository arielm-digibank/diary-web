#!/usr/bin/env python3
"""
Add styling for .title-text class (replaces marquee).
Injects CSS into existing style blocks.
"""

import re
from pathlib import Path

ENTRIES_DIR = Path(__file__).parent.parent / "src" / "entries"

TITLE_CSS = """
    .title-text {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      font-weight: 700;
      display: inline-block;
    }
"""


def add_title_style(filepath):
    """Add .title-text CSS to pages that have it."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if "title-text" not in content:
        return False

    if ".title-text" in content.split("<style>")[1].split("</style>")[0] if "<style>" in content else "":
        return False

    # Inject before </style>
    new_content = content.replace("</style>", TITLE_CSS + "  </style>", 1)

    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False


def main():
    fixed = 0
    for f in sorted(ENTRIES_DIR.glob("*.html")):
        if add_title_style(f):
            fixed += 1

    print(f"Added .title-text styling to {fixed} pages.")


if __name__ == "__main__":
    main()
