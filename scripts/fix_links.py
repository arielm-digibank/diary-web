#!/usr/bin/env python3
"""
Fix broken internal links across all entry pages.
Changes .htm references to .html and fixes anchor links.
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup

ENTRIES_DIR = Path(__file__).parent.parent / "src" / "entries"


def fix_htm_links(filepath):
    """Fix .htm links to .html in a page."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Fix href="YYYYMMDD.htm" or href="YYYYMMDD.htm#anchor" -> .html
    new_content = re.sub(
        r'href="([0-9]+\.htm)(#[^"]*)?(")',
        lambda m: f'href="{m.group(1)}l{m.group(2) or ""}{m.group(3)}',
        content
    )

    # Fix href="email_YYYYMMDD.htm" -> .html
    new_content = re.sub(
        r'href="(email_[0-9]+\.htm)(#[^"]*)?(")',
        lambda m: f'href="{m.group(1)}l{m.group(2) or ""}{m.group(3)}',
        new_content
    )

    # Fix href="gallery_YYYYMM.htm" -> .html  
    new_content = re.sub(
        r'href="(gallery_[0-9]+\.htm)(#[^"]*)?(")',
        lambda m: f'href="{m.group(1)}l{m.group(2) or ""}{m.group(3)}',
        new_content
    )

    # Fix href="index.htm" -> ../index.html (from entries/ folder)
    new_content = new_content.replace('href="index.htm"', 'href="../index.html"')
    new_content = new_content.replace("href='index.htm'", "href='../index.html'")

    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False


def main():
    fixed = 0
    for f in sorted(ENTRIES_DIR.glob("*.html")):
        if fix_htm_links(f):
            fixed += 1

    print(f"Fixed .htm links in {fixed} files.")


if __name__ == "__main__":
    main()
