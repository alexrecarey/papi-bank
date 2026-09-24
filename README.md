# 🐷 Papi Bank

A tiny, playful bank website for the kids — balances, earnings, and movement
history, generated as a static site and published with GitHub Pages.

## How it works

1. The ledger lives in the **Papi Bank** Google Sheet (one tab per kid).
2. After any ledger change, export fresh CSVs:
   `python3 tools/export.py`
3. Commit and push — that's the whole publishing mechanism:
   `git add data && git commit -m "..." && git push`
4. GitHub Actions runs `site/build.py`, which renders `site/dist/index.html`
   from `data/*.csv`, and deploys it to GitHub Pages.

## Layout

- `site/template.html` — the page template (tokens: `%%LOGO%%`, `%%DATA%%`)
- `site/build.py` — the static site generator (reads `data/`, writes `site/dist/`)
- `site/assets/` — logo and other static assets (inlined into the page)
- `data/alejandro.csv`, `data/juliana.csv` — one row per movement:
  `Date,Type,Description,Amount,Balance`
- `tools/export.py` — pulls the Google Sheet tabs into `data/*.csv`
- `.github/workflows/publish.yml` — CI: build on every push, deploy to Pages
