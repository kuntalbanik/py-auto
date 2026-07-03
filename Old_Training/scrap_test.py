#!/usr/bin/env python3
"""
Scrape a BuiltWith Trends report into CSV.

What it does:
- fetches the report page
- extracts the table with pandas.read_html()
- streams rows to CSV
- tries to discover the next page from HTML links
- falls back to common pagination URL patterns

Usage:
    python builtwith_scrape.py \
        --url "https://trends.builtwith.com/websitelist/DataTables" \
        --out datatables.csv

Dependencies:
    pip install requests pandas beautifulsoup4 lxml
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import time
from typing import List, Optional, Tuple
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse

import pandas as pd
import requests
from bs4 import BeautifulSoup


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/146.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection": "keep-alive",
}


def fetch_html(session: requests.Session, url: str, timeout: int = 30) -> str:
    resp = session.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def extract_page_info(html: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Reads text like:
      '... Page 1 of 10489 ...'
    """
    m = re.search(r"Page\s+(\d+)\s+of\s+(\d+)", html, flags=re.IGNORECASE)
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2))


def choose_table(soup):
    tables = soup.find_all("table")
    if len(tables) < 1:
        return None
    elif len(tables) == 1:
        return tables[0]
    else:
        for i, table in enumerate(tables, start=1):
            print(f"{i}. {table.find('caption').text.strip()}")
        while True:
            choice = input("Choose a table (enter the number): ")
            try:
                table_index = int(choice) - 1
                if 0 <= table_index < len(tables):
                    return tables[table_index]
            except ValueError:
                pass
            print("Invalid input. Please enter a valid number.")

def extract_page_info(table):
    rows = table.find_all("tr")
    page_info = {}
    for row in rows:
        row_text = row.text.strip()
        if row_text.startswith("Page"):
            key, value = row_text.split(":", 1)
            page_info[key.strip()] = value.strip()
    return page_info

def discover_next_url(html, page_url, current_page):
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a")
    next_url = None
    for link in links:
        href = link.get("href")
        if href and href.startswith("/wiki/"):
            url = "[https://en.wikipedia.org](https://en.wikipedia.org)" + href
            if url != page_url:
                next_url = url
                break
    return next_url

def df_to_rows(df):
    rows = []
    for _, row in df.iterrows():
        row_data = []
        for column in df.columns:
            value = row[column]
            if isinstance(value, float) and pd.isna(value):
                value = ""
            row_data.append(str(value))
        rows.append(row_data)
    return rows

def fetch_html(url, session):
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching HTML from {url}: {e}")
        return None

def scrape(args):
    out_path = os.path.join(args.out_path, "data")
    os.makedirs(out_path, exist_ok=True)

    page_url = args.start_url
    total_pages = 0

    if args.max_pages:
        total_pages = args.max_pages
    elif ".wikibooks" in page_url:
        total_pages = 100
    elif "wiktionary" in page_url:
        total_pages = 50
    else:
        total_pages = 500

    page_count = 0
    seen_urls = set()
    session = requests.Session()
    writer = csv.writer(open(os.path.join(out_path, "data.csv"), "w", newline="")

    while True:
        if page_count >= total_pages:
            break

        page_count += 1
        print(f"Scraping page {page_count} of {total_pages} ({page_url})")

        html = fetch_html(page_url, session)
        if not html:
            break

        soup = BeautifulSoup(html, "html.parser")
        table = choose_table(soup)
        if not table:
            print("No table found in the page.")
            continue

        page_info = extract_page_info(table)
        rows = df_to_rows(pd.read_html(html)[0])

        if args.overwrite:
            seen_urls = set()
        if page_url in seen_urls:
            print("Page already scraped. Skipping...")
            continue

        seen_urls.add(page_url)

        for row in rows:
            row.extend([page_url, page_info.get("Page created", ""), page_info.get("Page updated", "")])
            writer.writerow(row)

        next_url = discover_next_url(html, page_url, page_count)
        if not next_url or next_url == page_url:
            break

        page_url = next_url

        if args.delay > 0:
            time.sleep(args.delay)

        sys.stdout.write(f"[OK] Saved page {page_count or page_count} ")
        sys.stdout.write((f"of {total_pages}" if total_pages else "") + f" -> {page_url}\n")
        sys.stdout.flush()

def main():
    parser = argparse.ArgumentParser(description="Scrape data from Wikipedia pages")
    parser.add_argument("--start-url", required=True, help="URL of the starting page")
    parser.add_argument("--out-path", default="output", help="Output directory path")
    parser.add_argument("--max-pages", type=int, help="Maximum number of pages to scrape")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing data")
    parser.add_argument("--delay", type=int, default=0, help="Delay between page requests (in seconds)")
    args = parser.parse_args()

    scrape(args)

if __name__ == "__main__":
    main()
