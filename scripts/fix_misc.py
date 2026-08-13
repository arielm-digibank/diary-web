#!/usr/bin/env python3
"""
Fix multiple issues across pages:
1. Remove 'This site was last updated...' text from all pages
2. Remove 'Hi' title from email and gallery page headers
3. Style date/title text properly (centered, larger font)
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup

ENTRIES_DIR = Path(__file__).parent.parent / "src" / "entries"


def fix_last_updated(content):
    """Remove 'This site was last updated...' text."""
    # Remove the paragraph containing the timestamp
    content = re.sub(
        r'<p><i><small>This site was last updated.*?</small></i>\s*</p>',
        '',
        content,
        flags=re.DOTALL | re.IGNORECASE
    )
    # Also try without <p> wrapper
    content = re.sub(
        r'<i><small>This site was last updated.*?</small></i>',
        '',
        content,
        flags=re.DOTALL | re.IGNORECASE
    )
    return content


def fix_hi_title(content, page_name):
    """Remove or replace 'Hi' title in email pages."""
    if page_name.startswith("email_"):
        # Extract date from filename for a better title
        date_part = page_name.replace("email_", "")
        # Format: YYYYMMDD -> DD.MM.YY
        if len(date_part) >= 8:
            y, m, d = date_part[:4], date_part[4:6], date_part[6:8]
            title = f"אי-מייל - {d}.{m}.{y}"
        else:
            title = "אי-מייל"
        content = content.replace("<h1>Hi</h1>", f"<h1>{title}</h1>")
        content = content.replace("<title>Hi</title>", f"<title>{title}</title>")
    return content


def fix_title_styling(content):
    """Update .title-text CSS to be centered and styled distinctly."""
    old_css = """    .title-text {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      font-weight: 700;
      display: inline-block;
    }"""
    
    new_css = """    .title-text {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      font-weight: 700;
      display: block;
      text-align: center;
      color: #1e293b;
    }
    .title-text.date {
      font-size: 1rem;
      color: #64748b;
      margin-bottom: 4px;
    }
    .title-text.subtitle {
      font-size: 1.4rem;
      color: #334155;
    }"""
    
    content = content.replace(old_css, new_css)
    return content


def classify_title_spans(content):
    """Add .date or .subtitle class to title-text spans based on content."""
    # The first title-text is usually the date (e.g., "6.10.01 - 17:50")
    # The second is the subtitle (e.g., "לא קיבלנו הלם תרבות")
    
    # Find all title-text spans and add appropriate classes
    # First occurrence -> date
    content = content.replace(
        '<span class="title-text">',
        '<span class="title-text date">',
        1
    )
    # Second occurrence -> subtitle (now the first remaining unclassified)
    content = content.replace(
        '<span class="title-text">',
        '<span class="title-text subtitle">',
        1
    )
    return content


def fix_page(filepath):
    """Apply all fixes to a single page."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    page_name = filepath.stem
    original = content

    content = fix_last_updated(content)
    content = fix_hi_title(content, page_name)

    # Only apply title styling to diary entries (not email/gallery)
    if not page_name.startswith(("email_", "gallery_", "test_")):
        content = fix_title_styling(content)
        content = classify_title_spans(content)

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def main():
    fixed = 0
    for f in sorted(ENTRIES_DIR.glob("*.html")):
        if fix_page(f):
            fixed += 1

    print(f"Fixed {fixed} pages (last-updated removal, Hi title, title styling).")


if __name__ == "__main__":
    main()
