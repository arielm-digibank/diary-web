#!/usr/bin/env python3
"""
Fix email pages:
1. Align content to left (English text in RTL page)
2. Rename home link to point to email section in index.html
"""

import re
from pathlib import Path

ENTRIES_DIR = Path(__file__).parent.parent / "src" / "entries"


def fix_email_page(filepath):
    """Fix alignment and home link in email pages."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # Add dir="ltr" and text-align:left to the content div
    content = content.replace(
        '    .content img {\n      float: right;',
        '    .content {\n      direction: ltr; text-align: left;\n    }\n    .content img {\n      float: left;'
    )
    # Also fix the float for images in LTR context
    content = content.replace(
        'margin: 0 0 15px 20px;',
        'margin: 0 20px 15px 0;'
    )

    # Rename home link
    content = content.replace(
        '<a href="../index.html" class="home-link">🏠 לעמוד הראשי</a>',
        '<a href="../index.html#emails" class="home-link">← כל האי-מיילים</a>'
    )

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def main():
    fixed = 0
    for f in sorted(ENTRIES_DIR.glob("email_*.html")):
        if fix_email_page(f):
            fixed += 1

    print(f"Fixed {fixed} email pages.")


if __name__ == "__main__":
    main()
