#!/usr/bin/env python3
"""Draw bookkeeping of run olmo-ifcurve (pre-registration preregistration/olmo-ifcurve.md, "Reuse inventory").
VPS-side; standard library only.

  cells.py rows <job> [<job> ...]   samples + graded -> artifacts/olmo_ifcurve/rows/<job>.csv (one row per draw, no text)
  cells.py check                    draws per cell and arm for every checkpoint (stdout), from the rows files present
  cells.py plans                    olmo_ifcurve/plan/B_s0100.pids, B_s0750.pids, B_s2300.pids (arm-B top-up jobs)

A cell is (checkpoint, pid, arm). Its draws are the first N of the cell's sources, taken in the order of SOURCES and
then (chunk, i) within a source; N = N_A for arm A (8; 16 for dpo; 4 at s0050-s0500 under amendment 1), 32 for arm B's base, N_X (64 under amendment 3) for an extended arm-B cell.
Draws whose existence depended on earlier outcomes (sequential stopping, hand-gate continuations) are still i.i.d.
when taken as such a prefix; missing positions are filled by this run's jobs.

Row fields: job pid chunk i n_tok finish strict loose think_end think_tok ans_tok think_words ans_words ans_key
  think_tok = response ids before the last `</` `think` pair (524, 27963); ans_tok = ids after the 3-token marker;
  think_end = the text has "</think>" (grade.py's answer rule); words split on whitespace; ans_key = sha1 of the
  whitespace-collapsed answer (identity inheritance in the hand gate), 16 hex.
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

A = Path("artifacts/olmo_ifcurve")
ROWS = A / "rows"
# amendment 3 (2026-11-21 20:2x UTC): s0350 cancelled before its first draw (the brief's cut 2, under the $40 balance
# floor, so that the arm-B extension can run); STEP keeps it for reference
CKPTS = ["dpo", "s0050", "s0100", "s0200", "s0500", "s0750", "s1100", "s1600", "s2300"]
STEP = {c: (0 if c == "dpo" else int(c[1:])) for c in CKPTS + ["s0350"]}
NEW = ["s0050", "s0200", "s0500", "s1100", "s1600"]
STORED = {  # job -> (samples, graded): olmo-ifomega fixed phase, olmo-iffu test 4
    "F_dpo_ifb": "olmo_ifomega", "F_s0100_ifb": "olmo_ifomega", "F_s0750_ifb": "olmo_ifomega",
    "F_s2300_ifb": "olmo_ifomega", "T4_s0750": "olmo_iffu", "T4b_s0750": "olmo_iffu"}
# arm -> checkpoint -> sources in draw order (arm B's extension job X_<ckpt> is appended after the base sources)
SOURCES = {
    "A": {"dpo": ["F_dpo_ifb"], "s0100": ["F_s0100_ifb"], "s0750": ["F_s0750_ifb"], "s2300": ["F_s2300_ifb"],
          **{c: [f"M_{c}"] for c in NEW}},
    "B": {"s0100": ["F_s0100_ifb", "B_s0100"], "s0750": ["T4_s0750", "T4b_s0750", "B_s0750"], "s2300": ["B_s2300"],
          **{c: [f"M_{c}"] for c in NEW}},
}
# arm A draws per prompt: dpo 16 (stored); amendment 1 (2026-11-21, budget after the pod incident): the brief's cut 1
# (8 -> 4) at s0050 / s0200 / s0350 / s0500, all 218 prompts (reach ones: the first 4 of their 32); 8 at s1100 / s1600,
# which the pre-registered shape reading needs, and at the stored checkpoints
N_A = {"dpo": 16, "s0050": 4, "s0200": 4, "s0350": 4, "s0500": 4}
N_B, N_X = 32, 128  # amendment 4: extension back to 128 per cell (X_ / X2_ 32 draws, then X3_ 64); amendment 3 had 64
FIELDS = ["job", "pid", "chunk", "i", "n_tok", "finish", "strict", "loose", "think_end", "think_tok", "ans_tok",
          "think_words", "ans_words", "ans_key"]


def paths(job):
    d = STORED.get(job, "olmo_ifcurve")
    return Path(f"artifacts/{d}/samples/{job}.jsonl.gz"), Path(f"artifacts/{d}/graded/{job}.jsonl")


def pid_list(name):
    return [ln.strip() for ln in open(f"olmo_ifcurve/{name}") if ln.strip()]


def armA():
    return pid_list("pids_armA.txt")


def reach():
    return pid_list("pids_reach.txt")


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
    """Rows of a job as dicts with ints, {} if its rows file is absent; sorted by (pid, chunk, i)."""
    if job not in _cache:
        p = ROWS / f"{job}.csv"
        if not p.exists():
            _cache[job] = []
        else:
            xs = list(csv.DictReader(open(p)))
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


def draws(ckpt, pid, arm, ext=True):
    """The cell's draws in order (list of row dicts). arm "A": first N_A; arm "B": first 32, or first N_X (128; 64 under amendment 3, 128 again under amendment 4) when the cell
    has an extension job (X_<ckpt>) with rows for this pid and ext is True."""
    if arm == "A":
        src, n = SOURCES["A"].get(ckpt, []), N_A.get(ckpt, 8)
    else:
        src, n = list(SOURCES["B"].get(ckpt, [])), N_B
        # extension jobs: X_<ckpt> (first batch) or X2_<ckpt> (second batch, prompts with F1 after s0750); a prompt has
        # rows in at most one of them
        xj = [j for j in (f"X_{ckpt}", f"X2_{ckpt}", f"X3_{ckpt}", f"X4_{ckpt}") if by_pid(j).get(pid)]
        if ext and xj:
            src, n = src + xj, N_X
    out = []
    for j in src:
        out.extend(by_pid(j).get(pid, []))
        if len(out) >= n:
            break
    return out[:n]


def cmd_check():
    R, AA = reach(), armA()
    print("ckpt   armA_cells armA_draws(min/max)  armB_cells armB_draws(min/max) ext_cells")
    for c in CKPTS:
        a = [len(draws(c, p, "A")) for p in AA]
        b = [len(draws(c, p, "B")) for p in R] if c != "dpo" else []
        x = sum(1 for p in R if by_pid(f"X_{c}").get(p) or by_pid(f"X2_{c}").get(p) or by_pid(f"X3_{c}").get(p))
        fa = f"{sum(1 for v in a if v)} {min(a) if a else 0}/{max(a) if a else 0}"
        fb = f"{sum(1 for v in b if v)} {min(b) if b else 0}/{max(b) if b else 0}" if b else "-"
        print(f"{c:6} {fa:28} {fb:28} {x}")


def cmd_plans():
    R = reach()
    ifb = [p for p in R if p.startswith("ifbench")]
    ife = [p for p in R if p.startswith("ifeval")]
    P = Path("olmo_ifcurve/plan")
    P.mkdir(parents=True, exist_ok=True)
    have = {p: len([x for j in ("T4_s0750", "T4b_s0750") for x in by_pid(j).get(p, [])]) for p in ifb}
    s0750 = [(p, N_B - have[p]) for p in ifb if have[p] < N_B] + [(p, N_B) for p in ife]
    for name, spec in (("B_s0100", [(p, 24) for p in ifb] + [(p, 32) for p in ife]), ("B_s0750", s0750),
                       ("B_s2300", [(p, 32) for p in R])):
        (P / f"{name}.pids").write_text("".join(f"{p}:{n}\n" for p, n in spec))
        print(name, len(spec), "prompts", sum(n for _, n in spec), "draws")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "rows":
        for j in sys.argv[2:]:
            build_rows(j)
    elif cmd == "check":
        cmd_check()
    elif cmd == "plans":
        cmd_plans()
    else:
        sys.exit(__doc__)
