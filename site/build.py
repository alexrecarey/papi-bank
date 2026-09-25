#!/usr/bin/env python3
"""Papi Bank static site generator.

Reads data/alejandro.csv and data/juliana.csv and renders a self-contained
static site into site/dist/index.html.

Run from the repo root:

    python3 site/build.py

GitHub Actions runs this on every push to main and publishes site/dist/
to GitHub Pages.
"""
import base64
import csv
import glob
import json
import mimetypes
import os
import shutil
from datetime import datetime

SITE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SITE)
DATA_DIR = os.path.join(ROOT, "data")
DIST = os.path.join(SITE, "dist")
ASSETS = os.path.join(SITE, "assets")
TEMPLATE = os.path.join(SITE, "template.html")


def read_csv(path):
    movs = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if not row.get("Description") and not row.get("Amount"):
                continue
            movs.append({
                "date": row.get("Date", ""),
                "type": row.get("Type", ""),
                "desc": row.get("Description", ""),
                "amount": float(row.get("Amount") or 0),
                "balance": float(row.get("Balance") or 0),
            })
    return movs


def build_account(movs, name):
    balance = movs[-1]["balance"] if movs else 0.0
    deposits = sum(m["amount"] for m in movs if m["amount"] > 0)
    books = sum(1 for m in movs
                if m["desc"].startswith("AR:") and m["amount"] > 0)
    return {
        "name": name,
        "balance": round(balance, 2),
        "deposits": round(deposits, 2),
        "books": books,
        "movements": list(reversed(movs)),
        "updated": datetime.now().strftime("%b %d, %Y"),
    }


def main():
    data = {
        "Alejandro": build_account(
            read_csv(os.path.join(DATA_DIR, "alejandro.csv")), "Alejandro"),
        "Juliana": build_account(
            read_csv(os.path.join(DATA_DIR, "juliana.csv")), "Juliana"),
    }

    with open(TEMPLATE, encoding="utf-8") as f:
        html = f.read()

    logo = sorted(glob.glob(os.path.join(ASSETS, "logo.*")))
    if logo:
        mime = mimetypes.guess_type(logo[0])[0] or "image/png"
        with open(logo[0], "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        logo_src = f"data:{mime};base64,{b64}"
    else:
        logo_src = ""
    html = html.replace("%%LOGO%%", logo_src)

    # guard against </script> inside data
    payload = json.dumps(data).replace("</", "<\\/")
    html = html.replace("%%DATA%%", payload)

    os.makedirs(DIST, exist_ok=True)
    with open(os.path.join(DIST, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    a, j = data["Alejandro"], data["Juliana"]
    print(f"Built site/dist/index.html — Alejandro ${a['balance']:.2f} "
          f"({len(a['movements'])} movements), Juliana ${j['balance']:.2f} "
          f"({len(j['movements'])} movements)")


if __name__ == "__main__":
    main()
