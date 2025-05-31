# Dutch Public Domain Texts: Rechtspraak Sync

This repository contains a GitHub Action to fetch, scrub, and upload Dutch court rulings from the [Rechtspraak](https://www.rechtspraak.nl) open data feed to the [Hugging Face Hub](https://huggingface.co/).

## Dataset Target

All data is pushed to the shared dataset:
**[`vGassen/dutch-public-domain-texts`](https://huggingface.co/datasets/vGassen/dutch-public-domain-texts)**

Each record contains:
- `url`: Canonical Rechtspraak link
- `content`: Lightly scrubbed ruling text
- `source`: Always set to `"Rechtspraak"`

## Structure

- `rechtspraak_sync.py`: Python script for fetching and uploading court rulings.
- `rechtspraak_sync.yml`: GitHub Actions workflow for automated sync.
- `requirements.txt`: Python dependencies.
- `judge_names.json`: List of known judge names used for redaction (you must add this manually).

## Setup

1. Clone this repository.
2. Add your `judge_names.json` file (UTF-8 encoded).
3. Add a GitHub Secret:
   - `HF_TOKEN`: your Hugging Face write token.

## Running Locally

```bash
pip install -r requirements.txt
export HF_TOKEN=your_token_here
python rechtspraak_sync.py
```

## Running in GitHub Actions

The sync runs automatically every 3 hours via cron. You can also trigger it manually from the Actions tab.

## License

This repo contains only public domain legal content. Scripts and workflows are MIT licensed.

