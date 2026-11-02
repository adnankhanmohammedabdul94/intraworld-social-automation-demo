# Social Media Automation

An AI-powered workflow that researches topics and automates social media content creation. This repository includes a demo that tests the research step using Canadian immigration data.

## Demo: IRCC Immigration Research Agent

This demo tests the automation in which an AI agent researches Canadian immigration data (IRCC: Immigration, Refugees and Citizenship Canada) and passes the findings to the social media pipeline.

### What it does

1. Takes a research topic as input, for example:
   - Express Entry draw results
   - Study permit processing times
   - Provincial Nominee Program updates
   - Canada immigration levels plan
2. Searches official and approved sources for current information.
3. Extracts and summarizes key findings (dates, CRS cut-offs, invitation numbers, fees, processing times) and keeps a source link for each.
4. Hands the results to the content generation and scheduling step.

### Data sources

- IRCC and Canada.ca immigration pages: https://www.canada.ca/en/services/immigration-citizenship.html
- IRCC processing times and Express Entry round-of-invitation pages
- Open Government Portal: https://open.canada.ca
- Provincial immigration sites (e.g. OINP, BC PNP, AAIP)

## Prerequisites

- [Python 3.10+ or Node.js 18+]
- An LLM API key
- A search API key

## Setup

```bash
git clone [your-repo-url]
cd [your-repo-name]
pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and add your keys:

```env
LLM_API_KEY=your_key_here
SEARCH_API_KEY=your_key_here
```

## Running the demo

```bash
python demo.py --topic "Express Entry draw results"
```

## Example output

```
[Paste a short sample of the agent's output here]
```

## What this demo tests

- Accuracy and freshness of retrieved data (e.g. the latest Express Entry draw)
- Whether answers come from official sources (canada.ca, open.canada.ca)
- Correct citation of source URLs and retrieval dates
- Handoff from the research step to the posting step
- Error handling and rate limits

## Limitations and disclaimer

- Canadian immigration rules, fees, draw results, and processing times change frequently. Verify all output against IRCC's official website before publishing.
- Every post draft should include a "Last verified: [date]" line.
- Output is for informational purposes only. It is not legal advice and is not a substitute for a licensed immigration consultant (RCIC) or lawyer.
- This project is not affiliated with or endorsed by IRCC or the Government of Canada.
- While testing, use a human-approval step before anything is posted publicly.

