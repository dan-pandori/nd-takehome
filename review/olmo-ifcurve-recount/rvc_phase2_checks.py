"""Phase-2 checks of the executor's stated numbers (after reading run_olmo_ifcurve.md / numbers.md / log.md):
hand-gate volume from its hand/ files; its F1 / F2 / F25 per prompt (hand/status.csv and olmo_ifcurve/emergence.csv)
vs mine; my walk re-run with the executor's labels; registry compute rows vs my job sums; pods left running.
Writes out/phase2_checks.txt."""
import collections
import csv
import json
from pathlib import Path

import rvc_hand as H
import rvc_compare as C
from rvc_core import ART, CODE, OUT, RAW, STEP, Tee

T = Tee("phase2_checks.txt")
HX = ART / "hand"
key = list(csv.DictReader(open(HX / "key.csv")))
reads = collections.Counter()
n_reads = 0
for lf in (HX / "labels").glob("*.json"):
    for x in json.load(open(lf)):
        reads[x["item"]] += 1
        n_reads += 1
T(f"executor hand files: items in key.csv {len(key)}; reads in labels/ {n_reads}; items with >= 2 reads "
  f"{sum(v >= 2 for v in reads.values())}, with 3 {sum(v >= 3 for v in reads.values())}; confirm.csv rows "
  f"{sum(1 for _ in csv.DictReader(open(HX / 'confirm.csv')))}; screen.csv rows {sum(1 for _ in csv.DictReader(open(HX / 'screen.csv')))}")
# executor per-prompt F values
em = {r["pid"]: r for r in csv.DictReader(open(CODE / "emergence.csv"))}
T(f"executor emergence.csv columns: {list(next(iter(em.values())).keys())[:14]}")
mine = json.load(open(OUT / "readings.json"))["prompts"]
ST = lambda c: 9999 if c is None else STEP[c]


def ex_val(r, *names):
    """executor checkpoint field ('s0500', '', 'never') -> step int (9999 = never within the sampled checkpoints)"""
    for n in names:
        if n in r:
            v = r[n]
            if v in ("", None, "never", "None"):
                return 9999
            if v.startswith("s") and v[1:].isdigit():
                return int(v[1:])
            try:
                return int(float(v))
            except ValueError:
                return v
    return None


diff = collections.Counter()
rows = []
for p in H.REACH:
    r = em.get(p, {})
    e = {f: ex_val(r, f) for f in ("F1", "F2", "F25")}
    e["F1s"] = ex_val(r, "F1star")
    m = {f: ST(mine[p][f]) for f in ("F1", "F2", "F25", "F1s")}
    for f in ("F1", "F2", "F25", "F1s"):
        if e[f] is not None and e[f] != m[f]:
            diff[f] += 1
            rows.append((p, f, m[f], e[f]))
T(f"per-prompt F values that differ (mine vs executor emergence.csv): {dict(diff)}")
for x in rows:
    T(f"   {x[0]:12s} {x[1]:4s} mine {x[2]:5d} executor {x[3]}")
# my walk with the executor's labels
ex, exreads, conf, keymap = C.exec_labels()
bygrp = {}
for k, (v, s) in ex.items():
    if v and k in H.answers():
        bygrp.setdefault(H.gkey(k), v)


def exlab(k):
    if k in ex and ex[k][0]:
        return ex[k][0]
    return bygrp.get(H.gkey(k))


inc = []
agree = collections.Counter()
for p in H.REACH:
    w = H.walk(p, exlab)
    r = em.get(p, {})
    for f in ("F1", "F2", "F25"):
        agree[(f, ST(w[f]) == ex_val(r, f))] += 1
    if not w["complete"]:
        inc.append(p)
T(f"my walk re-run with the executor's labels vs its emergence.csv: {dict(agree)}; incomplete walks (an executor "
  f"label missing where my walk needs one): {inc}")
# registry rows
reg = list((RAW / "artifacts" / "olmo-ifcurve" / "registry").glob("*"))
T(f"registry files: {[p.name for p in reg]}")
tot = collections.Counter()
for p in reg:
    if p.suffix in (".jsonl",):
        for ln in open(p):
            r = json.loads(ln)
            tot[r.get("metric")] += float(r.get("value", 0) or 0)
T(f"registry metric sums: {dict(tot)}")
# pods
pl = [ln.strip() for ln in open(Path.home() / "pods.log") if "olmo-ifcurve" in ln or " ifc-" in ln]
T("last pods.log lines for the run:")
for ln in pl[-6:]:
    T("   " + ln[:160])
