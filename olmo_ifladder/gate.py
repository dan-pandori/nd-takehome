#!/usr/bin/env python3
"""Hand-gate bookkeeping for the ladder and LoRA cells of run olmo-ifladder (pre-registration § Grading and the hand gate).

A cell = (job, reach prompt). Its strict successes are walked in draw order (chunk, i). Labels come from, in order:
the mechanical rule-1 pre-screen (MECH), this run's gate (olmo_ifladder/handcheck.csv: final_label), and identity
inheritance (an identical whitespace-collapsed answer on the same prompt, in any cell, already labelled). Reads are
needed until the cell has 2 genuine or no strict success left, and at least min(n, 4) labels (gamed share).

  gate.py items <name> <job> [<job> ...]   unlabelled successes to read next (per cell, the next LOOK in draw order),
                                           written to artifacts/olmo_ifladder/hand/round_<name>.csv and prepped
  gate.py second <name> <job> ...          deciding items (2 genuine of every elicited cell, read items only) without a
                                           second reader yet -> hand/batches/<name>.txt (existing item ids)
  gate.py status <job> [<job> ...]         per-cell table (stdout) and artifacts/olmo_ifladder/gate_status.csv
"""
import csv
import gzip
import json
import re
import subprocess
import sys
from pathlib import Path

A = Path("artifacts/olmo_ifladder")
H = A / "hand"
O = Path("olmo_ifladder")
LOOK = 4
PROBLEMS = {"R2": "olmo_ifladder/problems_r2.jsonl", "R3": "olmo_ifladder/problems_r3.jsonl",
            "R4": "olmo_ifladder/problems_r4.jsonl", "L": "olmo_ifladder/problems_plain.jsonl"}
NOTE_JOBS = ("R2", "R3", "R4")
PER_SENTENCE = {"sentence:increment", "sentence:alliteration_increment", "words:last_first", "format:emoji"}


def answer_of(text):
    return text.rsplit("</think>", 1)[1].strip() if "</think>" in text else None


def norm(a):
    return re.sub(r"\s+", " ", a or "").strip()


def ids_of(p):
    x = p["instruction_id_list"]
    return list(eval(x) if isinstance(x, str) else x)  # noqa: S307


def mech(p, ans):
    """Rule-1 pre-screen: a reason string if the pass is vacuous, else None."""
    ids = set(ids_of(p))
    a = ans or ""
    if ids & PER_SENTENCE and not re.search(r"[.!?][\"')\]]*\s+\S", a):
        return "one sentence (per-sentence constraint)"
    if "format:line_indent" in ids and sum(1 for ln in a.splitlines() if ln.strip()) < 2:
        return "single non-empty line (stairs)"
    if "format:sub-bullets" in ids and not any(ln.lstrip().startswith("*") for ln in a.splitlines()):
        return "no * bullet (sub-bullets)"
    return None


def problems_for(job):
    return {r["pid"]: r for r in map(json.loads, open(PROBLEMS[job.split("_")[0][:2] if job.startswith("R") else "L"]))}


def reach():
    return [r["pid"] for r in csv.DictReader(open(O / "prompts.csv")) if r["set"] == "reach"]


def load(job):
    texts = {}
    with gzip.open(A / "samples" / f"{job}.jsonl.gz", "rt") as f:
        try:
            for ln in f:
                r = json.loads(ln)
                texts[(r["pid"], r["chunk"], r["i"])] = r["text"]
        except (EOFError, json.JSONDecodeError):
            pass
    succ = {}
    for ln in open(A / "graded" / f"{job}.jsonl"):
        r = json.loads(ln)
        if r["strict"]:
            succ.setdefault(r["pid"], []).append((r["chunk"], r["i"]))
    for v in succ.values():
        v.sort()
    return texts, succ


def labels():
    lab, n_readers = {}, {}
    f = O / "handcheck.csv"
    if f.exists():
        for r in csv.DictReader(open(f)):
            k = (r["job"], r["pid"], int(r["chunk"]), int(r["i"]))
            n_readers[k] = len(r["reader_labels"].split())
            if r["final_label"]:
                lab[k] = (r["final_label"], "gate:" + r["item"])
    return lab, n_readers


def walk(jobs):
    lab, n_readers = labels()
    R = set(reach())
    data = {j: load(j) for j in jobs}
    probs = {j: problems_for(j) for j in jobs}
    # identity map: (pid, normalized answer) -> label, from every labelled item of these jobs and the gate
    ident = {}
    for j in jobs:
        texts, _ = data[j]
        for (jj, pid, c, i), (l, src) in lab.items():
            if jj == j and (pid, c, i) in texts:
                ident.setdefault((pid, norm(answer_of(texts[(pid, c, i)]))), (l, src))
    cells, todo = [], []
    for j in jobs:
        texts, succ = data[j]
        for pid in sorted(succ, key=lambda p: (p not in R, p)):
            if pid not in R:
                continue
            p = probs[j][pid]
            seq = []  # (key, label or None) in draw order
            mch = inh = nread = 0
            for c, i in succ[pid]:
                k = (j, pid, c, i)
                ans = answer_of(texts.get((pid, c, i), ""))
                l = None
                m = mech(p, ans)
                if m:
                    l = "gamed"
                    mch += 1
                elif k in lab:
                    l = lab[k][0]
                    nread += 1
                elif (pid, norm(ans)) in ident:
                    l = ident[(pid, norm(ans))][0]
                    inh += 1
                seq.append((k, l))
            n = len(seq)
            gen = sum(l == "genuine" for _, l in seq)
            gam = sum(l == "gamed" for _, l in seq)
            first = [l for _, l in seq[:min(n, LOOK)]]
            need_first = any(l is None for l in first)
            elicited = gen >= 2
            done_all = all(l is not None for _, l in seq)
            open_ = need_first or not (elicited or done_all)
            deciding = [k for k, l in seq if l == "genuine"][:2]
            cells.append({"job": j, "pid": pid, "strict": n, "labelled": gen + gam, "genuine": gen, "gamed": gam,
                          "mech": mch, "inherited": inh, "read": nread, "elicited": elicited,
                          "status": "open" if open_ else ("elicited" if elicited else "not elicited"),
                          "first4_read": sum(l is not None for l in first),
                          "first4_gamed": sum(l == "gamed" for l in first),
                          "deciding": " ".join(f"{c}.{i}" for _, _, c, i in deciding),
                          "second_read": all(n_readers.get(k, 0) >= 2 for k in deciding) if elicited else ""})
            if open_:
                todo += [k for k, l in seq if l is None][:LOOK]
    return cells, todo, data


def write_items(name, keys, data):
    rows = []
    for (j, pid, c, i) in keys:
        rows.append({"samples": str(A / "samples" / f"{j}.jsonl.gz"), "graded": str(A / "graded" / f"{j}.jsonl"),
                     "problems": PROBLEMS[j.split("_")[0][:2] if j.startswith("R") else "L"], "job": j, "pid": pid,
                     "chunk": c, "i": i, "model": j.split("_", 1)[1] if "_" in j else j,
                     "role": "deciding" if name.startswith("second") else "cell", "note": "1" if j.startswith(NOTE_JOBS) else "0"})
    H.mkdir(parents=True, exist_ok=True)
    f = H / f"round_{name}.csv"
    with open(f, "w", newline="") as g:
        w = csv.DictWriter(g, fieldnames=list(rows[0]) if rows else ["job"])
        w.writeheader()
        w.writerows(rows)
    if rows:
        subprocess.run([sys.executable, str(O / "handcheck.py"), "prep", str(f), str(H)], check=True)
    print(f"round {name}: {len(rows)} items -> {f}")


def cmd_status(jobs):
    cells, todo, _ = walk(jobs)
    with open(A / "gate_status.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(cells[0]))
        w.writeheader()
        w.writerows(cells)
    from collections import Counter
    for j in jobs:
        c = Counter(x["status"] for x in cells if x["job"] == j)
        f4 = [x for x in cells if x["job"] == j]
        g = sum(x["first4_gamed"] for x in f4)
        n = sum(x["first4_read"] for x in f4)
        print(f"{j}: cells with a strict success {len(f4)}; {dict(c)}; gamed share (first 4) {g}/{n}; to read {sum(1 for t in todo if t[0] == j)}")


if __name__ == "__main__":
    cmd, rest = sys.argv[1], sys.argv[2:]
    if cmd == "status":
        cmd_status(rest)
    elif cmd == "items":
        only = None
        if "--pids" in rest:  # restrict reads to these prompts (s2300 sanity cells: where dpo failed at that rung)
            k = rest.index("--pids")
            only = set(open(rest[k + 1]).read().split())
            rest = rest[:k] + rest[k + 2:]
        cells, todo, data = walk(rest[1:])
        if only is not None:
            todo = [t for t in todo if t[1] in only]
        write_items(rest[0], todo, data)
    elif cmd == "second":
        cells, _, data = walk(rest[1:])
        lab, nr = labels()
        key = {(r["job"], r["pid"], int(r["chunk"]), int(r["i"])): r["item"] for r in csv.DictReader(open(H / "key.csv"))}
        ids = []
        for x in cells:
            if x["elicited"]:
                for ci in x["deciding"].split():
                    c, i = map(int, ci.split("."))
                    k = (x["job"], x["pid"], c, i)
                    if nr.get(k, 0) < 2 and k in key:  # mech / inherited labels have no item: not re-read
                        ids.append(key[k])
        (H / "batches").mkdir(parents=True, exist_ok=True)
        (H / "batches" / f"{rest[0]}.txt").write_text("\n".join(ids) + "\n")
        print(f"second-read batch {rest[0]}: {len(ids)} items")
