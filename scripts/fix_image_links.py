#!/usr/bin/env python3
"""
Fix inline image links that still use old nested paths.
Rewrites: href="images/pictures/COUNTRY/filename.jpg" -> href="../images/filename.jpg"
These are text links that open a photo in a new tab.
"""

import re
from pathlib import Path

ENTRIES_DIR = Path(__file__).parent.parent / "src" / "entries"
IMAGES_DIR = Path(__file__).parent.parent / "src" / "images"


def get_available_images():
    """Get set of available image filenames (lowercase for case-insensitive matching)."""
    return {f.name.lower(): f.name for f in IMAGES_DIR.iterdir() if f.is_file()}


def fix_image_links(filepath, available_images):
    """Fix image href links to point to flattened images folder."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    def replace_image_path(match):
        prefix = match.group(1)  # href="
        full_path = match.group(2)  # images/pictures/country/filename.jpg
        suffix = match.group(3)  # " target=...

        # Extract just the filename
        filename = full_path.split("/")[-1]

        # Check if the image exists in our flat images folder
        lookup = filename.lower().replace("&amp;", "&")
        if lookup in available_images:
            return f'{prefix}../images/{available_images[lookup]}{suffix}'
        else:
            # Image might not exist, still fix the path
            return f'{prefix}../images/{filename}{suffix}'

    # Match href="images/..." patterns (various subdirectories)
    new_content = re.sub(
        r'(href=")(images/[^"]+)(")',
        replace_image_path,
        content
    )

    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False


def main():
    available_images = get_available_images()
    print(f"Found {len(available_images)} images in flat folder.")

    fixed = 0
    for f in sorted(ENTRIES_DIR.glob("*.html")):
        if fix_image_links(f, available_images):
            fixed += 1

    print(f"Fixed image links in {fixed} pages.")


if __name__ == "__main__":
    main()
