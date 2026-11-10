"""Phase-2 rule-7 variant (run olmo-ifladder): my labels with the one item of hand/confirm_phase2.json set to the executor's rule-7
reading, applied in memory (the committed phase-1 outputs are left as they are). Re-runs the walk for every cell, the
pre-registered readings, the Fisher sensitivity on the teachable set and the expectation verdicts that depend on them.
Writes out/p2_adjusted.txt."""
import json

from rvl_core import KIT, OUT, Tee
from rvl_hand import cells_of, gkey, labels, mech_labels, walk

P = Tee("p2_adjusted.txt")
lab, mech = labels(), mech_labels()
conf = json.load(open(KIT / "hand" / "confirm_phase2.json"))
for c in conf:
    g = gkey(tuple(c["key"]))
    P(f"rule-7 variant: {c['key']} {lab[g]['label']} -> {c['label']} ({c['reason']})")
    lab[g] = dict(lab[g], label=c["label"], how="rule-7 variant")
cell = {}
for c, pid in cells_of():
    cell[(c, pid)] = walk(c, pid, lab, mech)["outcome"]
C = {r["pid"]: r for r in json.load(open(OUT / "classify_mine.json"))["rows"]}
changed = []
for (c, pid), o in cell.items():
    old = {"E": "elicited", "N": "not elicited"}.get(C[pid][c]) if c in C[pid] else None
    if old and o != old:
        changed.append((c, pid, old, o))
P(f"cells changed by the variant: {changed}")
for c, pid, old, o in changed:
    C[pid][c] = "E" if o == "elicited" else "N"
read = {}
for pid, r in C.items():
    first = next((x for x in ("R1", "R2", "R3", "R4") if r[x] == "E"), None)
    if first:
        read[pid] = f"rung {first[1]}"
    elif r["LM"] == "E" and r["LC"] == "E":
        read[pid] = "any fine-tune"
    elif r["LM"] == "E":
        read[pid] = "teachable"
    elif r["LC"] == "E":
        read[pid] = "ctrl only"
    else:
        read[pid] = "neither"
from collections import Counter  # noqa: E402

cnt = Counter(read.values())
P(f"readings under the variant: {dict(cnt)}; prompt-elicitable {sum(v.startswith('rung') for v in read.values())}")
F = {x["pid"]: x for x in json.load(open(OUT / "outcomes.json"))["fisher"]}
t = [p for p, v in read.items() if v == "teachable"]
P(f"teachable {len(t)}: {sorted(t)}; Fisher p_est < 0.05: {sum(F[p]['p_est'] < 0.05 for p in t)}; failing "
  f"{[p for p in t if F[p]['p_est'] >= 0.05]}")
not1 = [p for p, r in C.items() if r["R1"] == "N"]
e1 = sum(C[p]["R2"] == "E" for p in not1)
not12 = [p for p in not1 if C[p]["R2"] != "E"]
e2 = sum(C[p]["R3"] == "E" for p in not12)
not123 = [p for p in not12 if C[p]["R3"] != "E"]
e3 = sum(C[p]["R4"] == "E" for p in not123)
P(f"expectations: E1 {e1} of {len(not1)}; E2 {e2} of {len(not12)}; E3 {e3} of {len(not123)} (0-8: "
  f"{'held' if 0 <= e3 <= 8 else 'missed'}); E4 {sum(v.startswith('rung') for v in read.values())} (19-33); E6 "
  f"teachable {cnt['teachable']} (0-4: {'held' if cnt['teachable'] <= 4 else 'missed'}); lora_main elicited & "
  f"prompt-elicitable {sum(C[p]['LM'] == 'E' and read[p].startswith('rung') for p in C)}")
fam = {}
for p, v in read.items():
    fam.setdefault(C[p]["family"], Counter())[v] += 1
P("by family: " + "; ".join(f"{f} {dict(c)}" for f, c in sorted(fam.items())))

g = n = 0
for pid in [x for x in C]:
    w = walk("R4", pid, lab, mech)
    for ch, i, L, src in w["seq"][:min(w["n"], 4)]:
        if L is None:
            continue
        n += 1
        g += L == "gamed"
P(f"R4 gamed share under the variant (first min(n, 4) of every reach cell): {g}/{n}")
