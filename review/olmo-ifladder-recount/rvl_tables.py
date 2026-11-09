"""The review's tables for run olmo-ifladder, generated from out/classify_mine.json, out/outcomes.json, out/sets.json.
Writes out/tables.md."""
import collections
import json

from rvl_core import OUT

C = json.load(open(OUT / "classify_mine.json"))["rows"]
O = json.load(open(OUT / "outcomes.json"))
F = {s["pid"]: s for s in O["fisher"]}
TR = json.load(open(OUT / "train.json"))
cov = set(TR["slots"])
L = []
L.append("| prompt | binding id | trained id | R1 | R2 | R3 | R4 | `lora_main` strict / genuine read | `lora_ctrl` strict "
         "| one-sided Fisher p (est.) | reading | flags |")
L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")


def cellv(r, c):
    v = r[c]
    s = r["strict"].get(c)
    g = r["gen"].get(c)
    if v == "U":
        return "–"
    return f"{v} ({s}" + (f"/{g}" if g is not None else "") + ")"


order = sorted(C, key=lambda r: (r["reading"], r["family"], r["pid"]))
for r in order:
    p = r["pid"]
    fl = []
    if r["t3"]:
        fl.append("test-3 survivor")
    if r["drop60"]:
        fl.append("DROP60")
    if r["failed_rungs_breaking_s2300"]:
        fl.append("failed rungs breaking s2300: " + r["failed_rungs_breaking_s2300"])
    if r["R1"] != r["R1s"]:
        fl.append("rung 1 rests on ALL-CAPS answers (strict reading: rung 2)")
    f = F[p]
    L.append(f"| {p.replace('ifbench_', 'b').replace('ifeval_', 'e')} | `{r['binding']}` | "
             f"{'yes' if r['binding'] in cov else 'no'} | {r['R1']} | {cellv(r, 'R2')} | {cellv(r, 'R3')} | "
             f"{cellv(r, 'R4')} | {r['LM']} ({f['LM_strict']}/{f['LM_gen_lb']}) | {f['LC_strict']} | "
             f"{f['p_est']:.3g} | {r['reading']} | {'; '.join(fl)} |")
L.append("")
L.append("Cells: E elicited (≥ 2 genuine of 64), N not, – not run (cut 2). In parentheses: strict successes / genuine "
         "reads in my walk (the walk stops at 2 genuine and ≥ min(n, 4) draws, so genuine reads are a lower bound).")
L.append("")
fam = collections.defaultdict(collections.Counter)
for r in C:
    fam[r["family"]][r["reading"]] += 1
cols = ["prompt-elicitable at rung 1", "prompt-elicitable at rung 2", "prompt-elicitable at rung 3",
        "prompt-elicitable at rung 4", "teachable from RL's trajectories", "teachable by any light fine-tune",
        "lora_ctrl only", "neither"]
L.append("| family | n | rung 1 | rung 2 | rung 3 | rung 4 | teachable (RL traj.) | any fine-tune | ctrl only | neither |")
L.append("|---|---|---|---|---|---|---|---|---|---|")
tot = collections.Counter()
for f_, c_ in sorted(fam.items(), key=lambda x: -sum(x[1].values())):
    L.append(f"| {f_} | {sum(c_.values())} | " + " | ".join(str(c_.get(k, 0)) for k in cols) + " |")
    tot.update(c_)
L.append(f"| all | {sum(tot.values())} | " + " | ".join(str(tot.get(k, 0)) for k in cols) + " |")
(OUT / "tables.md").write_text("\n".join(L) + "\n")
print("\n".join(L))
