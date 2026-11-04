"""Per-cell table (model x problem) from raw rows, fixed phase and all phases (reviewer)."""
import collections, csv, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_core as C
rs = C.rows(); probs = C.problems(); pids = [p["pid"] for p in probs]
jobs = collections.Counter(r["job"] for r in rs)
print("jobs:", dict(jobs))
print("s0_dpo pids all aime2024:", all(r["pid"].startswith("aime2024") for r in rs if r["job"] == "s0_dpo"))
cells = []
for m in C.MODELS:
    for pid in pids:
        d = C.draws(rs, m, pid)
        fx = [r for r in d if r["job"].startswith("F_")]
        def cnt(sub, g): return sum(1 for r in sub if r[g])
        first = {g: next((i + 1 for i, r in enumerate(d) if r[g]), None) for g in ("rl", "final", "doubly")}
        second = {}
        for g in ("rl", "final", "doubly"):
            idx = [i + 1 for i, r in enumerate(d) if r[g]]
            second[g] = idx[1] if len(idx) > 1 else None
        cells.append({"model": m, "pid": pid, "excluded": pid in C.excluded(), "n_fixed": len(fx),
                      "fixed_rl": cnt(fx, "rl"), "fixed_final": cnt(fx, "final"), "fixed_doubly": cnt(fx, "doubly"),
                      "fixed_main": cnt(fx, "main"), "fixed_cut": sum(r["finish"] == "length" for r in fx),
                      "fixed_tok_mean": round(sum(r["n_tok"] for r in fx) / max(len(fx), 1)),
                      "n_all": len(d), "all_rl": cnt(d, "rl"), "all_final": cnt(d, "final"), "all_doubly": cnt(d, "doubly"),
                      "first_rl": first["rl"], "second_rl": second["rl"], "first_final": first["final"],
                      "second_final": second["final"], "first_doubly": first["doubly"], "second_doubly": second["doubly"]})
with open(os.path.join(C.HERE, "out", "cells.csv"), "w") as f:
    w = csv.DictWriter(f, fieldnames=list(cells[0])); w.writeheader(); w.writerows(cells)
bad = [(c["model"], c["pid"], c["n_fixed"]) for c in cells if c["n_fixed"] != (16 if c["model"] == "dpo" else 8)]
print("cells", len(cells), "with wrong fixed n:", bad)
for c in cells:
    if c["n_all"] != c["n_fixed"]:
        print("extended:", c["model"], c["pid"], {k: c[k] for k in ("n_all", "all_rl", "all_final", "all_doubly", "first_rl", "second_rl", "first_final", "second_final", "first_doubly", "second_doubly")})
