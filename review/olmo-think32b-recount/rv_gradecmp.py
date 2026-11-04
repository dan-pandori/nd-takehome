"""Compare my re-grade (out/regrade_*.jsonl) with the executor's graded rows (artifacts/olmo32/graded/*.jsonl), row by
row on (job, pid, chunk, i); plus storage checks. Reviewer code."""
import collections, glob, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
mine, theirs = {}, {}
for f in glob.glob(os.path.join(HERE, "out", "regrade_*.jsonl")):
    for ln in open(f):
        r = json.loads(ln); mine[(r["job"], r["pid"], r["chunk"], r["i"])] = r
for f in glob.glob(os.path.join(ROOT, "artifacts", "olmo32", "graded", "*.jsonl")):
    for ln in open(f):
        r = json.loads(ln); theirs[(r["job"], r["pid"], r["chunk"], r["i"])] = r
print("rows mine", len(mine), "theirs", len(theirs), "keys equal", set(mine) == set(theirs))
dis = collections.Counter(); ex = collections.defaultdict(list)
for k, m in mine.items():
    t = theirs.get(k)
    if t is None:
        dis["missing_in_theirs"] += 1; continue
    for a, b in (("rl", "rl"), ("final", "final"), ("main", "main"), ("think_end", "think_end")):
        if m[a] != t[b]:
            dis[a] += 1; ex[a].append((k, m[a], t[b], m.get("final_val"), t.get("final_ans"), m.get("final_src"), t.get("final_from")))
    if m["final_val"] != t["final_ans"]:
        dis["final_value"] += 1; ex["final_value"].append((k, m["final_val"], t["final_ans"], m["final_src"], t["final_from"]))
    if m["n_tok"] != t["n_tok"] or m["finish"] != t["finish"]:
        dis["ntok_finish"] += 1
print("disagreements:", dict(dis))
for a in ex:
    print(a, ex[a][:12])
# storage checks
st = collections.Counter()
for k, m in mine.items():
    st["n"] += 1
    st["ids==n_tok"] += m["n_ids"] == m["n_tok"]
    st["length&32768"] += (m["finish"] == "length") and m["n_tok"] == 32768
    st["length"] += m["finish"] == "length"
    st["stop"] += m["finish"] == "stop"
    st["stop&last_eos"] += (m["finish"] == "stop") and m["last_id"] == 100257
    st["eos_inside"] += m["eos_inside"] > 0
    st["n_tok>32768"] += m["n_tok"] > 32768
print("storage:", dict(st))
json.dump({"disagreements": dict(dis), "examples": {a: ex[a][:50] for a in ex}, "storage": dict(st)},
          open(os.path.join(HERE, "out", "gradecmp.json"), "w"), indent=1, default=str)
