"""Phase 2: my readings code run on the EXECUTOR's labels (to separate label differences from computation
differences): F1 / F2 (per cell, pre-registered; and cumulative 'second genuine', the executor's hand.py) / F25 / F1*,
reading-1 medians and intervals, reading-2 categories, H. Writes out/phase2_exec.txt."""
import collections
import json

import numpy as np

import rvc_hand as H
import rvc_compare as C
import rvc_readings as R
from rvc_core import STEP, Tee

T = Tee("phase2_exec.txt")
ex, exreads, conf, keymap = C.exec_labels()
bygrp = {}
for k, (v, s) in ex.items():
    if v and k in H.answers():
        bygrp.setdefault(H.gkey(k), v)
lab = lambda k: (ex[k][0] if k in ex and ex[k][0] else bygrp.get(H.gkey(k)))
ST = lambda c: 9999 if c is None else STEP[c]
res = {}
for p in H.REACH:
    w = H.walk(p, lab)
    g = 0
    f2c = None
    for c in H.CK:
        for k in H.B[c][p]:
            if lab(k) == "genuine":
                g += 1
        if g >= 2 and f2c is None:
            f2c = c
    res[p] = {"F1": w["F1"], "F2": w["F2"], "F2cum": f2c, "F25": w["F25"], "F1s": w["F1s"]}
for var in ("F1", "F2", "F2cum"):
    vals = [ST(res[p][var]) for p in H.REACH]
    cls = [R.CLS[p] for p in H.REACH]
    med = {c: float(np.median([v for v, k in zip(vals, cls) if k == c])) for c in "PTN"}
    bs = R.boot_med_diff(vals, cls, ["P"], ["T", "N"])
    lo, hi = np.percentile(bs, [5, 95])
    T(f"executor labels, {var}: medians {med}; med(TuN)-med(P) 90 % [{lo:.0f}, {hi:.0f}]")
cat = collections.Counter()
for p in H.REACH:
    f1s, f25 = res[p]["F1s"], res[p]["F25"]
    if f1s is None:
        cat["never"] += 1
        continue
    i = H.CKA.index(f1s)
    prev = H.CKA[i - 1]
    if f25 is None:
        cat["slow"] += 1
    elif f25 == f1s and prev == "dpo":
        cat["abrupt"] += 1
    elif sum(1 for c in H.CK if STEP[f1s] < STEP[c] < STEP[f25]) >= 2:
        cat["gradual"] += 1
    else:
        cat["intermediate"] += 1
T(f"executor labels, reading-2 categories with my code (abrupt needs prev 0/128; checked only for dpo here): {dict(cat)}")
for c in H.CK:
    n = sum(1 for p in H.REACH if res[p]["F2"] is not None and STEP[res[p]["F2"]] <= STEP[c])
    ncum = sum(1 for p in H.REACH if res[p]["F2cum"] is not None and STEP[res[p]["F2cum"]] <= STEP[c])
    T(f"   F2 <= {c}: per-cell {n}, cumulative {ncum}")
json.dump({p: {k: v for k, v in r.items()} for p, r in res.items()}, open(R.OUT / "phase2_exec.json", "w"), indent=0)
