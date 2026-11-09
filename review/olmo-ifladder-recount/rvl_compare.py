"""Phase 2: the executor's classification, cells and hand labels against mine (run olmo-ifladder).

 1. classify.csv vs my out/classify_mine.json: every column (R1-R4, main, ctrl, reading) per prompt
 2. the executor's hand labels (olmo_ifladder/handcheck.csv final_label) joined to my labels by draw key through my
    label groups (pid, prompt group, answer sha): coverage, agreement matrix by cell, every disagreement with both
    readers' evidence; which disagreements decide a cell in my walk or in the executor's
 3. my walk re-run with the executor's labels in place of mine (same walk, same mechanical labels): cell outcomes and
    gamed shares, so differences can be attributed to labels vs protocol
Writes out/compare.{txt,json}.
"""
import collections
import csv
import json

from rvl_core import OUT, Tee, dump
from rvl_hand import CELLS, GROUP, SHA, cells_of, gkey, labels, mech_labels, reads, walk

P = Tee("compare.txt")
WT = OUT.parent.parent.parent  # the worktree
mine = {r["pid"]: r for r in json.load(open(OUT / "classify_mine.json"))["rows"]}
ex = {r["pid"]: r for r in csv.DictReader(open(WT / "olmo_ifladder" / "classify.csv"))}
MAPV = {"elicited": "E", "no": "N", "not run": "U", "": "N"}
P("[1] classification, executor vs mine (cells: E elicited, N not, U not run)")
nd = 0
for pid in mine:
    m, e = mine[pid], ex[pid]
    em = {"R1": MAPV.get(e["R1"], e["R1"]), "R2": MAPV.get(e["R2"], e["R2"]), "R3": MAPV.get(e["R3"], e["R3"]),
          "R4": MAPV.get(e["R4"], e["R4"]), "LM": MAPV.get(e["main"], e["main"]), "LC": MAPV.get(e["ctrl"], e["ctrl"])}
    diffs = [f"{c}: exec {em[c]} / mine {m[c]}" for c in ("R1", "R2", "R3", "R4", "LM", "LC") if em[c] != m[c]]
    if e["reading"] != m["reading"]:
        diffs.append(f"reading: exec '{e['reading']}' / mine '{m['reading']}'")
    if diffs:
        nd += 1
        P(f"    {pid}: " + "; ".join(diffs))
P(f"    prompts with any difference: {nd} of {len(mine)}")
P(f"    executor readings: {dict(collections.Counter(e['reading'] for e in ex.values()))}")

# ---------------------------------------------------------------- 2. hand labels
JOBCELL = {"R2_dpo": "R2", "R3_dpo": "R3", "R4_dpo": "R4", "Leval_main": "LM", "Leval_ctrl": "LC",
           "R2_s2300": "S2", "R3_s2300": "S3", "R4_s2300": "S4"}
hc = list(csv.DictReader(open(WT / "olmo_ifladder" / "handcheck.csv")))
lab, mech = labels(), mech_labels()
rd = reads()
ev = collections.defaultdict(list)
for k, rs in rd.items():
    for r in rs:
        ev[gkey(k)].append(f"{r[0]} {r[1]}: {r[2][:200]}")
exl = {}
skipped = collections.Counter()
for r in hc:
    c = JOBCELL.get(r["job"])
    if c is None:
        skipped[r["job"]] += 1
        continue
    k = (c, r["pid"], int(r["chunk"]), int(r["i"]))
    if k not in SHA:
        skipped["not a strict success in my re-grade"] += 1
        continue
    exl[k] = (r["final_label"].strip().lower(), r.get("reader_evidence", ""), r.get("my_note", ""), r["item"])
P(f"\n[2] executor hand items {len(hc)}; joined to my draw keys {len(exl)}; skipped {dict(skipped)}")
agree = collections.Counter()
dis = []
for k, (L, evid, note, item) in exl.items():
    g = gkey(k)
    if k in mech:
        my = "gamed(mech)"
    elif g in lab and lab[g]["label"]:
        my = lab[g]["label"]
    else:
        agree[(k[0], "unread by me")] += 1
        continue
    myl = "gamed" if my.startswith("gamed") else my
    agree[(k[0], L == myl)] += 1
    if L != myl:
        dis.append((k, L, my, evid, note, item))
for c in CELLS:
    a, d, u = agree[(c, True)], agree[(c, False)], agree[(c, "unread by me")]
    if a + d + u:
        P(f"    {c}: both read {a + d}, agree {a}, disagree {d}; executor-only items {u}")
P(f"    total both read {sum(v for k, v in agree.items() if k[1] in (True, False))}, agree "
  f"{sum(v for k, v in agree.items() if k[1] is True)}")
# my items the executor did not read
mine_only = [k for k in SHA if gkey(k) in lab and k not in exl and k[1] in mine]
P(f"    draws I labelled (by read or shared label) that the executor has no item for: "
  f"{len([k for k in mine_only if any(r for r in rd.get(k, []))])} read by me directly")
dec_mine = set()
from rvl_hand import deciding  # noqa: E402

for k in deciding(lab, mech):
    dec_mine.add(k)
P(f"\n    disagreements ({len(dis)}), by direction: "
  f"{dict(collections.Counter((d[1], d[2].split('(')[0]) for d in dis))}")
for k, L, my, evid, note, item in sorted(dis):
    P(f"  - {k[0]} {k[1]} draw {k[2]}/{k[3]}: executor {L} / mine {my}{' [deciding in my walk]' if k in dec_mine else ''}")
    P(f"      executor ({item}): {evid[:260]}")
    if note:
        P(f"      executor note: {note[:260]}")
    for e_ in ev.get(gkey(k), []):
        P(f"      mine: {e_}")

# ---------------------------------------------------------------- 3. my walk with the executor's labels and screen
exg = {}
for k, (L, *_r) in exl.items():
    exg.setdefault(gkey(k), {"label": L, "how": "executor", "reads": []})
# the executor's rule-1 screen (gate.py `mech`, re-typed): one-sentence test [.!?]["')\]]*\s+\S; stairs < 2 lines;
# sub-bullets with no line starting with '*'
import re as _re  # noqa: E402

from rvl_core import answer_of, iter_job, upstream_record  # noqa: E402
from rvl_hand import JOB_OF, PER_SENT, SL  # noqa: E402

xmech = {}
for c, job in JOB_OF.items():
    want = {(p, ch, i) for p, xs in SL[c].items() for ch, i, _ in xs}
    for r in iter_job(job):
        k = (r["pid"], int(r["chunk"]), int(r["i"]))
        if k not in want:
            continue
        a = answer_of(r["text"]) or ""
        ids = set(upstream_record(r["pid"])[1]["instruction_id_list"])
        if ids & PER_SENT and not _re.search(r"[.!?][\"')\]]*\s+\S", a):
            xmech[(c,) + k] = "exec one sentence"
        elif "format:line_indent" in ids and sum(1 for ln in a.splitlines() if ln.strip()) < 2:
            xmech[(c,) + k] = "exec stairs"
        elif "format:sub-bullets" in ids and not any(ln.lstrip().startswith("*") for ln in a.splitlines()):
            xmech[(c,) + k] = "exec sub-bullets"
P(f"\n[3] my walk with the executor's labels and the executor's screen ({len(xmech)} screen labels; mine {len(mech)}); "
  "unlabelled draws stop the walk")
mech_mine = mech
mech = xmech
res = {"cells": {}}
for c in CELLS:
    out = collections.Counter()
    diff = []
    for cc, pid in cells_of():
        if cc != c:
            continue
        w_e = walk(c, pid, exg, xmech)
        w_m = walk(c, pid, lab, mech_mine)
        oe, om = w_e["outcome"] or "unsettled", w_m["outcome"] or "unsettled"
        out[oe] += 1
        if oe != om:
            diff.append(f"{pid}: mine {om} / with executor labels {oe}")
        res["cells"][f"{c}|{pid}"] = {"exec": oe, "mine": om}
    P(f"    {c}: {dict(out)}; differences: {diff}")


def gshare(labmap, c):
    g = n = 0
    for cc, pid in cells_of():
        if cc != c:
            continue
        w = walk(c, pid, labmap, xmech if labmap is exg else mech_mine)
        for ch, i, L, src in w["seq"][:min(w["n"], 4)]:
            if L is None:
                continue
            n += 1
            g += L == "gamed"
    return g, n


P("    gamed share, first min(n, 4) of my walk order, executor labels vs mine:")
for c in ("R2", "R3", "R4", "LM", "LC"):
    ge, ne = gshare(exg, c)
    gm, nm = gshare(lab, c)
    P(f"      {c}: executor labels {ge}/{ne}; mine {gm}/{nm}")
dump(res, "compare.json")
