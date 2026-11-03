#!/usr/bin/env python3
"""
research_agent.py
Demo research agent: fetches an official IRCC page (canada.ca) and writes
research/latest.json for make_content.py.

Usage:
    python scripts/research_agent.py
    python scripts/research_agent.py --index 1     # pick a specific source
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

BASE = "https://www.canada.ca/en/immigration-refugees-citizenship"
SOURCES = [
    {
        "topic": "Express Entry draw update",
        "url": f"{BASE}/corporate/mandate/policies-operational-instructions-agreements/"
               "ministerial-instructions/express-entry-rounds.html",
    },
    {
        "topic": "Study permit update for international students",
        "url": f"{BASE}/services/study-canada/study-permit.html",
    },
    {
        "topic": "Post-Graduation Work Permit reminder",
        "url": f"{BASE}/services/study-canada/work/after-graduation.html",
    },
]
HEADERS = {"User-Agent": "intraworld-social-agent/0.1 (demo research bot)"}


def pick_source(index):
    if index is None:
        index = date.today().timetuple().tm_yday % len(SOURCES)  # rotate daily
    return SOURCES[index]


def fetch(url: str) -> BeautifulSoup:
    host = urlparse(url).netloc
    if not host.endswith("canada.ca"):
        sys.exit(f"refusing non-official source: {host}")
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def extract(soup: BeautifulSoup) -> dict:
    meta = soup.find("meta", attrs={"name": "description"})
    summary = meta["content"].strip() if meta and meta.get("content") else ""

    modified = soup.find("time", attrs={"property": "dateModified"})
    published = modified.get_text(strip=True) if modified else None

    main = soup.find("main") or soup
    points = []
    for li in main.find_all("li"):
        text = " ".join(li.get_text(" ", strip=True).split())
        if 25 <= len(text) <= 140 and text not in points:
            points.append(text)
        if len(points) == 3:
            break
    return {"summary": summary, "published": published, "key_points": points}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", type=int, default=None)
    ap.add_argument("--out", type=Path, default=Path("research/latest.json"))
    args = ap.parse_args()

    src = pick_source(args.index)
    found = extract(fetch(src["url"]))
    if not found["key_points"]:
        sys.exit("no usable key points found; page layout may have changed")

    result = {
        "topic": src["topic"],
        "source_url": src["url"],
        "summary": found["summary"] or f"IRCC has updated its {src['topic'].lower()} page.",
        "published": found["published"] or date.today().isoformat(),
        "key_points": found["key_points"],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
