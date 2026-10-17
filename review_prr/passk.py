"""Reviewer's pass@k recount of our stored reads on several theorem sets (unbiased estimator, Chen et al. 2021).

python3 review_prr/passk.py [k list] > review_prr/out/passk.txt
Per arm and seed: mean over theorems of pass@k from (n_ok, n_tried = 256); 'solved' = n_ok > 0 (pass@256).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reads  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
EXPOSED = set()
ov = json.load(open(os.path.join(HERE, "out", "overlap_rl_targets.json")))
for e in ("tb72_dev58", "tb72_train14"):
    EXPOSED |= {h["name"] for h in ov[e]["inst"]}
assert len(EXPOSED) == 10
REMOVED24 = set(json.load(open(os.path.join(HERE, "out", "leon_removed24.json"))))
C173 = reads.C_V0 + reads.C_V1 + reads.C_B3
SETS = {
    "tb72": reads.TB72,
    "dev58": reads.TB_DEV,
    "train14": reads.TB_TRAIN,
    "tb72_clean62": [n for n in reads.TB72 if n not in EXPOSED],
    "C173": C173,
    "C149": [n for n in C173 if n not in REMOVED24],
}
assert len(SETS["C149"]) == 149 and len(SETS["tb72_clean62"]) == 62


def table(ks, arms=None, sets=None):
    arms = arms or list(reads.arms())
    sets = sets or list(SETS)
    rows = []
    for lab in arms:
        d = reads.load(lab)
        for sname in sets:
            S = SETS[sname]
            if not all(n in d[0] for n in S):
                continue
            for s in (0, 1, 2):
                m = d[s]
                vals = [sum(reads.passk(m[n][1], m[n][0], k) for n in S) / len(S) for k in ks]
                solved = sum(1 for n in S if m[n][0] > 0)
                rows.append((lab, sname, s, len(S), solved, vals))
    return rows


if __name__ == "__main__":
    ks = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else [1, 5, 10, 32, 64, 256]
    print(f"{'arm':<46} {'set':<13} seed  n  solved@256 | " + " ".join(f"p@{k:<6}" for k in ks))
    for lab, sname, s, n, solved, vals in table(ks):
        print(f"{lab:<46} {sname:<13} s{s} {n:>4} {solved:>4} | " + " ".join(f"{v:.4f} " for v in vals))
