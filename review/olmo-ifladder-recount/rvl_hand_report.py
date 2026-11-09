"""Summary of my hand gate for run olmo-ifladder: reader files, reads by round and cell, items, label groups, how labels
were reached, agreement, deciding items with a second read, mechanical labels, and the strict ALL-CAPS reading of
ifbench_290 (rule 6). Writes out/hand_report.txt."""
import collections
import glob
import json

from rvl_core import OUT, Tee
from rvl_hand import CELLS, HAND, RL, cells_of, deciding, gkey, labels, mech_labels, reads, walk

P = Tee("hand_report.txt")
lab, mech = labels(), mech_labels()
rd = reads()
files = sorted(RL.glob("*.json"))
P(f"reader files {len(files)}: " + " ".join(f.stem for f in files))
byround = collections.Counter()
bycell = collections.Counter()
for k, rs in rd.items():
    for r in rs:
        byround[r[0][0]] += 1
        bycell[(k[0], r[0][0])] += 1
P(f"reads by round type (A first, B second, C/M mixed, T extra): {dict(byround)}; total {sum(byround.values())}")
P("reads by cell and round type: " + "; ".join(f"{c}: " + ", ".join(f"{t} {bycell[(c, t)]}" for t in "ABMT" if bycell[(c, t)])
                                              for c in CELLS + ["SRC"]))
P(f"sample keys read {len(rd)}; label groups {len(lab)}; how: {dict(collections.Counter(v['how'].split(':')[0] for v in lab.values()))}")
P(f"mechanical rule-1 labels (no reader): {len(mech)}, by cell {dict(collections.Counter(k[0] for k in mech))}")
dec = deciding(lab, mech)
dg = {gkey(k) for k in dec}
P(f"deciding items (rvl_hand.deciding) {len(dec)} keys / {len(dg)} label groups; with >= 2 reads "
  f"{sum(len(lab[g]['reads']) >= 2 for g in dg)}; with a third read {sum(len(lab[g]['reads']) >= 3 for g in dg)}")
two = [(g, v) for g, v in lab.items() if len(v["reads"]) >= 2]
P(f"items with >= 2 reads {len(two)}; first two agree {sum(v['reads'][0][1] == v['reads'][1][1] for g, v in two)}")
for g, v in two:
    if v["reads"][0][1] != v["reads"][1][1]:
        P(f"    split: {g[:3] if g[0] == 'SRC' else g[:2]} reads {[r[:2] for r in v['reads']]} -> {v['label']} ({v['how']})")
src = {g: v for g, v in lab.items() if g[0] == "SRC"}
P(f"training trajectories read: {len(src)}; genuine {sum(v['label'] == 'genuine' for v in src.values())} "
  f"(s2300 {sum(v['label'] == 'genuine' for g, v in src.items() if g[2] == 's2300')}/"
  f"{sum(g[2] == 's2300' for g in src)}, dpo {sum(v['label'] == 'genuine' for g, v in src.items() if g[2] == 'dpo')}/"
  f"{sum(g[2] == 'dpo' for g in src)}); reads per item {sorted(collections.Counter(len(v['reads']) for v in src.values()).items())}")
# reads per cell walk: how many draws read vs strict n
for c in CELLS:
    ws = [walk(c, pid, lab, mech) for cc, pid in cells_of() if cc == c]
    P(f"{c}: cells with >= 1 strict {len(ws)}; strict successes {sum(w['n'] for w in ws)}; draws labelled in walks "
      f"{sum(len(w['seq']) for w in ws)}; elicited {sum(w['outcome'] == 'elicited' for w in ws)}")
# rule 6: strict ALL-CAPS reading for ifbench_290 (ALL-CAPS-flagged genuine items count as not successes)
caps = {}
for k, rs in rd.items():
    if k[0] != "SRC" and k[1] == "ifbench_290":
        caps[gkey(k)] = any(r[3] for r in rs)
for c in ("R2", "LM", "LC", "S2"):
    xs = json.load(open(OUT / "strict_lists.json"))[c].get("ifbench_290", [])
    seq = []
    g_all = g_strict = 0
    unread = 0
    for ch, i, s in xs:
        k = (c, "ifbench_290", ch, i)
        v = lab.get(gkey(k))
        if k in mech:
            seq.append("mech")
            continue
        if v is None:
            unread += 1
            continue
        if v["label"] == "genuine":
            g_all += 1
            if not caps.get(gkey(k)):
                g_strict += 1
    P(f"ifbench_290 {c}: strict {len(xs)}; genuine read {g_all}; genuine and not ALL-CAPS {g_strict}; unread {unread} "
      f"-> strict ALL-CAPS reading: {'elicited' if g_strict >= 2 else 'not elicited' if unread == 0 else 'unsettled'}")
