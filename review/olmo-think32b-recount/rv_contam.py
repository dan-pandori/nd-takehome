"""Contamination re-scan (reviewer, own definitions): word n-gram containment of each of the 60 problems in every
Dolci-Think-RL-32B prompt (rev d581ecde). Tokens = lowercase [a-z0-9]+ runs. containment_n = |G_n(problem) & G_n(doc)|
/ |G_n(problem)|. Reports per problem the max 8-gram and 5-gram containment, the best doc, and its ground truth."""
import collections, glob, json, os, re, sys
import pyarrow.parquet as pq
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
probs = [json.loads(l) for l in open(os.path.join(ROOT, "olmo32", "problems.jsonl"))]
tokz = lambda s: re.findall(r"[a-z0-9]+", s.lower())
def grams(t, n): return {tuple(t[i:i + n]) for i in range(len(t) - n + 1)}
G = {n: {p["pid"]: grams(tokz(p["problem"]), n) for p in probs} for n in (8, 5)}
index = {n: collections.defaultdict(set) for n in (8, 5)}
for n in (8, 5):
    for pid, gs in G[n].items():
        for g in gs:
            index[n][g].add(pid)
best = {n: {p["pid"]: (0.0, None, None, None) for p in probs} for n in (8, 5)}
files = sorted(glob.glob(sys.argv[1] + "/*.parquet")); ndoc = 0
for f in files:
    pf = pq.ParquetFile(f)
    for rg in range(pf.num_row_groups):
        t = pf.read_row_group(rg, columns=["prompt", "ground_truth", "custom_id"]).to_pylist()
        for r in t:
            ndoc += 1
            toks = tokz(r["prompt"] or "")
            for n in (8, 5):
                hits = collections.Counter()
                for g in grams(toks, n):
                    for pid in index[n].get(g, ()):
                        hits[pid] += 1
                for pid, h in hits.items():
                    c = h / max(len(G[n][pid]), 1)
                    if c > best[n][pid][0]:
                        best[n][pid] = (c, r["custom_id"], (r["prompt"] or "")[:240], r["ground_truth"])
out = []
ans = {p["pid"]: str(p["answer"]) for p in probs}
for p in probs:
    pid = p["pid"]
    c8, id8, t8, gt8 = best[8][pid]; c5, id5, t5, gt5 = best[5][pid]
    out.append({"pid": pid, "c8": round(c8, 3), "c8_doc": id8, "c8_gt": gt8, "c5": round(c5, 3), "c5_doc": id5,
                "c5_gt": gt5, "c5_same_answer": bool(gt5 and ans[pid] in gt5), "c5_text": t5})
json.dump({"n_docs": ndoc, "files": [os.path.basename(f) for f in files], "rows": out},
          open(os.path.join(HERE, "out", "contam_rl.json"), "w"), indent=1)
print("docs scanned:", ndoc)
for r in sorted(out, key=lambda r: -r["c8"])[:12]:
    print(r["pid"], "c8", r["c8"], "c5", r["c5"], "same_ans@c5", r["c5_same_answer"], "|", (r["c5_text"] or "")[:110].replace("\n", " "))
print("max c8 overall:", max(r["c8"] for r in out), "| problems with c8 >= 0.5:", [r["pid"] for r in out if r["c8"] >= 0.5])
