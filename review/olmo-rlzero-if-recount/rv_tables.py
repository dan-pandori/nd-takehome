"""Markdown tables for the review, generated from out/*.json (never hand-copied). Output: out/tables.md"""
import json
import os
from collections import Counter

import rv_core as C


def load(n):
    p = os.path.join(C.OUT, n)
    return json.load(open(p)) if os.path.exists(p) else None


def main():
    st, hd, cp, fl = load("stats.json"), load("hand.json"), load("compute.json"), load("fail.json")
    cells = load("cells.json")
    out = []
    # pass@k
    out.append("### T1. Fixed-phase pass@k, strict (loose in brackets for pass@1); prompt bootstrap 95 %\n")
    out.append("| prompt set | model | pass@1 | pass@8 | pass@16 | loose pass@1 |")
    out.append("|---|---|---|---|---|---|")
    for s in ("ifbench_h297", "ifbench_all300", "ifbench_s218", "ifeval_all150"):
        for m in ("base", "s0100", "s0500", "main"):
            r = st["passk"][f"{s}|{m}|strict"]
            lo = st["passk"][f"{s}|{m}|loose"]["1"]
            f = lambda k: f"{r[k][0]:.3f} [{r[k][1]:.3f}, {r[k][2]:.3f}]" if k in r else "—"
            out.append(f"| {s} | {m} | {f('1')} | {f('8')} | {f('16')} | {lo[0]:.3f} |")
    out.append("")
    out.append("### T2. Fixed-phase lengths (tokens)\n")
    out.append("| task | model | samples | mean | median | cut at 16,384 | `</think>` in text |")
    out.append("|---|---|---|---|---|---|---|")
    for k, v in st["lengths"].items():
        t, m = k.split("|")
        out.append(f"| {t} | {m} | {v['n']} | {v['mean']:.0f} | {v['median']:.0f} | {v['cut']} ({v['cut'] / v['n']:.1%}) | "
                   f"{v['think_end']} |")
    out.append("")
    out.append("### T3. Candidates and strict fates at 256 (non-excluded)\n")
    out.append("| task | R | V | R (loose) | V (loose) | REACH | resolved | base 1 success at 256 | dissolved | open | strict verdict |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for t in ("ifbench", "ifeval"):
        c = st["cands"][t]
        s = st["verdict"][t]["states"]
        out.append(f"| {t} | {len(c['R'])} | {len(c['V'])} | {len(c['R_loose'])} | {len(c['V_loose'])} | {s.get('REACH', 0)} | "
                   f"{s.get('resolved', 0)} | {s.get('base-1-at-256', 0)} | {s.get('dissolved', 0)} | {s.get('open', 0)} | "
                   f"{st['verdict'][t]['strict']} |")
    out.append("")
    if hd:
        out.append("### T4. Hand fates (my blind gate + my confirmations), every candidate the base was drawn to 256 on\n")
        out.append("| prompt | strict fate | main reads (genuine) | main status | base strict successes (genuine) | hand fate |")
        out.append("|---|---|---|---|---|---|")
        for p, c in sorted(hd["cands"].items(), key=lambda kv: (kv[1]["task"], kv[0])):
            if c["base_n"] >= 256:
                out.append(f"| {p} | {c['strict_state']} | {c['main_read']} ({c['main_genuine']}) | {c['main']} | "
                           f"{c['base_succ']} ({c['base_genuine']}) | **{c['hand_state']}** |")
        out.append("")
        out.append("| task | hand states | hand verdict | gamed share of main's first reads |")
        out.append("|---|---|---|---|")
        for t in ("ifbench", "ifeval"):
            g = hd["gamed_share"][t]
            out.append(f"| {t} | {hd['verdict'][t]['states']} | **{hd['verdict'][t]['hand']}** ({', '.join(hd['verdict'][t]['reach'])}) | "
                       f"{g['gamed']}/{g['read']} = {g['gamed'] / g['read']:.1%} |")
        out.append("")
    if cp:
        out.append("### T6. Compute axis (cumulative RL ÷ pretraining FLOPs; pre-registered definitions, my lengths)\n")
        out.append("| step | low | high | geometric mean |")
        out.append("|---|---|---|---|")
        for s, v in cp["axis"].items():
            out.append(f"| {s} | {v['low']:.2e} | {v['high']:.2e} | {v['geomean']:.2e} |")
        out.append("")
    open(os.path.join(C.OUT, "tables.md"), "w").write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
