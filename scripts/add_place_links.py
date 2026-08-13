#!/usr/bin/env python3
"""
Add place links (Google Maps + Wikipedia) to the map icon in diary entry pages.
Uses the exact URLs from diary-locations-map.md (parsed into places.json).
When the map icon is clicked, a popup appears with links.
"""

import json
import re
from pathlib import Path

ENTRIES_DIR = Path(__file__).parent.parent / "src" / "entries"
PLACES_FILE = Path(__file__).parent.parent / "src" / "_data" / "places.json"

POPUP_CSS = """
    .hero-map-wrap {
      position: relative; flex-shrink: 0; cursor: pointer;
    }
    .hero-map-wrap:hover .hero-map { opacity: 1; }
    .place-popup {
      display: none;
      position: absolute; top: 100%; left: 50%; transform: translateX(-50%);
      background: white; border: 1px solid #e5e7eb;
      border-radius: 12px; padding: 16px 20px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.15);
      min-width: 220px; z-index: 200; text-align: center;
    }
    .place-popup.show { display: block; }
    .place-popup h4 {
      font-size: 0.95rem; color: #1a1a2e; margin-bottom: 12px;
      font-weight: 700;
    }
    .place-popup .place-links {
      display: flex; gap: 10px; justify-content: center;
    }
    .place-popup .place-links a {
      display: inline-flex; align-items: center; gap: 6px;
      padding: 8px 14px; border-radius: 8px;
      font-size: 0.85rem; font-weight: 600;
      text-decoration: none; transition: background 0.2s;
    }
    .place-popup .link-maps {
      background: #dcfce7; color: #166534;
    }
    .place-popup .link-maps:hover { background: #bbf7d0; }
    .place-popup .link-wiki {
      background: #e0f2fe; color: #075985;
    }
    .place-popup .link-wiki:hover { background: #bae6fd; }
"""

POPUP_JS = """
<script>
document.addEventListener('DOMContentLoaded', function() {
  var wrap = document.querySelector('.hero-map-wrap');
  var popup = document.querySelector('.place-popup');
  if (!wrap || !popup) return;
  wrap.addEventListener('click', function(e) {
    e.stopPropagation();
    popup.classList.toggle('show');
  });
  document.addEventListener('click', function() {
    popup.classList.remove('show');
  });
});
</script>
"""


def strip_existing_popup(content):
    """Remove previously applied popup markup so we can re-apply cleanly."""
    # Remove the wrapper div, keeping just the img
    content = re.sub(
        r'<div class="hero-map-wrap">\s*(<img[^>]*class="hero-map"[^>]*>)\s*<div class="place-popup">.*?</div>\s*</div>\s*</div>',
        r'\1',
        content,
        flags=re.DOTALL
    )
    # Remove previously injected CSS
    content = re.sub(
        r'\n\s*\.hero-map-wrap \{[^}]*\}.*?\.place-popup \.link-wiki:hover \{[^}]*\}\s*\n',
        '\n',
        content,
        flags=re.DOTALL
    )
    # Remove previously injected JS
    content = re.sub(
        r'\n<script>\s*document\.addEventListener\(\'DOMContentLoaded\'.*?</script>\s*\n',
        '\n',
        content,
        flags=re.DOTALL
    )
    return content


def process_page(filepath, place_data):
    """Add place popup to map icon using exact URLs from NotebookLM."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Strip any existing popup from previous run
    content = strip_existing_popup(content)

    # Check the img exists
    img_pattern = re.compile(r'<img\s+class="hero-map"[^>]*>')
    match = img_pattern.search(content)
    if not match:
        return False

    place_name = place_data["name"]
    maps_url = place_data["maps_url"]
    wiki_url = place_data["wiki_url"]

    original_img = match.group(0)

    # Inject CSS before .hero-map {
    css_inject = POPUP_CSS
    content = content.replace("    .hero-map {", css_inject + "\n    .hero-map {", 1)

    # Replace img with wrapper + popup
    popup_html = f'''<div class="hero-map-wrap">
    {original_img}
    <div class="place-popup">
      <h4>{place_name}</h4>
      <div class="place-links">
        <a href="{maps_url}" target="_blank" class="link-maps">📍 Google Maps</a>
        <a href="{wiki_url}" target="_blank" class="link-wiki">📖 Wikipedia</a>
      </div>
    </div>
  </div>'''

    content = content.replace(original_img, popup_html, 1)

    # Add JS before </body>
    content = content.replace("</body>", POPUP_JS + "\n</body>", 1)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return True


def main():
    with open(PLACES_FILE, "r", encoding="utf-8") as f:
        places = json.load(f)

    updated = 0
    skipped = 0
    not_found = 0

    for filepath in sorted(ENTRIES_DIR.glob("*.html")):
        name = filepath.stem
        if name.startswith(("email_", "gallery_", "test_")):
            continue

        place = places.get(name)
        if not place:
            not_found += 1
            continue

        if process_page(filepath, place):
            updated += 1
        else:
            skipped += 1

    print(f"Updated: {updated} pages (with NotebookLM places)")
    print(f"Skipped (no map img): {skipped}")
    print(f"No place data: {not_found} pages")


if __name__ == "__main__":
    main()
