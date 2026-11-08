"""Pre-registered expected results vs the reviewer's values (run olmo-transplant).
Reads out/rates_<mode>.json for mode in (mine, exec, strict). Output: out/expect_<mode>.md
Usage: rvt_expect.py <mode>"""
import json
import sys

from rvt_core import OUT

mode = sys.argv[1]
R = json.load(open(OUT / f"rates_{mode}.json"))
S = json.load(open(OUT / "rates_strict.json"))
f = "g" if mode != "strict" else "strict"


def T(name, st="reach", field=None, src=None):
    src = src or R
    return src["tables"][f"{st}|{field or f}"][name][0]


rows = []


def add(q, exp, lo, hi, val, note=""):
    if val is None:
        rows.append((q, exp, f"{lo}–{hi}", "n/a", "not derivable", note))
        return
    v = round(val, 3)
    verdict = "within" if lo <= v <= hi else ("above" if v > hi else "below")
    rows.append((q, exp, f"{lo}–{hi}", f"{v:.3f}", verdict, note))


add("T2", 0.80, 0.65, 0.95, T("T2"))
add("T1", 0.55, 0.30, 0.80, T("T1"))
add("R1 = T1 / T2", 0.70, 0.45, 0.95, R[f"R1|reach|{f}"][0])
add("T3", 0.08, 0.01, 0.25, T("T3"))
add("T4", 0.02, 0.00, 0.08, T("T4"))
add("T0-s2300", 0.08, 0.00, 0.25, T("T0-s2300"))
add("T0-dpo", 0.02, 0.00, 0.06, T("T0-dpo"))
for N, e in zip((1024, 2048, 4096, 8192), (0.12, 0.20, 0.40, 0.70)):
    add(f"G_s2300({N})", e, round(e - 0.15, 2), round(e + 0.15, 2), R[f"G|reach|{f}|s2300|{N}"])
for N, e in zip((1024, 2048, 4096, 8192), (0.05, 0.10, 0.25, 0.45)):
    add(f"G_dpo({N})", e, round(e - 0.15, 2), round(e + 0.15, 2), R[f"G|reach|{f}|dpo|{N}"])
add("F_s2300(2,048)", 0.20, 0.05, 0.45, R[f"F|reach|{f}|s2300|2048"])
add("F_s2300(P)", 0.35, 0.10, 0.70, R[f"F|reach|{f}|s2300|P"])
add("F_dpo(P)", 0.25, 0.10, 0.70, R[f"F|reach|{f}|dpo|P"])
for w in ("s2300", "dpo"):
    d = R[f"draftsplit|{f}|{w}"]
    add(f"draft in cut prefix − not, {w} (pooled points)", ">= 0.30", 0.15, 0.60, d[0] - d[2])
    add(f"draft in cut prefix − not, {w} (prompt-weighted)", ">= 0.30", 0.15, 0.60, d[4] - d[5])
for N, e in zip((2048, 4096, 8192), (0.3, 0.6, 0.9)):
    v = S[f"fresh|strict|{N}"][1]  # strict F(N) / s2300 fixed-phase strict rate on the 6
    add(f"fresh F({N}) / natural strict (fixed phase)", e, round(e - 0.25, 2), round(e + 0.25, 2), v,
        f"all olmo-ifomega s2300 draws: {S[f'fresh|strict|{N}'][2]:.2f}")
for nm, e in (("T1", 0.90), ("T2", 0.90), ("T0-dpo", 0.60), ("T0-s2300", 0.60)):
    add(f"calibration {nm} (strict)", e, round(e - 0.20, 2), round(e + 0.20, 2), T(nm, "calib", "strict", S))
cuts = []
for job in ("R_dpo", "R_s2300", "C_dpo", "C_s2300", "F_s2300"):
    for cell, v in S[f"cut|{job}"].items():
        cuts.append((v[1] / v[0], job, cell, v[1], v[0]))
worst = max(cuts)
over = [c for c in cuts if c[0] >= 0.01]
rows.append(("answers cut at the budget", "< 1 % in every condition", "–", f"max {100 * worst[0]:.2f} % ({worst[1]} {worst[2]})",
             "miss" if over else "within", "; ".join(f"{j} {c} {n}/{d}" for _, j, c, n, d in over)))
with open(OUT / f"expect_{mode}.md", "w") as g:
    g.write(f"| quantity | expected | range | reviewer ({mode} labels; reach-41 unless named) | verdict | note |\n|---|---|---|---|---|---|\n")
    for r in rows:
        g.write("| " + " | ".join(str(x) for x in r) + " |\n")
print(open(OUT / f"expect_{mode}.md").read())
