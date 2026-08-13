#!/usr/bin/env python3
"""
Apply V2 Magazine Blocks design to all diary entry pages.
Extracts content, images, captions and regenerates with new layout.
"""

import os
import re
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

ENTRIES_DIR = Path(__file__).parent.parent / "src" / "entries"

COUNTRY_MAPS = {
    "India.gif": "הודו",
    "Nepal.gif": "נפאל",
    "Thailand.gif": "תאילנד",
    "Australia.gif": "אוסטרליה",
    "New_Zealand.gif": "ניו-זילנד",
    "New_Zealand_south_island.gif": "ניו-זילנד, אי דרומי",
    "New_Zealand_north_island.gif": "ניו-זילנד, אי צפוני",
    "Denmark.gif": "דנמרק",
    "Laos.gif": "לאוס",
    "Cambodia.gif": "קמבודיה",
    "Philippines.gif": "פיליפינים",
}

DATE_TO_COUNTRY = [
    ("20011005", "20011006", "Denmark.gif"),
    ("20011006", "20011030", "India.gif"),
    ("20011030", "20011115", "Nepal.gif"),
    ("20011115", "20011201", "Nepal.gif"),
    ("20011201", "20011210", "Nepal.gif"),
    ("20011210", "20020108", "Thailand.gif"),
    ("20020108", "20020123", "Laos.gif"),
    ("20020123", "20020203", "Thailand.gif"),
    ("20020203", "20020210", "Australia.gif"),
    ("20020210", "20020326", "New_Zealand.gif"),
    ("20020326", "20020506", "New_Zealand.gif"),
    ("20020506", "20020603", "Philippines.gif"),
    ("20020603", "20020701", "Cambodia.gif"),
]


def get_country_map(page_name):
    """Determine which country map to use based on page date."""
    date_str = page_name[:8]
    for start, end, map_file in DATE_TO_COUNTRY:
        if start <= date_str < end:
            return map_file
    return "India.gif"


def get_country_name(map_file):
    """Get Hebrew country name from map filename."""
    return COUNTRY_MAPS.get(map_file, "")


def extract_date_text(soup):
    """Extract date from title-text.date span or first marquee."""
    date_span = soup.find("span", class_="title-text date")
    if date_span:
        return date_span.get_text(strip=True)
    # Try marquee (original format)
    marquees = soup.find_all("marquee")
    if marquees:
        first_text = marquees[0].get_text(strip=True)
        # Check if it looks like a date (e.g., "7.10.01" or "5.10.01 - 11:00")
        if re.match(r'\d{1,2}\.\d{1,2}\.\d{2}', first_text):
            return first_text
    # Try span with title-text (without .date class)
    spans = soup.find_all("span", class_="title-text")
    for span in spans:
        text = span.get_text(strip=True)
        if re.match(r'\d{1,2}\.\d{1,2}\.\d{2}', text):
            return text
    return ""


def extract_subtitle(soup):
    """Extract subtitle from title-text.subtitle span or second marquee."""
    sub_span = soup.find("span", class_="title-text subtitle")
    if sub_span:
        return sub_span.get_text(strip=True)
    # Try second marquee
    marquees = soup.find_all("marquee")
    if len(marquees) >= 2:
        return marquees[1].get_text(strip=True)
    elif len(marquees) == 1:
        text = marquees[0].get_text(strip=True)
        # If it doesn't look like a date, it's the subtitle
        if not re.match(r'\d{1,2}\.\d{1,2}\.\d{2}', text):
            return text
    return ""


def extract_page_title(soup):
    """Extract the page title from <title> or <h1>."""
    title_tag = soup.find("title")
    if title_tag:
        text = title_tag.get_text(strip=True)
        if text and text != "my trip web site":
            return text
    h1 = soup.find("h1")
    if h1:
        text = h1.get_text(strip=True)
        if text and text != "my trip web site":
            return text
    return ""


def extract_map_from_page(soup, page_name):
    """Try to find the country map image in the page, or infer from date."""
    for img in soup.find_all("img"):
        src = img.get("src", "")
        filename = os.path.basename(src)
        if filename in COUNTRY_MAPS:
            return filename
    return get_country_map(page_name)


def extract_images_with_captions(soup):
    """Extract all images (sidebar + content) with their captions."""
    images = []
    seen_srcs = set()

    for img in soup.find_all("img"):
        src = img.get("src", "")
        if not src or src in seen_srcs:
            continue

        filename = os.path.basename(src)
        # Skip non-content images
        if filename in COUNTRY_MAPS:
            continue
        if "button" in filename.lower():
            continue
        if "fachsepa" in filename.lower():
            continue
        if filename == "contract_highlighter_rolling_md_wht.gif":
            continue

        seen_srcs.add(src)

        caption = ""
        # Look for caption in adjacent <p> with <font color="#660099">
        parent = img.parent
        next_el = img.find_next_sibling()
        if not next_el and parent:
            next_el = parent.find_next_sibling()

        if next_el:
            font = next_el.find("font", color="#660099") if hasattr(next_el, 'find') else None
            if font:
                caption = font.get_text(strip=True)
            elif hasattr(next_el, 'name') and next_el.name == "p":
                font = next_el.find("font", color="#660099")
                if font:
                    caption = font.get_text(strip=True)

        # Also check the parent <p>'s next sibling
        if not caption and parent and parent.name == "p":
            next_p = parent.find_next_sibling("p")
            if next_p:
                font = next_p.find("font", color="#660099")
                if font:
                    caption = font.get_text(strip=True)

        images.append({"src": src, "caption": caption})

    return images


def extract_text_content(soup):
    """Extract the main text content as clean HTML paragraphs."""
    paragraphs = []

    # Find all text-bearing elements in the content area
    content_div = soup.find("div", class_="content")
    if not content_div:
        content_div = soup.find("body")

    # Collect text from various elements
    for el in content_div.find_all(["p", "h3", "h1", "h4", "dt", "li"]):
        # Skip elements that are just images or navigation
        if el.find_parent(class_="page-nav"):
            continue
        if el.find_parent(class_="header"):
            continue

        # Skip the old webbot navigation bar
        el_text_raw = el.get_text()
        if "webbot bot" in el_text_raw or "webbot" in str(el):
            continue
        if "S-Type=\"sequence\"" in str(el):
            continue

        # Skip old country navigation nobr links
        if el.find("nobr") and el.find("a", href="index.html"):
            continue

        # Get the text content - track which text nodes are inside links
        text = ""
        skip_descendants = set()

        for child in el.descendants:
            if id(child) in skip_descendants:
                continue

            if child.name == "a":
                onclick = child.get("onclick", "")
                href = child.get("href", "")
                link_text = child.get_text()

                # Mark all descendants of this <a> to skip
                for desc in child.descendants:
                    skip_descendants.add(id(desc))

                if "openLightbox" in onclick:
                    match = re.search(r"openLightbox\('([^']+)'\)", onclick)
                    if match:
                        img_src = match.group(1)
                        text += f'<a onclick="openLightbox(\'{img_src}\')">{link_text}</a>'
                    else:
                        text += link_text
                elif href and re.search(r'\.(jpg|jpeg|gif|png)$', href, re.IGNORECASE):
                    # Image link - convert to lightbox
                    filename = os.path.basename(href)
                    text += f'<a onclick="openLightbox(\'../images/{filename}\')">{link_text}</a>'
                elif href and "javascript" not in href and "#URL#" not in href:
                    text += f'<a href="{href}">{link_text}</a>'
                else:
                    text += link_text
            elif isinstance(child, NavigableString):
                text += str(child)
            elif child.name in ("br",):
                text += " "

        # Clean the text
        text = re.sub(r'\s+', ' ', text).strip()
        text = text.replace('\xa0', ' ').strip()

        # Skip empty, very short, or navigation-only paragraphs
        if not text or len(text) < 3:
            continue
        if text in ("&nbsp;", " "):
            continue

        # Skip title-text spans (already extracted)
        if el.find("span", class_=re.compile("title-text")):
            continue

        # Skip captions (purple text)
        if el.find("font", color="#660099"):
            other_text = re.sub(r'<[^>]+>', '', text).strip()
            pure_caption = el.find("font", color="#660099")
            if pure_caption and pure_caption.get_text(strip=True) == other_text:
                continue

        # Final filter: skip if it contains webbot remnants
        if "webbot" in text or "S-Btn-Nml" in text or "#URL#" in text:
            continue
        if "startspan" in text or "endspan" in text:
            continue

        paragraphs.append(text)

    return paragraphs


def extract_nav_links(soup):
    """Extract prev/next navigation links."""
    prev_href = None
    next_href = None

    nav = soup.find("div", class_="page-nav")
    if nav:
        links = nav.find_all("a")
        for link in links:
            href = link.get("href", "")
            text = link.get_text()
            if "הבא" in text:
                next_href = href
            elif "הקודם" in text:
                prev_href = href

    return prev_href, next_href


def format_date_display(date_text):
    """Format date text for display (already formatted like 8.10.01)."""
    if not date_text:
        return ""
    # Try to parse DD.MM.YY format
    match = re.match(r'(\d{1,2})\.(\d{1,2})\.(\d{2,4})', date_text)
    if match:
        d, m, y = match.groups()
        if len(y) == 2:
            y = "20" + y if int(y) < 50 else "19" + y
        months = {
            "1": "ינואר", "2": "פברואר", "3": "מרץ", "4": "אפריל",
            "5": "מאי", "6": "יוני", "7": "יולי", "8": "אוגוסט",
            "9": "ספטמבר", "10": "אוקטובר", "11": "נובמבר", "12": "דצמבר"
        }
        month_name = months.get(str(int(m)), m)
        return f"{int(d)} ב{month_name} {y}"
    return date_text


def extract_day_number(date_text):
    """Extract just the day number for the big date display."""
    match = re.match(r'(\d{1,2})\.', date_text)
    if match:
        return match.group(1).zfill(2)
    return ""


def extract_month_year(date_text):
    """Extract month and year for the detail line."""
    match = re.match(r'\d{1,2}\.(\d{1,2})\.(\d{2,4})', date_text)
    if match:
        m, y = match.groups()
        if len(y) == 2:
            y = "20" + y if int(y) < 50 else "19" + y
        months = {
            "1": "ינואר", "2": "פברואר", "3": "מרץ", "4": "אפריל",
            "5": "מאי", "6": "יוני", "7": "יולי", "8": "אוגוסט",
            "9": "ספטמבר", "10": "אוקטובר", "11": "נובמבר", "12": "דצמבר"
        }
        month_name = months.get(str(int(m)), m)
        return f"{month_name} {y}"
    return ""


def generate_photo_html(images, start_idx, count):
    """Generate HTML for a group of photos."""
    group = images[start_idx:start_idx + count]
    if not group:
        return ""

    if count == 1:
        img = group[0]
        html = f'''    <div class="photo-block">
      <img src="{img['src']}" onclick="openLightbox(this.src)">
      {f'<div class="caption">{img["caption"]}</div>' if img["caption"] else ''}
    </div>
'''
        return html

    if count == 2:
        html = '    <div class="photo-pair">\n'
        for img in group:
            html += f'''      <div class="photo-item">
        <img src="{img['src']}" onclick="openLightbox(this.src)">
        {f'<div class="caption">{img["caption"]}</div>' if img["caption"] else ''}
      </div>
'''
        html += '    </div>\n'
        return html

    # count == 3
    html = '    <div class="photo-trio">\n'
    for img in group:
        html += f'''      <div class="photo-item">
        <img src="{img['src']}" onclick="openLightbox(this.src)">
        {f'<div class="caption">{img["caption"]}</div>' if img["caption"] else ''}
      </div>
'''
    html += '    </div>\n'
    return html


def build_page(page_name, date_text, subtitle, page_title, map_file, country_name,
               paragraphs, images, prev_href, next_href, page_titles):
    """Generate the full V2 Magazine page HTML."""

    day_num = extract_day_number(date_text)
    month_year = extract_month_year(date_text)
    title = subtitle or page_title or "יומן מסע"
    date_display = date_text  # Keep original date text like "7.10.01"

    # Distribute images evenly among paragraphs
    total_images = len(images)
    total_paras = len(paragraphs)

    # Calculate where to insert photo blocks
    photo_positions = []
    if total_images > 0 and total_paras > 0:
        # Insert photos every N paragraphs
        interval = max(2, total_paras // (total_images // 2 + 1))
        img_idx = 0
        for pos in range(interval, total_paras, interval):
            if img_idx >= total_images:
                break
            remaining = total_images - img_idx
            if remaining >= 3 and (total_images - img_idx) > 4:
                photo_positions.append((pos, img_idx, 3))
                img_idx += 3
            elif remaining >= 2:
                photo_positions.append((pos, img_idx, 2))
                img_idx += 2
            else:
                photo_positions.append((pos, img_idx, 1))
                img_idx += 1

        # If there are leftover images, add them at the end
        while img_idx < total_images:
            remaining = total_images - img_idx
            if remaining >= 3:
                photo_positions.append((total_paras, img_idx, 3))
                img_idx += 3
            elif remaining >= 2:
                photo_positions.append((total_paras, img_idx, 2))
                img_idx += 2
            else:
                photo_positions.append((total_paras, img_idx, 1))
                img_idx += 1

    # Separate "השלמות" section from main paragraphs
    main_paras = []
    supplements = []
    in_supplements = False
    for para in paragraphs:
        if "השלמות:" in para or "השלמות :" in para:
            in_supplements = True
            continue
        if in_supplements:
            supplements.append(para)
        else:
            main_paras.append(para)

    # Build content with interleaved photos (only in main paragraphs)
    total_paras = len(main_paras)
    content_html = ""
    photo_pos_map = {}
    for pos, idx, count in photo_positions:
        capped_pos = min(pos, total_paras)
        if capped_pos not in photo_pos_map:
            photo_pos_map[capped_pos] = []
        photo_pos_map[capped_pos].append((idx, count))

    for i, para in enumerate(main_paras):
        content_html += f"    <p>{para}</p>\n\n"
        if (i + 1) in photo_pos_map:
            for idx, count in photo_pos_map[i + 1]:
                content_html += generate_photo_html(images, idx, count) + "\n"

    # Add any remaining photos at end of main content
    if total_paras in photo_pos_map:
        for idx, count in photo_pos_map[total_paras]:
            content_html += generate_photo_html(images, idx, count) + "\n"

    # Add supplements section if present
    if supplements:
        content_html += '    <div class="supplements">\n'
        content_html += '      <h3>השלמות:</h3>\n'
        content_html += '      <ol>\n'
        for item in supplements:
            # Strip leading number + dot/space
            clean = re.sub(r'^\d+[\.\)]\s*', '', item)
            content_html += f'        <li>{clean}</li>\n'
        content_html += '      </ol>\n'
        content_html += '    </div>\n'

    # Navigation cards
    nav_html = ""
    if next_href or prev_href:
        next_title = page_titles.get(next_href.replace(".html", ""), "הדף הבא") if next_href else ""
        prev_title = page_titles.get(prev_href.replace(".html", ""), "הדף הקודם") if prev_href else ""

        nav_html = '  <div class="nav-cards">\n'
        if next_href:
            nav_html += f'''    <a href="{next_href}" class="nav-card">
      <div class="label">הבא →</div>
      <div class="card-title">{next_title}</div>
    </a>
'''
        else:
            nav_html += '    <div></div>\n'

        if prev_href:
            nav_html += f'''    <a href="{prev_href}" class="nav-card">
      <div class="label">← הקודם</div>
      <div class="card-title">{prev_title}</div>
    </a>
'''
        else:
            nav_html += '    <div></div>\n'
        nav_html += '  </div>\n'

    # Country navigation bar
    country_nav_html = '''  <div class="country-nav">
    <a href="200110052040.html">דנמרק</a>
    <a href="20011006.html">הודו</a>
    <a href="20011030.html">נפאל</a>
    <a href="20011115.html">טרק אנאפורנה</a>
    <a href="20011210.html">תאילנד</a>
    <a href="20020108.html">לאוס</a>
    <a href="20020123.html">צפון תאילנד</a>
    <a href="20020203.html">אוסטרליה</a>
    <a href="20020210.html">ניו-זילנד, אי דרומי</a>
    <a href="20020326.html">ניו-זילנד, אי צפוני</a>
    <a href="20020506.html">פיליפינים</a>
    <a href="20020603.html">קמבודיה</a>
  </div>
'''

    html = f'''<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <link href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;700;900&display=swap" rel="stylesheet">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      background: #ffffff;
      font-family: 'Heebo', sans-serif;
      color: #1a1a2e;
      line-height: 1.9;
    }}
    .top-nav {{
      position: sticky; top: 0; z-index: 100;
      background: rgba(255,255,255,0.95);
      backdrop-filter: blur(10px);
      border-bottom: 1px solid #eee;
      padding: 12px 30px;
      display: flex; justify-content: space-between; align-items: center;
      font-size: 0.9rem;
    }}
    .top-nav a {{
      color: #1d4ed8; text-decoration: none; font-weight: 600;
    }}
    .top-nav a:hover {{ text-decoration: underline; }}
    .top-nav .nav-links {{ display: flex; gap: 20px; }}
    .hero {{
      max-width: 900px; margin: 0 auto;
      padding: 50px 40px 30px;
      display: flex; align-items: flex-start; gap: 30px;
    }}
    .hero-text {{ flex: 1; }}
    .hero-map {{
      width: 120px; height: auto; object-fit: contain;
      flex-shrink: 0; opacity: 0.85;
    }}
    .meta-line {{
      display: flex; align-items: center; gap: 12px; margin-bottom: 16px;
    }}
    .date-big {{
      font-size: 3.5rem; font-weight: 900; color: #e5e7eb; line-height: 1;
    }}
    .date-details {{ font-size: 0.9rem; color: #6b7280; }}
    .country-badge {{
      display: inline-flex; align-items: center; gap: 6px;
      background: #f0f9ff; border: 1px solid #bfdbfe;
      border-radius: 20px; padding: 4px 14px;
      font-size: 0.8rem; color: #1d4ed8; font-weight: 600;
    }}
    .title {{
      font-size: 2.2rem; font-weight: 900; color: #111827;
      margin: 20px 0 8px; line-height: 1.3;
    }}
    .date-subtitle {{
      font-size: 1.1rem; font-weight: 300; color: #4b5563;
      margin-bottom: 16px;
    }}
    .title-divider {{
      width: 60px; height: 4px; background: #1d4ed8; border-radius: 2px;
    }}
    .content {{
      max-width: 900px; margin: 30px auto; padding: 0 40px; font-size: 1.05rem;
    }}
    .content p {{ margin-bottom: 18px; }}
    .content a {{
      color: #1d4ed8; cursor: pointer;
      text-decoration: underline;
      text-decoration-color: rgba(29,78,216,0.3);
    }}
    .photo-block {{
      margin: 30px 0; border-radius: 12px; overflow: hidden;
      box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }}
    .photo-block img {{
      width: 100%; display: block; cursor: pointer;
      transition: transform 0.3s;
    }}
    .photo-block img:hover {{ transform: scale(1.01); }}
    .photo-block .caption {{
      padding: 12px 16px; font-size: 0.85rem; color: #6b7280;
      background: #f9fafb; border-top: 1px solid #f3f4f6;
    }}
    .photo-pair {{
      display: grid; grid-template-columns: 1fr 1fr;
      gap: 14px; margin: 30px 0;
    }}
    .photo-pair .photo-item {{
      border-radius: 10px; overflow: hidden;
      box-shadow: 0 3px 14px rgba(0,0,0,0.06);
    }}
    .photo-pair .photo-item img {{
      width: 100%; height: 200px; object-fit: cover;
      display: block; cursor: pointer; transition: transform 0.2s;
    }}
    .photo-pair .photo-item img:hover {{ transform: scale(1.03); }}
    .photo-pair .photo-item .caption {{
      padding: 8px 12px; font-size: 0.8rem; color: #6b7280; background: #f9fafb;
    }}
    .photo-trio {{
      display: grid; grid-template-columns: 1fr 1fr 1fr;
      gap: 12px; margin: 30px 0;
    }}
    .photo-trio .photo-item {{
      border-radius: 10px; overflow: hidden;
      box-shadow: 0 3px 14px rgba(0,0,0,0.06);
    }}
    .photo-trio .photo-item img {{
      width: 100%; height: 180px; object-fit: cover;
      display: block; cursor: pointer; transition: transform 0.2s;
    }}
    .photo-trio .photo-item img:hover {{ transform: scale(1.03); }}
    .photo-trio .photo-item .caption {{
      padding: 8px 10px; font-size: 0.78rem; color: #6b7280; background: #f9fafb;
    }}
    .nav-cards {{
      max-width: 900px; margin: 50px auto 20px; padding: 0 40px;
      display: grid; grid-template-columns: 1fr 1fr; gap: 16px;
    }}
    .nav-card {{
      padding: 20px 24px; border: 1px solid #e5e7eb; border-radius: 12px;
      text-decoration: none; color: inherit; transition: all 0.2s;
    }}
    .nav-card:hover {{
      border-color: #1d4ed8; box-shadow: 0 4px 12px rgba(29,78,216,0.1);
    }}
    .nav-card .label {{ font-size: 0.8rem; color: #6b7280; margin-bottom: 4px; }}
    .nav-card .card-title {{ font-weight: 700; font-size: 1rem; color: #1d4ed8; }}
    .supplements {{
      margin-top: 35px; padding: 25px 30px;
      background: #f9fafb; border-radius: 12px; border: 1px solid #e5e7eb;
    }}
    .supplements h3 {{
      font-size: 1.1rem; font-weight: 700; margin-bottom: 14px; color: #374151;
    }}
    .supplements ol {{ padding-right: 20px; }}
    .supplements li {{ margin-bottom: 10px; color: #4b5563; }}
    .country-nav {{
      max-width: 900px; margin: 20px auto 40px; padding: 0 40px;
      display: flex; flex-wrap: wrap; gap: 8px; justify-content: center;
    }}
    .country-nav a {{
      padding: 6px 14px; border-radius: 20px;
      background: #f0f9ff; border: 1px solid #bfdbfe;
      color: #1d4ed8; text-decoration: none;
      font-size: 0.82rem; font-weight: 600;
      transition: all 0.2s;
    }}
    .country-nav a:hover {{
      background: #1d4ed8; color: white; border-color: #1d4ed8;
    }}
    .lightbox {{
      display: none; position: fixed; z-index: 9999;
      top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(0,0,0,0.92);
      justify-content: center; align-items: center; cursor: pointer;
    }}
    .lightbox img {{ max-width: 92%; max-height: 92%; border-radius: 8px; }}
  </style>
</head>
<body>
  <div class="top-nav">
    <div class="nav-links">
      <a href="../index.html">עמוד ראשי</a>
    </div>
    <div class="nav-links">
      {"" if not prev_href else f'<a href="{prev_href}">← הקודם</a>'}
      {"" if not next_href else f'<a href="{next_href}">הבא →</a>'}
    </div>
  </div>

  <div class="hero">
    <div class="hero-text">
      <div class="meta-line">
        <span class="date-big">{day_num}</span>
        <div>
          <div class="date-details">{month_year}</div>
          <span class="country-badge">{country_name}</span>
        </div>
      </div>
      <h1 class="title">{title}</h1>
      <div class="title-divider"></div>
    </div>
    <img class="hero-map" src="../images/{map_file}" alt="{country_name}">
  </div>

  <div class="content">
{content_html}
  </div>

{nav_html}
{country_nav_html}
  <div id="lightbox" class="lightbox" onclick="this.style.display='none'">
    <img id="lightbox-img" src="" alt="">
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
    return html


def process_page(filepath, page_titles, prev_href, next_href):
    """Process a single diary entry page."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    soup = BeautifulSoup(content, "lxml")
    page_name = filepath.stem

    # Extract metadata
    date_text = extract_date_text(soup)
    subtitle = extract_subtitle(soup)
    page_title = extract_page_title(soup)
    map_file = extract_map_from_page(soup, page_name)
    country_name = get_country_name(map_file)

    # Extract content
    images = extract_images_with_captions(soup)
    paragraphs = extract_text_content(soup)

    if not paragraphs:
        print(f"  WARNING: No paragraphs found in {page_name}.html - skipping")
        return False

    # Generate new page
    new_html = build_page(
        page_name, date_text, subtitle, page_title, map_file, country_name,
        paragraphs, images, prev_href, next_href, page_titles
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_html)

    return True


def get_page_title_from_file(filepath):
    """Quick extraction of title/subtitle from a page for nav cards."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        soup = BeautifulSoup(content, "lxml")
        sub = extract_subtitle(soup)
        if sub:
            return sub
        title = extract_page_title(soup)
        if title and title != "my trip web site":
            return title
        return ""
    except:
        return ""


def main():
    entries = []
    for f in sorted(ENTRIES_DIR.glob("*.html")):
        name = f.stem
        if name.startswith(("email_", "gallery_", "test_")):
            continue
        entries.append(f)

    print(f"Processing {len(entries)} diary entry pages...")
    print()

    # Pre-build page titles map for navigation cards
    print("  Building page titles index...")
    page_titles = {}
    for filepath in entries:
        page_titles[filepath.stem] = get_page_title_from_file(filepath)
    print(f"  Indexed {len(page_titles)} page titles.\n")

    # Build navigation order (prev/next for each page)
    nav_order = [f.stem for f in entries]

    success = 0
    for i, filepath in enumerate(entries):
        try:
            prev_href = f"{nav_order[i-1]}.html" if i > 0 else None
            next_href = f"{nav_order[i+1]}.html" if i < len(nav_order) - 1 else None
            if process_page(filepath, page_titles, prev_href, next_href):
                success += 1
                print(f"  ✓ {filepath.name}")
            else:
                print(f"  ✗ {filepath.name} (skipped)")
        except Exception as e:
            print(f"  ✗ {filepath.name} ERROR: {e}")

    print(f"\nDone. Successfully converted {success}/{len(entries)} pages to V2 Magazine design.")


if __name__ == "__main__":
    main()
