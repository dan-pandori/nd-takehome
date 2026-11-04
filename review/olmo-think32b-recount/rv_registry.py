"""Compute rows check (reviewer): registry rows of run olmo-think32b vs my own per-job derivation from meta
(gpu_seconds = (t_load_s + t_gen_s) x tp, gen_tokens from my rows, attempts = sample rows), and a per-arm table."""
import collections, glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_core as C
reg = []
for f in glob.glob(os.path.join(C.ROOT, "artifacts", "olmo-think32b", "registry", "*.jsonl")):
    reg += [json.loads(l) for l in open(f)]
print("registry rows:", len(reg), "metrics:", collections.Counter(r.get("metric") for r in reg))
ex = reg[0]; print("example keys:", sorted(ex.keys()), {k: ex[k] for k in ("metric", "value") if k in ex}, ex.get("labels"))
rows = C.rows(); tok = collections.Counter(); att = collections.Counter()
for r in rows:
    tok[r["job"]] += r["n_tok"]; att[r["job"]] += 1
mine = {}
for f in glob.glob(os.path.join(C.ROOT, "artifacts", "olmo32", "meta", "*.json")):
    m = json.loads(open(f).read().strip().splitlines()[-1])
    j = m["job"]
    mine[j] = {"gpu_seconds": round((m["t_load_s"] + m["t_gen_s"]) * (m.get("tp") or 1), 1), "gen_tokens": tok.get(j, 0),
               "attempts": att.get(j, 0), "meta_gen_tokens": m["gen_tokens"], "meta_samples": m["samples"], "model": m["name"]}
def lab(r, k):
    return (r.get("labels") or {}).get(k, r.get(k))
regj = collections.defaultdict(dict)
for r in reg:
    regj[lab(r, "job")][r["metric"]] = r["value"]
mism = []
for j, v in sorted(mine.items()):
    rj = regj.get(j, {})
    for k in ("gpu_seconds", "gen_tokens", "attempts"):
        if rj.get(k) is None or abs(float(rj[k]) - float(v[k])) > 0.5:
            mism.append((j, k, rj.get(k), v[k]))
    if v["gen_tokens"] != v["meta_gen_tokens"] or v["attempts"] != v["meta_samples"]:
        mism.append((j, "meta_vs_rows", v["meta_gen_tokens"], v["gen_tokens"], v["meta_samples"], v["attempts"]))
print("mismatches (job, metric, registry, mine):", mism)
arm = collections.defaultdict(lambda: collections.Counter())
for j, v in mine.items():
    ph = j.split("_")[0]
    arm[(v["model"], ph)]["gpu_h"] += v["gpu_seconds"] / 3600; arm[(v["model"], ph)]["tok"] += v["gen_tokens"]; arm[(v["model"], ph)]["n"] += v["attempts"]
tot = collections.Counter()
for k in sorted(arm):
    print(k, {a: round(b, 2) for a, b in arm[k].items()}); tot.update(arm[k])
print("total:", {a: round(b, 2) for a, b in tot.items()})
json.dump({"mine": mine, "mismatches": mism}, open(os.path.join(C.HERE, "out", "registry_check.json"), "w"), indent=1)
