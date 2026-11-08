#!/usr/bin/env python3
"""Word n-gram overlap of run olmo-rlzero-if's evaluation prompts with RL-Zero-IF's training prompts.

olmo_ifomega/contam.py's definitions, one corpus: allenai/Dolci-RL-Zero-IF-7B @ c96e4e42 (13,179 prompts; the
`prompt` field without its "user: " prefix). Text lower-cased, [a-z0-9]+ word tokens; G(P) = distinct 8-grams of P;
raw containment(P, D) = |G(P) & G(D)| / |G(P)|; any shared 13-gram; **content** containment = the same ratio over
C(P) = the 8-grams of P that occur in fewer than DF_MAX = 20 RL prompts (constraint sentences recur in thousands of RL
prompts; a prompt's own request does not); if |C(P)| < 5 the content containment is the raw one.
Exclusion rule (olmo-ifomega's, pre-registered): content >= 0.5 or raw >= 0.8 against any RL prompt, or a variant
(the same request with other constraints) confirmed by reading among the matches with raw or content >= 0.3.

Usage: contam.py <problems.jsonl> <dolci.parquet> <out.csv> <read.jsonl>
  out.csv: one row per evaluation prompt (best raw / content match, shared 13-gram, auto flag);
  read.jsonl: every (prompt, RL prompt) pair with raw or content >= 0.3, with both texts, for reading.
"""
import csv
import json
import re
import sys
from collections import Counter, defaultdict

WORD = re.compile(r"[a-z0-9]+")
N, N_LONG, KEEP, DF_MAX, MIN_CONTENT = 8, 13, 0.3, 20, 5


def words(t):
    return WORD.findall(t.lower())


def grams(ws, n):
    return {hash(g) for g in zip(*[ws[i:] for i in range(n)])}


def main():
    import pandas as pd
    probs_path, pq, out_csv, read_path = sys.argv[1:5]
    probs = [json.loads(l) for l in open(probs_path)]
    df = pd.read_parquet(pq)
    docs = [(str(k), p[len("user: "):] if p.startswith("user: ") else p) for k, p in zip(df["key"], df["prompt"])]
    dg8 = [grams(words(t), N) for _, t in docs]
    dfreq = Counter(g for s in dg8 for g in s)
    inv = defaultdict(list)
    for j, s in enumerate(dg8):
        for g in s:
            inv[g].append(j)
    rows, reads = [], []
    for p in probs:
        ws = words(p["prompt"])
        g8, g13 = grams(ws, N), grams(ws, N_LONG)
        content = {g for g in g8 if dfreq.get(g, 0) < DF_MAX}
        use_c = content if len(content) >= MIN_CONTENT else g8
        hits = Counter(j for g in g8 for j in inv.get(g, ()))
        best = {"raw": 0.0, "content": 0.0, "raw_doc": "", "content_doc": "", "share13": False}
        for j, h in hits.items():
            raw = h / len(g8) if g8 else 0.0
            con = len(use_c & dg8[j]) / len(use_c) if use_c else 0.0
            if raw > best["raw"]:
                best["raw"], best["raw_doc"] = raw, docs[j][0]
            if con > best["content"]:
                best["content"], best["content_doc"] = con, docs[j][0]
            if raw >= KEEP or con >= KEEP:
                reads.append({"pid": p["pid"], "task": p["task"], "rl_key": docs[j][0], "raw": round(raw, 3),
                              "content": round(con, 3), "prompt": p["prompt"], "rl_prompt": docs[j][1]})
        best["share13"] = any(g in inv and dfreq[g] > 0 for g in g13) and bool(
            g13 & set().union(*(grams(words(docs[j][1]), N_LONG) for j, _ in hits.most_common(20)))) if hits else False
        auto = best["content"] >= 0.5 or best["raw"] >= 0.8
        rows.append({"pid": p["pid"], "task": p["task"], "n8": len(g8), "n_content": len(content),
                     "rl_max_raw": round(best["raw"], 3), "rl_raw_doc": best["raw_doc"],
                     "rl_max_content": round(best["content"], 3), "rl_content_doc": best["content_doc"],
                     "share13_top20": best["share13"], "auto_excl": auto,
                     "n_read": sum(r["pid"] == p["pid"] for r in reads)})
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with open(read_path, "w") as f:
        for r in reads:
            f.write(json.dumps(r) + "\n")
    for t in ("ifbench", "ifeval"):
        rt = [r for r in rows if r["task"] == t]
        print(t, len(rt), "auto_excl", sum(r["auto_excl"] for r in rt), "to read (>=0.3)",
              sum(r["n_read"] > 0 for r in rt), "max raw", max(r["rl_max_raw"] for r in rt),
              "max content", max(r["rl_max_content"] for r in rt))


if __name__ == "__main__":
    main()
