#!/usr/bin/env python3
"""Verify the reviewer's fresh-search quotes (scratch TSVs RA/RB/RC) with ledger_check's normaliser + an altered-quote
negative control. python3 review_onv/fresh_check.py --dir ~/review/olmo-novelty/scratch_onv/fresh"""
import argparse, csv, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from ledger_check import norm, alnum, alter

ap = argparse.ArgumentParser(); ap.add_argument("--dir", required=True); a = ap.parse_args()
rng = random.Random(3)
tot = ok = neg = 0
for f in sorted(Path(a.dir).expanduser().glob("R?.tsv")):
    for r in csv.DictReader(open(f), delimiter="\t", quoting=csv.QUOTE_NONE):
        p = Path(r["source_file"]).expanduser()
        if not p.is_absolute():
            p = Path.home() / "onv_rev_sources" / r["source_file"]
        t = p.read_text(errors="replace") if p.exists() else ""
        q = r["quote"]
        found = bool(t) and (norm(q) in norm(t) or alnum(q) in alnum(t))
        tot += 1; ok += found
        qa = alter(q, rng)
        neg += bool(t) and (norm(qa) in norm(t) or alnum(qa) in alnum(t))
        if not found or len(q.split()) > 25:
            print("  FAIL", f.stem, r["claim"], r["arxiv_id"], len(q.split()), "words", q[:80])
print(f"fresh-search quotes found {ok}/{tot}; altered-quote negative controls passing {neg}/{tot}")
