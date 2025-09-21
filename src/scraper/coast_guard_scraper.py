# src/scraper/coast_guard_scraper.py
from __future__ import annotations

import os
import sys
from typing import List, Optional

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BROWSER_HEADERS = {
    # A realistic desktop Chrome UA
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    # Some sites expect a same-origin-ish Referer; set to the section root
    "Referer": "https://www.history.uscg.mil/",
}

def make_session() -> requests.Session:
    sess = requests.Session()
    sess.headers.update(BROWSER_HEADERS)

    # Robust retries for transient blocks
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=0.6,
        status_forcelist=(403, 408, 429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "HEAD"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
    sess.mount("http://", adapter)
    sess.mount("https://", adapter)
    return sess

def fetch_html(url: str, timeout: int = 25) -> str:
    sess = make_session()
    r = sess.get(url, timeout=timeout)
    # Some CDNs send 200 with a block page—quick heuristic to catch that:
    if r.status_code == 403 or ("Access Denied" in r.text and "Akamai" in r.text):
        raise requests.HTTPError(f"403 from requests for {url}", response=r)
    r.raise_for_status()
    return r.text

def parse_paragraphs(html: str) -> List[str]:
    soup = BeautifulSoup(html, "lxml")
    container = soup.find(id="dnn_ctr22881_HtmlModule_lblContent")
    if not container:
        # Try a looser fallback selector in case the id shifts
        container = soup.select_one("div[id*=HtmlModule_lblContent], div.DNNModuleContent")
    if not container:
        raise RuntimeError("Content container not found.")
    out: List[str] = []
    for p in container.find_all("p"):
        txt = p.get_text(" ", strip=True)
        if txt:
            out.append(txt)
    return out

def scrape_paragraphs(url: str) -> List[str]:
    try:
        html = fetch_html(url)
        return parse_paragraphs(html)
    except requests.HTTPError as e:
        # 403 or other hard block: try Playwright if present
        if e.response is not None and e.response.status_code == 403:
            try:
                return scrape_with_playwright(url)
            except ModuleNotFoundError:
                raise RuntimeError(
                    "Got 403 and Playwright is not installed. Install with:\n"
                    "  pip install playwright && playwright install"
                ) from e
        raise

def scrape_with_playwright(url: str) -> List[str]:
    # Lazy import so the dependency is optional
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            # Default viewport & UA are already realistic; can set geolocation/timezone if needed
            user_agent=BROWSER_HEADERS["User-Agent"],
            locale="en-US",
        )
        page = ctx.new_page()
        # Being a good citizen: small delay and direct navigation
        page.goto(url, wait_until="domcontentloaded", timeout=45000)
        # If content hydrates late, wait for the container to exist
        page.wait_for_selector("#dnn_ctr22881_HtmlModule_lblContent, div[id*=HtmlModule_lblContent], .DNNModuleContent", timeout=45000)
        html = page.content()
        browser.close()
    return parse_paragraphs(html)

if __name__ == "__main__":
    url = "https://www.history.uscg.mil/Browse-by-Topic/Assets/Land/All/Lighthouses/"
    paras = scrape_paragraphs(url)
    SCRAPER_PATH = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(SCRAPER_PATH,'..','..','data','raw','lighthouses_uscg.txt')
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, t in enumerate(paras, 1):
            f.write(f"{i:03}: {t}\n")
    print(f"Saved {len(paras)} paragraphs to {output_file}\n")
    for i, t in enumerate(paras, 1):
        print(f"{i:03}: {t}")
