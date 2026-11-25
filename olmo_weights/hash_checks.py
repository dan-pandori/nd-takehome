"""Hash checks from the Hub's LFS sha256 of each safetensors shard (no downloads).

A checkpoint's fingerprint is the sorted tuple of its *.safetensors shard sha256. Equal fingerprints = byte-identical
weights files. Different sharding of the same weights would show as unequal here (checked separately on a pod).
Writes olmo_weights/manifest/hash_checks.json and prints the findings.
"""
import glob, json, re
from collections import defaultdict

T = {}
for p in glob.glob("olmo_weights/manifest/trees/*.json"):
    d = json.load(open(p))
    st = [f for f in d["files"] if f["path"].endswith(".safetensors")]
    T[(d["repo"], d["revision"])] = {"fp": tuple(sorted(f["sha256"] for f in st)), "n": len(st),
                                     "bytes": sum(f["size"] for f in st),
                                     "index_blob": next((f["blob_id"] for f in d["files"]
                                                         if f["path"] == "model.safetensors.index.json"), None),
                                     "config_blob": next((f["blob_id"] for f in d["files"]
                                                          if f["path"] == "config.json"), None)}
by_fp = defaultdict(list)
for k, v in T.items():
    by_fp[v["fp"]].append(k)
res = {}


def eq(a, b):
    return a in T and b in T and T[a]["fp"] == T[b]["fp"]


def same_as(key):
    return sorted(f"{r}@{v}" for r, v in by_fp[T[key]["fp"]] if (r, v) != key)


for repo in sorted({r for r, _ in T}):
    m = (repo, "main")
    if m in T:
        res[f"{repo}@main"] = {"equals": same_as(m), "n_shards": T[m]["n"], "GB": round(T[m]["bytes"] / 1e9, 2)}
        print(f"{repo}@main ({T[m]['n']} shards, {T[m]['bytes']/1e9:.2f} GB) equals: {same_as(m) or 'nothing else fetched'}")
# duplicate weights between non-main revisions
dups = [sorted(f"{r}@{v}" for r, v in ks if v != "main") for ks in by_fp.values()]
dups = [d for d in dups if len(d) > 1]
res["duplicates_excluding_main"] = dups
print("duplicate fingerprints among non-main revisions:", dups if dups else "none")
# Olmo-3-32B-Think steps vs Olmo-3.1-32B-Think steps
a = sorted(v for r, v in T if r == "allenai/Olmo-3-32B-Think" and v != "main")
cmp = {}
for v in a:
    cmp[v] = eq(("allenai/Olmo-3-32B-Think", v), ("allenai/Olmo-3.1-32B-Think", v))
res["Olmo-3-32B-Think_vs_3.1_same_step"] = cmp
print("Olmo-3-32B-Think steps:", a)
print("  equal to the 3.1 run's same-named step:", sum(cmp.values()), "of", len(cmp),
      "| unequal:", [v for v, x in cmp.items() if not x])
# configs: which revisions share config.json blobs / index layouts
for repo in sorted({r for r, _ in T}):
    blobs = defaultdict(list)
    for (r, v), x in T.items():
        if r == repo:
            blobs[(x["config_blob"], x["index_blob"], x["n"])].append(v)
    if len(blobs) > 1:
        print(f"{repo}: {len(blobs)} distinct (config, index, n_shards) groups:",
              [(k[2], len(vs), sorted(vs)[:3]) for k, vs in blobs.items()])
json.dump(res, open("olmo_weights/manifest/hash_checks.json", "w"), indent=1)
