#!/usr/bin/env python3
"""Print a stratified random sample of ledger rows with source context, for a by-reader 'supports' check.
    python3 review_onv/ledger_sample.py --root ~/review/olmo-novelty --src ~/onv_sources --per 5 --seed 11"""
import argparse, csv, random, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from ledger_check import norm

ap = argparse.ArgumentParser()
ap.add_argument("--root", default="."); ap.add_argument("--src", default="~/onv_sources")
ap.add_argument("--per", type=int, default=5); ap.add_argument("--seed", type=int, default=11)
ap.add_argument("--ids", default="")
a = ap.parse_args()
root, src = Path(a.root).expanduser(), Path(a.src).expanduser()
rng = random.Random(a.seed)
want = set(a.ids.split(",")) if a.ids else None
for led in sorted((root / "olmo_novelty" / "ledger").glob("*.tsv")):
    rows = list(csv.DictReader(open(led), delimiter="\t", quoting=csv.QUOTE_NONE))
    pick = [r for r in rows if r["claim_id"] in want] if want else rng.sample(rows, min(a.per, len(rows)))
    for r in pick:
        t = norm((src / r["source_file"]).read_text(errors="replace"))
        q = norm(r["quote"])
        i = t.find(q)
        ctx = t[max(0, i - 350): i + len(q) + 250] if i >= 0 else "(not found by norm)"
        print(f"=== {r['claim_id']} | {r['source_file']} | {r['location']} | used_for={r['used_for']}")
        print(f"QUOTE: {r['quote']}")
        print(f"SUPPORTS: {r['supports']}")
        print(f"CONTEXT: ...{ctx}...")
