#!/usr/bin/env python3
"""Per-prompt results of run olmo-iffu (pre-registration preregistration/olmo-iffu.md) -> olmo_iffu/results.csv.

Reads artifacts/olmo_iffu/graded/<job>.jsonl (+ <job>_trunc32k.jsonl for test 1), samples (answer word counts) and
olmo_iffu/handcheck.csv (final labels). One row per job x prompt: draws, cut share, token quantiles, grade counts,
hand counts, first / second genuine (sound) draw index (chunk * 16 + i within the job; test 3/4 continuations count on
from their chunk0), and the pre-registered outcome label. Usage: analyze.py [--print]
"""
import csv
import gzip
import json
import statistics
import sys
from pathlib import Path

A = Path("artifacts/olmo_iffu")
O = Path("olmo_iffu")
GOOD = {"genuine", "sound"}


def answer_of(text):  # olmo_ifomega/grade.py answer_of, verbatim
    return text.rsplit("</think>", 1)[1].strip() if "</think>" in text else None


def q(xs, f):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(f * len(xs)))] if xs else ""


def load_hand():
    f = O / "handcheck.csv"
    if not f.exists():
        return {}
    return {(r["job"], r["pid"], int(r["chunk"]), int(r["i"])): r["final_label"] for r in csv.DictReader(open(f))}


def jobs():
    return sorted(p.stem for p in (A / "graded").glob("T*.jsonl") if not p.stem.endswith("_trunc32k"))


def main():
    hand = load_hand()
    out = []
    for job in jobs():
        test = job.split("_")[0]
        rows = [json.loads(l) for l in open(A / "graded" / f"{job}.jsonl")]
        trunc = {}
        tf = A / "graded" / f"{job}_trunc32k.jsonl"
        if tf.exists():
            for l in open(tf):
                r = json.loads(l)
                trunc[(r["pid"], r["chunk"], r["i"])] = r
        words = {}
        sf = A / "samples" / f"{job}.jsonl.gz"
        if sf.exists() and rows and rows[0]["task"] in ("ifbench", "ifeval"):
            with gzip.open(sf, "rt") as f:
                for l in f:
                    try:
                        r = json.loads(l)
                    except json.JSONDecodeError:
                        break
                    a = answer_of(r["text"])
                    words[(r["pid"], r["chunk"], r["i"])] = None if a is None else len(a.split())
        by = {}
        for r in rows:
            by.setdefault(r["pid"], []).append(r)
        for pid, rs in sorted(by.items()):
            rs.sort(key=lambda r: (r["chunk"], r["i"]))
            model = rs[0]["model"]
            d = {"test": test, "job": job, "model": model, "pid": pid, "task": rs[0]["task"], "draws": len(rs),
                 "cut": sum(r["finish"] == "length" for r in rs),
                 "tok_mean": round(statistics.mean(r["n_tok"] for r in rs)),
                 "tok_q25_finished": q([r["n_tok"] for r in rs if r["finish"] != "length"], .25),
                 "tok_median_finished": q([r["n_tok"] for r in rs if r["finish"] != "length"], .5),
                 "tok_q75_finished": q([r["n_tok"] for r in rs if r["finish"] != "length"], .75),
                 "tok_max_finished": max([r["n_tok"] for r in rs if r["finish"] != "length"], default=""),
                 "max_tokens": rs[0].get("max_tokens", "")}
            keyed = [(r, hand.get((job, pid, r["chunk"], r["i"]), "")) for r in rs]
            if rs[0]["task"] in ("ifbench", "ifeval"):
                succ = [(r, h) for r, h in keyed if r["strict"]]
                w = [words.get((pid, r["chunk"], r["i"])) for r in rs]
                w = [x for x in w if x is not None]
                d.update({"strict": len(succ), "loose": sum(r["loose"] for r in rs),
                          "words_median": q(w, .5), "words_le60": sum(x <= 60 for x in w), "no_answer": len(rs) - len(w)})
            else:
                for g in ("omega", "rl", "doubly"):
                    d[g] = sum(r[g] for r in rs)
                d["any"] = sum(r["omega"] or r["rl"] for r in rs)
                succ = [(r, h) for r, h in keyed if r["omega"] or r["rl"]]
                if trunc:
                    t = [trunc[(pid, r["chunk"], r["i"])] for r in rs]
                    d.update({"finished_by_32k": sum(x["finish_cut"] != "length" for x in t),
                              "omega_32k": sum(x["omega"] for x in t), "rl_32k": sum(x["rl"] for x in t),
                              "any_32k": sum(x["omega"] or x["rl"] for x in t)})
                    d["sound_any_after_32k"] = sum(h == "sound" and not (trunc[(pid, r["chunk"], r["i"])]["omega"] or
                                                                          trunc[(pid, r["chunk"], r["i"])]["rl"])
                                                   for r, h in succ)
                d["sound_doubly"] = sum(h == "sound" and r["doubly"] for r, h in succ)
            labels = [h for _, h in succ]
            good = [r["chunk"] * 16 + r["i"] for r, h in succ if h in GOOD]
            d.update({"credited": len(succ), "hand_read": sum(bool(h) for h in labels),
                      "hand_good": sum(h in GOOD for h in labels), "hand_bad": sum(bool(h) and h not in GOOD for h in labels),
                      "first_good": good[0] if good else "", "second_good": good[1] if len(good) > 1 else ""})
            out.append(d)
    keys = []
    for d in out:
        keys += [k for k in d if k not in keys]
    with open(O / "results.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=keys)
        wr.writeheader()
        wr.writerows(out)
    if "--print" in sys.argv:
        for d in out:
            print(" ".join(f"{k}={d[k]}" for k in keys if k in d and k not in ("test", "task", "max_tokens")))
    print(f"results.csv: {len(out)} rows")


if __name__ == "__main__":
    main()
