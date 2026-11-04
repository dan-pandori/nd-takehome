#!/usr/bin/env python3
"""Word n-gram overlap between run olmo-ifomega's evaluation prompts and the Olmo 3 Think 32B post-training data.

olmo32/contam32.py's definitions (text lower-cased, [a-z0-9]+ word tokens; G(P) = distinct 8-grams of prompt P;
containment(P, D) = |G(P) & G(D)| / |G(P)|; any shared 13-gram), plus a **content** containment for templated text:
the same ratio over C(P) = the 8-grams of P that occur in fewer than DF_MAX = 20 RL prompts (IFEval-style constraint
sentences and OMEGA problem templates recur across thousands of RL prompts; a prompt's own task text does not).
If |C(P)| < 5, content containment is the raw one.

Corpora (kind -> document text): rl = Dolci-Think-RL-32B `prompt`; dpo = Dolci-Think-DPO-32B `prompt` + every turn of
`chosen` / `rejected`; sft = Dolci-Think-SFT-32B every turn of `messages`.

Modes
  df    <problems.jsonl> <template.json> <rl.parquet> ...          RL document frequency of every problem 8-gram
  scan  <problems.jsonl> <kind> <out.jsonl> <template.json> <file.parquet> ...
                          one summary row per (file, problem) with a match, plus every document with raw or content
                          containment >= 0.3 (with a text window, for reading)
  merge <problems.jsonl> <out.csv> <scan.jsonl> ...                 one row per problem and corpus
"""
import csv
import json
import os
import re
import sys
from collections import defaultdict
from multiprocessing import Pool

WORD = re.compile(r"[a-z0-9]+")
N, N_LONG, KEEP, DF_MAX, MIN_CONTENT = 8, 13, 0.3, 20, 5


def words(t):
    return WORD.findall(t.lower())


def grams(ws, n):
    return set(zip(*[ws[i:] for i in range(n)]))


def load_problems(path):
    return [json.loads(ln) for ln in open(path)]


def doc_text(kind, row):
    if kind == "rl":
        return row["prompt"] or ""
    if kind == "dpo":
        parts = [row.get("prompt") or ""]
        for k in ("chosen", "rejected"):
            v = row.get(k) or []
            parts += [m.get("content") or "" for m in v] if isinstance(v, list) else [str(v)]
        return "\n".join(parts)
    return "\n".join(m.get("content") or "" for m in (row.get("messages") or []))


def doc_id(row, j):
    for k in ("id", "prompt_id", "custom_id", "key"):
        if row.get(k):
            return str(row[k])
    return str(j)


PROBS = IDX = LONG = None  # pid -> (raw grams, content grams, long grams)


def _init(problems, template):
    global PROBS, IDX, LONG
    tmpl = set()
    if template and os.path.exists(template):
        tmpl = {tuple(g) for g in json.load(open(template))["template"]}
    PROBS, IDX, LONG = {}, defaultdict(list), defaultdict(list)
    for p in load_problems(problems):
        ws = words(p["prompt"])
        g8 = grams(ws, N)
        c8 = g8 - tmpl
        if len(c8) < MIN_CONTENT:
            c8 = g8
        PROBS[p["pid"]] = (g8, c8, grams(ws, N_LONG))
        for g in g8:
            IDX[g].append(p["pid"])
        for g in PROBS[p["pid"]][2]:
            LONG[g].append(p["pid"])


def _iter_rows(kind, path):
    import pyarrow.parquet as pq
    cols = {"rl": ["prompt", "id", "custom_id", "original_dataset"],
            "dpo": ["prompt", "chosen", "rejected", "prompt_id", "dataset", "source"],
            "sft": ["messages", "id", "source", "dataset"]}[kind]
    pf = pq.ParquetFile(path)
    cols = [c for c in cols if c in set(pf.schema_arrow.names)]
    for batch in pf.iter_batches(batch_size=500, columns=cols):
        yield from batch.to_pylist()


def df_file(path):
    df = defaultdict(int)
    for row in _iter_rows("rl", path):
        for g in grams(words(row["prompt"] or ""), N):
            if g in IDX:
                df[g] += 1
    return dict(df)


def mode_df(problems, out, files):
    tot = defaultdict(int)
    with Pool(min(len(files), int(os.environ.get("PROCS", 2))), initializer=_init, initargs=(problems, None)) as pool:
        for d in pool.imap_unordered(df_file, files):
            for g, c in d.items():
                tot[g] += c
    tmpl = sorted(list(g) for g, c in tot.items() if c >= DF_MAX)
    json.dump({"df_max": DF_MAX, "n": N, "files": [f.rsplit("/", 1)[-1] for f in files], "template": tmpl},
              open(out, "w"))
    print(f"df: {len(tot)} problem 8-grams seen in RL, {len(tmpl)} with df >= {DF_MAX} -> {out}")


def scan_file(task):
    kind, path = task
    best = {}  # pid -> [raw, content, doc, source]
    n_ge = defaultdict(int)
    n_13 = defaultdict(int)
    kept, n_docs = [], 0
    for j, row in enumerate(_iter_rows(kind, path)):
        n_docs += 1
        ws = words(doc_text(kind, row))
        hits = defaultdict(set)
        for g in zip(*[ws[i:] for i in range(N)]):
            for pid in IDX.get(g, ()):
                hits[pid].add(g)
        if not hits:
            continue
        long_hit = {pid for g in zip(*[ws[i:] for i in range(N_LONG)]) for pid in LONG.get(g, ())}
        src = str(row.get("source") or row.get("dataset") or row.get("original_dataset") or "")
        did = doc_id(row, j)
        for pid, hs in hits.items():
            g8, c8, _ = PROBS[pid]
            raw, con = len(hs) / max(len(g8), 1), len(hs & c8) / max(len(c8), 1)
            b = best.setdefault(pid, [0.0, 0.0, "", "", ""])
            if raw > b[0]:
                b[0], b[2] = raw, did
            if con > b[1]:
                b[1], b[3], b[4] = con, did, src
            n_ge[pid] += max(raw, con) >= 0.5
            if max(raw, con) >= KEEP:
                first = next(iter(hs & c8 or hs))
                k = next((i for i in range(len(ws) - N + 1) if tuple(ws[i:i + N]) == first), 0)
                kept.append({"pid": pid, "kind": kind, "file": path.rsplit("/", 1)[-1], "doc": did, "source": src,
                             "raw": round(raw, 3), "content": round(con, 3), "long13": pid in long_hit,
                             "window": " ".join(ws[max(0, k - 60):k + 140])})
        for pid in long_hit:
            n_13[pid] += 1
    out = [{"kind": kind, "file": path.rsplit("/", 1)[-1], "n_docs": n_docs, "pid": pid, "max_raw": round(b[0], 3),
            "max_content": round(b[1], 3), "best_raw_doc": b[2], "best_content_doc": b[3], "best_source": b[4],
            "n_docs_ge_0.5": n_ge[pid], "n_docs_13gram": n_13[pid]} for pid, b in best.items()]
    if not out:
        out = [{"kind": kind, "file": path.rsplit("/", 1)[-1], "n_docs": n_docs, "pid": None}]
    return out, kept


def mode_scan(problems, kind, out, template, files):
    procs = min(len(files), int(os.environ.get("PROCS", 2)))
    with Pool(procs, initializer=_init, initargs=(problems, template)) as pool, open(out, "w") as f:
        for rows, kept in pool.imap_unordered(scan_file, [(kind, p) for p in files]):
            for r in rows:
                f.write(json.dumps(r) + "\n")
            for r in kept:
                f.write(json.dumps({"kept": True, **r}) + "\n")
            f.flush()
            print(f"{rows[0]['file']}: {rows[0]['n_docs']} docs, {len(kept)} kept", flush=True)


def mode_merge(problems, out, scans):
    probs = load_problems(problems)
    agg = defaultdict(lambda: {"max_raw": 0.0, "max_content": 0.0, "best_raw_doc": "", "best_content_doc": "",
                               "best_source": "", "n_docs_ge_0.5": 0, "n_docs_13gram": 0})
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
            if r["max_raw"] > a["max_raw"]:
                a.update(max_raw=r["max_raw"], best_raw_doc=r["best_raw_doc"])
            if r["max_content"] > a["max_content"]:
                a.update(max_content=r["max_content"], best_content_doc=r["best_content_doc"],
                         best_source=r["best_source"])
            a["n_docs_ge_0.5"] += r["n_docs_ge_0.5"]
            a["n_docs_13gram"] += r["n_docs_13gram"]
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        cols = ["max_raw", "max_content", "n_docs_ge_0.5", "n_docs_13gram", "best_raw_doc", "best_content_doc",
                "best_source"]
        w.writerow(["pid", "task", "kind", "files_scanned", "docs_scanned"] + cols)
        for p in probs:
            for kind in sorted(files):
                a = agg[(p["pid"], kind)]
                w.writerow([p["pid"], p["task"], kind, len(files[kind]), sum(files[kind].values())] + [a[c] for c in cols])
    print(f"wrote {out}: files per corpus", {k: len(v) for k, v in files.items()},
          "docs", {k: sum(v.values()) for k, v in files.items()})


if __name__ == "__main__":
    m = sys.argv[1]
    if m == "df":
        mode_df(sys.argv[2], sys.argv[3], sys.argv[4:])
    elif m == "scan":
        mode_scan(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6:])
    elif m == "merge":
        mode_merge(sys.argv[2], sys.argv[3], sys.argv[4:])


# ---- OMEGA instance check: templated problems share most n-grams with their family, so n-gram containment cannot
# tell a new instance from a reworded copy. Same instance = the same ordered sequence of numbers as an RL prompt (or
# an OMEGA train problem) of any family; also the closest RL prompt by word-sequence similarity (difflib ratio).
NUM = re.compile(r"-?\d+(?:\.\d+)?")


def mode_omega(problems, out, rl_files, omega_dir):
    import difflib
    import glob
    import pyarrow.parquet as pq
    probs = [p for p in load_problems(problems) if p["task"].startswith("omega")]
    rl = []
    for f in rl_files:
        for r in pq.read_table(f, columns=["prompt", "original_dataset", "custom_id"]).to_pylist():
            if r["original_dataset"] == "hamishivi/omega-combined-no-boxed_filtered":
                t = r["prompt"][6:] if r["prompt"].startswith("user: ") else r["prompt"]
                rl.append((r["custom_id"], t))
    train = []
    for f in sorted(glob.glob(f"{omega_dir}/omega-explorative/*/train-*.parquet")):
        for r in pq.read_table(f, columns=["id", "messages"]).to_pylist():
            train.append((r["id"], r["messages"][0]["content"]))
    sig = defaultdict(list)
    for kind, docs in (("rl", rl), ("train", train)):
        for did, t in docs:
            sig[tuple(NUM.findall(t))].append((kind, did))
    by_head = defaultdict(list)  # RL prompts by their first 4 words (the family template's opening)
    for did, t in rl:
        ws = words(t)
        by_head[tuple(ws[:4])].append((did, ws))
    with open(out, "w", newline="") as g:
        w = csv.writer(g)
        w.writerow(["pid", "family", "n_numbers", "same_numbers_rl", "same_numbers_train", "max_ratio_rl",
                    "best_rl_doc"])
        for p in probs:
            s = tuple(NUM.findall(p["prompt"]))
            m = sig.get(s, [])
            pw = words(p["prompt"])
            best = (0.0, "")
            for d, ws in by_head.get(tuple(pw[:4]), []):
                sm = difflib.SequenceMatcher(None, pw, ws, autojunk=False)
                if sm.real_quick_ratio() > best[0] and sm.quick_ratio() > best[0]:
                    best = max(best, (sm.ratio(), d))
            w.writerow([p["pid"], p["family"], len(s), sum(k == "rl" for k, _ in m), sum(k == "train" for k, _ in m),
                        round(best[0], 3), best[1]])
    print(f"omega instance check: {len(probs)} problems vs {len(rl)} RL OMEGA prompts, {len(train)} train -> {out}")


if __name__ == "__main__" and sys.argv[1] == "omega":
    mode_omega(sys.argv[2], sys.argv[3], sys.argv[4:-1], sys.argv[-1])
