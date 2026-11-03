# INTRAWORLD Social Agent (Demo)

A demo pipeline that researches official IRCC updates and turns them into brand-checked social media drafts for human review.

> **Status:** demo / proof of concept. Nothing is posted automatically. Every draft goes through a pull request first.

## How it works

```
IRCC (canada.ca)  →  research_agent.py  →  research/latest.json
                                                   │
                                                   ▼
                     content/drafts/*.json  ←  make_content.py  (brand + disclaimer checks)
                                                   │
                                                   ▼
                              GitHub Action opens a Pull Request
                                                   │
                                      Human review & approval
                                                   │
                                                   ▼
                                       content/published/
```

1. **Research:** `scripts/research_agent.py` fetches an official IRCC page and extracts the summary and key points.
2. **Generate:** `scripts/make_content.py` builds LinkedIn, Instagram and X posts and validates them against the brand rules.
3. **Review:** the GitHub Action opens a PR with the draft. A person verifies the facts against the source link before merging.

## Repository structure

```
intraworld-social-agent/
├── .github/
│   └── workflows/
│       └── daily-content.yml    # scheduled workflow (weekdays, 09:00 IST)
├── scripts/
│   ├── research_agent.py        # fetches IRCC page → research/latest.json
│   └── make_content.py          # research → branded draft JSON
├── research/
│   └── latest.json              # latest agent output
├── content/
│   ├── drafts/                  # new items awaiting review
│   └── published/               # approved and posted items
├── brand/
│   └── brand.json               # wordmark, contact, palette, disclaimer
├── requirements.txt
└── README.md
```

## Brand rules

All rules live in `brand/brand.json` and are enforced by `make_content.py`.

| Rule | Value |
|------|-------|
| Wordmark | INTRAWORLD |
| Palette | Navy `#0B1F3A`, Crimson `#B3122E`, Gold `#C9A227`, Slate `#5B6770` |
| Contact | Hannan |
| Disclaimer | General information only, not legal advice. |
| Forbidden names | Listed in `brand.json`; any match fails validation |
| Sources | Official `canada.ca` pages only |

A draft fails validation (exit code 1) if it is missing the disclaimer, omits the contact on LinkedIn, uses an off-palette color, exceeds 280 characters on X, contains a forbidden name, or cites a non-official source. A failed validation stops the workflow before any PR is created.

## Getting started

**Requirements:** Python 3.12+

```bash
git clone <your-repo-url>
cd intraworld-social-agent
pip install -r requirements.txt

# 1. Research
python scripts/research_agent.py

# 2. Generate a draft
python scripts/make_content.py research/latest.json
```

The draft is written to `content/drafts/YYYY-MM-DD-<topic>.json`.

To research a specific source, use `python scripts/research_agent.py --index 1`. The sources are defined in the `SOURCES` list in `research_agent.py`.

## GitHub Actions setup

1. Go to **Settings → Actions → General → Workflow permissions**.
2. Select **Read and write permissions**.
3. Tick **Allow GitHub Actions to create and approve pull requests**.

The workflow runs on weekdays at 03:30 UTC (09:00 IST). You can also trigger it manually from the **Actions** tab with **Run workflow**.

## Content file format

Each draft in `content/drafts/` is JSON:

```json
{
  "date": "2026-10-13",
  "topic": "...",
  "source": { "name": "IRCC", "url": "...", "published": "..." },
  "brand": { "wordmark": "INTRAWORLD", "palette": {}, "contact": "Hannan" },
  "disclaimer": "General information only, not legal advice.",
  "posts": {
    "linkedin":  { "text": "..." },
    "instagram": { "text": "...", "visual": {} },
    "x":         { "text": "..." }
  },
  "status": "draft"
}
```

`status` moves from `draft` to `published` when the file is moved to `content/published/`.

## Review checklist (before merging a PR)

- [ ] Every fact matches the linked IRCC page
- [ ] Figures, dates and deadlines are current
- [ ] Disclaimer present on all three posts
- [ ] Wording is general information, not advice
- [ ] Visual spec uses brand colors only

## Known limitations

- Page extraction uses simple HTML parsing. If IRCC changes a page layout, the agent exits with an error rather than producing a draft.
- Source topics are a fixed demo list, not a live feed of IRCC news.
- No automatic posting yet. Approved drafts are moved to `published/` and posted manually.

## Roadmap

- [ ] Use an LLM to summarize fetched pages instead of HTML parsing
- [ ] Script to move approved drafts to `content/published/`
- [ ] Image rendering from the `visual` spec
- [ ] Posting integrations for LinkedIn, Instagram and X
- [ ] Scheduled check for IRCC page changes

## Disclaimer

General information only, not legal advice.s only. It is not legal advice and is not a substitute for a licensed immigration consultant (RCIC) or lawyer.
- This project is not affiliated with or endorsed by IRCC or the Government of Canada.
- While testing, use a human-approval step before anything is posted publicly.

