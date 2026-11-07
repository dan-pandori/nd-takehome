#!/usr/bin/env python3
"""Every number of run olmo-iffu's write-up, from olmo_iffu/results.csv, status.csv, lengths_hint.csv and the metas.
Prints markdown tables (stdout) for numbers.md: test 1 per prompt (with Clopper-Pearson 95 % intervals on `dpo`'s
sound rate), test 2 / 2c per prompt, test 3 per prompt (one-sided 95 % bounds), test 4 counts, and per-job compute.
"""
import csv
import json
from math import comb
from pathlib import Path


def cp(x, n, a=0.05, one_sided=False):
    def cdf(k, p):
        return sum(comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k + 1))

    def solve(f):
        lo, hi = 0.0, 1.0
        for _ in range(80):
            m = (lo + hi) / 2
            lo, hi = (m, hi) if f(m) else (lo, m)
        return (lo + hi) / 2
    up_a = a if one_sided else a / 2
    upper = 1.0 if x == n else solve(lambda p: cdf(x, p) > up_a)
    lower = 0.0 if x == 0 else solve(lambda p: 1 - cdf(x - 1, p) < a / 2)
    return lower, upper


def short(pid):
    return pid.replace("omega_out_geometry_perpendicular_intersection_test_out_", "perp_")


def main():
    R = {(r["job"], r["pid"]): r for r in csv.DictReader(open("olmo_iffu/results.csv"))}
    S = {r["pid"]: r for r in csv.DictReader(open("olmo_iffu/status.csv"))}
    L = {(r["pid"], r["model"], r["condition"]): r for r in csv.DictReader(open("olmo_iffu/lengths_hint.csv"))}
    print("### Test 1\n\n| prompt | budget | cut | finished length q1 / median / q3 / max | credited any / doubly | "
          "sound any / doubly | `dpo` sound rate [95 %] | credited at 32,768 | label |\n|---|---|---|---|---|---|---|---|---|")
    for (job, pid), r in sorted(R.items()):
        if job != "T1_dpo":
            continue
        g, n = int(r["hand_good"]), int(r["draws"])
        lo, hi = cp(g, n)
        print(f"| {short(pid)} | {r['max_tokens']} | {r['cut']} / {n} | {r['tok_q25_finished']} / {r['tok_median_finished']} / "
              f"{r['tok_q75_finished']} / {r['tok_max_finished']} | {r['any']} / {r['doubly']} | {g} / {r['sound_doubly']} | "
              f"{g / n:.3f} [{lo:.4f}, {hi:.3f}] | {r['any_32k']} | {S[pid].get('t1_label')} |")
    print("\n### Test 2 / 2c (hint)\n\n| prompt | set | `dpo` strict / 64 | `dpo` genuine (read) | `dpo` words: unhinted → hinted "
          "(median) | `s2300` strict / 16 | `s2300` genuine (read) | `s2300` words unhinted → hinted | label |\n|---|---|---|---|---|---|---|---|---|")
    for pid, s in S.items():
        job = s.get("t2_job")
        if not job:
            continue
        d, z = R[(job, pid)], R.get((job.replace("dpo", "s2300"), pid), {})
        w = lambda m, c: L.get((pid, m, c), {}).get("words_median", "–")
        print(f"| {pid} | {'2' if job == 'T2_dpo' else '2c'} | {d['strict']} | {d['hand_good']} ({d['hand_read']}) | "
              f"{w('dpo', 'unhinted')} → {w('dpo', 'hinted')} | {z.get('strict', '–')} | {z.get('hand_good', '–')} ({z.get('hand_read', '–')}) | "
              f"{w('s2300', 'unhinted')} → {w('s2300', 'hinted')} | {s.get('t2_label')} |")
    print("\n### Test 3\n\n| prompt | new draws | strict | binding-constraint passes | genuine in 1,024 | one-sided 95 % bound |\n|---|---|---|---|---|---|")
    for (job, pid), r in sorted(R.items(), key=lambda kv: kv[0][1]):
        if job != "T3_dpo":
            continue
        g = int(r["hand_good"] or 0)
        print(f"| {pid} | {r['draws']} | {r['strict']} | see log | {g} / 1,024 | {cp(g, 1024, one_sided=True)[1]:.5f} |")
    from collections import Counter
    print("\n### Test 4\n", dict(Counter(s.get("t4_label", "untested") for s in S.values())))
    print("\n### Compute (job metas)\n\n| job | samples | tokens | t_load + t_gen (s) | tp | tok/s |\n|---|---|---|---|---|---|")
    for f in sorted(Path("artifacts/olmo_iffu/meta").glob("T*.json")):
        m = json.loads(f.read_text().strip().splitlines()[-1])
        print(f"| {m['job']} | {m['samples']:,} | {m['gen_tokens'] / 1e6:.2f} M | {m['t_load_s']:.0f} + {m['t_gen_s']:.0f} | {m['tp']} | {m['tok_per_s']:.0f} |")


if __name__ == "__main__":
    main()
