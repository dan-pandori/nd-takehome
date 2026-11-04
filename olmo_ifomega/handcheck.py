#!/usr/bin/env python3
"""Blinded hand-check of the responses that decide a candidate (pre-registration olmo-ifomega, Grades / Hand).

olmo32/handcheck.py with task-specific item files: IF items show the prompt, its constraints with the official
checker's per-constraint verdicts, and the answer (the text after the last </think>; the thinking is not shown);
OMEGA items show the problem, the official answer and the whole response. Labels: IF genuine | gamed; OMEGA sound |
flawed | guess.

prep  <items.csv> <outdir>   items.csv: job,pid,chunk,i,model,side,role (one row per solution to check). Writes one
                             file per solution, <outdir>/items/<item>.md (problem, official answer, the response text
                             as RL's reward saw it), named by a random id; the key (item -> job, pid, chunk, i, model,
                             side, role) goes to <outdir>/key.csv, which the readers are not given.
table <outdir>               merges <outdir>/labels/*.json (reader: {"item", "label", "evidence"}) and
                             <outdir>/confirm.csv (item,label,note: my confirmation) with the key into
                             olmo32/handcheck.csv.
"""
import csv
import gzip
import json
import random
import sys
from pathlib import Path

A = Path("artifacts/olmo_ifomega")
O = Path("olmo_ifomega")
LABELS = {"if": ("genuine", "gamed"), "omega": ("sound", "flawed", "guess")}


def prep(items_csv, outdir):
    out = Path(outdir)
    (out / "items").mkdir(parents=True, exist_ok=True)
    probs = {r["pid"]: r for r in (json.loads(ln) for ln in open(O / "problems.jsonl"))}
    want = list(csv.DictReader(open(items_csv)))
    keyf = out / "key.csv"
    have = {(r["job"], r["pid"], r["chunk"], r["i"]): r["item"] for r in csv.DictReader(open(keyf))} if keyf.exists() else {}
    used = set(have.values())
    rng = random.Random(20261104 + len(have))
    sys.path.insert(0, str(O))
    import grade
    texts = {}
    for job in sorted({w["job"] for w in want}):
        with gzip.open(A / "samples" / f"{job}.jsonl.gz", "rt") as f:
            try:
                for ln in f:
                    r = json.loads(ln)
                    texts[(job, r["pid"], str(r["chunk"]), str(r["i"]))] = r
            except (EOFError, json.JSONDecodeError):
                pass  # a copy pulled while the job was still writing: complete rows only
    rows = []
    for w in want:
        k = (w["job"], w["pid"], str(w["chunk"]), str(w["i"]))
        if k in have:
            continue
        item = f"h{rng.randrange(16**6):06x}"
        while item in used:
            item = f"h{rng.randrange(16**6):06x}"
        used.add(item)
        r = texts[k]
        p = probs[w["pid"]]
        if p["task"] in ("ifbench", "ifeval"):
            g = grade.grade_if(p["task"], r["text"], p)
            ans = grade.answer_of(r["text"])
            think = len(r["text"]) - len(ans or "")
            cons = "\n".join(f"- `{c}` {json.dumps({a: b for a, b in kw.items() if b is not None})}: checker says "
                             f"{'followed' if ok else 'NOT followed'}"
                             for c, kw, ok in zip(p["instruction_id_list"], p["kwargs"], g["per"]))
            body = (f"# Item {item}\n\n## Prompt (sent to the model verbatim)\n\n{p['prompt']}\n\n"
                    f"## Constraints checked (official checker)\n\n{cons}\n\n"
                    f"## Answer (the text after the model's last </think>; {think} characters of thinking not shown; "
                    f"{r['n_tok']} tokens in all, finish={r['finish']})\n\n{ans}\n")
        else:
            body = (f"# Item {item}\n\n## Problem\n\n{p['prompt']}\n\n## Official answer\n\n{p['answer']}\n\n"
                    f"## Response ({r['n_tok']} tokens, finish={r['finish']})\n\n{r['text']}\n")
        (out / "items" / f"{item}.md").write_text(body)
        rows.append({"item": item, **{c: w[c] for c in ("job", "pid", "chunk", "i", "model", "side", "role")}})
    new = not keyf.exists()
    with open(keyf, "a", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=["item", "job", "pid", "chunk", "i", "model", "side", "role"])
        if new:
            wr.writeheader()
        wr.writerows(rows)
    print(f"wrote {len(rows)} items to {out / 'items'} ({len(have)} already prepared)")


def table(outdir):
    out = Path(outdir)
    key = {r["item"]: r for r in csv.DictReader(open(out / "key.csv"))}
    lab, allr = {}, {}
    for f in sorted((out / "labels").glob("*.json"), key=lambda f: f.stat().st_mtime):
        for r in json.load(open(f)):
            lab[r["item"]] = r  # the latest reader's label (consistency-pass labels supersede earlier ones)
            allr.setdefault(r["item"], []).append(f"{f.stem}:{r['label']}")
    conf = {r["item"]: r for r in csv.DictReader(open(out / "confirm.csv"))} if (out / "confirm.csv").exists() else {}
    rows = []
    for item, k in sorted(key.items(), key=lambda kv: (kv[1]["pid"], kv[1]["model"], kv[1]["job"])):
        rl = lab.get(item, {})
        c = conf.get(item, {})
        rows.append({**k, "reader_label": rl.get("label", ""), "all_reader_labels": " ".join(allr.get(item, [])),
                     "final_label": c.get("label", ""),
                     "overturned": bool(c and rl and c.get("label") != rl.get("label")),
                     "reader_evidence": (rl.get("evidence") or "")[:400].replace("\n", " "),
                     "my_note": c.get("note", "")})
    with open(O / "handcheck.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)
    print(f"handcheck.csv: {len(rows)} rows, {sum(bool(r['final_label']) for r in rows)} confirmed")


if __name__ == "__main__":
    {"prep": lambda: prep(sys.argv[2], sys.argv[3]), "table": lambda: table(sys.argv[2])}[sys.argv[1]]()
