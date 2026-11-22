"""Agreement with the executor's labels under my label variants: final; first pass (before the rule-5 pass, the
rule 10-12 prompt pass and the reads they triggered: rounds R5 / ADJ4 confirmations and B7 / B9 / C7 reads left out);
adjall (every adjudicator proposal accepted). Writes out/agree_variants.txt."""
import collections
import json

import rvc_hand as H
import rvc_compare as C
from rvc_core import Tee

T = Tee("agree_variants.txt")
ex, exreads, conf, keymap = C.exec_labels()
bygrp = {}
for k, (v, s) in ex.items():
    if v and k in H.answers():
        bygrp.setdefault(H.gkey(k), v)
allk = set()
for c in H.CK:
    for p in H.REACH:
        allk |= set(H.B[c][p])
for p, d in H.X.items():
    for c, ks in d.items():
        allk |= set(ks)
for c in H.CKA:
    allk |= set(H.ARMC[c])
exl = {k: (ex[k][0] if k in ex and ex[k][0] else bygrp.get(H.gkey(k))) for k in allk}


def first_pass_labels():
    late = {"B7", "B9", "C7"}
    orig = H.reads

    def reads_early():
        out = orig()
        return {g: [r for r in rs if r[0] not in late] for g, rs in out.items() if any(r[0] not in late for r in rs)}
    H.reads = reads_early
    try:
        return H.labels(exclude_rounds=("R5", "ADJ4"))
    finally:
        H.reads = orig


def adjall_labels():
    import rvc_readings as R
    return R.variant_labels("adjall")


for name, L in (("final", H.labels()), ("first pass", first_pass_labels()), ("adjall", adjall_labels())):
    lab = H.lab_fn(L)
    both = [k for k in allk if lab(k) and exl[k]]
    a = sum(lab(k) == exl[k] for k in both)
    n = len(both)
    pm = sum(lab(k) == "genuine" for k in both) / n
    pe_ = sum(exl[k] == "genuine" for k in both) / n
    pe = pm * pe_ + (1 - pm) * (1 - pe_)
    kap = (a / n - pe) / (1 - pe)
    tab = collections.Counter((lab(k), exl[k]) for k in both)
    T(f"{name:10s}: both {n}, agree {a} ({a / n:.3f}), kappa {kap:.3f}, mine gamed/exec genuine "
      f"{tab[('gamed', 'genuine')]}, mine genuine/exec gamed {tab[('genuine', 'gamed')]}")
