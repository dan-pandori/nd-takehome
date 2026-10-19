"""Per ladder: σ-covered RL targets proved AT ALL (any Lean-accepted proof) by round r, vs with a working reductio
(rl_<arm>.json). Streams create-or-elicit found_16.jsonl; name + round only."""
import gzip
import json
import re
import sys

arm, fn = sys.argv[1], sys.argv[2]
tg = [json.loads(l) for l in open("../data/ladder/rl_targets.jsonl")]
th = [json.loads(l) for l in gzip.open("out/thm_rl_targets.jsonl.gz", "rt")]
sc = {r["name"] for r, t in zip(tg, th) if t["sc_sem"]}
NM = re.compile(r'"name": "([^"]+)"')
RD = re.compile(r'"round": (\d+)')
first = {}
for line in open(fn):
    m = NM.search(line)
    if not m or m.group(1) not in sc:
        continue
    r = int(RD.search(line).group(1))
    first[m.group(1)] = min(r, first.get(m.group(1), 99))
W = json.load(open(f"out/rl_{arm}.json"))["sigma_cov_first_working_round"]
res = {"arm": arm, "n_sigma_cov_targets": len(sc), "proved_any_by16": len(first), "proved_any_r1": sum(1 for v in first.values() if v == 1),
       "working_by16": len(W), "proved_without_working": sorted(set(first) - set(W)),
       "first_any_earlier_than_working": sum(1 for n in W if first.get(n, 99) < W[n])}
json.dump(res, open(f"out/rl_sigcov_{arm}.json", "w"), indent=1)
print(arm, {k: (v if not isinstance(v, list) else len(v)) for k, v in res.items()}, flush=True)
