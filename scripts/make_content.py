#!/usr/bin/env python3
"""
make_content.py
Turns research/latest.json into a brand-checked draft in content/drafts/.

Usage:
    python scripts/make_content.py research/latest.json
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

BRAND = json.loads(Path("brand/brand.json").read_text(encoding="utf-8"))
DISCLAIMER = BRAND["disclaimer"]
X_LIMIT = 280


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:50]


def load_research(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in ("topic", "source_url", "summary", "key_points"):
        if not data.get(key):
            sys.exit(f"research file missing required field: {key}")
    return data


def visual_spec(r: dict) -> dict:
    c = BRAND["palette"]
    return {
        "background": c["navy"],
        "headline_color": c["gold"],
        "accent": c["crimson"],
        "body_color": c["slate"],
        "wordmark": BRAND["wordmark"],
        "headline": r["topic"],
    }


def build_posts(r: dict) -> dict:
    points = r["key_points"][:3]
    bullets = "\n".join(f"• {p}" for p in points)
    contact = f"Questions? Contact {BRAND['contact']} at {BRAND['wordmark']}."

    linkedin = (f"{r['topic']}\n\n{r['summary']}\n\n{bullets}\n\n"
                f"Source: {r['source_url']}\n\n{contact}\n\n{DISCLAIMER}")
    instagram = (f"{r['topic']}\n\n{bullets}\n\n{contact}\n\n{DISCLAIMER}\n\n"
                 "#CanadaImmigration #IRCC #StudyInCanada")

    # X: trim the first point so the whole post fits in 280 characters
    fixed = f"{r['topic']}: \n\n{r['source_url']}\n\n{DISCLAIMER}"
    room = max(X_LIMIT - len(fixed), 0)
    point = points[0] if len(points[0]) <= room else points[0][: max(room - 1, 0)].rstrip() + "…"
    x_post = f"{r['topic']}: {point}\n\n{r['source_url']}\n\n{DISCLAIMER}"

    return {
        "linkedin": {"text": linkedin},
        "instagram": {"text": instagram, "visual": visual_spec(r)},
        "x": {"text": x_post},
    }


def validate(content: dict) -> list[str]:
    errors = []
    blob = json.dumps(content, ensure_ascii=False).lower()
    for name in BRAND["forbidden_names"]:
        if name.lower() in blob:
            errors.append(f"forbidden name found: {name}")

    host = urlparse(content["source"]["url"]).netloc.lower()
    if not host.endswith("canada.ca"):
        errors.append(f"source is not an official domain: {host}")

    for platform, post in content["posts"].items():
        if DISCLAIMER not in post["text"]:
            errors.append(f"{platform}: disclaimer missing")
    if len(content["posts"]["x"]["text"]) > X_LIMIT:
        errors.append("x: post exceeds 280 characters")
    if BRAND["contact"] not in content["posts"]["linkedin"]["text"]:
        errors.append("linkedin: contact missing")

    allowed = {v.lower() for v in BRAND["palette"].values()}
    for k, v in content["posts"]["instagram"]["visual"].items():
        if isinstance(v, str) and v.startswith("#") and v.lower() not in allowed:
            errors.append(f"off-brand color in visual.{k}: {v}")
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("research", type=Path)
    ap.add_argument("--out", type=Path, default=Path("content/drafts"))
    args = ap.parse_args()

    r = load_research(args.research)
    content = {
        "date": date.today().isoformat(),
        "topic": r["topic"],
        "source": {"name": "IRCC", "url": r["source_url"], "published": r.get("published")},
        "brand": {"wordmark": BRAND["wordmark"], "palette": BRAND["palette"],
                  "contact": BRAND["contact"]},
        "disclaimer": DISCLAIMER,
        "posts": build_posts(r),
        "status": "draft",
    }

    errors = validate(content)
    if errors:
        print("Validation failed:\n - " + "\n - ".join(errors), file=sys.stderr)
        sys.exit(1)

    args.out.mkdir(parents=True, exist_ok=True)
    out = args.out / f"{content['date']}-{slugify(r['topic'])}.json"
    out.write_text(json.dumps(content, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
