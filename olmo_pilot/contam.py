#!/usr/bin/env python3
"""Word n-gram overlap between the evaluation problems and a training corpus.

Text is lower-cased and reduced to alphanumeric word tokens ([a-z0-9]+), so LaTeX markup and punctuation do not
matter. For each evaluation problem P with distinct 8-gram set G(P), and each training document D,
containment(P, D) = |G(P) ∩ G(D)| / |G(P)|. We report per problem the best document (max containment), the number of
documents with containment ≥ 0.5, and whether any 13-gram of P occurs in D.

Modes
  rl      <dolci.parquet> <problems.jsonl> <out.csv>          Dolci-RL-Zero-Math-7B prompts (also the nearest prompt)
  scan    <problems.jsonl> <out.jsonl> <file.jsonl.zst> ...     stream midtraining shards; one summary row per file
  merge   <out.csv> <scan.jsonl> ...                           combine scan rows into one row per problem
"""
import csv
import io
import json
import re
import sys
from collections import defaultdict

WORD = re.compile(r"[a-z0-9]+")
N, N_LONG, FLAG = 8, 13, 0.5


def words(t):
    return WORD.findall(t.lower())


def grams(ws, n):
    return set(zip(*[ws[i:] for i in range(n)]))


def load_problems(path):
    ps = [json.loads(ln) for ln in open(path)]
    return {p["pid"]: (grams(words(p["problem"]), N), grams(words(p["problem"]), N_LONG), p) for p in ps}


def index(probs):
    idx = defaultdict(list)
    for pid, (g8, _, _) in probs.items():
        for g in g8:
            idx[g].append(pid)
    long_idx = defaultdict(list)
    for pid, (_, g13, _) in probs.items():
        for g in g13:
            long_idx[g].append(pid)
    return idx, long_idx


def doc_hits(text, idx, long_idx):
    ws = words(text)
    hits = defaultdict(set)
    for g in zip(*[ws[i:] for i in range(N)]):
        for pid in idx.get(g, ()):
            hits[pid].add(g)
    long_hit = set()
    if hits:
        for g in zip(*[ws[i:] for i in range(N_LONG)]):
            for pid in long_idx.get(g, ()):
                long_hit.add(pid)
    return hits, long_hit


def idf_nearest(prompts, probs, n=5):
    """IDF-weighted n-gram containment: shared n-grams weighted by log(N / df) over the training prompts, so
    boilerplate ("relatively prime positive integers. Find m+n") counts little. Returns pid -> (score, idx)."""
    import math
    docs = [grams(words(t), n) for t in prompts]
    df = defaultdict(int)
    for g in docs:
        for x in g:
            df[x] += 1
    N_ = len(docs)
    out = {}
    for pid, (_, _, p) in probs.items():
        gp = grams(words(p["problem"]), n)
        w = {x: math.log((N_ + 1) / (df.get(x, 0) + 1)) for x in gp}
        tot = sum(w.values()) or 1.0
        best = (0.0, -1)
        for j, g in enumerate(docs):
            s = sum(w[x] for x in gp & g) / tot if gp & g else 0.0
            if s > best[0]:
                best = (s, j)
        out[pid] = best
    return out


def mode_rl(parquet, problems, out):
    import pandas as pd
    t = pd.read_parquet(parquet)
    probs = load_problems(problems)
    idx, long_idx = index(probs)
    best = {pid: (0.0, -1) for pid in probs}
    n_ge = defaultdict(int)
    long_any = defaultdict(int)
    for j, (prompt, gt) in enumerate(zip(t["prompt"], t["ground_truth"])):
        hits, long_hit = doc_hits(prompt, idx, long_idx)
        for pid, hs in hits.items():
            c = len(hs) / max(len(probs[pid][0]), 1)
            if c > best[pid][0]:
                best[pid] = (c, j)
            n_ge[pid] += c >= FLAG
        for pid in long_hit:
            long_any[pid] += 1
    near = idf_nearest(list(t["prompt"]), probs)
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pid", "set", "n_8grams", "max_containment", "best_idx", "best_answer", "same_answer",
                    "n_docs_ge_0.5", "n_docs_13gram", "flag", "idf5", "idf5_idx", "idf5_answer", "best_prompt_head",
                    "idf5_prompt_head"])
        for pid, (g8, _, p) in probs.items():
            c, j = best[pid]
            s5, j5 = near[pid]
            ans = str(t["ground_truth"].iloc[j]) if j >= 0 else ""
            w.writerow([pid, p["set"], len(g8), f"{c:.3f}", j, ans, ans.strip() == p["answer"].strip(),
                        n_ge[pid], long_any[pid], c >= FLAG, f"{s5:.3f}", j5,
                        str(t["ground_truth"].iloc[j5]) if j5 >= 0 else "",
                        (t["prompt"].iloc[j][:160].replace("\n", " ") if j >= 0 else ""),
                        (t["prompt"].iloc[j5][:300].replace("\n", " ") if j5 >= 0 else "")])
    print(f"wrote {out}")


def mode_scan(problems, out, files):
    import zstandard
    probs = load_problems(problems)
    idx, long_idx = index(probs)
    with open(out, "a") as g:
        for fn in files:
            best = {}
            n_ge = defaultdict(int)
            long_any = defaultdict(int)
            ndocs = 0
            with open(fn, "rb") as fh:
                rd = io.TextIOWrapper(zstandard.ZstdDecompressor().stream_reader(fh), encoding="utf-8")
                for ln in rd:
                    try:
                        d = json.loads(ln)
                    except json.JSONDecodeError:
                        continue
                    ndocs += 1
                    text = d.get("text") or ""
                    hits, long_hit = doc_hits(text, idx, long_idx)
                    for pid, hs in hits.items():
                        c = len(hs) / max(len(probs[pid][0]), 1)
                        if c > best.get(pid, (0.0,))[0]:
                            k = text.lower().find(" ".join(next(iter(hs))[:3]))
                            best[pid] = (c, str(d.get("id", ndocs)), text[max(0, k - 80):k + 240].replace("\n", " "))
                        n_ge[pid] += c >= FLAG
                    for pid in long_hit:
                        long_any[pid] += 1
            g.write(json.dumps({"file": fn, "docs": ndocs, "best": best, "n_ge": n_ge, "long": long_any}) + "\n")
            g.flush()


def mode_merge(out, scans):
    agg = {}
    files = docs = 0
    for s in scans:
        for ln in open(s):
            r = json.loads(ln)
            files += 1
            docs += r["docs"]
            for pid, (c, did, snip) in r["best"].items():
                a = agg.setdefault(pid, {"max": 0.0, "file": "", "id": "", "snip": "", "n_ge": 0, "long": 0})
                if c > a["max"]:
                    a.update(max=c, file=r["file"], id=did, snip=snip)
            for pid, n in r["n_ge"].items():
                agg.setdefault(pid, {"max": 0.0, "file": "", "id": "", "snip": "", "n_ge": 0, "long": 0})["n_ge"] += n
            for pid, n in r["long"].items():
                agg.setdefault(pid, {"max": 0.0, "file": "", "id": "", "snip": "", "n_ge": 0, "long": 0})["long"] += n
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pid", "max_containment", "n_docs_ge_0.5", "n_docs_13gram", "flag", "best_file", "best_id", "snippet"])
        for pid in sorted(agg):
            a = agg[pid]
            w.writerow([pid, f"{a['max']:.3f}", a["n_ge"], a["long"], a["max"] >= FLAG, a["file"].split("/data/")[-1],
                        a["id"], a["snip"][:300]])
    print(f"merged {files} files, {docs} docs -> {out}")


if __name__ == "__main__":
    m = sys.argv[1]
    if m == "rl":
        mode_rl(*sys.argv[2:5])
    elif m == "scan":
        mode_scan(sys.argv[2], sys.argv[3], sys.argv[4:])
    elif m == "merge":
        mode_merge(sys.argv[2], sys.argv[3:])
