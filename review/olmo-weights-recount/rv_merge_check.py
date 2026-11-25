"""Reviewer (olmo-weights): are the released merges exact averages, rounded once to bf16?

For each merge M of ingredients I_1..I_k (equal weights), on chosen tensors: avg = (sum I_j) / k computed in float32
(as a merge tool would), rounded to bf16 (round-to-nearest-even, torch's cast), compared bit for bit with M; plus the
float64 residual norms ||M - avg64||, ||round(avg) - avg64|| and ||M - round(avg)||. Files are found per checkpoint by
tensor name (shard layouts may differ), downloaded at the manifest commit and sha256-checked.
Usage: python rv_merge_check.py merge_plan.json OUT.json [--dl /root/rvmerge]"""
import hashlib, json, os, shutil, sys, time

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rv_recompute import header, read_rows

plan = json.load(open(sys.argv[1]))
OUT = sys.argv[2]
DL = sys.argv[4] if len(sys.argv) > 4 and sys.argv[3] == "--dl" else "/root/rvmerge"
dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
os.makedirs(DL, exist_ok=True)


def fetch(lab, fn):
    from huggingface_hub import hf_hub_download
    c = plan["checkpoints"][lab]
    i = c["files"].index(fn)
    d = os.path.join(DL, lab.replace("/", "_"))
    p = hf_hub_download(c["repo"], fn, revision=c["commit"], local_dir=d)
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    assert h.hexdigest() == c["sha256"][i] and os.path.getsize(p) == c["sizes"][i], ("HASH", lab, fn)
    return p


results = []
for chk in plan["checks"]:
    t0 = time.time()
    labs = [chk["merge"]] + chk["ingredients"]
    paths = {lab: fetch(lab, chk["files"][lab]) for lab in labs}
    hdr = {lab: header(paths[lab]) for lab in labs}
    out = dict(name=chk["name"], merge=chk["merge"], ingredients=chk["ingredients"], tensors=[])
    for t in chk["tensors"]:
        H = {lab: hdr[lab][t] for lab in labs}
        shp = H[chk["merge"]]["shape"]
        rows = shp[0]
        per_row = int(np.prod(shp[1:])) if len(shp) > 1 else 1
        step = max(1, (1 << 25) // per_row)
        acc = dict(n=0, eq=0, mism_1ulp=0, mism_more=0, r_m_avg=0.0, r_rnd_avg=0.0, r_m_rnd=0.0, n_m2=0.0)
        for r0 in range(0, rows, step):
            r1 = min(rows, r0 + step)
            M64, Mb = read_rows(H[chk["merge"]], r0, r1, dev)
            ing = [read_rows(H[lab], r0, r1, dev) for lab in chk["ingredients"]]
            s32 = ing[0][0].float()
            for x in ing[1:]:
                s32 = s32 + x[0].float()
            avg32 = s32 / len(ing)
            rnd = avg32.to(torch.bfloat16)
            rb = rnd.view(torch.int16)
            avg64 = sum(x[0] for x in ing) / len(ing)
            acc["n"] += Mb.numel()
            eq = rb == Mb
            acc["eq"] += int(eq.sum())
            d = (rb.to(torch.int32) - Mb.to(torch.int32)).abs()
            acc["mism_1ulp"] += int(((d == 1) & ~eq).sum())
            acc["mism_more"] += int((d > 1).sum())
            acc["r_m_avg"] += float(((M64 - avg64) ** 2).sum())
            acc["r_rnd_avg"] += float(((rnd.double() - avg64) ** 2).sum())
            acc["r_m_rnd"] += float(((M64 - rnd.double()) ** 2).sum())
            acc["n_m2"] += float((M64 ** 2).sum())
        for k in ("r_m_avg", "r_rnd_avg", "r_m_rnd", "n_m2"):
            acc[k] = acc[k] ** 0.5
        acc["frac_bitwise_equal"] = acc["eq"] / acc["n"]
        acc["tensor"] = t
        out["tensors"].append(acc)
        print(chk["name"], t, json.dumps({k: v for k, v in acc.items() if k != "tensor"}), flush=True)
    out["seconds"] = round(time.time() - t0, 1)
    results.append(out)
    for lab in labs:
        shutil.rmtree(os.path.join(DL, lab.replace("/", "_")), ignore_errors=True)
json.dump(results, open(OUT, "w"), indent=1)
print("MERGE CHECK DONE")
