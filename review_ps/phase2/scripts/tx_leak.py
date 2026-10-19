#!/usr/bin/env python3
"""Phase-2 sub-audit: do the 29 sequents / ND proofs / Lean texts shown in EXAMPLES.md coincide with a textbook72 or a
Charles (private) theorem or reference proof?  Exact strings and the reviewer's renaming-class keys.  Counts only."""
import glob, json, re, sys
sys.path.insert(0, "/home/dan/review/proof-strategies/review_ps")
from nd import parse_prompt  # noqa: E402
from sealkey import keys  # noqa: E402
md = open("/home/dan/work/proof-strategies/proof_strategies/EXAMPLES.md").read()
prompts = re.findall(r"^(THM .* PRF)$", md, re.M)
nd_lines = set(re.findall(r"^(N\d+ .*)$", md, re.M))
print("EXAMPLES.md sequents:", len(prompts))
def classes(rows):
    K = {"po": set(), "set": set(), "cur": set(), "curneg": set()}
    P = set()
    for r in rows:
        P.add(r["prompt"])
        p, c = parse_prompt(r["prompt"])
        for k, v in keys(p, c).items():
            K[k].add(v)
    return K, P
tb = [json.loads(l) for l in open("/home/dan/review/proof-strategies/data/bs/textbook72.jsonl")]
ch = []
for fn in glob.glob("/home/dan/work/proof-strategies/data/ps/in/charles/*.jsonl"):
    ch += [json.loads(l) for l in open(fn)]
for name, rows in (("textbook72", tb), ("charles (all files)", [r for r in ch if r.get("prompt")])):
    K, P = classes(rows)
    exact = sum(1 for p in prompts if p in P)
    hits = {k: 0 for k in K}
    for pr in prompts:
        p, c = parse_prompt(pr)
        for k, v in keys(p, c).items():
            hits[k] += v in K[k]
    print(f"{name}: rows {len(rows)} | exact prompt matches {exact} | class hits {hits}")
# Charles reference proofs: any shown ND proof equal to a reference proof (as a line sequence)?
refs = 0
for r in ch:
    rp = r.get("reference_proof") or r.get("proof")
    if not rp:
        continue
    ls = [x.strip() for x in rp.split(";") if x.strip() and x.strip() != "QED"]
    if ls and all(x in nd_lines for x in ls) and len(ls) > 2:
        refs += 1
print("Charles reference proofs whose every line (> 2 lines) appears among EXAMPLES.md ND lines:", refs)
