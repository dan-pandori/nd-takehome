#!/usr/bin/env python3
"""Nearest RL training prompt by embedding (brief item 6; complements contam.py's n-gram / IDF match).

Embeds the evaluation problems and the 13,314 Dolci-RL-Zero-Math-7B prompts with sentence-transformers/all-MiniLM-L6-v2
(mean-pooled, L2-normalised, via transformers) and writes, per problem, the cosine similarity of its nearest training
prompt and that prompt's row. Usage: nearest_embed.py <dolci.parquet> <problems.jsonl> <out.csv>
"""
import csv
import json
import sys

import torch
from transformers import AutoModel, AutoTokenizer

M = "sentence-transformers/all-MiniLM-L6-v2"


def embed(texts, tok, model, dev, bs=256):
    out = []
    for i in range(0, len(texts), bs):
        b = tok(texts[i:i + bs], padding=True, truncation=True, max_length=256, return_tensors="pt").to(dev)
        with torch.no_grad():
            h = model(**b).last_hidden_state
        m = b["attention_mask"].unsqueeze(-1).float()
        e = (h * m).sum(1) / m.sum(1)
        out.append(torch.nn.functional.normalize(e, dim=-1).cpu())
    return torch.cat(out)


def main():
    import pandas as pd
    pq, probs, out = sys.argv[1:4]
    d = pd.read_parquet(pq)
    train = [m[0]["content"] for m in d["messages"]]
    P = [json.loads(ln) for ln in open(probs)]
    torch.set_num_threads(4)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(M)
    model = AutoModel.from_pretrained(M).to(dev).eval()
    et = embed(train, tok, model, dev)
    ep = embed([p["problem"] for p in P], tok, model, dev)
    sim = ep @ et.T
    v, ix = sim.max(1)
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pid", "set", "emb_cos_nearest", "emb_nearest_idx", "emb_nearest_answer", "same_answer"])
        for p, s, j in zip(P, v.tolist(), ix.tolist()):
            a = str(d["ground_truth"].iloc[j])
            w.writerow([p["pid"], p["set"], f"{s:.4f}", j, a, a.strip() == p["answer"].strip()])
    print(f"wrote {out} ({len(P)} problems vs {len(train)} prompts, {M})")


if __name__ == "__main__":
    main()
