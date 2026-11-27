"""Reviewer (olmo-lowrank): plan of the seeded raw-weight recompute (VPS side; my own code).

Members are taken from the pre-registration's model table: each name's repo and pinned commit come from
olmo_weights/manifest/checkpoints.csv (the same manifest the executor read), and for base / sft / s2300 I check here,
from the Hub's own LFS tree (HfApi.list_repo_tree, expand=True), that the pinned branch's shard sha256 list equals the
named `main` revision's (the pre-registration's "= main by shard hash"). Seeded sample: 4 of the 64 32B layers and 2
of the 32 7B layers (random.Random seeds below), all 7 matrix types. Each sampled tensor is located in its file from
the real safetensors header (8-byte length + JSON, fetched by an HTTP range request through huggingface_hub), not the
index. Output: pod/plan.json (members, files to fetch with sha256, tensor offsets) and out/plan_report.json.
"""
import csv
import json
import random
import struct
import sys
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_url, get_session

KIT = Path(__file__).resolve().parent
RAW = Path.home() / "review" / "olmo-lowrank"
TYPES = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
GROUP = {t: ("self_attn" if t[0] in "qkvo" else "mlp") for t in TYPES}
L32 = sorted(random.Random("olmo-lowrank review 2026-11-27 32B").sample(range(64), 4))
L7 = sorted(random.Random("olmo-lowrank review 2026-11-27 7B").sample(range(32), 2))

M = {r["label"]: r for r in csv.DictReader(open(RAW / "olmo_weights/manifest/checkpoints.csv"))}
# name -> manifest label (pre-registration table) ; named main revisions to compare by shard hash
MEM32 = {"dpo": "32B/dpo", "base": "32B/s3merge", "sft": "32B/sft5e-5/8000"}
for t in (50, 100, 500, 750, 1100, 1150, 1600, 2100, 2250, 2300):
    MEM32[f"s{t:04d}"] = f"32B/rl/{t}"
MEM7 = {"dpo": "7B/dpo", "base": "7B/s3/11921", "sft": "7B/sftmain", "zif": "7B/zifmain"}
for t in (25, 50, 100, 500, 525, 1000, 1350, 1375):
    MEM7[f"r{t:04d}"] = f"7B/rl/{t}"
MAINS = {"32B:base": ("allenai/Olmo-3-1125-32B", "c2b61dae"), "32B:sft": ("allenai/Olmo-3-32B-Think-SFT", "a6d7f3cf"),
         "32B:s2300": ("allenai/Olmo-3.1-32B-Think", "97ade57a"), "7B:base": ("allenai/Olmo-3-1025-7B", "a81bae42")}


def header(repo, commit, fn):
    url = hf_hub_url(repo, fn, revision=commit)
    s = get_session()
    r = s.get(url, headers={"Range": "bytes=0-7"}, follow_redirects=True)
    n = struct.unpack("<Q", r.content[:8])[0]
    r = s.get(url, headers={"Range": f"bytes=8-{8 + n - 1}"}, follow_redirects=True)
    h = json.loads(r.content)
    h.pop("__metadata__", None)
    return {k: {"dtype": v["dtype"], "shape": v["shape"], "off": 8 + n + v["data_offsets"][0],
                "nbytes": v["data_offsets"][1] - v["data_offsets"][0]} for k, v in h.items()}


def main():
    api = HfApi()
    rep = {"layers32": L32, "layers7": L7, "main_checks": {}}
    # pinned branch vs named main: shard sha256 lists from the Hub's LFS tree
    for key, (repo, short) in MAINS.items():
        fam, name = key.split(":")
        lab = (MEM32 if fam == "32B" else MEM7)[name]
        pinned = M[lab]
        main_tree = {f.path: f.lfs.sha256 for f in api.list_repo_tree(repo, revision="main", expand=True)
                     if f.path.endswith(".safetensors") and getattr(f, "lfs", None)}
        main_commit = api.repo_info(repo, revision="main").sha
        pin = dict(zip(pinned["files"].split(";"), pinned["sha256"].split(";")))
        rep["main_checks"][key] = {"repo": repo, "main_commit": main_commit, "prereg_short": short,
                                   "commit_matches_prereg": main_commit.startswith(short), "pinned_label": lab,
                                   "pinned_commit": pinned["commit"],
                                   "same_files_same_sha": sorted(main_tree.items()) == sorted(pin.items()),
                                   "same_sha_multiset": sorted(main_tree.values()) == sorted(pin.values())}
        print(key, rep["main_checks"][key], flush=True)
    plan = {"members": {}, "layers": {"32B": L32, "7B": L7}}
    for fam, MEM, LS in (("32B", MEM32, L32), ("7B", MEM7, L7)):
        want = [f"model.layers.{l}.{GROUP[t]}.{t}.weight" for l in LS for t in TYPES]
        for name, lab in MEM.items():
            r = M[lab]
            files, shas = r["files"].split(";"), r["sha256"].split(";")
            where = {}
            for fn, sh in zip(files, shas):
                h = header(r["repo"], r["commit"], fn)
                for k in want:
                    if k in h:
                        assert k not in where, (lab, k)
                        where[k] = dict(file=fn, sha256=sh, **h[k])
            missing = [k for k in want if k not in where]
            assert not missing, (lab, missing)
            plan["members"][f"{fam}:{name}"] = {"label": lab, "repo": r["repo"], "commit": r["commit"],
                                               "tensors": where,
                                               "files": sorted({(v["file"], v["sha256"]) for v in where.values()})}
            print(fam, name, lab, r["commit"][:8], len(plan["members"][f"{fam}:{name}"]["files"]), "files", flush=True)
    (KIT / "pod").mkdir(exist_ok=True)
    json.dump(plan, open(KIT / "pod" / "plan.json", "w"), indent=1)
    rep["download_bytes"] = {}
    for k, m in plan["members"].items():
        rep["download_bytes"][k] = sum(int(M[m["label"]]["sizes"].split(";")[M[m["label"]]["files"].split(";").index(f)])
                                       for f, _ in m["files"])
    rep["total_GB"] = round(sum(rep["download_bytes"].values()) / 1e9, 1)
    json.dump(rep, open(KIT / "out" / "plan_report.json", "w"), indent=1)
    print("total GB", rep["total_GB"])


if __name__ == "__main__":
    main()
