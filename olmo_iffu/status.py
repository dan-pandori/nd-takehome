#!/usr/bin/env python3
"""Status of every olmo-ifomega reach prompt before and after each olmo-iffu test -> olmo_iffu/status.csv.

Reads olmo_iffu/results.csv (analyze.py: per job x prompt draws, strict / credited counts, hand counts). Columns per
prompt: before (olmo-ifomega: `dpo` 0 genuine / sound in 256, by the definition of a hand-reach prompt), t1 (test 1:
`dpo` sound successes / 64 at the 65,536-token budget, `any` credit; `doubly` in t1_doubly), t2 (test 2 / 2c: `dpo`
genuine successes / 64 with the hint; "2+" = reading stopped at the second genuine one; t2_s2300 = `s2300`'s genuine
successes / 16 with the hint), t3 (test 3: `dpo` genuine / 1,024 including olmo-ifomega's 256), t4 (`s0750` genuine
successes in its fresh draws), and the pre-registered label of each.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from subsets import GEO3, IFEVAL3, REACH43, HINT_CONFLICT, subsets  # noqa: E402

IFEVAL_CAPS3 = ["ifeval_1314", "ifeval_2247", "ifeval_2563"]
RULE6 = {"ifbench_290"}  # rests on ALL-CAPS answers to a title-case request (rule 6: literal reading)


def main():
    R = {}
    for r in csv.DictReader(open("olmo_iffu/results.csv")):
        R[(r["job"], r["pid"])] = r
    t2set, t3set = subsets()
    rows = []
    groups = [("geometry", GEO3), ("ifeval", IFEVAL3 + IFEVAL_CAPS3),
              ("ifbench_t2", t2set), ("ifbench_t3", t3set),
              ("ifbench_other", [p for p in REACH43 if p not in t2set and p not in t3set])]
    for grp, pids in groups:
        for pid in pids:
            d = {"group": grp, "pid": pid, "before": "0/256"}
            if pid == GEO3[2]:
                d["before_note"] = "doubly reading; 2 rl-credited dpo responses read sound in the review (any reading: 2/256)"
            if pid == GEO3[0]:
                d["before_note"] = "label corrected 17 -> 15 (doubly reading)"
            t1 = R.get(("T1_dpo", pid))
            if t1:
                g = int(t1["hand_good"])
                d.update({"t1": f"{g}/{t1['draws']}", "t1_doubly": f"{t1['sound_doubly']}/{t1['draws']}",
                          "t1_label": "token budget" if g >= 2 else "one sound success" if g == 1 else "not reached at 65k"})
            for job, sjob in (("T2_dpo", "T2_s2300"), ("T2c_dpo", "T2c_s2300")):
                t2, s2 = R.get((job, pid)), R.get((sjob, pid))
                if not t2:
                    continue
                g, strict, read = int(t2["hand_good"]), int(t2["strict"]), int(t2["hand_read"])
                more = g >= 2 and strict > read
                d["t2"] = f"{g}{'+' if more else ''}/{t2['draws']}"
                d["t2_job"] = job
                if s2:
                    sg, ss, sr = int(s2["hand_good"]), int(s2["strict"]), int(s2["hand_read"])
                    d["t2_s2300"] = f"{sg}{'+' if sg >= 2 and ss > sr else ''}/{s2['draws']}"
                    broken = sg < 2
                else:
                    broken = None
                d["t2_label"] = ("prompt-elicitable (brevity)" if g >= 2 else "one genuine with the hint" if g == 1
                                 else "not elicited; hint breaks s2300" if broken else "not elicited by the hint")
                if pid in RULE6 and g >= 2:
                    d["t2_label"] += " [literal reading; strict: not elicited]"
            t3 = R.get(("T3_dpo", pid))
            if t3:
                g = int(t3["hand_good"]) if t3["hand_good"] else 0
                d.update({"t3": f"{g}/{256 + int(t3['draws'])}",
                          "t3_label": "survives at 1,024" if g == 0 else "one genuine at <= 1,024" if g == 1 else "resolved by sampling"})
            t4 = [R[k] for k in R if k[0].startswith("T4_s0750") and k[1] == pid]
            if t4:
                g = sum(int(x["hand_good"] or 0) for x in t4)
                n = sum(int(x["draws"]) for x in t4)
                d.update({"t4": f"{g}{'+' if g >= 2 else ''}/{n}", "t4_label": "s0750 confirmed" if g >= 2 else "s0750 not confirmed"})
            if pid in HINT_CONFLICT:
                d["t2_label"] = "not in test 2 (hint conflicts: 54 names)"
            rows.append(d)
    keys = []
    for d in rows:
        keys += [k for k in d if k not in keys]
    with open("olmo_iffu/status.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=keys)
        wr.writeheader()
        wr.writerows(rows)
    from collections import Counter
    for col in ("t1_label", "t2_label", "t3_label", "t4_label"):
        print(col, dict(Counter(d.get(col, "untested") for d in rows)))
    print(f"status.csv: {len(rows)} prompts")


if __name__ == "__main__":
    main()
