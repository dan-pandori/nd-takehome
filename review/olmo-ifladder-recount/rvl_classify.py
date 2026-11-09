"""Per-prompt classification of run olmo-ifladder from MY labels (pre-registered readings), with the families, the
olmo-iffu flags and the s2300 sanity flags.

usage: rvl_classify.py [MODE]     MODE = mine (default: my hand walk, out/hand.json) | strict (every strict success
                                  counts as genuine; an upper bound with no hand gate)

Rung 1 = olmo-iffu tests 2 / 2c from MY olmo-iffu review (review/olmo-iffu-recount/out/outcomes.json, primary
labels; the strict ALL-CAPS reading as a second column), cross-checked with olmo_iffu/status.csv. Rungs 2-4 and the
LoRAs from my walk: "elicited" = >= 2 genuine of 64. A rung not run on a prompt that my labels leave unelicited
before it is "unrun". s2300 sanity: a rung breaks s2300 on a prompt if < 2 genuine of 16.
Readings: prompt-elicitable at rung r (first rung) / teachable from RL's trajectories (no rung; LM yes, LC no) /
teachable by any light fine-tune (no rung; both) / lora_ctrl only / neither (no rung, neither LoRA); "neither" flagged
for olmo-iffu test-3 survivors (0 genuine in 1,024) and for failed rungs that break s2300.
Writes out/classify_<MODE>.{txt,json,csv}.
"""
import collections
import csv
import json
import sys

from rvl_core import CODE, KIT, OUT, RAW, Tee, dump, load_csv, upstream_record

MODE = sys.argv[1] if len(sys.argv) > 1 else "mine"
P = Tee(f"classify_{MODE}.txt")
prompts = load_csv(CODE / "prompts.csv")
REACH = [r["pid"] for r in prompts if r["set"] == "reach"]
DROP60 = {f"ifbench_{k}" for k in (52, 58, 0, 1, 3, 4, 166, 170, 188, 284)}
cons = load_csv(RAW / "olmo_ifomega" / "constraints.csv")
BIND = {}
for r in cons:
    if r["pid"] in REACH and r["binding"] == "True":
        BIND.setdefault(r["pid"], r["instruction_id"])
fam = {p: BIND[p].split(":")[0] for p in REACH}
pc = {r["pid"]: r for r in prompts}
P(f"binding ids from olmo_ifomega/constraints.csv: {len(BIND)} of {len(REACH)}; == prompts.csv binding: "
  f"{all(pc[p]['binding'] == BIND[p] for p in REACH)}")

# ---------------------------------------------------------------- rung 1 (my olmo-iffu review)
IFFU = KIT.parent / "olmo-iffu-recount" / "out" / "outcomes.json"
oi = json.load(open(IFFU))
r1, r1s, r1_break = {}, {}, {}
for t in ("t2", "t2c"):
    for pid, v in oi[t].items():
        if pid in REACH:
            r1[pid] = v["dpo_outcome"] == "prompt-elicitable"
            r1s[pid] = v["dpo_outcome_strict"] == "prompt-elicitable"
            r1_break[pid] = v["breaks"]
t3 = {pid: v["outcome"] for pid, v in oi["t3"].items()}
st = {r["pid"]: r for r in load_csv(RAW / "olmo_iffu" / "status.csv")}
P(f"rung 1 from my olmo-iffu review: {len(r1)} prompts; elicited {sum(r1.values())} (strict ALL-CAPS reading "
  f"{sum(r1s.values())}); olmo_iffu/status.csv 'prompt-elicitable' {sum('prompt-elicitable' in st[p]['t2_label'] for p in REACH)}; "
  f"disagreements with status.csv: {[p for p in REACH if r1[p] != ('prompt-elicitable' in st[p]['t2_label'])]}")
P(f"olmo-iffu test-3 outcomes on the reach set: { {p: v for p, v in t3.items() if p in REACH} }")

# ---------------------------------------------------------------- my cells
H = json.load(open(OUT / "hand.json"))["cells"]
SETS = json.load(open(OUT / "sets.json"))["cells"]
SL = json.load(open(OUT / "strict_lists.json"))


def cell(c, pid):
    """'E' elicited, 'N' not elicited, 'U' unrun, '?' unsettled."""
    if pid not in SETS[c]:
        return "U"
    if MODE == "strict":
        return "E" if SETS[c][pid]["strict"] >= 2 else "N"
    w = H.get(f"{c}|{pid}")
    if w is None:  # no strict success at all
        return "N"
    return {"elicited": "E", "not elicited": "N"}.get(w["outcome"], "?")


def gen(c, pid):
    w = H.get(f"{c}|{pid}")
    return None if w is None else w["genuine"]


rows = []
for pid in REACH:
    R = {"R1": "E" if r1[pid] else "N", "R1s": "E" if r1s[pid] else "N"}
    for c in ("R2", "R3", "R4", "LM", "LC", "S2", "S3", "S4"):
        R[c] = cell(c, pid)
    first = None
    for c in ("R1", "R2", "R3", "R4"):
        if R[c] == "E":
            first = c
            break
    unrun = [c for c in ("R2", "R3", "R4") if R[c] == "U" and first is None]
    unsettled = [c for c in ("R2", "R3", "R4", "LM", "LC") if R[c] == "?"]
    if first:
        reading = f"prompt-elicitable at rung {first[1]}"
    elif unrun or unsettled:
        reading = f"undetermined (rungs unrun {unrun}, unsettled {unsettled})"
    elif R["LM"] == "E" and R["LC"] == "E":
        reading = "teachable by any light fine-tune"
    elif R["LM"] == "E":
        reading = "teachable from RL's trajectories"
    elif R["LC"] == "E":
        reading = "lora_ctrl only"
    else:
        reading = "neither"
    # failed rungs that break s2300 (rung 1 from olmo-iffu's s2300 cells; rungs 2-4 from the sanity arm)
    brk = []
    if not r1[pid] and r1_break.get(pid):
        brk.append("R1")
    for c, s in (("R2", "S2"), ("R3", "S3"), ("R4", "S4")):
        if R[c] == "N" and R[s] == "N":
            brk.append(c)
    rows.append({"pid": pid, "family": fam[pid], "binding": BIND[pid], "drop60": pid in DROP60, **R,
                 "reading": reading, "t3": t3.get(pid, ""), "failed_rungs_breaking_s2300": brk,
                 "gen": {c: gen(c, pid) for c in ("R2", "R3", "R4", "LM", "LC", "S2", "S3", "S4")},
                 "strict": {c: SETS[c][pid]["strict"] if pid in SETS[c] else None for c in
                            ("R2", "R3", "R4", "LM", "LC", "S2", "S3", "S4")}})

P(f"\n{'pid':13s} {'family':11s} R1 R1s R2 R3 R4 LM LC | S2 S3 S4 | reading")
for r in rows:
    P(f"{r['pid']:13s} {r['family']:11s} {r['R1']}  {r['R1s']}   {r['R2']}  {r['R3']}  {r['R4']}  {r['LM']}  {r['LC']}  | "
      f"{r['S2']}  {r['S3']}  {r['S4']}  | {r['reading']}" + (f"  [t3: {r['t3']}]" if r["t3"] else "") +
      (f"  [breaks s2300 at failed {r['failed_rungs_breaking_s2300']}]" if r["failed_rungs_breaking_s2300"] else ""))
cnt = collections.Counter(r["reading"] for r in rows)
P(f"\nreadings: {dict(cnt)}")
for c in ("R2", "R3", "R4", "LM", "LC"):
    P(f"{c} elicited (all prompts it ran on): {sum(r[c] == 'E' for r in rows)}; unsettled {sum(r[c] == '?' for r in rows)}")
not1 = [r for r in rows if r["R1"] == "N"]
P(f"rung 1 not elicited: {len(not1)}; rung 2 elicits {sum(r['R2'] == 'E' for r in not1)} of them")
not12 = [r for r in not1 if r["R2"] != "E"]
P(f"still unelicited after rung 2: {len(not12)}; rung 3 elicits {sum(r['R3'] == 'E' for r in not12)} (unrun "
  f"{sum(r['R3'] == 'U' for r in not12)})")
not123 = [r for r in not12 if r["R3"] != "E"]
P(f"still unelicited after rung 3: {len(not123)}; rung 4 elicits {sum(r['R4'] == 'E' for r in not123)} (unrun "
  f"{sum(r['R4'] == 'U' for r in not123)})")
P(f"prompt-elicitable at some rung: {sum(r['reading'].startswith('prompt') for r in rows)} of {len(rows)}")
by = collections.defaultdict(collections.Counter)
for r in rows:
    by[r["family"]][r["reading"].split(" (")[0].replace("prompt-elicitable at rung ", "rung ")] += 1
P("by family (binding id prefix):")
for f_, c_ in sorted(by.items(), key=lambda x: -sum(x[1].values())):
    P(f"    {f_:12s} n {sum(c_.values()):2d}: {dict(c_)}")
nei = [r for r in rows if r["reading"] == "neither"]
P(f"neither: {[r['pid'] for r in nei]}; of these olmo-iffu test-3 survivors: "
  f"{[r['pid'] for r in nei if 'survives' in r['t3']]}; with a failed rung that breaks s2300: "
  f"{ {r['pid']: r['failed_rungs_breaking_s2300'] for r in nei if r['failed_rungs_breaking_s2300']} }")
six = ["ifbench_3", "ifbench_136", "ifbench_166", "ifbench_211", "ifbench_248", "ifbench_269"]
P(f"the 6 test-3 survivors not elicited at rung 1 (pre-registered list): "
  f"{ {p: next(r['reading'] for r in rows if r['pid'] == p) for p in six} }")
four = ["ifbench_78", "ifbench_133", "ifbench_252", "ifbench_253"]
P("the four 1,024-survivors that the hint elicits, every cell:")
for p in four:
    r = next(x for x in rows if x["pid"] == p)
    P(f"    {p}: R1 {r['R1']} R2 {r['R2']} R3 {r['R3']} R4 {r['R4']} LM {r['LM']} LC {r['LC']} S2 {r['S2']}; genuine "
      f"{r['gen']}; strict {r['strict']}")
TR = json.load(open(OUT / "train.json"))
covered = set(TR["slots"])
for grp, sel in (("binding id covered by a training slot", lambda r: r["binding"] in covered),
                 ("binding id NOT covered", lambda r: r["binding"] not in covered)):
    xs = [r for r in rows if sel(r)]
    P(f"{grp}: {len(xs)} prompts; lora_main elicits {sum(r['LM'] == 'E' for r in xs)}; lora_ctrl "
      f"{sum(r['LC'] == 'E' for r in xs)}; of them not prompt-elicitable: "
      f"{sum(r['LM'] == 'E' and not r['reading'].startswith('prompt') for r in xs)} / "
      f"{sum(not r['reading'].startswith('prompt') for r in xs)}")
sens = [r for r in rows if r["LM"] == "E" and r["LC"] != "E"]
P(f"lora_main elicited & lora_ctrl not: {len(sens)}")
for r in rows:
    r["failed_rungs_breaking_s2300"] = " ".join(r["failed_rungs_breaking_s2300"])
with open(OUT / f"classify_{MODE}.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=[k for k in rows[0] if k not in ("gen", "strict")], extrasaction="ignore")
    w.writeheader()
    w.writerows(rows)
dump({"rows": rows, "counts": dict(cnt)}, f"classify_{MODE}.json")
