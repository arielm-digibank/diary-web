#!/usr/bin/env python3
"""
Fix gallery pages:
1. WELCOME3.GIF -> link to ../index.html (home)
2. religion015.gif (book icon) -> link to corresponding diary entry
3. Remove broken 'לחץ להגדלה' title from non-photo elements (separators)
4. Remove lightbox from separator images (fachsepa.gif)
"""

import os
from pathlib import Path
from bs4 import BeautifulSoup

ENTRIES_DIR = Path(__file__).parent.parent / "src" / "entries"

# Map gallery prefix to the diary entry it links to (from original site navigation)
GALLERY_TO_ENTRY = {
    "gallery_2001101": "20011006",  # India Oct 1
    "gallery_2001102": "20011006",  # India Oct 2
    "gallery_2001103": "20011006",  # India Oct 3
    "gallery_2001111": "20011030",  # Nepal Nov 1
    "gallery_2001112": "20011030",  # Nepal Nov 2
    "gallery_2001113": "20011115",  # Annapurna trek Nov 3
    "gallery_2001121": "20011201",  # Nepal Dec 1
    "gallery_2001122": "20011210",  # Thailand Dec 2
    "gallery_2002011": "20020108",  # Laos Jan 1
    "gallery_2002012": "20020123",  # North Thailand Jan 2
    "gallery_2002021": "20020203",  # Australia Feb 1
    "gallery_2002022": "20020210",  # New Zealand Feb 2
    "gallery_2002031": "20020210",  # NZ South Mar 1
    "gallery_2002032": "20020210",  # NZ South Mar 2
    "gallery_2002033": "20020326",  # NZ North Mar 3
    "gallery_200204": "20020326",   # NZ North Apr
    "gallery_200205": "20020506",   # Philippines May
    "gallery_200206": "20020603",   # Cambodia Jun
}


def fix_gallery(filepath):
    """Fix a gallery page."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    soup = BeautifulSoup(content, "lxml")
    page_name = filepath.stem
    modified = False

    for img in soup.find_all("img"):
        src = img.get("src", "")
        filename = os.path.basename(src).upper()

        if filename == "WELCOME3.GIF":
            img.attrs.pop("onclick", None)
            img.attrs.pop("title", None)
            if img.parent.name != "a":
                link = soup.new_tag("a", href="../index.html", title="חזור לעמוד הראשי")
                img.wrap(link)
            else:
                img.parent["href"] = "../index.html"
                img.parent["title"] = "חזור לעמוד הראשי"
            modified = True

        elif filename == "RELIGION015.GIF":
            img.attrs.pop("onclick", None)
            img.attrs.pop("title", None)
            entry = GALLERY_TO_ENTRY.get(page_name, "20011006")
            if img.parent.name != "a":
                link = soup.new_tag("a", href=f"{entry}.html", title="אל הסיפור")
                img.wrap(link)
            else:
                img.parent["href"] = f"{entry}.html"
                img.parent["title"] = "אל הסיפור"
            modified = True

        elif filename == "FACHSEPA.GIF":
            img.attrs.pop("onclick", None)
            img.attrs.pop("title", None)
            modified = True

    if modified:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(str(soup))

    return modified


def main():
    fixed = 0
    for f in sorted(ENTRIES_DIR.glob("gallery_*.html")):
        if fix_gallery(f):
            fixed += 1
            print(f"  Fixed: {f.name}")

    print(f"\nFixed {fixed} gallery pages.")


if __name__ == "__main__":
    main()
