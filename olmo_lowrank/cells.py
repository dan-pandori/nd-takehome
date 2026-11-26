#!/usr/bin/env python3
"""Draw bookkeeping of run olmo-lowrank (VPS side, standard library only). olmo-ifcurve's cells.py row format and
functions (answer_of, ans_key, split_ids, build_rows), with this run's jobs and the stored endpoint jobs.

  cells.py rows <job> [<job> ...]   samples + graded -> artifacts/olmo_lowrank/rows/<job>.csv (one row per draw, no text)
  cells.py check                    draws, strict and cut per arm and set (stdout), from the rows files present

Arms (this run, artifacts/olmo_lowrank): dpo T1 T4 T16 T64 T256 F448 C16 (job = arm name; 1,472 draws each:
48 reach prompts x 16, 176 other arm-A prompts x 4). Stored endpoint jobs: B_s2300 (olmo-ifcurve; reach x 32),
F_s2300_ifb and F_dpo_ifb (olmo-ifomega; arm A x 8 / x 16).
"""
import base64
import csv
import gzip
import hashlib
import json
import re
import sys
from array import array
from pathlib import Path

A = Path("artifacts/olmo_lowrank")
ROWS = A / "rows"
ARMS = ["dpo", "T1", "T4", "T16", "T64", "T256", "F448", "C16"]
STORED = {"B_s2300": "olmo_ifcurve", "F_s2300_ifb": "olmo_ifomega", "F_dpo_ifb": "olmo_ifomega"}
FIELDS = ["job", "pid", "chunk", "i", "n_tok", "finish", "strict", "loose", "think_end", "think_tok", "ans_tok",
          "think_words", "ans_words", "ans_key"]


def paths(job):
    d = STORED.get(job, "olmo_lowrank")
    return Path(f"artifacts/{d}/samples/{job}.jsonl.gz"), Path(f"artifacts/{d}/graded/{job}.jsonl")


def pid_list(name):
    return [ln.strip() for ln in open(f"olmo_ifcurve/{name}") if ln.strip()]


def armA():
    return pid_list("pids_armA.txt")


def reach():
    return pid_list("pids_reach.txt")


def others():
    r = set(reach())
    return [p for p in armA() if p not in r]


def answer_of(text):  # olmo_ifomega/grade.py answer_of, verbatim
    return text.rsplit("</think>", 1)[1].strip() if "</think>" in text else None


def norm(a):
    return re.sub(r"\s+", " ", a or "").strip()


def ans_key(a):
    return hashlib.sha1(norm(a).encode()).hexdigest()[:16]


def split_ids(ids):
    """(thinking tokens, answer tokens) around the last `</` `think` pair; (len, 0) if there is none."""
    for j in range(len(ids) - 2, -1, -1):
        if ids[j] == 524 and ids[j + 1] == 27963:
            return j, max(0, len(ids) - (j + 3))
    return len(ids), 0


def build_rows(job):
    sp, gp = paths(job)
    grades = {}
    for ln in open(gp):
        g = json.loads(ln)
        grades[(g["pid"], int(g["chunk"]), int(g["i"]))] = g
    out, missing = [], 0
    with gzip.open(sp, "rt") as f:
        for ln in f:
            try:
                r = json.loads(ln)
            except json.JSONDecodeError:
                break
            k = (r["pid"], int(r["chunk"]), int(r["i"]))
            g = grades.get(k)
            if g is None:
                missing += 1
                continue
            ids = array("i")
            ids.frombytes(base64.b64decode(r["ids"]))
            tt, at = split_ids(ids)
            t = r["text"]
            a = answer_of(t)
            think = t.rsplit("</think>", 1)[0] if a is not None else t
            out.append({"job": job, "pid": k[0], "chunk": k[1], "i": k[2], "n_tok": r["n_tok"], "finish": r["finish"],
                        "strict": int(bool(g["strict"])), "loose": int(bool(g.get("loose"))),
                        "think_end": int(a is not None), "think_tok": tt, "ans_tok": at,
                        "think_words": len(think.split()), "ans_words": len(a.split()) if a is not None else 0,
                        "ans_key": ans_key(a) if a is not None else ""})
    ROWS.mkdir(parents=True, exist_ok=True)
    out.sort(key=lambda x: (x["pid"], x["chunk"], x["i"]))
    with open(ROWS / f"{job}.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(out)
    print(f"{job}: {len(out)} rows ({missing} sample rows without a grade, {len(grades) - len(out)} grades unmatched)")


_cache = {}


def rows(job):
    """Rows of a job as dicts with ints, [] if its rows file is absent; sorted by (pid, chunk, i)."""
    if job not in _cache:
        p = ROWS / f"{job}.csv"
        xs = list(csv.DictReader(open(p))) if p.exists() else []
        for x in xs:
            for k in ("chunk", "i", "n_tok", "strict", "loose", "think_end", "think_tok", "ans_tok", "think_words",
                      "ans_words"):
                x[k] = int(x[k])
        _cache[job] = xs
    return _cache[job]


def by_pid(job):
    key = ("by_pid", job)
    if key not in _cache:
        d = {}
        for x in rows(job):
            d.setdefault(x["pid"], []).append(x)
        _cache[key] = d
    return _cache[key]


def cmd_check():
    R, O = set(reach()), set(others())
    print("job        set     prompts draws strict  cut  no_think_end")
    for job in ARMS + list(STORED):
        bp = by_pid(job)
        for name, S in (("reach", R), ("others", O)):
            xs = [x for p in S for x in bp.get(p, [])]
            if not xs:
                continue
            print(f"{job:10s} {name:7s} {len({x['pid'] for x in xs}):7d} {len(xs):5d} {sum(x['strict'] for x in xs):6d} "
                  f"{sum(x['finish'] == 'length' for x in xs):4d} {sum(1 - x['think_end'] for x in xs):5d}")


if __name__ == "__main__":
    if sys.argv[1] == "rows":
        for j in sys.argv[2:]:
            build_rows(j)
    elif sys.argv[1] == "check":
        cmd_check()
