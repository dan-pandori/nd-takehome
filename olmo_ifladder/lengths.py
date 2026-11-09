#!/usr/bin/env python3
"""Thinking and answer lengths, no hints (pre-registration § Teachability, expectation 10): `dpo` and `s2300` from
olmo-ifomega's stored fixed-phase draws (F_dpo_*, F_s2300_*: 16 / 8 per prompt), `lora_main` / `lora_ctrl` from this
run's evaluation jobs (Leval_main / Leval_ctrl: 64 per reach prompt). Thinking tokens = response tokens through the
`</think>` marker (Olmo 3: `</` `think` = 524 27963, then `>\\n\\n`); answer words = whitespace words after the last
`</think>`. Per prompt the median, then the median over the 48 reach prompts (and over the 10 calibration prompts).

  python3 olmo_ifladder/lengths.py  -> olmo_ifladder/lengths.csv (per arm x prompt) and a summary table on stdout
"""
import array
import base64
import csv
import gzip
import json
import statistics as st
from collections import defaultdict
from pathlib import Path

A = Path("artifacts/olmo_ifladder")
OM = Path("artifacts/olmo_ifomega")
O = Path("olmo_ifladder")
SOURCES = {"dpo": [OM / "samples/F_dpo_ifb.jsonl.gz", OM / "samples/F_dpo_ife.jsonl.gz"],
           "s2300": [OM / "samples/F_s2300_ifb.jsonl.gz", OM / "samples/F_s2300_ife.jsonl.gz"],
           "lora_main": [A / "samples/Leval_main.jsonl.gz", A / "samples/Lchk_main.jsonl.gz"],
           "lora_ctrl": [A / "samples/Leval_ctrl.jsonl.gz", A / "samples/Lchk_ctrl.jsonl.gz"]}


def think_tokens(b64):
    a = array.array("i")
    a.frombytes(base64.b64decode(b64))
    for k in range(len(a) - 2, -1, -1):
        if a[k] == 524 and a[k + 1] == 27963:
            return k + 3
    return None


def main():
    pr = {r["pid"]: r for r in csv.DictReader(open(O / "prompts.csv"))}
    per = defaultdict(lambda: defaultdict(list))
    for arm, files in SOURCES.items():
        for f in files:
            if not f.exists():
                continue
            with gzip.open(f, "rt") as g:
                for ln in g:
                    r = json.loads(ln)
                    if r["pid"] not in pr:
                        continue
                    t = r["text"]
                    ans = t.rsplit("</think>", 1)[1].strip() if "</think>" in t else None
                    per[arm][r["pid"]].append((think_tokens(r["ids"]), len(ans.split()) if ans is not None else None,
                                               r["n_tok"], r["finish"]))
    rows = []
    for arm, d in per.items():
        for pid, xs in sorted(d.items()):
            th = [x[0] for x in xs if x[0] is not None]
            aw = [x[1] for x in xs if x[1] is not None]
            rows.append({"arm": arm, "pid": pid, "set": pr[pid]["set"], "draws": len(xs),
                         "think_median": st.median(th) if th else "", "answer_words_median": st.median(aw) if aw else "",
                         "no_think_end": sum(x[0] is None for x in xs), "cut": sum(x[3] == "length" for x in xs),
                         "tokens_mean": round(st.mean(x[2] for x in xs))})
    with open(O / "lengths.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("| arm | set | prompts | draws | median thinking tokens (median of prompt medians) | median answer words | mean tokens per draw |")
    print("|---|---|---|---|---|---|---|")
    for arm in SOURCES:
        for s in ("reach", "calib"):
            rr = [r for r in rows if r["arm"] == arm and r["set"] == s]
            if not rr:
                continue
            th = [r["think_median"] for r in rr if r["think_median"] != ""]
            aw = [r["answer_words_median"] for r in rr if r["answer_words_median"] != ""]
            print(f"| {arm} | {s} | {len(rr)} | {sum(r['draws'] for r in rr):,} | {st.median(th):,.0f} | {st.median(aw):.0f} | "
                  f"{st.mean(r['tokens_mean'] for r in rr):,.0f} |")


if __name__ == "__main__":
    main()
