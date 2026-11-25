"""Reviewer (olmo-weights): seeded sample of chain intervals for the on-pod recompute.

Universe: every chain interval (job, chain, idx) in olmo_weights/manifest/jobs.json with idx >= 2 (so the interval has a
predecessor in its chain and a lag-1 cosine exists). Draw, with random.Random(20261125), 2 intervals from 7B jobs and
2 from 32B jobs, uniformly within family. Fixed addition: the 32B RL endpoint (32B/dpo -> 32B/rl/2300) for the LoRA
cosine (E5). Writes plan.json with every needed checkpoint's repo / commit / files / sha256 / sizes from the manifest.
Usage: python3 rv_plan.py ROOT OUT
"""
import csv, json, random, sys

ROOT, OUT = sys.argv[1], sys.argv[2]
J = json.load(open(f"{ROOT}/olmo_weights/manifest/jobs.json"))
ck = {r["label"]: r for r in csv.DictReader(open(f"{ROOT}/olmo_weights/manifest/checkpoints.csv"))}
univ = {"7B": [], "32B": []}
for job, v in sorted(J.items()):
    for c in v["chains"]:
        m = c["members"]
        for i in range(2, len(m)):
            univ[m[i].split("/")[0]].append(dict(job=job, chain=c["name"], idx=i, a2=m[i - 2], a=m[i - 1], b=m[i],
                                                 s=c["start"]))
rng = random.Random(20261125)
tasks = []
for fam in ("7B", "32B"):
    for t in rng.sample(univ[fam], 2):
        tasks.append(dict(kind="triple", **t))
tasks.append(dict(kind="lora", job="p32_rl", chain="rl", s="32B/dpo", b="32B/rl/2300"))
# Targeted (not random): the one member the executor re-staged into another shard layout (32B/sft5e-5/8000 = SFT main),
# read here from its original Hub files: the 5e-5 chain triple around it, and its interval to DPO.
m5 = J["p32_sft"]["chains"][1]["members"]
i8 = m5.index("32B/sft5e-5/8000")
tasks.append(dict(kind="triple", job="p32_sft", chain="sft-5e-5", idx=i8 + 1, a2=m5[i8 - 1], a=m5[i8], b=m5[i8 + 1],
                  s=J["p32_sft"]["chains"][1]["start"], targeted=True))
tasks.append(dict(kind="pair", job="p32_sft", chain="sftmain-to-dpo", idx=1, a="32B/sft5e-5/8000", b="32B/dpo",
                  targeted=True))
# order: 7B first, then 32B grouped so that shared checkpoints (32B/dpo, 32B/s3merge) are downloaded once
rank = {"p32_rl": 0, "p32_sft": 2}
def key(t):
    fam = t.get("b", "").split("/")[0]
    if fam == "7B":
        return (0, 0, 0)
    if t["kind"] == "lora":
        return (1, 1, 0)
    if t["job"] == "p32_rl":
        return (1, 0, 0)
    if t["kind"] == "pair":
        return (1, 3, 0)
    if t.get("targeted"):
        return (1, 2, 0)
    if t["job"] == "p32_sft":
        return (1, 4, 0)
    return (1, 5, 0)
tasks.sort(key=key)
need = []
for t in tasks:
    for k in ("a2", "a", "b", "s"):
        if k in t and t[k] not in need:
            need.append(t[k])
plan = dict(seed=20261125, universe_sizes={k: len(v) for k, v in univ.items()}, tasks=tasks,
            checkpoints={m: dict(repo=ck[m]["repo"], branch=ck[m]["branch"], commit=ck[m]["commit"],
                                 files=ck[m]["files"].split(";"), sha256=ck[m]["sha256"].split(";"),
                                 sizes=[int(x) for x in ck[m]["sizes"].split(";")]) for m in need})
json.dump(plan, open(OUT, "w"), indent=1)
for t in tasks:
    print(t)
print("checkpoints", len(need), "bytes %.1f GB" % (sum(sum(plan["checkpoints"][m]["sizes"]) for m in need) / 1e9))
