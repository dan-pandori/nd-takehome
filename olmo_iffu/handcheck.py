#!/usr/bin/env python3
"""Blinded hand check of run olmo-iffu (pre-registration preregistration/olmo-iffu.md, Hand gate).

olmo_ifomega/handcheck.py with three changes: items are built from the graded rows (per-constraint verdicts from
artifacts/olmo_iffu/graded/<job>.jsonl), so prep runs on the VPS without the checkers' dependencies; IF items show the
prompt as sampled (`prompt_sample`, i.e. with test 2's hint, when present); problems come from the job's own problems
file (JOBS below). Labels: IF genuine | gamed; OMEGA sound | flawed | guess.

prep  <items.csv> <outdir>   items.csv: job,pid,chunk,i,model,side,role. Writes <outdir>/items/<item>.md named by a random
                             id; the key (item -> job, pid, chunk, i, model, side, role) goes to <outdir>/key.csv, which
                             readers are not given.
table <outdir>               merges <outdir>/labels/*.json (reader: [{"item", "label", ...}]) and <outdir>/confirm.csv
                             (item,label,note: my confirmation) with the key into olmo_iffu/handcheck.csv.
"""
import csv
import gzip
import json
import random
import sys
from pathlib import Path

A = Path("artifacts/olmo_iffu")
O = Path("olmo_iffu")
PROBLEMS = {"T1": "olmo_iffu/problems_geo.jsonl", "T2": "olmo_iffu/problems_hint.jsonl", "T2c": "olmo_iffu/problems_hint2c.jsonl",
            "T3": "olmo_ifomega/problems.jsonl", "T4": "olmo_ifomega/problems.jsonl", "T4b": "olmo_ifomega/problems.jsonl"}
HINT_NOTE = ("(The prompt's last paragraph is a length limit that the experimenter appended to the original request; an "
             "answer that is short because of it is not, for that reason, gutting the request.)")


def answer_of(text):  # olmo_ifomega/grade.py answer_of, verbatim
    return text.rsplit("</think>", 1)[1].strip() if "</think>" in text else None


def problems_for(job):
    return {r["pid"]: r for r in map(json.loads, open(PROBLEMS[job.split("_")[0]]))}


def prep(items_csv, outdir):
    out = Path(outdir)
    (out / "items").mkdir(parents=True, exist_ok=True)
    want = list(csv.DictReader(open(items_csv)))
    keyf = out / "key.csv"
    have = {(r["job"], r["pid"], r["chunk"], r["i"]): r["item"] for r in csv.DictReader(open(keyf))} if keyf.exists() else {}
    used = set(have.values())
    rng = random.Random(20261106 + len(have))
    texts, grades = {}, {}
    for job in sorted({w["job"] for w in want}):
        with gzip.open(A / "samples" / f"{job}.jsonl.gz", "rt") as f:
            try:
                for ln in f:
                    r = json.loads(ln)
                    texts[(job, r["pid"], str(r["chunk"]), str(r["i"]))] = r
            except (EOFError, json.JSONDecodeError):
                pass  # a copy pulled while the job was still writing: complete rows only
        for ln in open(A / "graded" / f"{job}.jsonl"):
            r = json.loads(ln)
            grades[(job, r["pid"], str(r["chunk"]), str(r["i"]))] = r
    rows = []
    for w in want:
        k = (w["job"], w["pid"], str(w["chunk"]), str(w["i"]))
        if k in have:
            continue
        item = f"h{rng.randrange(16**6):06x}"
        while item in used:
            item = f"h{rng.randrange(16**6):06x}"
        used.add(item)
        r, g = texts[k], grades[k]
        p = problems_for(w["job"])[w["pid"]]
        if p["task"] in ("ifbench", "ifeval"):
            ans = answer_of(r["text"])
            think = len(r["text"]) - len(ans or "")
            cons = "\n".join(f"- `{c}` {json.dumps({a: b for a, b in kw.items() if b is not None})}: checker says "
                             f"{'followed' if ok else 'NOT followed'}"
                             for c, kw, ok in zip(p["instruction_id_list"], p["kwargs"], g["per"]))
            sent = p.get("prompt_sample", p["prompt"])
            note = f"\n\n{HINT_NOTE}" if "prompt_sample" in p else ""
            body = (f"# Item {item}\n\n## Prompt (sent to the model verbatim){note}\n\n{sent}\n\n"
                    f"## Constraints checked (official checker)\n\n{cons}\n\n"
                    f"## Answer (the text after the model's last </think>; {think} characters of thinking not shown; "
                    f"{r['n_tok']} tokens in all, finish={r['finish']}; {len((ans or '').split())} words)\n\n{ans}\n")
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
    return rows


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
    for item, k in sorted(key.items(), key=lambda kv: (kv[1]["job"], kv[1]["pid"], int(kv[1]["chunk"]), int(kv[1]["i"]))):
        rl = lab.get(item, {})
        c = conf.get(item, {})
        rows.append({**k, "reader_label": rl.get("label", ""), "all_reader_labels": " ".join(allr.get(item, [])),
                     "where": rl.get("where", ""), "final_label": c.get("label", ""),
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
