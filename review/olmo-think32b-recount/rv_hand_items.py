"""Blinded hand-check items (reviewer): every solution that decides a candidate's fate, built from the raw texts.
Item = problem + official answer + full response; no model / phase / side. Key in hand/key.json (not given to readers)."""
import gzip, hashlib, json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_core as C
rs = C.rows(); probs = {p["pid"]: p for p in C.problems()}
want = []   # (model, pid, which): which = 'credited' (rl or final) or 'doubly'
want += [("dpo", "aime2025_28", "credited"), ("s2300", "aime2025_28", "doubly"), ("s2300", "aime2026_14", "doubly"),
         ("dpo", "aime2026_14", "doubly"), ("s0750", "aime2025_28", "doubly"), ("s0100", "aime2025_28", "doubly")]
sel = []
for m, pid, which in want:
    d = C.draws(rs, m, pid)
    for j, r in enumerate(d):
        if (which == "credited" and (r["rl"] or r["final"])) or (which == "doubly" and r["doubly"]):
            sel.append({"model": m, "pid": pid, "job": r["job"], "chunk": r["chunk"], "i": r["i"], "draw": j + 1,
                        "rl": r["rl"], "final": r["final"], "finish": r["finish"], "n_tok": r["n_tok"]})
texts = {}
for job in sorted({s["job"] for s in sel}):
    with gzip.open(os.path.join(C.ROOT, "artifacts", "olmo32", "samples", f"{job}.jsonl.gz"), "rt") as f:
        for ln in f:
            r = json.loads(ln)
            texts[(r["job"], r["pid"], r["chunk"], r["i"])] = r["text"]
rng = random.Random(20261104)
rng.shuffle(sel)
key = {}
for s in sel:
    t = texts[(s["job"], s["pid"], s["chunk"], s["i"])]
    iid = "r" + hashlib.sha256(f"rv|{s['job']}|{s['pid']}|{s['chunk']}|{s['i']}".encode()).hexdigest()[:6]
    s["item"] = iid; key[iid] = s
    p = probs[s["pid"]]
    with open(os.path.join(C.HERE, "hand", "items", f"{iid}.md"), "w") as g:
        g.write(f"# Item {iid}\n\n## Problem\n\n{p['problem']}\n\n## Official answer\n\n{p['answer']}\n\n"
                f"## Response (verbatim; the text before </think> is the model's thinking)\n\n{t}\n")
json.dump(key, open(os.path.join(C.HERE, "hand", "key.json"), "w"), indent=1)
import collections
print(len(sel), collections.Counter((s["model"], s["pid"]) for s in sel))
print("sizes KB:", sorted(round(os.path.getsize(os.path.join(C.HERE, "hand", "items", f"{s['item']}.md")) / 1024) for s in sel))
