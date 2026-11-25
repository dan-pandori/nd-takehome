"""Reviewer (olmo-weights): plan for rv_merge_check.py (stage-2 merge, stage-3 merge, the SFT soup under
5e-5-step8000); files per checkpoint located by tensor name from the reference index / the checkpoint's own header
listing. Usage: python3 rv_merge_plan.py ROOT OUT"""
import csv, json, sys
ROOT, OUT = sys.argv[1], sys.argv[2]
M = f"{ROOT}/olmo_weights/manifest"
ck = {r["label"]: r for r in csv.DictReader(open(f"{M}/checkpoints.csv"))}
ref = json.load(open(f"{M}/index/allenai__Olmo-3-1125-32B__stage1.json"))["weight_map"]
TENS = ["lm_head.weight", "model.layers.63.mlp.down_proj.weight"]


def where(lab, t):
    h = json.load(open(f"{M}/headers/{lab.replace('/', '_')}.json"))
    fs = [f for f, ts in h.items() if t in ts]
    assert len(fs) == 1, (lab, t, fs)
    return fs[0]


checks = []
for name, merge, ing in (("stage2-merge", "32B/s2merge", ["32B/s2i1/23842", "32B/s2i2/23842"]),
                         ("stage3-merge", "32B/s3merge", ["32B/s3/10000", "32B/s3/11000", "32B/s3/11921"]),
                         ("sft-soup", "32B/sft5e-5/8000", ["32B/sft5e-5/10790", "32B/sft1e-4/10790"])):
    for t in TENS:
        files = {lab: where(lab, t) for lab in [merge] + ing}
        checks.append(dict(name=name, merge=merge, ingredients=ing, tensors=[t], files=files))
need = sorted({lab for c in checks for lab in [c["merge"]] + c["ingredients"]})
plan = dict(checks=checks, checkpoints={m: dict(repo=ck[m]["repo"], commit=ck[m]["commit"],
            files=ck[m]["files"].split(";"), sha256=ck[m]["sha256"].split(";"),
            sizes=[int(x) for x in ck[m]["sizes"].split(";")]) for m in need})
json.dump(plan, open(OUT, "w"), indent=1)
for c in checks:
    print(c["name"], c["tensors"], c["files"])
print("bytes %.1f GB" % (sum(plan["checkpoints"][l]["sizes"][plan["checkpoints"][l]["files"].index(f)]
                              for c in checks for l, f in c["files"].items()) / 1e9))
