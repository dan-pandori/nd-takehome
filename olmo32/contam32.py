#!/usr/bin/env python3
"""Word n-gram overlap between the evaluation problems and the Olmo 3 Think 32B post-training data.

Definitions are the olmo-rlzero-pilot's (`olmo_pilot/contam.py`): text lower-cased and reduced to [a-z0-9]+ word
tokens; for problem P with distinct 8-gram set G(P) and document D, containment(P, D) = |G(P) ∩ G(D)| / |G(P)|; also
whether any 13-gram of P occurs in D; and, for the RL prompts, the IDF-weighted 5-gram nearest prompt.

Corpora (kind -> document text):
  rl   allenai/Dolci-Think-RL-32B  `prompt` (one RL prompt per row)
  dpo  allenai/Dolci-Think-DPO-32B `prompt` + every turn of `chosen` and `rejected`
  sft  allenai/Dolci-Think-SFT-32B every turn of `messages`

Modes
  scan  <problems.jsonl> <kind> <out.jsonl> <file.parquet> ...   one summary row per (file, problem) with a match,
                                                                  plus every document with containment >= 0.3
  idf   <problems.jsonl> <out.jsonl> <rl.parquet> ...             top-3 IDF-weighted 5-gram RL prompts per problem
  merge <problems.jsonl> <out.csv> <scan.jsonl> ...               one row per problem and corpus
"""
import csv
import json
import math
import re
import sys
from collections import defaultdict
from multiprocessing import Pool

WORD = re.compile(r"[a-z0-9]+")
N, N_LONG, KEEP = 8, 13, 0.3


def words(t):
    return WORD.findall(t.lower())


def grams(ws, n):
    return set(zip(*[ws[i:] for i in range(n)]))


def load_problems(path):
    ps = [json.loads(ln) for ln in open(path)]
    return {p["pid"]: (grams(words(p["problem"]), N), grams(words(p["problem"]), N_LONG), p) for p in ps}


PROBS = IDX = LONG = None


def _init(problems):
    global PROBS, IDX, LONG
    PROBS = load_problems(problems)
    IDX, LONG = defaultdict(list), defaultdict(list)
    for pid, (g8, g13, _) in PROBS.items():
        for g in g8:
            IDX[g].append(pid)
        for g in g13:
            LONG[g].append(pid)


def doc_text(kind, row):
    if kind == "rl":
        return row["prompt"] or ""
    if kind == "dpo":
        parts = [row.get("prompt") or ""]
        for k in ("chosen", "rejected"):
            parts += [m.get("content") or "" for m in (row.get(k) or [])]
        return "\n".join(parts)
    return "\n".join(m.get("content") or "" for m in (row.get("messages") or []))


def doc_id(kind, row, j):
    for k in ("id", "prompt_id", "custom_id", "key"):
        if row.get(k):
            return str(row[k])
    return str(j)


def scan_file(task):
    kind, path = task
    import pyarrow.parquet as pq
    cols = {"rl": ["prompt", "id", "original_dataset", "ground_truth"],
            "dpo": ["prompt", "chosen", "rejected", "prompt_id", "dataset"],
            "sft": ["messages", "id", "source"]}[kind]
    pf = pq.ParquetFile(path)
    have = set(pf.schema_arrow.names)
    cols = [c for c in cols if c in have]
    best = {}  # pid -> (containment, doc id, source)
    n_ge = defaultdict(int)
    n_13 = defaultdict(int)
    kept = []
    n_docs = 0
    j = 0
    for batch in pf.iter_batches(batch_size=1000, columns=cols):
        for row in batch.to_pylist():
            j += 1
            n_docs += 1
            text = doc_text(kind, row)
            ws = words(text)
            hits = defaultdict(set)
            for g in zip(*[ws[i:] for i in range(N)]):
                for pid in IDX.get(g, ()):
                    hits[pid].add(g)
            if not hits:
                continue
            long_hit = set()
            for g in zip(*[ws[i:] for i in range(N_LONG)]):
                for pid in LONG.get(g, ()):
                    long_hit.add(pid)
            src = str(row.get("source") or row.get("dataset") or row.get("original_dataset") or "")
            did = doc_id(kind, row, j)
            for pid, hs in hits.items():
                c = len(hs) / max(len(PROBS[pid][0]), 1)
                if c > best.get(pid, (0.0,))[0]:
                    best[pid] = (c, did, src)
                n_ge[pid] += c >= 0.5
                if c >= KEEP:
                    # a window of the document around its first shared 8-gram, for reading
                    first = next(iter(hs))
                    k = next((i for i in range(len(ws) - N + 1) if tuple(ws[i:i + N]) == first), 0)
                    kept.append({"pid": pid, "kind": kind, "file": path.rsplit("/", 1)[-1], "doc": did, "source": src,
                                 "containment": round(c, 3), "long13": pid in long_hit,
                                 "window": " ".join(ws[max(0, k - 40):k + 120]),
                                 "gt": str(row.get("ground_truth", ""))[:80]})
            for pid in long_hit:
                n_13[pid] += 1
    out = [{"kind": kind, "file": path.rsplit("/", 1)[-1], "n_docs": n_docs, "pid": pid, "max_containment": round(c, 3),
            "best_doc": d, "best_source": s, "n_docs_ge_0.5": n_ge[pid], "n_docs_13gram": n_13[pid]}
           for pid, (c, d, s) in best.items()]
    if not out:
        out = [{"kind": kind, "file": path.rsplit("/", 1)[-1], "n_docs": n_docs, "pid": None}]
    return out, kept


def mode_scan(problems, kind, out, files, procs=8):
    with Pool(procs, initializer=_init, initargs=(problems,)) as pool, open(out, "w") as f:
        for rows, kept in pool.imap_unordered(scan_file, [(kind, p) for p in files]):
            for r in rows:
                f.write(json.dumps(r) + "\n")
            for r in kept:
                f.write(json.dumps({"kept": True, **r}) + "\n")
            f.flush()
            print(f"{rows[0]['file']}: {rows[0]['n_docs']} docs, {len(kept)} kept", flush=True)


def mode_idf(problems, out, files, n=5, top=3):
    import pyarrow.parquet as pq
    probs = load_problems(problems)
    prompts, meta = [], []
    for p in files:
        t = pq.read_table(p, columns=["prompt", "id", "original_dataset", "ground_truth"]).to_pylist()
        prompts += [r["prompt"] or "" for r in t]
        meta += [(str(r["id"]), str(r["original_dataset"]), str(r["ground_truth"])[:80]) for r in t]
    docs = [grams(words(t), n) for t in prompts]
    df = defaultdict(int)
    for g in docs:
        for x in g:
            df[x] += 1
    n_ = len(docs)
    with open(out, "w") as f:
        for pid, (_, _, p) in probs.items():
            gp = grams(words(p["problem"]), n)
            w = {x: math.log((n_ + 1) / (df.get(x, 0) + 1)) for x in gp}
            tot = sum(w.values()) or 1.0
            sc = sorted(((sum(w[x] for x in gp & g) / tot, j) for j, g in enumerate(docs) if gp & g), reverse=True)[:top]
            for rank, (s, j) in enumerate(sc):
                f.write(json.dumps({"pid": pid, "rank": rank, "idf5": round(s, 3), "doc": meta[j][0],
                                    "source": meta[j][1], "gt": meta[j][2], "answer": p["answer"],
                                    "prompt": prompts[j][:600]}) + "\n")
    print(f"idf: {n_} RL prompts -> {out}")


def mode_merge(problems, out, scans):
    probs = [json.loads(ln) for ln in open(problems)]
    agg = defaultdict(lambda: {"max_containment": 0.0, "best_doc": "", "best_source": "", "n_docs_ge_0.5": 0,
                               "n_docs_13gram": 0, "n_files": 0, "n_docs": 0})
    files = defaultdict(dict)
    for s in scans:
        for ln in open(s):
            r = json.loads(ln)
            if r.get("kept"):
                continue
            files[r["kind"]][r["file"]] = r["n_docs"]
            if r["pid"] is None:
                continue
            a = agg[(r["pid"], r["kind"])]
            if r["max_containment"] > a["max_containment"]:
                a.update(max_containment=r["max_containment"], best_doc=r["best_doc"], best_source=r["best_source"])
            a["n_docs_ge_0.5"] += r["n_docs_ge_0.5"]
            a["n_docs_13gram"] += r["n_docs_13gram"]
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pid", "kind", "files_scanned", "docs_scanned", "max_containment", "n_docs_ge_0.5",
                    "n_docs_13gram", "best_doc", "best_source"])
        for p in probs:
            for kind in sorted(files):
                a = agg[(p["pid"], kind)]
                w.writerow([p["pid"], kind, len(files[kind]), sum(files[kind].values()), a["max_containment"],
                            a["n_docs_ge_0.5"], a["n_docs_13gram"], a["best_doc"], a["best_source"]])
    print(f"wrote {out}: files per corpus", {k: len(v) for k, v in files.items()},
          "docs", {k: sum(v.values()) for k, v in files.items()})


if __name__ == "__main__":
    m = sys.argv[1]
    if m == "scan":
        mode_scan(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5:], procs=int(__import__("os").environ.get("PROCS", 8)))
    elif m == "idf":
        mode_idf(sys.argv[2], sys.argv[3], sys.argv[4:])
    elif m == "merge":
        mode_merge(sys.argv[2], sys.argv[3], sys.argv[4:])
