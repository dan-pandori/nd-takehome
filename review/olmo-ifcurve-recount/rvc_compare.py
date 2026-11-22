"""Agreement of my hand-gate labels with the executor's (run after my labels are final; phase 1 per the reviewer brief).

Executor labels (read-only, artifacts/olmo_ifcurve/hand/): key.csv (item -> draw), labels/<round>_<k>.json (reader
JSON), confirm.csv (executor's adjudications, override), screen.csv (mechanical gamed). Executor label of a draw: its
reads in round order (1 read -> it; first two agree -> it; else majority of three), confirm.csv overrides by item, then
screen for unread draws, then identity inheritance by (pid, whitespace-collapsed answer sha) within the run's labels.
Compared on every draw both of us labelled; reported by source (my reader / my screen / my inherited; executor reader /
confirm / screen / inherited), by part (arm-B walk, extension, arm-C sample, s2300 rule f) and by checkpoint, with
Cohen's kappa; every disagreement on an item my walk treats as deciding is listed with both evidences.
Writes out/compare.txt / .json.
"""
import collections
import csv
import hashlib
import json
import re

import rvc_hand as H
from rvc_core import ART, OUT, Tee, dump

HX = ART / "hand"


def exec_labels():
    key = {r["item"]: (r["job"], r["pid"], int(r["chunk"]), int(r["i"])) for r in csv.DictReader(open(HX / "key.csv"))}
    def rkey(p):
        m = re.match(r"r(\d+)_(\d+)", p.stem)
        return (int(m.group(1)), int(m.group(2))) if m else (999, 0)
    reads = collections.defaultdict(list)
    for lf in sorted((HX / "labels").glob("*.json"), key=rkey):
        for x in json.load(open(lf)):
            k = key.get(x["item"])
            if k:
                reads[k].append((lf.stem, x["label"].strip().lower(), x.get("evidence", ""), x["item"]))
    lab = {}
    for k, rs in reads.items():
        ls = [r[1] for r in rs]
        if len(ls) == 1 or ls[0] == ls[1]:
            lab[k] = (ls[0], "reader")
        elif len(ls) >= 3:
            lab[k] = (collections.Counter(ls[:3]).most_common(1)[0][0], "reader majority")
        else:
            lab[k] = (None, "split")
    conf = {r["item"]: r for r in csv.DictReader(open(HX / "confirm.csv"))}
    for it, r in conf.items():
        k = key.get(it)
        if k:
            lab[k] = (r["label"].strip().lower(), "confirm")
    for r in csv.DictReader(open(HX / "screen.csv")):
        k = (r["job"], r["pid"], int(r["chunk"]), int(r["i"]))
        if k not in lab:
            lab[k] = ("gamed", "screen")
    return lab, reads, conf, key


def main():
    T = Tee("compare.txt")
    L = H.labels()
    mylab = H.lab_fn(L)
    ex, exreads, conf, key = exec_labels()
    # executor identity inheritance over every draw my kit can see
    allk = set()
    for c in H.CK:
        for p in H.REACH:
            allk |= set(H.B[c][p])
    for p, d in H.X.items():
        for c, ks in d.items():
            allk |= set(ks)
    for c in H.CKA:
        allk |= set(H.ARMC[c])
    bygrp = {}
    for k, (v, s) in ex.items():
        if v and k in H.answers():
            bygrp.setdefault(H.gkey(k), v)
    exl = {}
    for k in allk:
        if k in ex and ex[k][0]:
            exl[k] = ex[k]
        elif H.gkey(k) in bygrp:
            exl[k] = (bygrp[H.gkey(k)], "inherited")
    part = {}
    for c in H.CK:
        for p in H.REACH:
            for k in H.B[c][p]:
                part[k] = ("walk", c)
    for p, d in H.X.items():
        for c, ks in d.items():
            for k in ks:
                part[k] = ("extension", c)
    for c in H.CKA:
        for k in H.ARMC[c]:
            part.setdefault(k, ("armC", c))
    both = [k for k in allk if mylab(k) and k in exl]
    agree = sum(mylab(k) == exl[k][0] for k in both)
    T(f"draws labelled by both: {len(both)}; agree {agree} ({agree / max(1, len(both)):.3f})")
    def kappa(ks):
        n = len(ks)
        if not n:
            return None
        a = sum(mylab(k) == exl[k][0] for k in ks) / n
        pm = sum(mylab(k) == "genuine" for k in ks) / n
        pe_ = sum(exl[k][0] == "genuine" for k in ks) / n
        pe = pm * pe_ + (1 - pm) * (1 - pe_)
        return (a - pe) / (1 - pe) if pe < 1 else 1.0
    T(f"Cohen's kappa (all): {kappa(both):.3f}")
    tab = collections.Counter((mylab(k), exl[k][0]) for k in both)
    T(f"2x2 (mine, executor): {dict(tab)}")
    for grp, f in (("part", lambda k: part.get(k, ("?",))[0]), ("ckpt", lambda k: part.get(k, ("?", "?"))[1]),
                   ("my source", lambda k: H.source(L, k).split(":")[0]), ("executor source", lambda k: exl[k][1])):
        T(f"by {grp}:")
        g = collections.defaultdict(list)
        for k in both:
            g[f(k)].append(k)
        for kk in sorted(g, key=str):
            ks = g[kk]
            a = sum(mylab(k) == exl[k][0] for k in ks)
            tb = collections.Counter((mylab(k)[:3], exl[k][0][:3]) for k in ks)
            kp = kappa(ks)
            T(f"   {str(kk):22s} n {len(ks):4d} agree {a / len(ks):.3f} kappa {('%.2f' % kp) if kp is not None else '-'} {dict(tab) if False else dict(tb)}")
    # disagreements on my deciding items
    dec = set()
    for p in H.REACH:
        dec |= H.deciding(p, mylab)
    dis = [k for k in both if k in dec and mylab(k) != exl[k][0]]
    T(f"disagreements on items my walk treats as deciding: {len(dis)} of {sum(1 for k in both if k in dec)}")
    rd = H.reads()
    out = []
    for k in sorted(dis, key=lambda k: (k[1], k[0])):
        g = H.gkey(k)
        mine = [(r[0], r[1], r[3][:160]) for r in rd.get(g, [])]
        theirs = [(r[0], r[1], r[2][:160]) for r in exreads.get(k, [])]
        it = [i for i, kk in key.items() if kk == k]
        cf = conf.get(it[0]) if it else None
        out.append({"key": k, "part": part.get(k), "mine": mylab(k), "my_how": H.source(L, k), "my_reads": mine,
                    "exec": exl[k], "exec_reads": theirs, "exec_confirm": (cf["label"], cf["note"][:200]) if cf else None})
        T(f"   {k} {part.get(k)} mine {mylab(k)} ({H.source(L, k)[:40]}) | exec {exl[k][0]} ({exl[k][1]})"
          + (f" confirm: {cf['note'][:120]}" if cf else ""))
    # coverage: executor-labelled draws my kit never labelled, and vice versa (within my candidate set)
    only_ex = [k for k in allk if k in exl and not mylab(k)]
    only_me = [k for k in allk if mylab(k) and k not in exl]
    T(f"labelled only by the executor (within my candidate draws): {len(only_ex)}; only by me: {len(only_me)}")
    dump({"n_both": len(both), "agree": agree, "kappa": kappa(both), "table": {str(k): v for k, v in tab.items()},
          "disagreements_deciding": out}, "compare.json")


if __name__ == "__main__":
    main()
