"""Extension audit (reviewer): per extended (model, problem), chunks in draw order with grades, cumulative doubly
count over the completed chunk prefix, and the draw index of every credited sample."""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_core as C
rs = C.rows()
out = {}
for m, pid in [("dpo", "aime2025_28"), ("s2300", "aime2025_28"), ("s0750", "aime2025_28"), ("s0100", "aime2025_28"),
               ("s2300", "aime2026_14"), ("dpo", "aime2026_14")]:
    d = C.draws(rs, m, pid)
    print(f"== {m} {pid}: {len(d)} draws")
    chunks = collections.OrderedDict()
    for j, r in enumerate(d):
        chunks.setdefault((r["job"], r["chunk"]), []).append((j + 1, r))
    cum = 0; lines = []
    for (job, c), xs in chunks.items():
        n = len(xs); rl = sum(r["rl"] for _, r in xs); fi = sum(r["final"] for _, r in xs); db = sum(r["doubly"] for _, r in xs)
        cum += db
        hits = [(j, "D" if r["doubly"] else ("rl" if r["rl"] else "fin")) for j, r in xs if r["rl"] or r["final"]]
        cut = sum(r["finish"] == "length" for _, r in xs)
        lines.append({"job": job, "chunk": c, "n": n, "draws": [xs[0][0], xs[-1][0]], "rl": rl, "final": fi,
                      "doubly": db, "cum_doubly": cum, "cut": cut, "hits": hits})
        print(f"  {job:10s} c{c:<3d} n={n:3d} draws {xs[0][0]:3d}-{xs[-1][0]:3d} rl={rl} fin={fi} dbl={db} cum={cum} cut={cut} hits={hits}")
    out[f"{m}|{pid}"] = lines
json.dump(out, open(os.path.join(C.HERE, "out", "ext.json"), "w"), indent=1)
