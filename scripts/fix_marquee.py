#!/usr/bin/env python3
"""
Replace <marquee> running text with static styled text in all diary entries.
Also removes leftover marquee from date/subtitle areas.
"""

import re
from pathlib import Path

ENTRIES_DIR = Path(__file__).parent.parent / "src" / "entries"


def fix_marquees(filepath):
    """Replace marquee tags with static span elements."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace <marquee ...>TEXT</marquee> with <span class="title-text">TEXT</span>
    new_content = re.sub(
        r'<marquee[^>]*>(.*?)</marquee>',
        r'<span class="title-text">\1</span>',
        content,
        flags=re.IGNORECASE | re.DOTALL
    )

    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False


def main():
    fixed = 0
    for f in sorted(ENTRIES_DIR.glob("*.html")):
        if fix_marquees(f):
            fixed += 1

    print(f"Replaced marquee tags in {fixed} files.")


if __name__ == "__main__":
    main()
