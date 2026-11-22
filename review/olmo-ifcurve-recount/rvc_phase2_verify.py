"""Numbers quoted in the rewritten §Compare / Corrections: the executor's labels on my arm-C s0750 half-sample; the
adjall variant's F1 counts and F1* < F1 count; the slow prompts' share of the arm-B late first-4 items and of their
gamed ones; tokens-per-draw ratios to 3 decimals. Writes out/phase2_verify.txt."""
import csv
import collections

import rvc_hand as H
import rvc_compare as C
from rvc_core import OUT, Tee

T = Tee("phase2_verify.txt")
L = H.labels()
lab = H.lab_fn(L)
ex, exreads, conf, keymap = C.exec_labels()
bygrp = {}
for k, (v, s) in ex.items():
    if v and k in H.answers():
        bygrp.setdefault(H.gkey(k), v)
exl = lambda k: (ex[k][0] if k in ex and ex[k][0] else bygrp.get(H.gkey(k)))
for c in H.CKA:
    ks = H.ARMC[c]
    T(f"arm-C half-sample {c}: mine gamed {sum(lab(k) == 'gamed' for k in ks)}, executor gamed {sum(exl(k) == 'gamed' for k in ks)}, "
      f"executor unlabelled {sum(exl(k) is None for k in ks)}")
adj = list(csv.DictReader(open(OUT / "emergence_adjall.csv")))
T("adjall F1 counts:", dict(collections.Counter(r["F1"] for r in adj)), "| F1* < F1:", sum(1 for r in adj if r["F1s"] != r["F1"]))
em = {r["pid"]: r for r in csv.DictReader(open(OUT / "emergence.csv"))}
slow = {p for p, r in em.items() if r["category"] == "slow"}
items = [(p, k) for c in ("s1100", "s1600", "s2300") for p in H.REACH for k in H.B[c][p][:4] if lab(k)]
g = [(p, k) for p, k in items if lab(k) == "gamed"]
T(f"arm-B late first-4 items: {len(items)}, from slow prompts {sum(p in slow for p, _ in items)}; gamed {len(g)}, "
  f"from slow prompts {sum(p in slow for p, _ in g)}")
for c, t in (("s0750", 5564 / 4448), ("s1100", 6304 / 4448), ("s1600", 5540 / 4448), ("s2300", 6277 / 4448)):
    T(f"arm A tokens per draw {c} / dpo = {t:.3f}")
