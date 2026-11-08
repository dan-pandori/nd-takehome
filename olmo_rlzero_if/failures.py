#!/usr/bin/env python3
"""Format check of the base on the reach prompts (pre-registration Design 6 and Part B; from stored texts).

olmo_ifomega/failures.py (prep_if / table_if) for run olmo-rlzero-if.
prep_if <outdir>   Prompts: every non-excluded reach candidate (IFBench and IFEval) on which main is hand-confirmed
                   and the base has drawn 256 with no genuine success (`--all-tier1` style selection is done by the
                   caller through --pids). Per prompt and model the binding constraint (the constraint the model fails
                   most often over its draws there); a seeded sample (random.Random(20261108)) of up to 4 base failures
                   from 4 different extension chunks, and up to 2 main failures (any phase), as blinded items (prompt,
                   constraints with the checker's verdicts, the binding constraint, the answer the checker graded;
                   base and main shuffled together, random ids) in <outdir>/items/, the key in <outdir>/key.csv,
                   batch lists in <outdir>/batches.txt. A response cut at the cap with an empty answer is (u)
                   mechanically and gets no item.
table_if <outdir>  merges <outdir>/labels/*.json and <outdir>/confirm.csv (item,class,note) with the key into
                   olmo_rlzero_if/failures_if.csv and prints shares per model and per family.
Usage: failures.py prep_if <outdir> [--pids a,b,...] | table_if <outdir> [<outdir> ...]  (one table, column `set`)
"""
import csv
import gzip
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import grade  # noqa: E402

A, O = Path("artifacts/olmo_rlzero_if"), Path("olmo_rlzero_if")
K = 256
SEED = 20261108


def grade_ids(p):
    return grade._ids(p)


def graded(job):
    f = A / "graded" / f"{job}.jsonl"
    return [json.loads(ln) for ln in open(f)] if f.exists() else []


def jobs_of(model, phases=("fixed", "ext", "confirm")):
    return [j for j in csv.DictReader(open(O / "jobs.csv")) if j["model"] == model and j["phase"] in phases]


def prep_if(outdir):
    out = Path(outdir)
    (out / "items").mkdir(parents=True, exist_ok=True)
    probs = {r["pid"]: r for r in map(json.loads, open(O / "problems.jsonl"))}
    excl = {r["pid"] for r in csv.DictReader(open(O / "exclusions.csv")) if r["decision"] == "excluded"}
    want_p = None
    if "--pids" in sys.argv:
        want_p = set(sys.argv[sys.argv.index("--pids") + 1].split(","))
    cand = {c["pid"] for c in csv.DictReader(open(O / "candidates_fixed.csv"))
            if c["kind"] == "reach" and not c["excluded"] and (want_p is None or c["pid"] in want_p)}
    draws = defaultdict(list)  # (model, pid) -> [(order, chunk, i, job, phase, row)]
    for m in ("base", "main"):
        for j in jobs_of(m):
            for r in graded(j["job"]):
                if r["pid"] in cand:
                    draws[(m, r["pid"])].append((int(j["order"]), r["chunk"], r["i"], j["job"], j["phase"], r))
    for k in draws:
        draws[k] = sorted(draws[k], key=lambda t: t[:3])[:K]
    zero = sorted(p for p in cand if p not in excl and len(draws[("base", p)]) >= K)
    print(f"{len(zero)} reach prompts with the base at {K} draws")
    rng = random.Random(SEED)
    picks, binding = [], {}
    for p in zero:
        ids = grade_ids(probs[p])
        for m in ("base", "main"):
            ds = draws[(m, p)]
            rate = [sum(t[5]["per"][i] for t in ds) / len(ds) for i in range(len(ids))]
            binding[(m, p)] = min(range(len(ids)), key=lambda i: rate[i])
        ext = [t for t in draws[("base", p)] if t[4] == "ext" and not t[5]["strict"]]
        by_chunk = defaultdict(list)
        for t in ext:
            by_chunk[(t[3], t[1])].append(t)
        chunks = sorted(by_chunk)
        for c in sorted(rng.sample(chunks, min(4, len(chunks)))):
            picks.append(("base", p, rng.choice(by_chunk[c])))
        fails = [t for t in draws[("main", p)] if not t[5]["strict"]]
        for t in rng.sample(fails, min(2, len(fails))):
            picks.append(("main", p, t))
    want = {(t[3], p, t[1], t[2]) for _, p, t in picks}
    texts = {}
    for job in sorted({k[0] for k in want}):
        with gzip.open(A / "samples" / f"{job}.jsonl.gz", "rt") as f:
            for ln in f:
                r = json.loads(ln)
                k = (job, r["pid"], r["chunk"], r["i"])
                if k in want:
                    texts[k] = r["text"]
    rows, items = [], []
    used = set()
    for m, p, t in picks:
        r = t[5]
        b = binding[(m, p)]
        ids = grade_ids(probs[p])
        key = {"model": m, "job": t[3], "pid": p, "chunk": r["chunk"], "i": r["i"], "binding_k": b,
               "binding_id": ids[b], "n_constraints": len(ids), "finish": r["finish"], "n_tok": r["n_tok"]}
        text = texts[(t[3], p, r["chunk"], r["i"])]
        ans = grade.remove_thinking_section(text)
        if r["finish"] == "length" and not ans:
            rows.append({**key, "item": "", "class_mech": "u"})
            continue
        item = f"f{rng.randrange(16**6):06x}"
        while item in used:
            item = f"f{rng.randrange(16**6):06x}"
        used.add(item)
        where = ("the text after the model's last </think>" if "</think>" in text else
                 "the model never closed its reasoning, so this is its WHOLE response, as the checker graded it")
        cons = "\n".join(
            f"- `{c}` {json.dumps({a: v for a, v in kw.items() if v is not None})}: checker says "
            f"{'followed' if ok else 'NOT followed'}{'   <- binding constraint' if n == b else ''}"
            for n, (c, kw, ok) in enumerate(zip(ids, [k or {} for k in grade._kwargs(probs[p])], r["per"])))
        body = (f"# Item {item}\n\n## Prompt (sent to the model verbatim)\n\n{probs[p]['prompt']}\n\n"
                f"## Constraints (official checker's verdict on this answer)\n\n{cons}\n\n"
                f"## Answer ({where}; {r['n_tok']} tokens in all, finish={r['finish']})\n\n{ans}\n")
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


def table_if(*outdirs):
    # item ids repeat across directories (each prep draws them from the same seed): key everything by (set, item)
    key, lab, conf = [], {}, {}
    for od in outdirs:
        out = Path(od)
        key += [dict(k, set=out.name) for k in csv.DictReader(open(out / "key.csv"))]
        for f in sorted((out / "labels").glob("*.json")):
            for x in json.load(open(f)):
                lab[(out.name, x["item"])] = x
        if (out / "confirm.csv").exists():
            conf.update({(out.name, r["item"]): r for r in csv.DictReader(open(out / "confirm.csv"))})
    rows = []
    for k in key:
        kk = (k["set"], k["item"])
        x = lab.get(kk, {})
        cls = k["class_mech"] or (conf[kk]["class"] if kk in conf else x.get("class", ""))
        bid = k["binding_id"]
        rows.append({**k, "reader_class": x.get("class", ""), "checker_agrees": x.get("checker_agrees", ""),
                     "my_class": conf.get(kk, {}).get("class", ""), "class": cls,
                     "family": bid.split(":")[0], "evidence": x.get("evidence", "")})
    with open(O / "failures_if.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    done = [r for r in rows if r["class"]]
    print(f"{len(done)} of {len(rows)} classified")
    for m in ("base", "main"):
        sub = [r for r in done if r["model"] == m]
        c = Counter(r["class"] for r in sub)
        print(m, len(sub), {k: f"{c[k]} ({c[k] / len(sub):.0%})" for k in "uabcd"} if sub else "")
        for g in ("family",):
            by = defaultdict(Counter)
            for r in sub:
                by[r[g]][r["class"]] += 1
            for v, cc in sorted(by.items()):
                n = sum(cc.values())
                print(f"  {g}={v:10s} n={n:3d} " + " ".join(f"{k}:{cc[k]}" for k in "uabcd"))


if __name__ == "__main__":
    if sys.argv[1] == "prep_if":
        prep_if(sys.argv[2])
    else:
        table_if(*sys.argv[2:])
