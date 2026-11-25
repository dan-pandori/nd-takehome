"""Reviewer (olmo-weights): every job's files.csv (download / hash log) against the manifest and jobs.json: each
(member, shard) present with status ok and the manifest sha256 / size (or the restage record for a pre-staged member);
bytes downloaded per job; members x shards expected. Usage: python3 rv_files.py ROOT"""
import csv, json, os, sys
from collections import Counter, defaultdict
ROOT = sys.argv[1]
J = json.load(open(f"{ROOT}/olmo_weights/manifest/jobs.json"))
ck = {r["label"]: r for r in csv.DictReader(open(f"{ROOT}/olmo_weights/manifest/checkpoints.csv"))}
rs = json.load(open(f"{ROOT}/artifacts/olmo_weights/restage/32B_sft5e-5_8000.json"))
rmap = {x["file"]: x for x in rs["restaged"]}
tot_dl = 0; tot_exp = 0; n_exp = 0
out = {}
for job in sorted(J):
    rows = list(csv.reader(open(f"{ROOT}/artifacts/olmo_weights/stats/{job}/files.csv")))
    got = defaultdict(list)
    for r in rows:
        lab, repo, commit, fn, size, sha, status, dl_s, sha_s, how = r
        got[(lab, fn)].append((int(size), sha, status, how, commit))
    bad, dup, missing = [], 0, []
    bytes_hub = 0
    for m in J[job]["members"]:
        c = ck[m]
        for fn, want, sz in zip(c["files"].split(";"), c["sha256"].split(";"), c["sizes"].split(";")):
            n_exp += 1; tot_exp += int(sz)
            g = got.get((m, fn))
            if not g:
                missing.append((m, fn)); continue
            if len(g) > 1:
                dup += len(g) - 1
            for size, sha, status, how, commit in g:
                if how == "prestaged":
                    ok = sha == rmap[fn]["sha256"] and size == rmap[fn]["bytes"] and status == "ok"
                else:
                    ok = sha == want and size == int(sz) and status == "ok" and commit == c["commit"]
                    if how == "hub":
                        bytes_hub += size
                if not ok:
                    bad.append((m, fn, how, status))
    extra = [k for k in got if k[0] not in J[job]["members"]]
    hows = Counter(r[9] for r in rows)
    out[job] = dict(rows=len(rows), expected=sum(len(ck[m]["files"].split(";")) for m in J[job]["members"]),
                    missing=len(missing), bad=len(bad), repeated=dup, extra=len(extra), how=dict(hows),
                    hub_TB=round(bytes_hub / 1e12, 4))
    tot_dl += bytes_hub
    print(job, out[job])
print("total hub bytes downloaded (incl. repeats) %.3f TB; manifest bytes over job members %.3f TB in %d files"
      % (tot_dl / 1e12, tot_exp / 1e12, n_exp))
print("restage:", rs["label"], rs["commit"], "orig files", len(rs["orig"]), "byte-identical tensors",
      rs["tensors_byte_identical"], "/", rs["tensors_total"])
orig_ok = all(o["sha256"] == w and o["bytes"] == int(s) for o, w, s in
              zip(rs["orig"], ck["32B/sft5e-5/8000"]["sha256"].split(";"), ck["32B/sft5e-5/8000"]["sizes"].split(";")))
print("restage originals match manifest sha256/size:", orig_ok)
