"""Markdown tables for the review, generated from out/rates_<mode>.json (no hand-copied numbers).
Usage: rvt_tables.py [modes...]   (default: strict exec mine)  -> out/tables.md"""
import json
import sys

from rvt_core import OUT

modes = sys.argv[1:] or ["strict", "exec", "mine"]
R = {m: json.load(open(OUT / f"rates_{m}.json")) for m in modes if (OUT / f"rates_{m}.json").exists()}
FIELD = {"strict": "strict", "exec": "g", "exec_r6": "g", "mine": "g", "mine_r6": "g", "mine_sb": "g",
         "exec_vac": "g", "mine_vac": "g"}
HEAD = {"strict": "strict", "exec": "genuine (executor's labels)", "exec_r6": "genuine (executor's labels, rule 6 strict)",
        "mine": "genuine (my blinded labels)", "mine_r6": "genuine (my labels, rule 6 strict)",
        "mine_sb": "genuine (my labels, natural sub-bullet reading)",
        "exec_vac": "genuine (executor's labels + rule 1 mechanical)", "mine_vac": "genuine (my labels + rule 1 mechanical)"}
out = []


def cell(m, st, name):
    t = R[m]["tables"].get(f"{st}|{FIELD[m]}")
    if not t or name not in t:
        return "–"
    e, lo, hi, n = t[name]
    if e is None or e != e:
        return "n/a"
    return f"{e:.3f} [{lo:.3f}, {hi:.3f}]"


names = ["T2", "T1", "T3", "T4", "T0-s2300", "T0-dpo", "P-s2300", "P-dpo"] + \
        [f"B{N}-{w}" for w in ("s2300", "dpo") for N in (1024, 2048, 4096, 8192, 16384)]
for st, nm in (("reach", "reach-41"), ("brief20", "brief20"), ("calib", "calibration (10)")):
    ms = list(R)
    out.append(f"\n**{nm}** (mean over prompts, 95 % prompt bootstrap)\n")
    out.append("| condition | " + " | ".join(HEAD[m] for m in ms) + " |")
    out.append("|---|" + "---|" * len(ms))
    for n in names:
        out.append(f"| {n} | " + " | ".join(cell(m, st, n) for m in ms) + " |")
out.append("\n**Paired contrasts by prompt** (mean [95 %]; realised SD; MDD = 2.80 SD / √n)\n")
ms = list(R)
out.append("| set | contrast | " + " | ".join(HEAD[m] for m in ms) + " |")
out.append("|---|---|" + "---|" * len(ms))
for st in ("reach", "brief20", "calib"):
    for lab, key in (("Δ21 = T2 − T1", "T2-T1"), ("Δ34 = T3 − T4", "T3-T4"), ("Δ0 = T0s − T0d", "T0-s2300-T0-dpo"),
                     ("Δ30 = T3 − T0s", "T3-T0-s2300"), ("T1 − T0d", "T1-T0-dpo")):
        vals = []
        for m in ms:
            v = R[m].get(f"paired|{st}|{FIELD[m]}|{key}")
            vals.append("–" if not v else f"{v[0]:.3f} [{v[1]:.3f}, {v[2]:.3f}]; SD {v[3]:.3f}; MDD {v[5]:.3f} (n {v[4]})")
        out.append(f"| {st} | {lab} | " + " | ".join(vals) + " |")
    vals = []
    for m in ms:
        v = R[m].get(f"R1|{st}|{FIELD[m]}")
        vals.append("–" if not v else f"{v[0]:.3f} [{v[1]:.3f}, {v[2]:.3f}]")
    out.append(f"| {st} | R1 = T1 / T2 | " + " | ".join(vals) + " |")
out.append("\n**Retained gain F(N) = (G(N) − G(0)) / (G(full) − G(0))**, primary curve, reach-41\n")
out.append("| writer | N | " + " | ".join(HEAD[m] for m in ms) + " |")
out.append("|---|---|" + "---|" * len(ms))
for w in ("s2300", "dpo"):
    for N in (1024, 2048, 4096, 8192, 16384, "P"):
        vals = []
        for m in ms:
            v = R[m].get(f"F|reach|{FIELD[m]}|{w}|{N}")
            vals.append("undef" if v is None else f"{v:.3f}")
        out.append(f"| {w} | {N} | " + " | ".join(vals) + " |")
(OUT / "tables.md").write_text("\n".join(out) + "\n")
print("\n".join(out))
