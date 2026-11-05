#!/usr/bin/env python3
"""Failure-mode analysis of dpo (pre-registration Part C; Dan's request 2026-11-05; secondary, from stored texts).

prep_if <outdir>   IFBench: the reach prompts where dpo has 0 strict successes within 256; per prompt and model the
                   binding constraint (the constraint the model fails most often over its samples there); a seeded
                   sample (random.Random(20261105)) of up to 4 dpo failures, one from each of 4 of its extension
                   chunks, and up to 2 s2300 failures from its fixed phase; items for blinded readers (prompt,
                   constraints with the checker's verdicts, the binding constraint, the answer; dpo and s2300 items
                   shuffled together, random ids) in <outdir>/items/, the key in <outdir>/key.csv, batch lists in
                   <outdir>/batches.txt. Responses cut at the cap are class (f) mechanically and get no item.
table_if <outdir>  merges <outdir>/labels/*.json and <outdir>/confirm.csv (item,class,note) with the key into
                   olmo_ifomega/failures_if.csv and prints shares per model, family and instruction id.
Usage: failures.py prep_if|table_if <outdir>
"""
import csv
import gzip
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

A, O = Path("artifacts/olmo_ifomega"), Path("olmo_ifomega")
K = 256
SEED = 20261105


def graded(job):
    f = A / "graded" / f"{job}.jsonl"
    return [json.loads(ln) for ln in open(f)] if f.exists() else []


def jobs_of(model, phases=("fixed", "ext", "confirm")):
    return [j for j in csv.DictReader(open(O / "jobs.csv")) if j["model"] == model and j["phase"] in phases]


def prep_if(outdir):
    out = Path(outdir)
    (out / "items").mkdir(parents=True, exist_ok=True)
    probs = {r["pid"]: r for r in map(json.loads, open(O / "problems.jsonl"))}
    excl = {r["pid"] for r in csv.DictReader(open(O / "exclusions.csv"))}
    cand = {c["pid"] for c in csv.DictReader(open(O / "candidates_fixed.csv"))
            if c["task"] == "ifbench" and c["kind"] == "reach" and not c["excluded"]}
    draws = defaultdict(list)  # (model, pid) -> [(order, chunk, i, job, phase, row)]
    for m in ("dpo", "s2300"):
        for j in jobs_of(m):
            for r in graded(j["job"]):
                if r["pid"] in cand:
                    draws[(m, r["pid"])].append((int(j["order"]), r["chunk"], r["i"], j["job"], j["phase"], r))
    for k in draws:
        draws[k] = sorted(draws[k], key=lambda t: t[:3])[:K]
    zero = sorted(p for p in cand if p not in excl and len(draws[("dpo", p)]) >= K
                  and not any(t[5]["strict"] for t in draws[("dpo", p)]))
    print(f"{len(zero)} IFBench reach prompts with dpo 0 strict in {K}")
    rng = random.Random(SEED)
    picks, binding = [], {}
    for p in zero:
        ids = probs[p]["instruction_id_list"]
        for m in ("dpo", "s2300"):
            ds = draws[(m, p)]
            rate = [sum(t[5]["per"][i] for t in ds) / len(ds) for i in range(len(ids))]
            binding[(m, p)] = min(range(len(ids)), key=lambda i: rate[i])
        ext = [t for t in draws[("dpo", p)] if t[4] == "ext" and not t[5]["strict"]]
        by_chunk = defaultdict(list)
        for t in ext:
            by_chunk[(t[3], t[1])].append(t)
        chunks = sorted(by_chunk)
        for c in sorted(rng.sample(chunks, min(4, len(chunks)))):
            picks.append(("dpo", p, rng.choice(by_chunk[c])))
        fails = [t for t in draws[("s2300", p)] if t[4] == "fixed" and not t[5]["strict"]]
        for t in rng.sample(fails, min(2, len(fails))):
            picks.append(("s2300", p, t))
    want = {(t[3], p, t[1], t[2]) for _, p, t in picks}
    texts = {}
    for job in sorted({k[0] for k in want}):
        with gzip.open(A / "samples" / f"{job}.jsonl.gz", "rt") as f:
            for ln in f:
                r = json.loads(ln)
                k = (job, r["pid"], r["chunk"], r["i"])
                if k in want:
                    texts[k] = r["text"]
    sys.path.insert(0, str(O))
    import grade
    rows, items = [], []
    used = set()
    for m, p, t in picks:
        r = t[5]
        b = binding[(m, p)]
        ids = probs[p]["instruction_id_list"]
        key = {"model": m, "job": t[3], "pid": p, "chunk": r["chunk"], "i": r["i"], "binding_k": b,
               "binding_id": ids[b], "n_constraints": len(ids), "finish": r["finish"], "n_tok": r["n_tok"]}
        if r["finish"] == "length" or not r.get("think_end", True):
            rows.append({**key, "item": "", "class_mech": "f"})
            continue
        item = f"f{rng.randrange(16**6):06x}"
        while item in used:
            item = f"f{rng.randrange(16**6):06x}"
        used.add(item)
        text = texts[(t[3], p, r["chunk"], r["i"])]
        ans = grade.answer_of(text)
        cons = "\n".join(
            f"- `{c}` {json.dumps({a: v for a, v in kw.items() if v is not None})}: checker says "
            f"{'followed' if ok else 'NOT followed'}{'   <- binding constraint' if n == b else ''}"
            for n, (c, kw, ok) in enumerate(zip(ids, probs[p]["kwargs"], r["per"])))
        body = (f"# Item {item}\n\n## Prompt (sent to the model verbatim)\n\n{probs[p]['prompt']}\n\n"
                f"## Constraints (official checker's verdict on this answer)\n\n{cons}\n\n"
                f"## Answer (the text after the model's last </think>; {len(text) - len(ans or '')} characters of "
                f"thinking not shown; {r['n_tok']} tokens in all, finish={r['finish']})\n\n{ans}\n")
        (out / "items" / f"{item}.md").write_text(body)
        rows.append({**key, "item": item, "class_mech": ""})
        items.append(item)
    with open(out / "key.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    rng.shuffle(items)
    batches = [items[n:n + 20] for n in range(0, len(items), 20)]
    (out / "batches.txt").write_text("\n".join(" ".join(b) for b in batches) + "\n")
    c = Counter((r["model"], bool(r["item"])) for r in rows)
    print(f"items: {len(items)} in {len(batches)} batches; picks {dict(c)}")


def table_if(outdir):
    out = Path(outdir)
    key = list(csv.DictReader(open(out / "key.csv")))
    lab = {}
    for f in sorted((out / "labels").glob("*.json")):
        for x in json.load(open(f)):
            lab[x["item"]] = x
    conf = {r["item"]: r for r in csv.DictReader(open(out / "confirm.csv"))} if (out / "confirm.csv").exists() else {}
    rl_ids = {r["instruction_id"] for r in csv.DictReader(open(O / "rl_if_ids.csv"))}
    near = {r["ifbench_id"]: r for r in csv.DictReader(open(O / "ifbench_rl_map.csv"))}
    rows = []
    for k in key:
        x = lab.get(k["item"], {})
        cls = k["class_mech"] or (conf[k["item"]]["class"] if k["item"] in conf else x.get("class", ""))
        bid = k["binding_id"]
        rows.append({**k, "reader_class": x.get("class", ""), "checker_agrees": x.get("checker_agrees", ""),
                     "my_class": conf.get(k["item"], {}).get("class", ""), "class": cls,
                     "family": bid.split(":")[0], "rl_similarity": "same" if bid in rl_ids else
                     near.get(bid, {}).get("similarity", "none"), "evidence": x.get("evidence", "")})
    with open(O / "failures_if.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    done = [r for r in rows if r["class"]]
    print(f"{len(done)} of {len(rows)} classified")
    for m in ("dpo", "s2300"):
        sub = [r for r in done if r["model"] == m]
        c = Counter(r["class"] for r in sub)
        print(m, len(sub), {k: f"{c[k]} ({c[k] / len(sub):.0%})" for k in "abcdef"} if sub else "")
        for g in ("family", "rl_similarity"):
            by = defaultdict(Counter)
            for r in sub:
                by[r[g]][r["class"]] += 1
            for v, cc in sorted(by.items()):
                n = sum(cc.values())
                print(f"  {g}={v:10s} n={n:3d} " + " ".join(f"{k}:{cc[k]}" for k in "abcdef"))


if __name__ == "__main__":
    {"prep_if": prep_if, "table_if": table_if}[sys.argv[1]](sys.argv[2])
