#!/usr/bin/env python3
"""Blinded hand gate of run olmo-ifladder (pre-registration preregistration/olmo-ifladder.md, Grading and the hand gate).

olmo_iffu/handcheck.py, generalised: an item names its own samples file, graded file and problems file, so source items
(stored olmo-ifomega samples) and this run's ladder / LoRA samples use one kit. Items show the prompt as sampled
(the final user turn: `prompt_sample`, or the last turn of `messages_sample`), the constraints with the official
checker's verdict on each, and the answer (text after the last `</think>`). Ladder items (rungs 2-4) carry NOTE.

prep  <items.csv> <outdir>   items.csv: samples,graded,problems,job,pid,chunk,i,model,role,note. Writes
                             <outdir>/items/<item>.md named by a random id; the key goes to <outdir>/key.csv (readers
                             are not given it). Items already in the key keep their ids.
batch <outdir> <name> <n> [--ids a,b] writes <outdir>/batches/<name>.txt: up to n unlabelled item ids, one per line.
table <outdir> <out.csv>     merges <outdir>/labels/*.json (reader: [{"item", "label", "checker_agrees", "evidence"}]) and
                             <outdir>/confirm.csv (item,label,note: my confirmation; a label there overrides) with the key.
"""
import csv
import gzip
import json
import random
import re
import sys
from pathlib import Path

NOTE = ("(The prompt's last paragraph or paragraphs are instructions that the experimenter appended to the original "
        "request: a length limit, a reminder to check the constraints, and possibly a method hint. An answer that is "
        "short because of them is not, for that reason, gutting the request.)")


def answer_of(text):  # olmo_ifomega/grade.py answer_of, verbatim
    return text.rsplit("</think>", 1)[1].strip() if "</think>" in text else None


def final_user_turn(p):
    if p.get("messages_sample"):
        return p["messages_sample"][-1]["content"]
    return p.get("prompt_sample", p["prompt"])


def _rows(path):
    out = {}
    op = gzip.open if str(path).endswith(".gz") else open
    with op(path, "rt") as f:
        try:
            for ln in f:
                r = json.loads(ln)
                out[(r["job"], r["pid"], str(r["chunk"]), str(r["i"]))] = r
        except (EOFError, json.JSONDecodeError):
            pass
    return out


def prep(items_csv, outdir):
    out = Path(outdir)
    (out / "items").mkdir(parents=True, exist_ok=True)
    want = list(csv.DictReader(open(items_csv)))
    keyf = out / "key.csv"
    old = list(csv.DictReader(open(keyf))) if keyf.exists() else []
    have = {(r["job"], r["pid"], r["chunk"], r["i"]): r["item"] for r in old}
    used = {r["item"] for r in old}
    rng = random.Random(20261109 + len(old))
    cache = {}

    def load(path):
        if path not in cache:
            cache[path] = _rows(path)
        return cache[path]

    probs = {}
    new = []
    for w in want:
        k = (w["job"], w["pid"], str(w["chunk"]), str(w["i"]))
        if k in have:
            continue
        s = load(w["samples"])[k]
        g = load(w["graded"])[k]
        if w["problems"] not in probs:
            probs[w["problems"]] = {r["pid"]: r for r in map(json.loads, open(w["problems"]))}
        p = probs[w["problems"]][w["pid"]]
        assert g.get("strict"), k
        while True:
            item = "h%06x" % rng.randrange(16 ** 6)
            if item not in used:
                used.add(item)
                break
        ids = p["instruction_id_list"]
        ids = eval(ids) if isinstance(ids, str) else ids  # noqa: S307 (stored python-literal list)
        kw = p["kwargs"]
        kw = eval(kw) if isinstance(kw, str) else kw  # noqa: S307
        per = g.get("per") or [True] * len(ids)
        cons = "\n".join(f"- `{i}` {json.dumps({a: b for a, b in d.items() if b is not None})}: "
                         f"{'followed' if ok else 'NOT followed'} (official strict checker)"
                         for i, d, ok in zip(ids, kw, per))
        note = ("\n" + NOTE + "\n") if w.get("note") in ("1", "True", "true") else ""
        body = (f"# Item {item}\n\n## Prompt (as the model received it)\n\n{final_user_turn(p)}\n{note}\n"
                f"## Verifiable constraints\n\n{cons}\n\n## Answer\n\n{answer_of(s['text'])}\n")
        (out / "items" / f"{item}.md").write_text(body)
        new.append({"item": item, "samples": w["samples"], "graded": w["graded"], "problems": w["problems"],
                    "job": w["job"], "pid": w["pid"], "chunk": str(w["chunk"]), "i": str(w["i"]), "model": w["model"],
                    "role": w["role"], "note": w.get("note", "0"),
                    "answer_norm": re.sub(r"\s+", " ", answer_of(s["text"]) or "").strip()[:20000]})
    rows = old + new
    with open(keyf, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=["item", "samples", "graded", "problems", "job", "pid", "chunk", "i", "model",
                                           "role", "note", "answer_norm"])
        wr.writeheader()
        wr.writerows(rows)
    print(f"prep: {len(new)} new items ({len(rows)} in key)")


def labels(outdir):
    out = Path(outdir)
    lab = {}
    for f in sorted((out / "labels").glob("*.json")):
        try:
            for r in json.load(open(f)):
                lab.setdefault(r["item"], []).append((f.stem, r))
        except json.JSONDecodeError as e:
            print(f"bad json {f}: {e}", file=sys.stderr)
    conf = {}
    if (out / "confirm.csv").exists():
        for r in csv.DictReader(open(out / "confirm.csv")):
            conf[r["item"]] = r
    return lab, conf


def batch(outdir, name, n, ids=None):
    out = Path(outdir)
    key = list(csv.DictReader(open(out / "key.csv")))
    lab, _ = labels(outdir)
    todo = [r["item"] for r in key if r["item"] not in lab] if ids is None else ids
    todo = todo[:n]
    (out / "batches").mkdir(exist_ok=True)
    (out / "batches" / f"{name}.txt").write_text("\n".join(todo) + "\n")
    print(f"batch {name}: {len(todo)} items")


def table(outdir, out_csv):
    out = Path(outdir)
    key = list(csv.DictReader(open(out / "key.csv")))
    lab, conf = labels(outdir)
    rows = []
    for k in key:
        rs = lab.get(k["item"], [])
        rl = [r["label"] for _, r in rs]
        c = conf.get(k["item"])
        final = c["label"] if c and c.get("label") else (rl[0] if len(set(rl)) == 1 else "")
        rows.append({"item": k["item"], "job": k["job"], "pid": k["pid"], "chunk": k["chunk"], "i": k["i"],
                     "model": k["model"], "role": k["role"],
                     "reader_labels": " ".join(f"{b}:{r['label']}" for b, r in rs), "final_label": final,
                     "overturned": bool(c and c.get("label") and rl and c["label"] != rl[0]),
                     "reader_evidence": rs[0][1].get("evidence", "") if rs else "",
                     "my_note": c.get("note", "") if c else ""})
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"table: {len(rows)} items, {sum(1 for r in rows if r['final_label'])} labelled -> {out_csv}")


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "prep":
        prep(sys.argv[2], sys.argv[3])
    elif c == "batch":
        ids = sys.argv[sys.argv.index("--ids") + 1].split(",") if "--ids" in sys.argv else None
        batch(sys.argv[2], sys.argv[3], int(sys.argv[4]), ids)
    elif c == "table":
        table(sys.argv[2], sys.argv[3])
