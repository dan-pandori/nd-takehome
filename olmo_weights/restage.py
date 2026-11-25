"""Re-stage a checkpoint whose shard files use another tensor-to-file layout into the job's reference layout, byte for
byte, so the shard-major engine can stream it with the others (olmo-weights: 32B/sft5e-5/8000 = SFT main).

Downloads the original files (pinned commit), checks each against the manifest sha256, writes one file per reference
shard holding exactly the reference index's tensors for that shard, then re-reads every tensor from both copies and
compares their bytes (sha256 of each tensor's raw bytes). Writes <out>/restage.json and deletes the originals.
Usage: restage.py --label L --ref-index F --out DIR [--orig DIR]"""
import argparse, csv, hashlib, json, os, shutil, time
import torch
from safetensors import safe_open
from safetensors.torch import save_file
from huggingface_hub import hf_hub_download

ap = argparse.ArgumentParser()
ap.add_argument("--label", required=True)
ap.add_argument("--ref-index", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--orig", default="/root/restage_orig")
ap.add_argument("--ckpts", default="olmo_weights/manifest/checkpoints.csv")
a = ap.parse_args()
c = {r["label"]: r for r in csv.DictReader(open(a.ckpts))}[a.label]
files, shas, sizes = c["files"].split(";"), c["sha256"].split(";"), [int(x) for x in c["sizes"].split(";")]
od = os.path.join(a.orig, a.label.replace("/", "_"))
os.makedirs(od, exist_ok=True)
os.makedirs(a.out, exist_ok=True)
t0 = time.time()
rec = {"label": a.label, "repo": c["repo"], "commit": c["commit"], "orig": [], "restaged": []}


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


where = {}
for fn, want, sz in zip(files, shas, sizes):
    p = hf_hub_download(c["repo"], fn, revision=c["commit"], local_dir=od)
    got = sha_file(p)
    assert got == want and os.path.getsize(p) == sz, f"HASH MISMATCH {fn}"
    rec["orig"].append({"file": fn, "sha256": got, "bytes": sz})
    with safe_open(p, framework="pt") as f:
        for t in f.keys():
            where[t] = p
print(f"downloaded and verified {len(files)} files in {time.time() - t0:.0f} s; {len(where)} tensors")
ref = json.load(open(a.ref_index))["weight_map"]
assert set(ref) == set(where), "tensor sets differ between the checkpoint and the reference index"
groups = {}
for t, fn in ref.items():
    groups.setdefault(fn, []).append(t)


def tsha(x):
    return hashlib.sha256(x.contiguous().view(torch.uint8).numpy().tobytes()).hexdigest()


n_eq = 0
for fn in sorted(groups):
    d, hs = {}, {}
    for t in sorted(groups[fn]):
        with safe_open(where[t], framework="pt") as f:
            d[t] = f.get_tensor(t)
        assert d[t].dtype == torch.bfloat16
        hs[t] = tsha(d[t])
    q = os.path.join(a.out, fn)
    save_file(d, q, metadata={"format": "pt", "restaged_from": f"{c['repo']}@{c['commit']}"})
    del d
    with safe_open(q, framework="pt") as f:
        for t in f.keys():
            n_eq += tsha(f.get_tensor(t)) == hs[t]
    rec["restaged"].append({"file": fn, "sha256": sha_file(q), "bytes": os.path.getsize(q), "n_tensors": len(groups[fn])})
rec["tensors_byte_identical"] = n_eq
rec["tensors_total"] = len(ref)
rec["seconds"] = round(time.time() - t0, 1)
json.dump(rec, open(os.path.join(a.out, "restage.json"), "w"), indent=1)
shutil.rmtree(od)
print(f"RESTAGE {'OK' if n_eq == len(ref) else 'FAIL'}: {n_eq}/{len(ref)} tensors byte-identical, {rec['seconds']} s")
