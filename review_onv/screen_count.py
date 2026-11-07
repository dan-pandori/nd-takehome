#!/usr/bin/env python3
"""Count olmo-novelty's screening rows: unique sources, new vs prior (own prior list from the four earlier reviews'
files), depth, and the four must-read-in-full papers. python3 review_onv/screen_count.py --root ~/review/olmo-novelty"""
import argparse, csv, re
from collections import Counter, defaultdict
from pathlib import Path

ap = argparse.ArgumentParser(); ap.add_argument("--root", default=".")
ap.add_argument("--lit", default="~/nd-rl/docs/literature")
a = ap.parse_args()
root, lit = Path(a.root).expanduser(), Path(a.lit).expanduser()
DIRS = ["2026-09-29-lit-review", "2026-10-02-lit-review-2", "2026-10-04-capabilities", "2026-10-19-rl-compute-share"]
AID = re.compile(r"(?<![\d.])(2[0-9]{3}\.[0-9]{4,5})(?:v\d+)?(?![\d])")
prior = set()
for d in DIRS:
    for p in (lit / d).rglob("*"):
        if p.is_file() and p.suffix in (".md", ".tsv", ".csv", ".txt", ".bib"):
            prior |= set(AID.findall(p.read_text(errors="replace")))
# README of the literature dir (lists the five Olmo summaries' citations etc.) — reported separately
readme = set(AID.findall((lit / "README.md").read_text(errors="replace")))
rows = []
for f in sorted((root / "olmo_novelty" / "screen").glob("*.tsv")):
    if f.stem.endswith("_relations"):
        continue
    for r in csv.DictReader(open(f), delimiter="\t", quoting=csv.QUOTE_NONE):
        r["_agent"] = f.stem
        rows.append(r)
by = defaultdict(list)
for r in rows:
    m = AID.search(r["id"])
    key = m.group(1) if m else r["id"].strip().lower()
    by[key].append(r)
DEPTH = {"title": 0, "abstract": 1, "skim": 2, "in-depth": 3, "full": 4}
print(f"screen rows {len(rows)}; unique sources {len(by)}; arXiv ids {sum(bool(AID.fullmatch(k)) for k in by)}")
newc = Counter(); depth = Counter(); flag_disagree = []
for k, rs in by.items():
    mine = "yes" if k in prior else "no"
    theirs = {r["prior"].strip().lower() for r in rs}
    if theirs != {mine}:
        flag_disagree.append((k, theirs, mine, rs[0]["title"][:60]))
    best = max(rs, key=lambda r: DEPTH.get(r["depth"].strip().lower(), -1))["depth"].strip().lower()
    newc[mine] += 1
    depth[(mine, best)] += 1
print("new/prior by my list:", dict(newc))
print("max depth by prior:", dict(sorted(depth.items())))
print("in-depth or full, new:", sum(v for (p, d), v in depth.items() if p == "no" and d in ("in-depth", "full")),
      "| all:", sum(v for (p, d), v in depth.items() if d in ("in-depth", "full")))
print("relevance >= 2, new:", sum(1 for k, rs in by.items() if k not in prior and max(int(r["relevance"] or 0) for r in rs) >= 2))
print("prior-flag disagreements (id, run's flags, mine):")
for x in flag_disagree:
    print("  ", x)
for k in ("2505.24864", "2507.14843", "2610.34894", "2507.02833"):
    print("must-read", k, [(r["_agent"], r["depth"]) for r in by.get(k, [])])
dup = [(k, [r["_agent"] for r in rs]) for k, rs in by.items() if len(rs) > 1]
print("sources screened by > 1 agent:", len(dup))
