"""Pre-registered binding expectations (Part B and its addendum, committed before the fixed phase) against my recount.
'in range' uses the stated interval; a point expectation without an interval is reported, not judged.
Output: out/expect.md"""
import json
import os

import rv_core as C


def main():
    st = json.load(open(os.path.join(C.OUT, "stats.json")))
    ib, ie, oo = st["ifbench|headline"], st["ifeval|headline"], st["omega_out|headline"]
    rows = []

    def add(what, exp, lo, hi, val):
        if lo is None:
            verdict = "no interval stated"
        else:
            verdict = "within" if lo <= val <= hi else ("above" if val > hi else "below")
        rows.append((what, exp, f"{val:.3f}" if isinstance(val, float) else str(val), verdict))

    p = lambda d, g, m, k: d[g][m][f"pass@{k}"][0]  # noqa: E731
    add("IFBench dpo pass@1", "0.30 (0.20–0.40)", 0.20, 0.40, p(ib, "strict", "dpo", 1))
    add("IFBench dpo pass@8", "0.62 (0.50–0.75)", 0.50, 0.75, p(ib, "strict", "dpo", 8))
    add("IFBench s0100 pass@1 / @8", "0.32 / 0.64", None, None, p(ib, "strict", "s0100", 1))
    add("IFBench s0750 pass@1", "0.44 (0.32–0.56)", 0.32, 0.56, p(ib, "strict", "s0750", 1))
    add("IFBench s0750 pass@8", "0.76", None, None, p(ib, "strict", "s0750", 8))
    add("IFBench s2300 pass@1", "0.60 (0.45–0.72)", 0.45, 0.72, p(ib, "strict", "s2300", 1))
    add("IFBench s2300 pass@8", "0.86 (0.75–0.93)", 0.75, 0.93, p(ib, "strict", "s2300", 8))
    add("IFBench \\|R\\|", "30 (12–55)", 12, 55, len(ib["strict"]["R"]))
    add("IFBench \\|V\\|", "5 (1–15)", 1, 15, len(ib["strict"]["V"]))
    sc = ib["strict"]["verdict"]["status_counts"]
    add("IFBench dpo resolves (≥ 2 strict in 256), share of R", "50 % (25–75 %)", 0.25, 0.75,
        sc.get("dpo_resolved", 0) / len(ib["strict"]["R"]))
    rest = len(ib["strict"]["R"]) - sc.get("dpo_resolved", 0)
    conf = sum(1 for f in ib["strict"]["R_fate"].values() if f["status"] != "dpo_resolved" and f["rl"]["s2300"]["confirmed"])
    add("IFBench s2300 confirmed (strict) on the rest", "90 %", None, None, conf / rest)
    e = ib["strict"]["entries_exits_k8"]["s2300"]
    add("IFBench expected entries @8 (s2300 vs dpo)", "55 (35–75)", 35, 75, e["expected_entries"][0])
    add("IFBench expected exits @8", "5 (1–12)", 1, 12, e["expected_exits"][0])
    add("test_out dpo pass@1 (omega)", "0.32 (0.20–0.45)", 0.20, 0.45, p(oo, "omega", "dpo", 1))
    add("test_out dpo pass@8", "0.62 (0.45–0.78)", 0.45, 0.78, p(oo, "omega", "dpo", 8))
    add("test_out s2300 pass@1", "0.40 (0.25–0.55)", 0.25, 0.55, p(oo, "omega", "s2300", 1))
    add("test_out s2300 pass@8", "0.66 (0.50–0.80)", 0.50, 0.80, p(oo, "omega", "s2300", 8))
    add("test_out s0750 pass@1 (addendum)", "0.36 (0.22–0.52)", 0.22, 0.52, p(oo, "omega", "s0750", 1))
    add("test_out s0750 pass@8 (addendum)", "0.64", None, None, p(oo, "omega", "s0750", 8))
    add("test_out \\|R\\| (omega)", "8 (3–15)", 3, 15, len(oo["omega"]["R"]))
    add("test_out \\|V\\| (omega)", "5 (1–10)", 1, 10, len(oo["omega"]["V"]))
    e = oo["omega"]["entries_exits_k8"]["s2300"]
    add("test_out expected entries @8", "6 (2–12)", 2, 12, e["expected_entries"][0])
    add("test_out expected exits @8", "3 (1–7)", 1, 7, e["expected_exits"][0])
    so = oo["omega"]["verdict"]["status_counts"]
    add("test_out dpo resolves, share of extended R (omega)", "50 % (20–80 %)", 0.20, 0.80,
        so.get("dpo_resolved", 0) / len(oo["omega"]["R"]))
    for m in ("dpo", "s0750", "s2300"):
        d = abs(p(oo, "omega", m, 1) - p(oo, "rl", m, 1))
        add(f"test_out \\|omega − rl\\| pass@1, {m}", "≤ 0.04", 0.0, 0.04, d)
    add("IFEval dpo pass@1 (addendum)", "0.78 (0.70–0.86)", 0.70, 0.86, p(ie, "strict", "dpo", 1))
    add("IFEval s0750 pass@1", "0.84", None, None, p(ie, "strict", "s0750", 1))
    add("IFEval s2300 pass@1", "0.88 (0.80–0.94)", 0.80, 0.94, p(ie, "strict", "s2300", 1))
    add("IFEval \\|R\\|", "4 (1–10)", 1, 10, len(ie["strict"]["R"]))
    add("IFEval \\|V\\|", "2 (0–5)", 0, 5, len(ie["strict"]["V"]))
    se = ie["strict"]["verdict"]["status_counts"]
    add("IFEval dpo resolves, share of R", "75 %", None, None, se.get("dpo_resolved", 0) / len(ie["strict"]["R"]))
    L = st["ifbench|all"]["lengths_fixed"]
    add("IFBench dpo mean tokens", "1.5–4k", 1500, 4000, L["dpo"]["mean_tok"])
    for m in ("s0100", "s0750", "s2300"):
        add(f"IFBench {m} mean tokens / dpo", "within ±40 %", 0.6, 1.4, L[m]["mean_tok"] / L["dpo"]["mean_tok"])
    L2 = st["ifeval|headline"]["lengths_fixed"]
    add("IFEval dpo mean tokens", "1.5–4k", 1500, 4000, L2["dpo"]["mean_tok"])
    for m in ("s0750", "s2300"):
        add(f"IFEval {m} mean tokens / dpo", "within ±40 %", 0.6, 1.4, L2[m]["mean_tok"] / L2["dpo"]["mean_tok"])
    L3 = oo["lengths_fixed"]
    for m in ("dpo", "s0750", "s2300"):
        add(f"test_out {m} mean tokens", "18–26k", 18000, 26000, L3[m]["mean_tok"])
        add(f"test_out {m} cut share", "10–25 %", 0.10, 0.25, L3[m]["cut_share"])
    out = ["| quantity | pre-registered | recount | |", "|---|---|---|---|"]
    out += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows]
    open(os.path.join(C.OUT, "expect.md"), "w").write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
