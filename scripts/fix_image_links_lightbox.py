#!/usr/bin/env python3
"""
Convert inline image links (that open in new tab) to use the lightbox instead.
Also fixes previously broken escape sequences.
"""

import re
from pathlib import Path

ENTRIES_DIR = Path(__file__).parent.parent / "src" / "entries"


def fix_image_links_to_lightbox(filepath):
    """Convert target=_blank image links to lightbox triggers."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # Fix any previously broken escaped quotes from prior run
    content = re.sub(
        r"""<a href="javascript:void\(0\)" onclick="openLightbox\(\\'([^'\\]+)\\'\)">""",
        lambda m: f'<a href="javascript:void(0)" onclick="openLightbox(\'{m.group(1)}\')">',
        content
    )

    # Convert remaining target=_blank image links
    content = re.sub(
        r'<a href="(\.\./images/[^"]+)"[^>]*target="_blank"[^>]*>',
        lambda m: f'<a href="javascript:void(0)" onclick="openLightbox(\'{m.group(1)}\')">',
        content
    )

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def main():
    fixed = 0
    for f in sorted(ENTRIES_DIR.glob("*.html")):
        if fix_image_links_to_lightbox(f):
            fixed += 1

    print(f"Fixed image lightbox links in {fixed} pages.")


if __name__ == "__main__":
    main()
