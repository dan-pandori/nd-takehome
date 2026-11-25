"""Download throughput benchmark (stage 0): fetch a set of manifest files at concurrency P, report aggregate GB/s,
verify sha256, delete. Usage: dl_bench.py --p P --files label:k,label:k,... [--mode xet|transfer] [--work D]"""
import argparse, csv, hashlib, json, os, shutil, sys, time
from concurrent.futures import ThreadPoolExecutor

ap = argparse.ArgumentParser()
ap.add_argument("--p", type=int, required=True)
ap.add_argument("--files", required=True)
ap.add_argument("--mode", default="xet")
ap.add_argument("--work", default="/workspace/dl_bench")
ap.add_argument("--ckpts", default="olmo_weights/manifest/checkpoints.csv")
ap.add_argument("--out", default="artifacts/olmo_weights/stage0/dl_bench.jsonl")
a = ap.parse_args()
if a.mode == "transfer":
    os.environ["HF_HUB_DISABLE_XET"] = "1"
    os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
from huggingface_hub import hf_hub_download
import huggingface_hub
ck = {r["label"]: r for r in csv.DictReader(open(a.ckpts))}
items = []
for x in a.files.split(","):
    lab, k = x.rsplit(":", 1)
    r = ck[lab]
    items.append((lab, r["repo"], r["commit"], r["files"].split(";")[int(k)], r["sha256"].split(";")[int(k)]))
shutil.rmtree(a.work, ignore_errors=True)


def one(it):
    lab, repo, commit, fn, want = it
    t0 = time.time()
    p = hf_hub_download(repo, fn, revision=commit, local_dir=os.path.join(a.work, lab.replace("/", "_")))
    t1 = time.time()
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    t2 = time.time()
    return dict(label=lab, file=fn, bytes=os.path.getsize(p), dl_s=round(t1 - t0, 2), sha_s=round(t2 - t1, 2),
                sha_ok=h.hexdigest() == want)


t0 = time.time()
with ThreadPoolExecutor(max_workers=a.p) as ex:
    res = list(ex.map(one, items))
wall = time.time() - t0
tot = sum(r["bytes"] for r in res)
rec = dict(mode=a.mode, p=a.p, n_files=len(res), bytes=tot, wall_s=round(wall, 2), gb_per_s=round(tot / 1e9 / wall, 3),
           sha_all_ok=all(r["sha_ok"] for r in res), sha_gb_per_s=round(sum(r["bytes"] for r in res) / 1e9 /
                                                                       max(sum(r["sha_s"] for r in res), 1e-9), 3),
           hub=huggingface_hub.__version__, files=res, time=time.strftime("%FT%TZ", time.gmtime()))
os.makedirs(os.path.dirname(a.out), exist_ok=True)
open(a.out, "a").write(json.dumps(rec) + "\n")
shutil.rmtree(a.work, ignore_errors=True)
print("BENCH", a.mode, "P", a.p, "files", len(res), f"{tot / 1e9:.1f} GB in {wall:.1f} s = {tot / 1e9 / wall:.3f} GB/s",
      "sha_ok", rec["sha_all_ok"], "sha GB/s/thread", rec["sha_gb_per_s"])
