"""Search parsed ledger rows: python3 lg.py <pid-substring> [regex on claim+loc]  (read-only helper)"""
import json, re, sys
L = json.load(open("s2_claims.json"))
pid = sys.argv[1]; rx = re.compile(sys.argv[2], re.I) if len(sys.argv) > 2 else None
for r in L:
    if pid in r["pid"] and (rx is None or rx.search(r["claim"] + " " + r["loc"])):
        print(f"{r['reader']} #{r['n']} {r['pid'][:30]} [{r['status'][:12]}] loc={r['loc'][:50]} | {r['claim'][:330]}")
