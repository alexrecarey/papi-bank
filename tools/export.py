#!/usr/bin/env python3
"""Export the Papi Bank Google Sheet tabs to data/*.csv.

Run from the repo root after every ledger change, then commit and push —
GitHub Actions rebuilds the site and publishes it to GitHub Pages.

    python3 tools/export.py
"""
import csv
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")


def gws(*args):
    r = subprocess.run(["hatch_gws_cli", "sheets", *args],
                       capture_output=True, text=True)
    r.check_returncode()
    return json.loads(r.stdout)


def drive(*args):
    r = subprocess.run(["hatch_gws_cli", "drive", *args],
                       capture_output=True, text=True)
    r.check_returncode()
    return json.loads(r.stdout)


def money(s):
    if s is None:
        return 0.0
    s = str(s).replace("$", "").replace(",", "").strip()
    try:
        return float(s)
    except ValueError:
        return 0.0


def main():
    out = drive("files", "list", "--params", json.dumps(
        {"q": "name = 'Papi Bank' and trashed = false", "pageSize": 5}))
    files = out.get("files", [])
    if not files:
        raise RuntimeError("Papi Bank spreadsheet not found in Drive")
    sid = files[0]["id"]

    os.makedirs(DATA_DIR, exist_ok=True)
    for tab, fname in [("Alejandro", "alejandro.csv"),
                       ("Juliana", "juliana.csv")]:
        v = gws("spreadsheets", "values", "get", "--params", json.dumps(
            {"spreadsheetId": sid, "range": f"{tab}!A2:E2000"}))
        rows = v.get("values", [])
        path = os.path.join(DATA_DIR, fname)
        count = 0
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Date", "Type", "Description", "Amount", "Balance"])
            for row in rows:
                row = (row + [""] * 5)[:5]
                date, typ, desc, amt, bal = row
                if not desc and not amt:
                    continue
                w.writerow([date, typ, desc,
                            f"{money(amt):.2f}", f"{money(bal):.2f}"])
                count += 1
        print(f"wrote {path} ({count} movements)")


if __name__ == "__main__":
    main()
