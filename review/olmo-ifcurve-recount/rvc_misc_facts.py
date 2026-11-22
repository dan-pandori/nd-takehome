"""Ad-hoc numbers cited in the review, saved with their code: the inherited RL-data overlap (olmo-ifomega
contamination.csv, kind rl), the reproduction of the executor's arm-C sample by my implementation of the
pre-registered rule, F_s0100_ifb's strict successes on the 42 IFBench reach prompts, the prompts with no strict
success in any arm-A draw, and the pass@8 ceiling. Writes out/misc_facts.txt."""
import csv
import random

from rvc_cells import CKA, build
from rvc_core import ART, CODE, RAW, STEP, Tee

T = Tee("misc_facts.txt")
rows, armA, reach, A, B, XC, J = build()
rl = {r["pid"]: r for r in csv.DictReader(open(RAW / "olmo_ifomega" / "contamination.csv")) if r["kind"] == "rl"}
for name, s in (("arm A", armA), ("reach", reach)):
    v = [float(rl[p]["max_content"]) for p in s]
    T(f"RL-data overlap ({name}, {len(s)}): max content containment {max(v):.3f}; >= 0.5: {sum(x >= 0.5 for x in v)}; "
      f"with a shared 13-gram: {sum(int(rl[p]['n_docs_13gram']) > 0 for p in s)}; docs scanned {rl[s[0]]['docs_scanned']}")
key = {(r["job"], r["pid"], int(r["chunk"]), int(r["i"])) for r in csv.DictReader(open(ART / "hand" / "key.csv"))}
shas = {}
for k in key:
    shas.setdefault(k[1], set()).add(rows[k]["ans_sha"])
hit = inh = tot = 0
for c in CKA:
    pop = sorted(tuple(k) for p in armA for k in A[c][p] if rows[tuple(k)]["strict"])
    s = random.Random(4640 + STEP[c]).sample(pop, min(40, len(pop)))
    for k in s:
        tot += 1
        if k in key:
            hit += 1
        elif rows[k]["ans_sha"] in shas.get(k[1], ()):
            inh += 1
T(f"arm-C sample (my implementation of the pre-registered rule, population sorted by draw key): {tot} draws; in the "
  f"executor's key.csv {hit}; not in it but identical to an answer it read {inh}")
ifb_reach = [p for p in reach if p.startswith("ifbench")]
n = sum(1 for p in ifb_reach for k in A["s0100"][p])
st = sum(rows[tuple(k)]["strict"] for p in ifb_reach for k in A["s0100"][p])
T(f"F_s0100_ifb on the {len(ifb_reach)} IFBench reach prompts: {st} strict of {n} draws")
draws = {p: sum(len(A[c][p]) for c in CKA) for p in armA}
none = [p for p in armA if not any(rows[tuple(k)]["strict"] for c in CKA for k in A[c][p])]
T(f"arm-A prompts with no strict success in any of their {sorted(set(draws.values()))} draws over the nine checkpoints: "
  f"{len(none)}; pass@8 ceiling over the 218 = {(218 - len(none)) / 218:.3f}")
