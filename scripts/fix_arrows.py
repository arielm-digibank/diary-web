#!/usr/bin/env python3
"""
Replace arrow button images with beautiful styled prev/next navigation.
Removes the old button GIF images and replaces with CSS-styled links.
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup

ENTRIES_DIR = Path(__file__).parent.parent / "src" / "entries"

# CSS for the nav arrows (injected into page style)
NAV_CSS = """
    .page-nav {
      display: flex; justify-content: space-between; align-items: center;
      margin-top: 30px; padding-top: 20px;
      border-top: 1px solid #e2e8f0;
    }
    .page-nav a {
      display: inline-flex; align-items: center; gap: 8px;
      padding: 10px 18px; border-radius: 8px;
      background: #f1f5f9; color: #334155; text-decoration: none;
      font-weight: 600; font-size: 0.95rem;
      transition: background 0.2s, transform 0.2s;
    }
    .page-nav a:hover { background: #e2e8f0; transform: translateY(-1px); }
    .page-nav .arrow { font-size: 1.3rem; }
    .page-nav .placeholder { width: 120px; }
"""


def fix_arrows_in_page(filepath):
    """Replace arrow button images with styled navigation links."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    soup = BeautifulSoup(content, "lxml")
    modified = False

    # Find prev/next links from existing button images
    prev_href = None
    next_href = None

    for img in soup.find_all("img"):
        src = img.get("src", "")
        if "button104.gif" in src:
            if img.parent and img.parent.name == "a":
                prev_href = img.parent.get("href")
        elif "button106.gif" in src:
            if img.parent and img.parent.name == "a":
                next_href = img.parent.get("href")

    if not prev_href and not next_href:
        return False

    # Find and remove the table row containing the arrow buttons
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if "button104.gif" in src or "button106.gif" in src:
            # Walk up to the containing <td> and mark for removal
            parent = img.parent
            while parent and parent.name != "td":
                parent = parent.parent
            if parent:
                parent.clear()
                modified = True

    if not modified:
        return False

    # Build the new navigation HTML
    nav_parts = []
    nav_parts.append('<div class="page-nav">')

    if next_href:
        nav_parts.append(f'  <a href="{next_href}"><span class="arrow">→</span> הבא</a>')
    else:
        nav_parts.append('  <span class="placeholder"></span>')

    if prev_href:
        nav_parts.append(f'  <a href="{prev_href}">הקודם <span class="arrow">←</span></a>')
    else:
        nav_parts.append('  <span class="placeholder"></span>')

    nav_parts.append('</div>')
    nav_html = "\n".join(nav_parts)

    # Inject CSS into the existing <style> block
    style_tag = soup.find("style")
    if style_tag and style_tag.string:
        if ".page-nav" not in style_tag.string:
            style_tag.string = style_tag.string + NAV_CSS

    # Insert navigation before the closing content div or at end of body
    # Find the content div or body
    content_div = soup.find("div", class_="content")
    if content_div:
        nav_soup = BeautifulSoup(nav_html, "lxml")
        nav_div = nav_soup.find("div", class_="page-nav")
        if nav_div:
            content_div.append(nav_div)
    else:
        body = soup.find("body")
        if body:
            nav_soup = BeautifulSoup(nav_html, "lxml")
            nav_div = nav_soup.find("div", class_="page-nav")
            if nav_div:
                body.append(nav_div)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(str(soup))

    return True


def main():
    fixed = 0
    for f in sorted(ENTRIES_DIR.glob("*.html")):
        name = f.stem
        if name.startswith(("email_", "gallery_", "test_")):
            continue
        if fix_arrows_in_page(f):
            fixed += 1

    print(f"Replaced arrow buttons with styled navigation in {fixed} pages.")


if __name__ == "__main__":
    main()
