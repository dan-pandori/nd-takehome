"""Reviewer contamination scan, run olmo-rlzero-if: word 8-gram containment of every evaluation prompt (IFBench 300,
IFEval 150) and every Stage-0 prompt against all 13,179 prompts of allenai/Dolci-RL-Zero-IF-7B @ c96e4e42 (my own
download, sha256 5b3cb57d... = the LFS oid at that revision).

Tokens: lower-cased [a-z0-9]+ runs (my own tokeniser). raw = |G(p) & G(d)| / |G(p)| over word 8-gram sets; content =
the same over p's 8-grams that occur in fewer than 20 RL prompts (df over the RL corpus), the pre-registration's
definition. Also: the request part alone (the prompt minus its constraint sentences is not separable for IFBench, so
I report `req` = containment of the RL document's `prompt` minus its "user: " prefix in p, i.e. how much of the RL
document p contains: |G(p) & G(d)| / |G(d)|).
Exclusion rule (pre-registered): content >= 0.5, raw >= 0.8, or a confirmed variant among matches >= 0.3 (read).
Output: out/contam_mine.csv (one row per prompt: best raw / content / reverse with doc keys), ~/review/rzi_rv/contam/
matches.json (every match >= 0.3 with the RL text) and out/contam_report.txt"""
import csv
import json
import os
import re
from collections import Counter, defaultdict

import pyarrow.parquet as pq

import rv_core as C

W = re.compile(r"[a-z0-9]+")
N = 8


def grams(text):
    ws = W.findall(text.lower())
    if len(ws) < N:
        return set()
    return set(zip(*[ws[i:] for i in range(N)]))


def main():
    P = C.load_problems()
    S0 = C.load_problems(stage0=True)
    ev = {**{p: r["prompt"] for p, r in P.items()}, **{p: r["prompt"] for p, r in S0.items()}}
    EG = {p: grams(t) for p, t in ev.items()}
    rl = pq.read_table(os.path.join(C.BIG, "data", "dolci_rlzero_if.parquet"), columns=["key", "prompt"]).to_pylist()
    RG = [grams(r["prompt"]) for r in rl]
    df = Counter()
    for g in RG:
        df.update(g)
    content = {p: {g for g in gs if df[g] < 20} for p, gs in EG.items()}
    owner = defaultdict(list)
    for p, gs in EG.items():
        for g in gs:
            owner[g].append(p)
    best = {p: {"raw": (0.0, ""), "con": (0.0, ""), "rev": (0.0, "")} for p in EG}
    matches = defaultdict(list)
    for j, dg in enumerate(RG):
        cnt, ccnt = Counter(), Counter()
        for g in dg:
            for p in owner.get(g, ()):
                cnt[p] += 1
                if g in content[p]:
                    ccnt[p] += 1
        for p, k in cnt.items():
            raw = k / len(EG[p])
            con = ccnt[p] / len(content[p]) if content[p] else 0.0
            rev = k / len(dg)
            key = rl[j]["key"]
            for name, v in (("raw", raw), ("con", con), ("rev", rev)):
                if v > best[p][name][0]:
                    best[p][name] = (v, key)
            if raw >= 0.3 or con >= 0.3:
                matches[p].append({"key": key, "raw": round(raw, 4), "con": round(con, 4), "rev": round(rev, 4),
                                   "text": rl[j]["prompt"][:6000]})
    os.makedirs(os.path.join(C.BIG, "contam"), exist_ok=True)
    json.dump({"eval": {p: ev[p] for p in matches}, "matches": matches},
              open(os.path.join(C.BIG, "contam", "matches.json"), "w"), indent=1)
    with open(os.path.join(C.OUT, "contam_mine.csv"), "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["pid", "task", "n_grams", "n_content", "raw", "raw_key", "content", "content_key", "rev", "rev_key",
                    "n_matches_ge_0.3", "rule_excl"])
        for p in sorted(EG):
            b = best[p]
            task = (P.get(p) or S0.get(p))["task"]
            excl = b["con"][0] >= 0.5 or b["raw"][0] >= 0.8
            w.writerow([p, task, len(EG[p]), len(content[p]), round(b["raw"][0], 4), b["raw"][1], round(b["con"][0], 4),
                        b["con"][1], round(b["rev"][0], 4), b["rev"][1], len(matches.get(p, [])), int(excl)])
    lines = [f"RL prompts {len(rl)}; eval prompts {len(P)}; stage0 {len(S0)}"]
    for p in sorted(matches, key=lambda x: (x.split("_")[0], int(x.split("_")[1]) if x.split("_")[1].isdigit() else 0)):
        b = best[p]
        lines.append(f"{p}: raw {b['raw'][0]:.3f} ({b['raw'][1]}) content {b['con'][0]:.3f} ({b['con'][1]}) "
                     f"matches>=0.3: {len(matches[p])}{'  RULE-EXCLUDE' if b['con'][0] >= 0.5 or b['raw'][0] >= 0.8 else ''}")
    open(os.path.join(C.OUT, "contam_report.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
