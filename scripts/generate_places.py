#!/usr/bin/env python3
"""
Generate a JSON mapping of page_name -> { place_en, place_he }
based on page titles, subtitles, and known route.
Then update pages to make the map icon clickable with Google Maps + Wikipedia links.
"""

import json
import re
import os
from pathlib import Path
from bs4 import BeautifulSoup

ENTRIES_DIR = Path(__file__).parent.parent / "src" / "entries"
PLACES_FILE = Path(__file__).parent.parent / "src" / "_data" / "places.json"

# Known places mapping from Hebrew titles to English names for Maps/Wikipedia
PLACE_KEYWORDS = {
    "ניו דלהי": "New Delhi, India",
    "ניו-דלהי": "New Delhi, India",
    "main bazar": "Paharganj, New Delhi",
    "טאג' מאהאל": "Taj Mahal, Agra",
    "אגרה": "Agra, India",
    "ג'איפור": "Jaipur, India",
    "ג'ודפור": "Jodhpur, India",
    "אודייפור": "Udaipur, India",
    "פושקאר": "Pushkar, India",
    "ואראנסי": "Varanasi, India",
    "גואה": "Goa, India",
    "מנאלי": "Manali, India",
    "דרמסאלה": "Dharamshala, India",
    "מקלאוד גנג'": "McLeod Ganj, India",
    "ריישיקש": "Rishikesh, India",
    "רישיקש": "Rishikesh, India",
    "קאסול": "Kasol, India",
    "צ'לאל": "Chalal, India",
    "מאלאנה": "Malana, India",
    "קירגנגה": "Kheerganga, India",
    "שימלה": "Shimla, India",
    "אמריצר": "Amritsar, India",
    "בודגאיה": "Bodh Gaya, India",
    "קטמנדו": "Kathmandu, Nepal",
    "פוקהרה": "Pokhara, Nepal",
    "אנאפורנה": "Annapurna, Nepal",
    "בארדייה": "Bardia National Park, Nepal",
    "לומביני": "Lumbini, Nepal",
    "נגרקוט": "Nagarkot, Nepal",
    "בנגקוק": "Bangkok, Thailand",
    "קו פאנגן": "Koh Phangan, Thailand",
    "קו סמוי": "Koh Samui, Thailand",
    "צ'אנג מאי": "Chiang Mai, Thailand",
    "צ'אנג ראי": "Chiang Rai, Thailand",
    "קראבי": "Krabi, Thailand",
    "קו פי פי": "Koh Phi Phi, Thailand",
    "ויאנג ויאנג": "Vang Vieng, Laos",
    "לואנג פראבנג": "Luang Prabang, Laos",
    "ויינטיאן": "Vientiane, Laos",
    "סידני": "Sydney, Australia",
    "מלבורן": "Melbourne, Australia",
    "קיירנס": "Cairns, Australia",
    "אוקלנד": "Auckland, New Zealand",
    "קווינסטאון": "Queenstown, New Zealand",
    "מילפורד סאונד": "Milford Sound, New Zealand",
    "רוטורואה": "Rotorua, New Zealand",
    "דנידין": "Dunedin, New Zealand",
    "כריסטצ'רץ'": "Christchurch, New Zealand",
    "פינגווין": "Dunedin, New Zealand",
    "וואנאקה": "Wanaka, New Zealand",
    "פרנץ ג'וזף": "Franz Josef Glacier, New Zealand",
    "אבל טסמן": "Abel Tasman, New Zealand",
    "טונגרירו": "Tongariro, New Zealand",
    "מנילה": "Manila, Philippines",
    "בורקאי": "Boracay, Philippines",
    "אל נידו": "El Nido, Philippines",
    "פלאוואן": "Palawan, Philippines",
    "סיאם ריפ": "Siem Reap, Cambodia",
    "אנגקור ואט": "Angkor Wat, Cambodia",
    "פנום פן": "Phnom Penh, Cambodia",
    "קופנהגן": "Copenhagen, Denmark",
    "דנמרק": "Copenhagen, Denmark",
    "טריאונד": "Triund Hill, Dharamshala",
    "סרנקוט": "Sarangkot, Nepal",
    "דאמפוס": "Dhampus, Nepal",
    "מוקטינאת": "Muktinath, Nepal",
    "מארפה": "Marpha, Nepal",
    "טאטאפאני": "Tatopani, Nepal",
    "מאנאנג": "Manang, Nepal",
    "ת'ורונג": "Thorong La Pass, Nepal",
    "פיסאנג": "Pisang, Nepal",
    "צ'אמה": "Chame, Nepal",
    "ג'ומסום": "Jomsom, Nepal",
}

# Default places by date range (fallback)
DATE_RANGE_PLACES = [
    ("20011005", "20011006", "Copenhagen, Denmark"),
    ("20011006", "20011010", "New Delhi, India"),
    ("20011010", "20011013", "Agra, India"),
    ("20011013", "20011020", "Dharamshala, India"),
    ("20011020", "20011026", "Kasol, India"),
    ("20011026", "20011030", "Rishikesh, India"),
    ("20011030", "20011104", "Kathmandu, Nepal"),
    ("20011104", "20011114", "Bardia National Park, Nepal"),
    ("20011115", "20011128", "Annapurna Circuit, Nepal"),
    ("20011128", "20011201", "Pokhara, Nepal"),
    ("20011201", "20011210", "Kathmandu, Nepal"),
    ("20011210", "20011224", "Bangkok, Thailand"),
    ("20011224", "20020108", "Koh Phangan, Thailand"),
    ("20020108", "20020123", "Luang Prabang, Laos"),
    ("20020123", "20020203", "Chiang Mai, Thailand"),
    ("20020203", "20020210", "Sydney, Australia"),
    ("20020210", "20020326", "South Island, New Zealand"),
    ("20020326", "20020505", "North Island, New Zealand"),
    ("20020506", "20020601", "Philippines"),
    ("20020601", "20020701", "Siem Reap, Cambodia"),
]


def find_place_from_title(title):
    """Find place from page title using keyword matching."""
    if not title:
        return None
    for keyword, place_en in PLACE_KEYWORDS.items():
        if keyword in title:
            return place_en
    return None


def find_place_from_date(page_name):
    """Fallback: find place from date range."""
    date_str = page_name[:8]
    for start, end, place in DATE_RANGE_PLACES:
        if start <= date_str < end:
            return place
    return None


def extract_title_from_page(filepath):
    """Extract subtitle/title from the page."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    soup = BeautifulSoup(content, "lxml")

    # Try marquee tags (original format)
    marquees = soup.find_all("marquee")
    if len(marquees) >= 2:
        return marquees[1].get_text(strip=True)

    # Try title-text subtitle
    sub = soup.find("span", class_="title-text subtitle")
    if sub:
        return sub.get_text(strip=True)

    # Try page <title>
    title_tag = soup.find("title")
    if title_tag:
        text = title_tag.get_text(strip=True)
        if text != "my trip web site":
            return text

    return ""


def build_places_map():
    """Build the complete places mapping."""
    places = {}

    for filepath in sorted(ENTRIES_DIR.glob("*.html")):
        name = filepath.stem
        if name.startswith(("email_", "gallery_", "test_")):
            continue

        title = extract_title_from_page(filepath)
        place = find_place_from_title(title)

        if not place:
            # Try the <title> tag too
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            soup = BeautifulSoup(content, "lxml")
            page_title = soup.find("title")
            if page_title:
                place = find_place_from_title(page_title.get_text(strip=True))

        if not place:
            place = find_place_from_date(name)

        if place:
            places[name] = place

    return places


def main():
    print("Building places map from page titles and date ranges...")
    places = build_places_map()

    # Ensure _data directory exists
    PLACES_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(PLACES_FILE, "w", encoding="utf-8") as f:
        json.dump(places, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(places)} place mappings -> {PLACES_FILE}")
    print("\nSample entries:")
    for key in list(places.keys())[:10]:
        print(f"  {key}: {places[key]}")


if __name__ == "__main__":
    main()
