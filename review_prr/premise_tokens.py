"""Charles149 pass@1 by premise count (r8 trajectory seeds, plain) and sampled tokens per attempt on textbook72.
python3 review_prr/premise_tokens.py > review_prr/out/premise_tokens.txt"""
import json, os, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fml, reads  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
rem = set(json.load(open(os.path.join(HERE, "out", "leon_removed24.json"))))
C173 = reads.C_V0 + reads.C_V1 + reads.C_B3
C149 = [n for n in C173 if n not in rem]
prem = {}
for f in ["data/gt/candidate_v0.jsonl", "data/gt/candidate_v1.jsonl", "data/gt/batch3.jsonl"]:
    for r in reads.jl(os.path.join(reads.ROOT, f)):
        prem[r["name"]] = len(fml.parse_prompt(r["prompt"])[0])
for lab in ["gt_best12_r8_plain (trajectory seeds)", "gt_best12_r8_guided (trajectory seeds)"]:
    d = reads.load(lab)
    for s in (0, 1, 2):
        cells = []
        for b in range(5):
            ns = [n for n in C149 if prem[n] == b]
            cells.append(f"{b}p n={len(ns)}: {100 * sum(d[s][n][0] / d[s][n][1] for n in ns) / len(ns):.1f}")
        print(f"{lab[:24]} s{s} Charles149 pass@1 by premise count: " + " | ".join(cells))
    toks = []
    for s, (p, _) in reads.arms()[lab].items():
        toks.append(statistics.mean(t for r in reads.jl(p) if r["name"] in set(reads.TB72) for t in r["tokens"]))
    print(f"{lab[:24]} textbook72 sampled tokens per attempt s0/s1/s2: " + " / ".join(f"{t:.1f}" for t in toks))
