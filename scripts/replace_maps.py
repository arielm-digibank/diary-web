#!/usr/bin/env python3
"""
Replace generic country map icons with detailed maps based on the plan.
"""

import re
from pathlib import Path

ENTRIES_DIR = Path(__file__).parent.parent / "src" / "entries"

# Annapurna Circuit day maps (trek started Nov 15, 2001)
ANNAPURNA_MAPS = {
    "20011115": "anaporna_day_1.jpg",
    "20011117": "anaporna_day_3.jpg",
    "20011118": "anaporna_day_4.jpg",
    "20011119": "anaporna_day_5.jpg",
    "20011120": "anaporna_day_6.jpg",
    "20011121": "anaporna_day_7.jpg",
    "20011123": "anaporna_day_9.jpg",
    "20011124": "anaporna_day_10.jpg",
    "20011125": "anaporna_day_11.jpg",
    "20011127": "anaporna_day_13.jpg",
    "20011128": "anaporna_day_14.jpg",
}

# Little 3-day trek (Nov 13-14)
LITTLE_TREK_MAPS = {
    "20011113": "little_trek_map1.jpg",
    "20011114": "little_trek_map2.jpg",
}

# New Zealand South Island pages
NZ_SOUTH_ISLAND = [
    "20020210", "20020211", "20020212", "20020213", "20020215",
    "20020216", "20020218", "20020219", "20020220", "200202202030",
    "20020221", "20020223", "20020224", "20020226", "20020227",
    "20020228", "20020301", "20020303", "20020304", "20020306",
    "20020308", "20020310", "20020311", "20020312", "20020315",
    "20020317", "20020318", "20020320", "20020321", "20020322",
    "20020323", "20020324",
]

# New Zealand North Island pages
NZ_NORTH_ISLAND = [
    "200203280100", "200203282130", "20020330", "20020331",
    "20020402", "20020403", "20020405", "20020406", "20020408",
    "200204082300", "20020409", "20020410", "20020412", "20020413",
    "20020414", "20020416", "20020418", "20020420", "20020421",
    "20020423", "20020425", "20020427", "20020428", "20020430",
    "20020505", "200205050515",
]

# NZ date-specific maps (override south island for these)
NZ_SPECIFIC = {
    "20020224": "20020224_otago.jpg",
    "20020226": "20020226_east_catlins.jpg",
    "20020227": "20020227_east_catlins.jpg",
    "20020306": "20020306_wanaka_map.jpg",
}

# Thailand - Bangkok
THAILAND_BANGKOK = ["20011210", "20011211", "20011213", "20011214"]
THAILAND_BANGKOK2 = ["20020104", "20020107", "20020202"]

# Thailand - Islands
THAILAND_ISLANDS = [
    "20011215", "20011216", "20011218", "20011220", "20011222",
    "20011223", "20011224", "20011226", "20011230",
    "20020101", "20020102",
]

# Thailand - North
THAILAND_NORTH = ["20020123", "20020126", "20020127", "20020128", "20020129", "20020131"]

# Laos
LAOS_PAGES = [
    "20020108", "20020109", "20020110", "20020111", "20020112",
    "20020113", "20020114", "20020115", "20020116", "20020118",
    "20020119", "20020121", "20020122",
]

# Cambodia
CAMBODIA_PAGES = ["20020601", "200206012100", "20020603", "20020604", "20020605", "20020606"]

# Philippines
PHILIPPINES_PAGES = [
    "20020506", "20020507", "20020508", "20020510", "20020512",
    "200205122100", "20020513", "20020514", "20020515", "20020516",
    "20020517", "20020518", "20020519", "20020520", "20020522",
    "20020524", "20020526", "20020528", "20020530", "200205300800",
    "200205310915", "200205312115",
]


def replace_map(filepath, new_map_filename):
    """Replace the hero-map img src with a new map file."""
    content = filepath.read_text(encoding="utf-8")

    # Match the hero-map img tag and replace its src
    pattern = r'(<img\s+class="hero-map"\s+src=")([^"]+)(")'
    match = re.search(pattern, content)
    if not match:
        return False

    old_src = match.group(2)
    new_src = f"../images/{new_map_filename}"

    if old_src == new_src:
        return False

    content = content.replace(old_src, new_src, 1)
    filepath.write_text(content, encoding="utf-8")
    return True


def main():
    updated = 0

    # Build full mapping
    mapping = {}

    for page, mapfile in ANNAPURNA_MAPS.items():
        mapping[page] = mapfile
    for page, mapfile in LITTLE_TREK_MAPS.items():
        mapping[page] = mapfile
    for page in NZ_SOUTH_ISLAND:
        mapping[page] = "New_Zealand_south_island.gif"
    for page in NZ_NORTH_ISLAND:
        mapping[page] = "New_Zealand_north_island.gif"
    for page, mapfile in NZ_SPECIFIC.items():
        mapping[page] = mapfile  # Override south island
    for page in THAILAND_BANGKOK:
        mapping[page] = "bangkok_map_highlighted.jpg"
    for page in THAILAND_BANGKOK2:
        mapping[page] = "bangkok_map_highlighted2.jpg"
    for page in THAILAND_ISLANDS:
        mapping[page] = "3_islands_map.jpg"
    for page in THAILAND_NORTH:
        mapping[page] = "north_thailand_highlighted.jpg"
    for page in LAOS_PAGES:
        mapping[page] = "laos_map_highlighted.jpg"
    for page in CAMBODIA_PAGES:
        mapping[page] = "angkor_map_highlighted.jpg"
    for page in PHILIPPINES_PAGES:
        mapping[page] = "central_islands_highlighted.jpg"

    for page, mapfile in sorted(mapping.items()):
        filepath = ENTRIES_DIR / f"{page}.html"
        if not filepath.exists():
            print(f"  SKIP (no file): {page}")
            continue
        if replace_map(filepath, mapfile):
            updated += 1
        else:
            print(f"  SKIP (no hero-map or same): {page}")

    print(f"\nUpdated {updated} pages with detailed maps.")


if __name__ == "__main__":
    main()
