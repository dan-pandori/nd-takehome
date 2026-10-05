"""Distinct ledger paper ids -> source files via the s4 resolver (first token of the id cell, with/without version,
.txt then .abs.txt, or a backticked file name). Counts ids with a full text, abstract only, or no file; by status."""
import json
from collections import Counter
import s4_reverify as M
from common import OUT
L = json.load(open(f"{OUT}/s2_claims.json"))
ids = {}
for r in L:
    ids.setdefault(r["pid"], set()).add(r["cls"])
c = Counter(); none = []
for pid, cls in ids.items():
    f = M.find_source(pid)
    k = "none" if not f else ("full" if any(not x.endswith(".abs.txt") for x in f) else "abstract-only")
    c[k] += 1
    if k == "none": none.append((pid[:60], sorted(cls)))
out = [f"distinct ledger id strings: {len(ids)}; full text {c['full']}, abstract only {c['abstract-only']}, no file {c['none']}",
       f"ids with no file: {none}"]
open(f"{OUT}/s2b_sources.txt", "w").write("\n".join(out) + "\n"); print("\n".join(out))
