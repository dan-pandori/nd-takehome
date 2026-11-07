#!/usr/bin/env python3
"""Authenticity check: re-fetch a sample of the run's source texts from arXiv (one download at a time) and test every
ledger quote that cites them against the fresh copy (alnum-collapsed match, since PDF and HTML renderings differ).

    python3 review_onv/refetch.py --root ~/review/olmo-novelty --dest ~/onv_rev_sources/refetch

Fresh copies stay outside the repository (copyrighted). Prints per source: quotes found / quotes cited.
"""
import argparse
import csv
import re
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ledger_check import alnum  # noqa: E402

# source file in ~/onv_sources -> arXiv id with version (fetched as PDF)
SAMPLE = {
    "IF_2512.23457v1.txt": "2512.23457v1",
    "DT_2611.02574v1.txt": "2611.02574v1",
    "IL_2610.34894v1.txt": "2610.34894v1",
    "IF_2608.00220v2.txt": "2608.00220v2",
    "PR_2609.22547v3.txt": "2609.22547v3",
    "NV_2609.01274v1.txt": "2609.01274v1",
    "IF_2610.19525v1.txt": "2610.19525v1",
    "GG_2610.06851v1.txt": "2610.06851v1",
    "DT_2604.14877v1.txt": "2604.14877v1",
    "2606.15455v1.txt": "2606.15455v1",
    "2607.20543.txt": "2607.20543v1",
    "2507.14843v5.txt": "2507.14843v5",
    "2505.24864v1.txt": "2505.24864v1",
    "IF_2507.02833v3.txt": "2507.02833v3",
}


def busy():
    try:
        out = subprocess.run(["pgrep", "-c", "-f", "curl|pdftotext|wget"], capture_output=True, text=True).stdout
        return int(out.strip() or 0)
    except Exception:
        return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--dest", default="~/onv_rev_sources/refetch")
    a = ap.parse_args()
    root, dest = Path(a.root).expanduser(), Path(a.dest).expanduser()
    dest.mkdir(parents=True, exist_ok=True)
    quotes = defaultdict(list)
    for led in sorted((root / "olmo_novelty" / "ledger").glob("*.tsv")):
        for r in csv.DictReader(open(led), delimiter="\t", quoting=csv.QUOTE_NONE):
            quotes[r["source_file"]].append((r["claim_id"], r["quote"]))
    # every file holding the same paper shares the fresh copy
    by_id = defaultdict(list)
    for f in quotes:
        m = re.search(r"(\d{4}\.\d{4,5})", f)
        if m:
            by_id[m.group(1)].append(f)
    for f, aid in SAMPLE.items():
        out = dest / f"REF_{aid}.txt"
        if not out.exists() or out.stat().st_size < 1000:
            while busy() >= 3:
                time.sleep(20)
            pdf = Path(f"/tmp/REF_{aid}.pdf")
            subprocess.run(["curl", "-sL", "-m", "180", f"https://arxiv.org/pdf/{aid}", "-o", str(pdf)])
            subprocess.run(["pdftotext", str(pdf), str(out)])
            pdf.unlink(missing_ok=True)
        if not out.exists():
            print(f"{f}: FETCH FAILED")
            continue
        fresh = alnum(out.read_text(errors="replace"))
        base = aid.split("v")[0]
        files = by_id.get(base, [f])
        tot = hit = 0
        miss = []
        for ff in files:
            for cid, q in quotes[ff]:
                tot += 1
                if alnum(q) in fresh:
                    hit += 1
                else:
                    miss.append(cid)
        print(f"{aid} ({len(fresh)} alnum chars; files {','.join(files)}): {hit}/{tot} ledger quotes found in fresh copy"
              + (f"; missing {miss}" if miss else ""))


if __name__ == "__main__":
    main()
