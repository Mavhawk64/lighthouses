# src/scraper/lighthousefriends_latlong_scraper.py
from __future__ import annotations

import json
import os
import re
import time
from typing import Dict, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://www.lighthousefriends.com/"

# Input/Output paths
SCRAPER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
INPUT_FILE = os.path.join(
    SCRAPER_PATH, "..", "..", "data", "processed", "lighthousefriends.json"
)
OUTPUT_FILE = os.path.join(
    SCRAPER_PATH, "..", "..", "data", "processed", "lighthousefriends_latlongs.json"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

LATLON_REGEX = re.compile(
    r"Latitude:\s*([+-]?\d+(?:\.\d+)?)\s*,\s*Longitude:\s*([+-]?\d+(?:\.\d+)?)",
    re.IGNORECASE,
)


def make_session() -> requests.Session:
    """Requests session with simple retries."""
    s = requests.Session()
    s.headers.update(HEADERS)
    # Basic manual retry loop in fetch(); keeping session simple here.
    return s


def fetch_html(
    session: requests.Session, url: str, timeout: int = 20, retries: int = 3
) -> str:
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            r = session.get(url, timeout=timeout)
            r.raise_for_status()
            return r.text
        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(0.8 * attempt)
            else:
                raise last_err
    return ""


def parse_latlon_from_html(html: str) -> Optional[tuple[float, float]]:
    """
    Extract (lat, lon) from the Map section.
    Expected structure examples:

    <div id="Map">
      <center>
        <div class="...">
          <div class="w3-center">
            <h3>Map</h3>
            Located ...
            <br>Latitude: ##.####, Longitude: ##.#####
            <br>
          </div>
        </div>
      </center>
    </div>
    """
    soup = BeautifulSoup(html, "lxml")

    # Try to locate the Map container in a few robust ways
    map_div = soup.select_one("div#Map") or soup.find(
        "div", id=lambda v: isinstance(v, str) and v.strip() == "Map"
    )
    text_source = None

    if map_div:
        # Get compacted text from the Map section
        text_source = map_div.get_text(" ", strip=True)
    else:
        # Fallback: search entire page text if id changed
        text_source = soup.get_text(" ", strip=True)

    m = LATLON_REGEX.search(text_source)
    if not m:
        return None

    try:
        lat = float(m.group(1))
        lon = float(m.group(2))
        return lat, lon
    except ValueError:
        return None


def ensure_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def load_input(path: str) -> List[Dict[str, str]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_output(path: str, records: List[Dict]) -> None:
    ensure_dir(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def main() -> None:
    if not os.path.isfile(INPUT_FILE):
        raise FileNotFoundError(f"Input file not found: {os.path.abspath(INPUT_FILE)}")

    base_records: List[Dict[str, str]] = load_input(INPUT_FILE)
    session = make_session()

    results: List[Dict] = []
    failures: List[Dict] = []

    total = len(base_records)
    print(f"Loaded {total} records from {os.path.abspath(INPUT_FILE)}")

    for idx, rec in enumerate(base_records, start=1):
        name = rec.get("name", "").strip()
        state = rec.get("state", "").strip()
        url = rec.get("url", "").strip()

        if not url:
            print(f"[{idx}/{total}] {state} :: {name} — missing URL, skipping.")
            failures.append({**rec, "error": "missing-url"})
            continue

        full_url = url if url.startswith("http") else urljoin(BASE, url)
        print(f"[{idx}/{total}] {state} :: {name} → {full_url}")

        try:
            html = fetch_html(session, full_url)
            latlon = parse_latlon_from_html(html)
            if not latlon:
                print("  ⚠ Could not extract lat/long")
                failures.append({**rec, "error": "latlon-not-found"})
                time.sleep(0.4)
                continue

            lat, lon = latlon
            out = {
                "name": name,
                "city": rec.get("city", ""),
                "state": state,
                "url": full_url,
                "latitude": lat,
                "longitude": lon,
            }
            results.append(out)
            print(f"  ✓ lat={lat:.6f}, lon={lon:.6f}")
        except Exception as e:
            print(f"  ⚠ Error: {e}")
            failures.append({**rec, "error": str(e)[:500]})
        finally:
            # polite delay between requests
            time.sleep(0.5)

    save_output(OUTPUT_FILE, results)
    print(f"\nWrote {len(results)} records to {os.path.abspath(OUTPUT_FILE)}")

    if failures:
        # Optional: also drop a small failure log next to it
        fail_path = OUTPUT_FILE.replace(".json", "_failures.json")
        save_output(fail_path, failures)
        print(f"Logged {len(failures)} failures to {os.path.abspath(fail_path)}")


if __name__ == "__main__":
    main()
