"""Supplementary (automated, no manual location check): run the s4 matcher on EVERY V-status ledger row.
Per row: worst match level over its quoted fragments. Also flags V rows located outside the abstract whose only
source file on disk is an abstract (.abs.txt). Writes s4b_population.tsv and s4b_population.txt."""
import json
import re
from collections import Counter

import s4_reverify as M
from common import OUT

ledger = json.load(open(f"{OUT}/s2_claims.json"))
V = [r for r in ledger if r["cls"] == "V"]
srcs = {}
rank = {"exact": 0, "exact(dehyph)": 0, "alnum": 1}
rows = []
for r in V:
    files = M.find_source(r["pid"])
    frs = M.fragments(r["claim"])
    if not files:
        rows.append((r, "source-missing", None, files))
        continue
    if not frs:
        rows.append((r, "no-quote", None, files))
        continue
    worst, worst_score, detail = "exact", 1.0, []
    for f in frs:
        best = None
        for fn in files:
            if fn not in srcs:
                srcs[fn] = M.Source(fn)
            got = srcs[fn].search(f)
            lvl = got[0]
            score = 1.0 if lvl in rank else (float(lvl[5:]) if lvl.startswith("fuzzy") else 0.0)
            if best is None or score > best[1] or (score == best[1] and rank.get(lvl, 9) < rank.get(best[0], 9)):
                best = (lvl, score, fn)
            if lvl in rank:
                break
        detail.append((f[:80], best[0], best[2]))
        if best[1] < worst_score or (best[1] == worst_score and rank.get(best[0], 9) > rank.get(worst, 9)):
            worst, worst_score = best[0], best[1]
    rows.append((r, worst, worst_score, detail))


def bucket(level, score):
    if level in ("source-missing", "no-quote"):
        return level
    if level in ("exact", "exact(dehyph)"):
        return "exact"
    if level == "alnum":
        return "alnum (punctuation/markup only)"
    if score >= 0.85:
        return "fuzzy >= 0.85"
    if score >= 0.6:
        return "fuzzy 0.60-0.85"
    return "fuzzy < 0.60 / not found"


lines = []
c = Counter(bucket(l, s) for _, l, s, _ in rows)
lines.append(f"V rows scanned: {len(rows)}")
for k in ["exact", "alnum (punctuation/markup only)", "fuzzy >= 0.85", "fuzzy 0.60-0.85", "fuzzy < 0.60 / not found",
          "no-quote", "source-missing"]:
    lines.append(f"  {k}: {c.get(k, 0)}")
for tag in ["L1", "L2", "L3", "L4", "L5", "L6"]:
    cc = Counter(bucket(l, s) for r, l, s, _ in rows if r["reader"] == tag)
    lines.append(f"  {tag}: {dict(cc)}")
lines.append("\nrows below fuzzy 0.85 (need manual inspection):")
for r, l, s, d in rows:
    if bucket(l, s) in ("fuzzy 0.60-0.85", "fuzzy < 0.60 / not found", "source-missing"):
        lines.append(f"  {r['reader']} #{r['n']} {r['pid'][:40]} | {l} | loc={r['loc'][:40]} | {r['claim'][:200]}")
        if d:
            for x in d:
                lines.append(f"        {x}")
# abstract-only sources used for non-abstract locations
lines.append("\nV rows whose location is not the abstract but whose only on-disk source is an abstract file:")
k = 0
for r, l, s, d in rows:
    files = M.find_source(r["pid"])
    if files and all(f.endswith(".abs.txt") for f in files) and not re.search(r"abstract", r["loc"], re.I):
        k += 1
        lines.append(f"  {r['reader']} #{r['n']} {r['pid'][:40]} | loc={r['loc'][:60]} | match={l} | {r['claim'][:150]}")
lines.append(f"  total: {k}")
with open(f"{OUT}/s4b_population.tsv", "w", encoding="utf-8") as fh:
    fh.write("reader\tn\tpid\tloc\tworst_level\tworst_score\tbucket\n")
    for r, l, s, d in rows:
        fh.write(f"{r['reader']}\t{r['n']}\t{r['pid'][:60]}\t{r['loc'][:60]}\t{l}\t{s}\t{bucket(l, s)}\n")
open(f"{OUT}/s4b_population.txt", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
