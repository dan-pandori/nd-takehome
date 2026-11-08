#!/usr/bin/env python3
"""Blinded hand gate of run olmo-transplant (pre-registration preregistration/olmo-transplant.md, Hand gate).

olmo_iffu/handcheck.py adapted: an item is any strict IF success, either a stored source sample (calibration traces)
or an answer sampled by this run. Readers see the prompt, the constraints with the checker's per-constraint verdicts
and the answer (the text after the last `</think>`), never the thinking, its length, the condition or the model.
Item ids are random; the key is kept from readers.

prep  <items.csv> <outdir>  items.csv: samples,graded,key (key = "job|pid|chunk|i" for stored samples, "rid|i" for this
                            run's rows), plus any extra columns, which are copied to the key. Writes
                            <outdir>/items/<item>.md and appends <outdir>/key.csv.
batch <outdir> <size> [seed] writes <outdir>/batches.json: unread items shuffled into batches.
table <outdir> <out.csv>    merges <outdir>/labels/*.json (reader: [{"item", "label", "checker_agrees", "evidence"}];
                            file stem = reader id) and <outdir>/adjudicate.csv (item,label,note) into one row per item:
                            all reader labels, the majority, the adjudicated label, final_label, and r6 (a title-case
                            prompt whose reader evidence says "all caps": rule 6's strict reading drops it).
"""
import collections
import csv
import gzip
import json
import random
import re
import sys
from pathlib import Path

PROBLEMS = "olmo_ifomega/problems.jsonl"


def answer_of(text):  # olmo_ifomega/grade.py answer_of, verbatim
    return text.rsplit("</think>", 1)[1].strip() if "</think>" in text else None


def row_key(r):
    return f"{r['rid']}|{r['i']}" if "rid" in r else f"{r['job']}|{r['pid']}|{r['chunk']}|{r['i']}"


def full_text(r):
    """The text the grader sees: stored samples carry their thinking; this run's rows carry only the sampled answer
    after an inserted thinking that ends in `</think>`."""
    return r["text"] if "rid" not in r else "</think>" + r["text"]


def load(path, keys, gz=True):
    out = {}
    op = gzip.open if gz else open
    with op(path, "rt") as f:
        try:
            for ln in f:
                r = json.loads(ln)
                k = row_key(r)
                if k in keys:
                    out[k] = r
        except (EOFError, json.JSONDecodeError):
            pass  # a copy pulled while the job was still writing: complete rows only
    return out


def prep(items_csv, outdir):
    out = Path(outdir)
    (out / "items").mkdir(parents=True, exist_ok=True)
    want = list(csv.DictReader(open(items_csv)))
    keyf = out / "key.csv"
    old = list(csv.DictReader(open(keyf))) if keyf.exists() else []
    have = {r["key"] for r in old}
    used = {r["item"] for r in old}
    rng = random.Random(20261108 + len(old))
    probs = {r["pid"]: r for r in map(json.loads, open(PROBLEMS))}
    texts, grades = {}, {}
    by_file = collections.defaultdict(set)
    for w in want:
        by_file[(w["samples"], w["graded"])].add(w["key"])
    for (sf, gf), keys in by_file.items():
        texts.update(load(sf, keys))
        grades.update(load(gf, keys, gz=False))
    rows = []
    extra = [c for c in want[0].keys() if c not in ("samples", "graded", "key")] if want else []
    for w in want:
        k = w["key"]
        if k in have:
            continue
        item = f"h{rng.randrange(16 ** 6):06x}"
        while item in used:
            item = f"h{rng.randrange(16 ** 6):06x}"
        used.add(item)
        have.add(k)
        r, g = texts[k], grades[k]
        assert g["strict"], f"not a strict success: {k}"
        p = probs[r["pid"]]
        ans = answer_of(full_text(r))
        cons = "\n".join(f"- `{c}` {json.dumps({a: b for a, b in kw.items() if b is not None})}: checker says "
                         f"{'followed' if ok else 'NOT followed'}"
                         for c, kw, ok in zip(p["instruction_id_list"], p["kwargs"], g["per"]))
        cut = " The answer was cut off at the length limit." if r["finish"] == "length" else ""
        body = (f"# Item {item}\n\n## Prompt (sent to the model verbatim)\n\n{p['prompt']}\n\n"
                f"## Constraints checked (official checker)\n\n{cons}\n\n"
                f"## Answer (the text after the model's private reasoning, which is not shown; "
                f"{len((ans or '').split())} words){cut}\n\n{ans}\n")
        (out / "items" / f"{item}.md").write_text(body)
        rows.append({"item": item, "key": k, "pid": r["pid"], "samples": w["samples"],
                     **{c: w[c] for c in extra}})
    fields = ["item", "key", "pid", "samples"] + extra
    new = not keyf.exists()
    with open(keyf, "a", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        if new:
            wr.writeheader()
        wr.writerows(rows)
    print(f"wrote {len(rows)} items to {out / 'items'} ({len(old)} already prepared)")


def labels(outdir):
    out = Path(outdir)
    lab = collections.defaultdict(list)
    for f in sorted((out / "labels").glob("*.json")):
        for r in json.load(open(f)):
            lab[r["item"]].append((f.stem, r["label"], (r.get("evidence") or "").replace("\n", " ")))
    return lab


def batch(outdir, size, seed=1):
    out = Path(outdir)
    key = [r["item"] for r in csv.DictReader(open(out / "key.csv"))]
    lab = labels(outdir)
    todo = [k for k in key if k not in lab]
    random.Random(int(seed)).shuffle(todo)
    b = [todo[i:i + int(size)] for i in range(0, len(todo), int(size))]
    json.dump(b, open(out / "batches.json", "w"), indent=0)
    print(f"{len(todo)} unread items in {len(b)} batches")


def table(outdir, out_csv):
    out = Path(outdir)
    key = list(csv.DictReader(open(out / "key.csv")))
    lab = labels(outdir)
    adj = {r["item"]: r for r in csv.DictReader(open(out / "adjudicate.csv"))} if (out / "adjudicate.csv").exists() else {}
    probs = {r["pid"]: r for r in map(json.loads, open(PROBLEMS))}
    rows = []
    for k in key:
        ls = lab.get(k["item"], [])
        title = "format:title_case" in probs[k["pid"]]["instruction_id_list"]
        r6 = title and any(re.search(r"all[ -]?caps", e, re.I) for _, _, e in ls)
        c = collections.Counter(l for _, l, _ in ls)
        maj = c.most_common(1)[0][0] if ls and (len(c) == 1 or c.most_common(2)[0][1] > c.most_common(2)[1][1]) else ""
        a = adj.get(k["item"], {})
        final = a.get("label") or maj
        rows.append({**k, "reader_labels": " ".join(f"{s}:{l}" for s, l, _ in ls), "n_readers": len(ls),
                     "majority": maj, "adjudicated": a.get("label", ""), "final_label": final,
                     "r6": r6, "evidence_1": ls[0][2][:400] if ls else "", "note": a.get("note", "")})
    with open(out_csv, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)
    print(f"{out_csv}: {len(rows)} rows; final labels {collections.Counter(r['final_label'] for r in rows)}")


if __name__ == "__main__":
    {"prep": lambda: prep(sys.argv[2], sys.argv[3]), "batch": lambda: batch(*sys.argv[2:5]),
     "table": lambda: table(sys.argv[2], sys.argv[3])}[sys.argv[1]]()
