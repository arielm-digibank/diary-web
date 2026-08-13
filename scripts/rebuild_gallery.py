#!/usr/bin/env python3
"""
Rebuild gallery pages with masonry layout, captions from filenames,
and updated navigation link.
"""

import re
import os
from pathlib import Path
from bs4 import BeautifulSoup

ENTRIES_DIR = Path(__file__).parent.parent / "src" / "entries"

GALLERY_TITLES = {
    "gallery_2001101": "גלריה - הודו, אוקטובר 2001 (1)",
    "gallery_2001102": "גלריה - הודו, אוקטובר 2001 (2)",
    "gallery_2001103": "גלריה - הודו, אוקטובר 2001 (3)",
    "gallery_2001111": "גלריה - נפאל, נובמבר 2001 (1)",
    "gallery_2001112": "גלריה - נפאל, נובמבר 2001 (2)",
    "gallery_2001113": "גלריה - טרק אנאפורנה, נובמבר 2001",
    "gallery_2001121": "גלריה - נפאל/תאילנד, דצמבר 2001 (1)",
    "gallery_2001122": "גלריה - תאילנד, דצמבר 2001 (2)",
    "gallery_2002011": "גלריה - לאוס, ינואר 2002 (1)",
    "gallery_2002012": "גלריה - צפון תאילנד, ינואר 2002 (2)",
    "gallery_2002021": "גלריה - אוסטרליה, פברואר 2002 (1)",
    "gallery_2002022": "גלריה - ניו-זילנד, פברואר 2002 (2)",
    "gallery_2002031": "גלריה - ניו-זילנד, מרץ 2002 (1)",
    "gallery_2002032": "גלריה - ניו-זילנד, מרץ 2002 (2)",
    "gallery_2002033": "גלריה - ניו-זילנד, מרץ 2002 (3)",
    "gallery_200204": "גלריה - ניו-זילנד, אפריל 2002",
    "gallery_200205": "גלריה - פיליפינים, מאי 2002",
    "gallery_200206": "גלריה - קמבודיה, יוני 2002",
}

GALLERY_TO_ENTRY = {
    "gallery_2001101": "20011006",
    "gallery_2001102": "20011006",
    "gallery_2001103": "20011006",
    "gallery_2001111": "20011030",
    "gallery_2001112": "20011030",
    "gallery_2001113": "20011115",
    "gallery_2001121": "20011201",
    "gallery_2001122": "20011210",
    "gallery_2002011": "20020108",
    "gallery_2002012": "20020123",
    "gallery_2002021": "20020203",
    "gallery_2002022": "20020210",
    "gallery_2002031": "20020210",
    "gallery_2002032": "20020210",
    "gallery_2002033": "20020326",
    "gallery_200204": "20020326",
    "gallery_200205": "20020506",
    "gallery_200206": "20020603",
}


def parse_image_caption(src):
    """Parse a filename into a human-readable caption.
    e.g. '../images/20011007_gonen_with_cobra1.jpg' -> '7.10.2001 - gonen with cobra'
    """
    filename = os.path.basename(src)
    name = os.path.splitext(filename)[0]

    # Try to extract date prefix (YYYYMMDD_)
    date_match = re.match(r'^(\d{4})(\d{2})(\d{2})_(.+)$', name)
    if date_match:
        y, m, d, rest = date_match.groups()
        date_str = f"{int(d)}.{int(m)}.{y}"
        # Clean up the rest: replace underscores, remove trailing numbers
        caption = rest.replace("_", " ").strip()
        caption = re.sub(r'\d+$', '', caption).strip()
        if caption:
            return f"{date_str} - {caption}"
        return date_str

    # No date prefix - just clean the name
    caption = name.replace("_", " ").strip()
    caption = re.sub(r'\d+$', '', caption).strip()
    return caption if caption else name


def rebuild_gallery(filepath):
    """Rebuild a gallery page with masonry layout and captions."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    soup = BeautifulSoup(content, "lxml")
    page_name = filepath.stem
    title = GALLERY_TITLES.get(page_name, f"גלריה - {page_name}")
    entry_link = GALLERY_TO_ENTRY.get(page_name, "20011006")

    # Extract all gallery image sources
    images = []
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if src and "fachsepa" not in src and "WELCOME" not in src.upper() and "religion015" not in src:
            # Get original dimensions to determine orientation
            w = int(img.get("width", 180) or 180)
            h = int(img.get("height", 180) or 180)
            is_vertical = h > w
            images.append({"src": src, "vertical": is_vertical})

    new_html = f'''<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    body {{
      background-color: #f8fafc;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      margin: 0; padding: 20px; color: #334155;
    }}
    .container {{
      max-width: 1100px; margin: 0 auto; background: #ffffff;
      padding: 35px; border-radius: 12px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    }}
    .header {{
      border-bottom: 2px solid #e2e8f0; padding-bottom: 15px;
      margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center;
    }}
    .header h1 {{ margin: 0; color: #0f172a; font-size: 1.6rem; }}
    .home-link {{ color: #2563eb; text-decoration: none; font-weight: 600; }}
    .masonry {{
      columns: 3;
      column-gap: 14px;
      margin: 20px 0;
    }}
    @media (max-width: 800px) {{ .masonry {{ columns: 2; }} }}
    @media (max-width: 500px) {{ .masonry {{ columns: 1; }} }}
    .masonry-item {{
      break-inside: avoid;
      margin-bottom: 14px;
      border-radius: 10px;
      overflow: hidden;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
      transition: transform 0.2s, box-shadow 0.2s;
    }}
    .masonry-item:hover {{
      transform: translateY(-3px);
      box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    }}
    .masonry-item img {{
      width: 100%; display: block; cursor: pointer;
    }}
    .masonry-item .caption {{
      padding: 8px 12px;
      font-size: 0.82rem;
      color: #64748b;
      background: #f8fafc;
      direction: ltr;
      text-align: left;
    }}
    .footer-nav {{
      margin-top: 30px; padding-top: 20px;
      border-top: 1px solid #e2e8f0;
      display: flex; gap: 16px; justify-content: center;
    }}
    .footer-nav a {{
      display: inline-flex; align-items: center; gap: 8px;
      padding: 10px 18px; border-radius: 8px;
      background: #f1f5f9; color: #334155; text-decoration: none;
      font-weight: 600; font-size: 0.95rem;
      transition: background 0.2s;
    }}
    .footer-nav a:hover {{ background: #e2e8f0; }}
    .lightbox {{
      display: none; position: fixed; z-index: 9999;
      top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(0,0,0,0.92); justify-content: center; align-items: center; cursor: pointer;
    }}
    .lightbox img {{ max-width: 92%; max-height: 92%; border-radius: 8px; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>{title}</h1>
      <a href="../index.html#galleries" class="home-link">← כל הגלריות</a>
    </div>
    <div class="masonry">
'''

    for img_data in images:
        caption = parse_image_caption(img_data["src"])
        new_html += f'''      <div class="masonry-item">
        <img src="{img_data["src"]}" onclick="openLightbox(this.src)"/>
        <div class="caption">{caption}</div>
      </div>
'''

    new_html += f'''    </div>
    <div class="footer-nav">
      <a href="../index.html#galleries">← כל הגלריות</a>
      <a href="{entry_link}.html">📖 אל היומן</a>
    </div>
  </div>

  <div id="lightbox" class="lightbox" onclick="this.style.display='none'">
    <img id="lightbox-img" src="" alt="Enlarged">
  </div>

  <script>
    function openLightbox(src) {{
      document.getElementById('lightbox-img').src = src;
      document.getElementById('lightbox').style.display = 'flex';
    }}
  </script>
</body>
</html>
'''

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_html)

    return len(images)


def main():
    for f in sorted(ENTRIES_DIR.glob("gallery_*.html")):
        count = rebuild_gallery(f)
        print(f"  {f.name}: {count} images")

    print(f"\nRebuilt all 18 gallery pages with masonry + captions.")


if __name__ == "__main__":
    main()
