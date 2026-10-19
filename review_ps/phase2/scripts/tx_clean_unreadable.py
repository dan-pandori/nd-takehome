#!/usr/bin/env python3
"""Phase-2 sub-audit: for each strategy, is there a CLEAN K12 record SHORTER than the shortest clean READABLE one (i.e.
does the unstated readability filter change 'shortest clean')?  Counts + the readable() clause; no theorem text."""
import collections, gzip, json, sys
sys.path.insert(0, "/home/dan/review/proof-strategies/phase2/scripts")
from tx_shortest_lib import readable_why  # noqa: E402
import importlib.util
spec = importlib.util.spec_from_file_location("txs", "/home/dan/review/proof-strategies/phase2/scripts/tx_shortest.py")
src = open("/home/dan/review/proof-strategies/phase2/scripts/tx_shortest.py").read()
ns = {}
exec(src.split("EX = json.load")[0], ns)   # CLEAN, STRATS, readable() only (no data pass)
CLEAN, STRATS = ns["CLEAN"], ns["STRATS"]
best = {s: {} for s in STRATS}   # s -> {'read': minLp, 'any': minLp}
why = collections.Counter()
rows = []
fa = gzip.open("/home/dan/work/proof-strategies/artifacts/ps/labels/k12.jsonl.gz", "rt")
fs = gzip.open("/home/dan/review/proof-strategies/data/ps/in/train_k12.jsonl.gz", "rt")
for la, ls in zip(fa, fs):
    a = json.loads(la)
    sts = [s for s in STRATS if CLEAN[s](a)]
    if not sts:
        continue
    s_ = json.loads(ls)
    w = readable_why(s_["prompt"], s_["proof"])
    for s in sts:
        b = best[s]
        b["any"] = min(b.get("any", 99), a["Lp"])
        if not w:
            b["read"] = min(b.get("read", 99), a["Lp"])
        rows.append((s, a["Lp"], w))
for s in STRATS:
    b = best[s]
    shorter = collections.Counter(w for (t, lp, w) in rows if t == s and w and lp < b.get("read", 99))
    print(s, "min Lp clean (any readability):", b.get("any"), "| clean & readable:", b.get("read"),
          "| unreadable clean records shorter than the readable minimum:", dict(shorter))
