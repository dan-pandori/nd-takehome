"""Part B's binding expectations (preregistration/olmo-rlzero-if.md, "Binding expectations") against my recount.
Reads out/stats.json, out/hand.json, out/fail.json (if present). Output: out/expect.md"""
import json
import os

import rv_core as C


def inside(v, lo, hi):
    return "inside" if lo <= v <= hi else "MISS"


def main():
    st = json.load(open(os.path.join(C.OUT, "stats.json")))
    hd = json.load(open(os.path.join(C.OUT, "hand.json"))) if os.path.exists(os.path.join(C.OUT, "hand.json")) else None
    fl = json.load(open(os.path.join(C.OUT, "fail.json"))) if os.path.exists(os.path.join(C.OUT, "fail.json")) else None
    pk = st["passk"]
    L = st["lengths"]
    rows = []

    def add(what, exp, lo, hi, val, fmt="{:.3f}"):
        rows.append((what, exp, f"{lo}–{hi}" if lo is not None else "—", fmt.format(val),
                     inside(val, lo, hi) if lo is not None else "(point only)"))

    for s, task, E in (("ifbench_h297", "IFBench", {"base": (0.07, 0.03, 0.14), "s0100": (0.10, 0.04, 0.22),
                                                   "s0500": (0.25, 0.10, 0.40), "main": (0.30, 0.15, 0.45)}),
                       ("ifeval_all150", "IFEval", {"base": (0.20, 0.12, 0.30), "s0100": (0.35, 0.20, 0.55),
                                                    "s0500": (0.65, 0.45, 0.80), "main": (0.75, 0.60, 0.88)})):
        for m, (e, lo, hi) in E.items():
            add(f"{task} {m} strict pass@1", e, lo, hi, pk[f"{s}|{m}|strict"]["1"][0])
    add("IFBench base pass@8", 0.30, None, None, pk["ifbench_h297|base|strict"]["8"][0])
    add("IFBench main pass@8", 0.60, 0.40, 0.75, pk["ifbench_h297|main|strict"]["8"][0])
    add("IFEval base pass@8", 0.60, None, None, pk["ifeval_all150|base|strict"]["8"][0])
    add("IFEval main pass@8", 0.93, None, None, pk["ifeval_all150|main|strict"]["8"][0])
    add("IFBench base mean tokens", 2300, 1200, 4000, L["ifbench|base"]["mean"], "{:.0f}")
    add("IFEval base mean tokens", 2100, None, None, L["ifeval|base"]["mean"], "{:.0f}")
    for m, (e, lo, hi) in {"s0100": (1500, 300, 3000), "s0500": (300, 60, 1500), "main": (60, 30, 200)}.items():
        for t in ("ifbench", "ifeval"):
            add(f"{t} {m} mean tokens", e, lo, hi, L[f"{t}|{m}"]["mean"], "{:.0f}")
    for t in ("ifbench", "ifeval"):
        add(f"{t} base cut at the cap", "2 %", 0.005, 0.05, L[f"{t}|base"]["cut"] / L[f"{t}|base"]["n"], "{:.4f}")
    add("IFBench candidates R (all 300)", 110, 60, 170, len(st["cands"]["ifbench"]["R"]), "{:.0f}")
    add("IFEval candidates R", 45, 25, 70, len(st["cands"]["ifeval"]["R"]), "{:.0f}")
    add("IFBench reverse V", 5, 0, 15, len(st["cands"]["ifbench"]["V"]), "{:.0f}")
    add("IFEval reverse V", 3, 0, 10, len(st["cands"]["ifeval"]["V"]), "{:.0f}")
    ext = [f for t in ("ifbench", "ifeval") for p, f in st["cands"][t]["fates"].items() if f["base"]["n"] > 16
           and not f["excluded"]]
    res = sum(f["state"] == "resolved" for f in ext)
    add("base resolves under strict, of all extended", "40 %", 0.20, 0.70, res / len(ext), "{:.3f}")
    if hd:
        for t, task in (("ifbench", "IFBench"), ("ifeval", "IFEval")):
            gs = hd["gamed_share"][t]
            add(f"{task} gamed share of main's first reads", "80 %", 0.60, 0.95, gs["gamed"] / gs["read"])
            c = [x for x in hd["cands"].values() if x["task"] == t]
            add(f"{task} main hand-confirmed share of R", "25 %", 0.10, 0.45,
                sum(x["main"] == "confirmed" for x in c) / len(c))
            add(f"{task} main open-gaming share of R", "50 %", 0.30, 0.75,
                sum(x["main"] == "open-gaming" for x in c) / len(c))
            add(f"{task} hand-reach prompts", 3, 0, 15 if t == "ifbench" else 10,
                len(hd["verdict"][t]["reach"]), "{:.0f}")
    if fl:
        for cls, (e, lo, hi) in {"u": (0.45, 0.25, 0.70)}.items():
            add(f"format check ({cls}) share of base failures", e, lo, hi, fl["share"].get(cls, 0))
        for cls, e in (("a", 0.20), ("c", 0.15), ("d", 0.12), ("b", 0.08)):
            add(f"format check ({cls}) share", e, None, None, fl["share"].get(cls, 0))
    out = ["| quantity | expected | interval | recount | verdict |", "|---|---|---|---|---|"]
    out += [f"| {a} | {b} | {c} | {d} | {e} |" for a, b, c, d, e in rows]
    open(os.path.join(C.OUT, "expect.md"), "w").write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
