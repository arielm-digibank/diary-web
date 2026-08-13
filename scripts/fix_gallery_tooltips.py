#!/usr/bin/env python3
"""
Remove 'title="לחץ להגדלה"' tooltips from gallery page images.
The lightbox works by clicking - no need for tooltip instruction text.
"""

import re
from pathlib import Path

ENTRIES_DIR = Path(__file__).parent.parent / "src" / "entries"


def remove_tooltips(filepath):
    """Remove the tooltip title from images in gallery pages."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = content.replace(' title="לחץ להגדלה"', '')

    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False


def main():
    fixed = 0
    for f in sorted(ENTRIES_DIR.glob("gallery_*.html")):
        if remove_tooltips(f):
            fixed += 1

    print(f"Removed 'לחץ להגדלה' tooltips from {fixed} gallery pages.")


if __name__ == "__main__":
    main()
