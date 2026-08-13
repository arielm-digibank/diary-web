#!/usr/bin/env python3
"""
Fix navigation arrows, email links, and map icons across all diary entry pages.

Issues fixed:
1. Arrow buttons (button104.gif, button106.gif) - restore prev/next links
2. Email icons (contract_highlighter_rolling_md_wht.gif) - link to email pages
3. Map icons (country .gif files) - remove lightbox behavior
"""

import os
import re
from pathlib import Path
from bs4 import BeautifulSoup

ENTRIES_DIR = Path(__file__).parent.parent / "src" / "entries"

COUNTRY_MAPS = {
    "India.gif", "Nepal.gif", "Thailand.gif", "Australia.gif",
    "New_Zealand.gif", "New_Zealand_south_island.gif",
    "New_Zealand_north_island.gif", "Denmark.gif", "Laos.gif",
    "Cambodia.gif", "Philippines.gif"
}


def get_navigation_order():
    """Build sorted list of diary entries (excluding email_, gallery_, test_)."""
    entries = []
    for f in ENTRIES_DIR.glob("*.html"):
        name = f.stem
        if name.startswith(("email_", "gallery_", "test_")):
            continue
        entries.append(name)
    entries.sort()
    return entries


def get_email_pages():
    """Get set of available email page basenames."""
    return {f.stem for f in ENTRIES_DIR.glob("email_*.html")}


def find_matching_email(page_name, email_pages):
    """Find the email page that corresponds to a diary entry."""
    candidate = f"email_{page_name}"
    if candidate in email_pages:
        return candidate

    date_prefix = page_name[:8]
    for ep in sorted(email_pages):
        if ep.startswith(f"email_{date_prefix}"):
            return ep
    return None


def fix_page(filepath, prev_page, next_page, email_pages):
    """Fix a single entry page."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    modified = False
    soup = BeautifulSoup(content, "lxml")
    page_name = filepath.stem

    # Fix arrow buttons - restore navigation links
    for img in soup.find_all("img"):
        src = img.get("src", "")
        filename = os.path.basename(src)

        if filename == "button104.gif":
            # button104 = previous page link
            if prev_page:
                img.attrs.pop("onclick", None)
                img.attrs.pop("title", None)
                if img.parent.name != "a":
                    link = soup.new_tag("a", href=f"{prev_page}.html")
                    img.wrap(link)
                else:
                    img.parent["href"] = f"{prev_page}.html"
                modified = True

        elif filename == "button106.gif":
            # button106 = next page link
            if next_page:
                img.attrs.pop("onclick", None)
                img.attrs.pop("title", None)
                if img.parent.name != "a":
                    link = soup.new_tag("a", href=f"{next_page}.html")
                    img.wrap(link)
                else:
                    img.parent["href"] = f"{next_page}.html"
                modified = True

        elif filename == "contract_highlighter_rolling_md_wht.gif":
            # Email icon - link to corresponding email page
            email_page = find_matching_email(page_name, email_pages)
            if email_page:
                img.attrs.pop("onclick", None)
                img.attrs.pop("title", None)
                if img.parent.name != "a":
                    link = soup.new_tag("a", href=f"{email_page}.html")
                    img.wrap(link)
                else:
                    img.parent["href"] = f"{email_page}.html"
                modified = True

        elif filename in COUNTRY_MAPS:
            # Map icons - remove lightbox, keep as plain image
            img.attrs.pop("onclick", None)
            img.attrs.pop("title", None)
            modified = True

    if modified:
        html_str = str(soup)
        # lxml wraps in <html><body>, extract just the original structure
        # Since our files are full HTML docs, this should be fine
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_str)

    return modified


def main():
    nav_order = get_navigation_order()
    email_pages = get_email_pages()

    print(f"Navigation sequence: {len(nav_order)} pages")
    print(f"Email pages available: {len(email_pages)}")
    print()

    fixed_count = 0
    for i, page_name in enumerate(nav_order):
        filepath = ENTRIES_DIR / f"{page_name}.html"
        prev_page = nav_order[i - 1] if i > 0 else None
        next_page = nav_order[i + 1] if i < len(nav_order) - 1 else None

        if fix_page(filepath, prev_page, next_page, email_pages):
            fixed_count += 1
            print(f"  Fixed: {page_name}.html (prev={prev_page}, next={next_page})")

    print(f"\nDone. Fixed {fixed_count}/{len(nav_order)} pages.")


if __name__ == "__main__":
    main()
