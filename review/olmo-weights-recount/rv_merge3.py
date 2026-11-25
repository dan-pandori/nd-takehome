"""Reviewer (olmo-weights): which arithmetic reproduces the 32B stage-3 merge bit for bit? lm_head.weight (model-00014)
of s3merge against variants of the mean of s3/10000, s3/11000, s3/11921 (downloaded at the manifest commits, sha256
checked). Row-chunked."""
import hashlib, json, os, torch
from huggingface_hub import hf_hub_download
from rv_recompute import header, read_rows
plan = json.load(open("merge_plan.json"))
labs = ["32B/s3merge", "32B/s3/10000", "32B/s3/11000", "32B/s3/11921"]
fn = "model-00014-of-00014.safetensors"
dev = torch.device("cuda")
H = {}
for lab in labs:
    c = plan["checkpoints"][lab]; i = c["files"].index(fn)
    p = hf_hub_download(c["repo"], fn, revision=c["commit"], local_dir="/root/rvm3/" + lab.replace("/", "_"))
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 24), b""):
            h.update(blk)
    assert h.hexdigest() == c["sha256"][i], lab
    H[lab] = header(p)["lm_head.weight"]
w = torch.tensor(1 / 3, dtype=torch.float32, device=dev)
wb = w.to(torch.bfloat16)
names = ["f32 (a+b+c)/3", "f32 a/3+b/3+c/3", "f32 w*a+w*b+w*c (w=fl32(1/3))", "f32 ((a+b)+c)*w",
         "bf16 ops ((a+b)+c)/3", "bf16 ops a*w+b*w+c*w", "f64 exact mean", "f32 running mean"]
eq = {k: 0 for k in names}
n = 0
rows = H[labs[0]]["shape"][0]
for r0 in range(0, rows, 8192):
    r1 = min(rows, r0 + 8192)
    _, M = read_rows(H[labs[0]], r0, r1, dev)
    A = [read_rows(H[l], r0, r1, dev)[0] for l in labs[1:]]
    a, b, c = (x.float() for x in A)
    ab, bb, cb = (x.float().to(torch.bfloat16) for x in A)
    m = a + (b - a) / 2
    V = {names[0]: (a + b + c) / 3, names[1]: a / 3 + b / 3 + c / 3, names[2]: w * a + w * b + w * c,
         names[3]: ((a + b) + c) * w, names[4]: ((ab + bb) + cb) / 3, names[5]: ab * wb + bb * wb + cb * wb,
         names[6]: (A[0] + A[1] + A[2]) / 3, names[7]: m + (c - m) / 3}
    for k, v in V.items():
        r = v.to(torch.bfloat16) if v.dtype != torch.bfloat16 else v
        eq[k] += int((r.view(torch.int16) == M).sum())
    n += M.numel()
out = {k: v / n for k, v in eq.items()}
for k, v in out.items():
    print(f"{v:.6f}  {k}", flush=True)
json.dump(dict(n=n, frac_bitwise_equal=out), open("out/merge3_variants.json", "w"), indent=1)
