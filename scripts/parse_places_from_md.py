#!/usr/bin/env python3
"""
Parse diary-locations-map.md (from NotebookLM) and rebuild places.json
with the proper place names, Google Maps URLs, and Wikipedia URLs.
Then re-apply the map icon popups on all pages.
"""

import json
import re
from pathlib import Path

MD_FILE = Path(__file__).parent.parent / "diary-locations-map.md"
PLACES_FILE = Path(__file__).parent.parent / "src" / "_data" / "places.json"
ENTRIES_DIR = Path(__file__).parent.parent / "src" / "entries"


def parse_date_to_filestem(date_str):
    """
    Convert date strings like "5.10 11:00", "7.10", "8.10.01", "1.1 18:30"
    to file stems like "200110051100", "20011007", "20011008", "20020101".
    """
    date_str = date_str.strip().strip("*")
    
    # Split date and time
    parts = date_str.split()
    date_part = parts[0]
    time_part = parts[1] if len(parts) > 1 else None
    # Handle "2.1 13:00 / 23:45" - take first time
    if time_part and "/" in time_part:
        time_part = None
    if len(parts) > 2 and parts[1] == "/":
        time_part = None
    
    # Parse date: "5.10", "8.10.01", "1.1"
    date_components = date_part.split(".")
    day = int(date_components[0])
    month = int(date_components[1])
    
    # Determine year: Oct-Dec = 2001, Jan-Sep = 2002
    if month >= 10:
        year = 2001
    else:
        year = 2002
    
    # Build file stem
    stem = f"{year}{month:02d}{day:02d}"
    
    if time_part and ":" in time_part:
        h, m = time_part.split(":")
        stem += f"{int(h):02d}{int(m):02d}"
    
    return stem


def parse_markdown_table():
    """Parse the markdown table and extract place data."""
    with open(MD_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    places = {}
    
    # Match table rows: | date | place_he | maps_link | wiki_link |
    row_pattern = re.compile(
        r'\|\s*\*\*([^*]+)\*\*\s*\|'   # date
        r'\s*([^|]+)\|'                  # place name (Hebrew)
        r'\s*\[.*?\]\((https://www\.google\.com/maps/[^)]+)\)\s*\|'  # maps URL
        r'\s*\[.*?\]\(([^)]+)\)\s*\|'   # wiki URL
    )
    
    for match in row_pattern.finditer(content):
        date_str = match.group(1).strip()
        place_he = match.group(2).strip()
        maps_url = match.group(3).strip()
        wiki_url = match.group(4).strip()
        
        stem = parse_date_to_filestem(date_str)
        
        places[stem] = {
            "name": place_he,
            "maps_url": maps_url,
            "wiki_url": wiki_url
        }
    
    return places


def match_to_files(places):
    """Match parsed places to actual entry files using flexible date matching."""
    actual_files = set()
    for f in ENTRIES_DIR.glob("*.html"):
        if not f.stem.startswith(("email_", "gallery_", "test_")):
            actual_files.add(f.stem)
    
    matched = {}
    unmatched_places = []
    
    for stem, data in places.items():
        if stem in actual_files:
            # Exact match (with time)
            matched[stem] = data
        else:
            # Try date-only (first 8 chars) - find a file that starts with this date
            date_only = stem[:8]
            if date_only in actual_files:
                # Only set if not already matched by a better entry
                if date_only not in matched:
                    matched[date_only] = data
            else:
                unmatched_places.append((stem, data["name"]))
    
    # Find files still unmatched
    unmatched_files = []
    for f in sorted(actual_files):
        if f not in matched:
            # Check if a timestamped version matched
            found = False
            for m in matched:
                if m.startswith(f) or f.startswith(m[:8]):
                    found = True
                    break
            if not found:
                unmatched_files.append(f)
    
    return matched, unmatched_places, unmatched_files


def main():
    print("Parsing diary-locations-map.md...")
    places = parse_markdown_table()
    print(f"Parsed {len(places)} entries from markdown")
    
    matched, unmatched_places, unmatched_files = match_to_files(places)
    print(f"Matched to files: {len(matched)}")
    
    if unmatched_places:
        print(f"\nPlaces that didn't match a file ({len(unmatched_places)}):")
        for stem, name in unmatched_places[:15]:
            print(f"  {stem} -> {name}")
    
    if unmatched_files:
        print(f"\nFiles without a place ({len(unmatched_files)}):")
        for f in unmatched_files[:15]:
            print(f"  {f}")
    
    # Save the matched places
    PLACES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PLACES_FILE, "w", encoding="utf-8") as f:
        json.dump(matched, f, ensure_ascii=False, indent=2)
    
    print(f"\nSaved {len(matched)} places to {PLACES_FILE}")


if __name__ == "__main__":
    main()
