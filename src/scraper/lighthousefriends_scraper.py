# src/scraper/lighthousefriends_scraper.py
from __future__ import annotations

import json
import os
import time
from typing import Dict, List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://www.lighthousefriends.com/"
STATE_URL = BASE + "pull-state.asp?state={code}"

# Output path (per your request)
SCRAPER_PATH = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(SCRAPER_PATH, "..", "..", "data", "processed", "lighthousefriends.json")

# 50 states + DC (adjust if you want territories too)
STATE_CODES = [
    "AL","AK","AZ","AR","CA","CO","CT","DE","DC","FL",
    "GA","HI","ID","IL","IN","IA","KS","KY","LA","ME",
    "MD","MA","MI","MN","MS","MO","MT","NE","NV","NH",
    "NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI",
    "SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def fetch_html(url: str, timeout: int = 20) -> str:
    r = requests.get(url, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    return r.text

def parse_state(html: str, state_code: str) -> List[Dict[str, str]]:
    """
    Parse one state's page and return a list of dicts:
      {"name": "...", "city": "CITY", "state": "ST", "url": "https://..."}
    """
    soup = BeautifulSoup(html, "lxml")

    # The page structure you described:
    # <div id="Light List"><center><div class="w3-row"> ... </div></center></div>
    # Note: id has a space ("Light List"), so we match it exactly.
    container = soup.select_one('div[id="Light List"]')
    if not container:
        # Fallbacks if they tweak markup
        container = soup.select_one('div#Light\\ List') or soup.find("div", id=lambda v: v and v.strip() == "Light List")
    if not container:
        return []

    data: List[Dict[str, str]] = []

    # Each lighthouse is an <a> inside a .w3-row under the container
    # Often multiple rows: iterate all .w3-row, then anchor tags
    rows = container.select("div.w3-row")
    if not rows:
        # Sometimes the <a> might be nested differently—fallback to any anchors inside the container
        rows = [container]

    for row in rows:
        for a in row.select("a[href]"):
            href = a.get("href", "").strip()
            if not href:
                continue
            full_url = urljoin(BASE, href)

            # Inside <a>, there should be two <span>: NAME and "Location, ST"
            spans = a.find_all("span")
            if len(spans) < 2:
                # Skip if unexpected structure
                continue

            name = spans[0].get_text(strip=True)

            loc = spans[1].get_text(" ", strip=True)
            # Expect "City, ST" (sometimes City may have extra spaces)
            city, st = _split_city_state(loc, fallback_state=state_code)

            data.append({
                "name": name,
                "city": city,
                "state": st,
                "url": full_url,
            })

    return data

def _split_city_state(loc_text: str, fallback_state: str) -> tuple[str, str]:
    """
    Split strings like "Mobile, AL" -> ("Mobile", "AL").
    If the state code is missing, use the fallback provided by the query.
    """
    parts = [p.strip() for p in loc_text.split(",")]
    if len(parts) >= 2:
        city = ",".join(parts[:-1]).strip()  # join back in case city also had a comma
        st = parts[-1].strip()
        # Normalize common edge cases
        if len(st) == 2 and st.isalpha():
            st = st.upper()
        return city, st
    else:
        return loc_text.strip(), fallback_state

def scrape_all_states(state_codes: List[str]) -> List[Dict[str, str]]:
    all_items: List[Dict[str, str]] = []
    for idx, code in enumerate(state_codes, start=1):
        url = STATE_URL.format(code=code)
        print(f"[{idx}/{len(state_codes)}] Scraping state: {code} → {url}")
        try:
            html = fetch_html(url)
            items = parse_state(html, state_code=code)
            print(f"  ✓ Found {len(items)} lighthouses in {code}")
            all_items.extend(items)
            time.sleep(0.5)  # polite delay
        except Exception as e:
            print(f"  ⚠ [WARN] Failed to scrape {code}: {e}")
    return all_items


def ensure_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)

def main() -> None:
    results = scrape_all_states(STATE_CODES)
    ensure_dir(output_file)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(results)} records to {os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()
