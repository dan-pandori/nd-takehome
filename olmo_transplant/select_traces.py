#!/usr/bin/env python3
"""Trace manifest for run olmo-transplant: which stored olmo-ifomega samples supply the thinking.

Per prompt in olmo_transplant/prompts.csv (set reach | calib), in a seeded order (SEED, per pid):
  rl   : reach -> s2300 samples labelled genuine in olmo_ifomega/handcheck.csv (final_label), at most 4;
         calib -> s2300 strict successes of F_s2300_ifb that this run's blinded readers label genuine
                  (olmo_transplant/handcheck_src.csv), at most 4 (`prep` lists the candidates to read).
  dpo  : strict failures of F_dpo_ifb (dpo, 16 per prompt), at most 4.
Each trace records the stored token ids' sha256, think_k (tokens through the token that completes `</think>`; it is
always `>\\n\\n` or `>\\n`), c = think_k - 3 (thinking content before `</`), and the pre-draft cut (`draft_k`: the
token where the final answer's first 40 non-space-collapsed characters first appear in the thinking; empty if they
never do). Writes olmo_transplant/traces.csv.
Usage: select_traces.py prep   (calibration candidates -> olmo_transplant/handcheck_src_items.csv)
       select_traces.py build  (traces.csv)"""
import collections
import csv
import gzip
import hashlib
import json
import random
import re
import sys

sys.path.insert(0, "olmo_transplant")
from tok import Tok, ids_of, think_end

SEED = 20261108
S = "artifacts/olmo_transplant/src"
CAP = 4
DRAFT_CHARS = 40


def order(rows, pid, salt):
    rows = sorted(rows, key=lambda r: (r["job"], r["chunk"], r["i"]))
    random.Random(f"{SEED}|{salt}|{pid}").shuffle(rows)
    return rows


def norm_map(s):
    """Whitespace-collapsed copy of s and, for each of its characters, the offset in s."""
    out, pos, prev_ws = [], [], False
    for j, ch in enumerate(s):
        if ch.isspace():
            if not prev_ws and out:
                out.append(" ")
                pos.append(j)
            prev_ws = True
        else:
            out.append(ch)
            pos.append(j)
            prev_ws = False
    return "".join(out), pos


def draft_k(tok, ids, k, answer):
    """First token index t such that the thinking ids[:k] contain the final answer's opening at character offset
    inside token t (the cut keeps ids[:t]); None if the opening never appears."""
    pieces = [tok.piece[i] for i in ids[:k]]
    think = b"".join(pieces).decode("utf-8", errors="replace")
    a, _ = norm_map(answer.strip())
    a = a[:DRAFT_CHARS]
    if len(a) < 8:
        return None
    h, pos = norm_map(think)
    j = h.find(a)
    if j < 0:
        return None
    byte_off = len(think[:pos[j]].encode("utf-8", errors="replace"))
    acc = 0
    for t, pc in enumerate(pieces):
        if acc + len(pc) > byte_off:
            return t
        acc += len(pc)
    return None


def load_samples(keys):
    out = {}
    for job in sorted({k[0] for k in keys}):
        for ln in gzip.open(f"{S}/{job}.jsonl.gz", "rt"):
            r = json.loads(ln)
            k = (job, r["pid"], r["chunk"], r["i"])
            if k in keys:
                out[k] = r
    return out


def main():
    mode = sys.argv[1]
    prompts = list(csv.DictReader(open("olmo_transplant/prompts.csv")))
    idx = [json.loads(l) for l in open(f"{S}/index.jsonl")]
    by = collections.defaultdict(list)
    for r in idx:
        by[(r["job"], r["pid"])].append(r)
    if mode == "prep":
        with open("olmo_transplant/handcheck_src_items.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["job", "pid", "chunk", "i", "model", "side", "role"])
            for p in prompts:
                if p["set"] != "calib":
                    continue
                for r in order([r for r in by[("F_s2300_ifb", p["pid"])] if r["strict"]], p["pid"], "rl"):
                    w.writerow([r["job"], r["pid"], r["chunk"], r["i"], "s2300", "source", "calib-source"])
        return
    hc = list(csv.DictReader(open("olmo_ifomega/handcheck.csv")))
    gen = {(r["job"], r["pid"], int(r["chunk"]), int(r["i"])) for r in hc
           if r["model"] == "s2300" and r["final_label"] == "genuine"}
    src_lab = {}
    try:
        for r in csv.DictReader(open("olmo_transplant/handcheck_src.csv")):
            job, pid, ch, i = r["key"].split("|")
            src_lab[(job, pid, int(ch), int(i))] = r["final_label"]
    except FileNotFoundError:
        pass
    pick = []
    for p in prompts:
        pid = p["pid"]
        if p["set"] == "reach":
            rl = [r for jb in ("F_s2300_ifb", "C1_s2300_ifb", "C2_s2300_ifb") for r in by[(jb, pid)]
                  if (r["job"], pid, r["chunk"], r["i"]) in gen]
            rl = order(rl, pid, "rl")[:CAP]
        elif p["set"] == "calib":
            rl = [r for r in order([r for r in by[("F_s2300_ifb", pid)] if r["strict"]], pid, "rl")
                  if src_lab.get((r["job"], pid, r["chunk"], r["i"])) == "genuine"][:CAP]
        else:
            continue
        dp = order([r for r in by[("F_dpo_ifb", pid)] if not r["strict"] and r["think_k"]], pid, "dpo")[:CAP]
        for kind, rows in (("rl", rl), ("dpo", dp)):
            for n, r in enumerate(rows):
                pick.append((p["set"], kind, n, r))
    keys = {(r["job"], r["pid"], r["chunk"], r["i"]) for _, _, _, r in pick}
    samples = load_samples(keys)
    tok = Tok()
    with open("olmo_transplant/traces.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["trace", "set", "pid", "kind", "rank", "job", "chunk", "i", "src_model", "n_tok", "think_k", "c",
                    "draft_k", "close_tok", "ids_sha256", "prefix_sha256", "label_source"])
        for st, kind, n, r in pick:
            s = samples[(r["job"], r["pid"], r["chunk"], r["i"])]
            ids = ids_of(s)
            assert tok.decode(ids) == s["text"]
            k, clean, tail = think_end(tok, ids)
            assert ids[k - 3:k - 1] == [524, 27963] and ids[k - 1] in (1363, 397), (r, ids[k - 3:k])
            ans = s["text"].split("</think>", 1)[1]
            dk = draft_k(tok, ids, k, ans) if kind == "rl" else None
            lab = "olmo_ifomega/handcheck.csv" if (st, kind) == ("reach", "rl") else \
                ("olmo_transplant/handcheck_src.csv" if kind == "rl" else "strict failure (F_dpo_ifb)")
            w.writerow([f"{r['pid']}|{kind}{n}", st, r["pid"], kind, n, r["job"], r["chunk"], r["i"], s["model"],
                        len(ids), k, k - 3, "" if dk is None else dk, ids[k - 1],
                        hashlib.sha256(json.dumps(ids).encode()).hexdigest(),
                        hashlib.sha256(json.dumps(ids[:k]).encode()).hexdigest(), lab])
    c = collections.Counter((st, kind) for st, kind, _, _ in pick)
    print(c)


if __name__ == "__main__":
    main()
