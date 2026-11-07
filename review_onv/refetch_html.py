#!/usr/bin/env python3
"""Second authenticity pass for sources the run took from arXiv HTML: fetch the same HTML, strip tags, test the quotes
that the PDF pass missed (alnum-collapsed). python3 review_onv/refetch_html.py --root ~/review/olmo-novelty"""
import argparse, csv, html, re, subprocess, sys, time
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from ledger_check import alnum
from refetch import busy

IDS = {"2507.14843v5": ["2507.14843v5.txt"], "2505.24864v1": ["2505.24864v1.txt", "2505.24864v1.pdf.txt"],
       "2607.20543v1": ["2607.20543.txt"], "2606.15455v1": ["2606.15455v1.txt"]}
ap = argparse.ArgumentParser(); ap.add_argument("--root", default="."); ap.add_argument("--dest", default="~/onv_rev_sources/refetch")
a = ap.parse_args()
root, dest = Path(a.root).expanduser(), Path(a.dest).expanduser()
quotes = defaultdict(list)
for led in sorted((root / "olmo_novelty" / "ledger").glob("*.tsv")):
    for r in csv.DictReader(open(led), delimiter="\t", quoting=csv.QUOTE_NONE):
        quotes[r["source_file"]].append((r["claim_id"], r["quote"]))
for aid, files in IDS.items():
    out = dest / f"REFH_{aid}.txt"
    if not out.exists() or out.stat().st_size < 1000:
        while busy() >= 3:
            time.sleep(20)
        raw = subprocess.run(["curl", "-sL", "-m", "180", f"https://arxiv.org/html/{aid}"], capture_output=True).stdout.decode("utf-8", "replace")
        # keep LaTeX alttext of math, drop tags
        raw = re.sub(r'<math[^>]*alttext="([^"]*)"[^>]*>.*?</math>', lambda m: " " + html.unescape(m.group(1)) + " ", raw, flags=re.S)
        raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S)
        raw = re.sub(r"<[^>]+>", " ", raw)
        out.write_text(html.unescape(raw))
    fresh = alnum(out.read_text(errors="replace"))
    pdf = dest / f"REF_{aid}.txt"
    freshpdf = alnum(pdf.read_text(errors="replace")) if pdf.exists() else ""
    tot = hit = 0; miss = []
    for f in files:
        for cid, q in quotes[f]:
            tot += 1
            if alnum(q) in fresh or alnum(q) in freshpdf:
                hit += 1
            else:
                miss.append(cid)
    print(f"{aid}: {hit}/{tot} found in fresh HTML or PDF" + (f"; missing {miss}" if miss else ""))
