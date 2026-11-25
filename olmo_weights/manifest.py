"""Build the olmo-weights checkpoint manifest and job list (Hub API only; no weights are downloaded).

Inputs: olmo_weights/manifest/refs.json (list_refs.py) and the cached file trees (fetch_trees.py).
Outputs (olmo_weights/manifest/):
  stage1_locations.json  the stage-1 sample rule and the full / cut location lists
  checkpoints.csv        one row per checkpoint: label, family, stage, repo, branch, commit, step, files, bytes, sha256s
  jobs.json              per job: members (download order) and the statistics to compute (chains, gram sets, pairs)
Usage: manifest.py [--cut7 0|1] [--cut32 0|1] [--drop-i2 0|1] [--drop-zcode 0|1]   (the brief's cut order, 1 = cut)
"""
import argparse, json, math, os, re, subprocess, sys

M = "olmo_weights/manifest"
R = json.load(open(f"{M}/refs.json"))
B32, B7 = "allenai/Olmo-3-1125-32B", "allenai/Olmo-3-1025-7B"


def branches(repo, pat):
    out = {}
    for n, c in R[repo]["branches"].items():
        m = re.fullmatch(pat, n)
        if m:
            out[int(m.group(1))] = (n, c)
    return dict(sorted(out.items()))


# ---------------------------------------------------------------- stage-1 locations (fixed before any download)
def stage1_locations(repo, n_total, early_factor):
    """Pair starts s (s and s+1000 both released). Early: targets 1000 * f^k up to 64,000, plus 0, each mapped to the
    nearest pair start in log distance (ties to the lower), duplicates dropped. Even: the remaining locations at
    equal spacing over (64,000, last pair start], each rounded to the nearest pair start."""
    s1 = branches(repo, r"stage1-step(\d+)")
    starts = sorted(s for s in s1 if s % 1000 == 0 and s + 1000 in s1)
    early_t = [0] + [1000 * early_factor ** k for k in range(0, 20) if 1000 * early_factor ** k <= 64000]

    def nearest(t, log):
        if t == 0:
            return 0
        key = (lambda s: (abs(math.log(max(s, 1) / t)), s)) if log else (lambda s: (abs(s - t), s))
        return min((s for s in starts if s > 0), key=key)
    early = []
    for t in early_t:
        s = nearest(t, True)
        if s not in early:
            early.append(s)
    lo, hi = 64000, starts[-1]
    n_even = n_total - len(early)
    even = []
    for j in range(1, n_even + 1):
        s = nearest(lo + j * (hi - lo) / n_even, False)
        if s not in early and s not in even:
            even.append(s)
    locs = sorted(early + even)
    assert len(locs) == n_total, (repo, len(locs))
    return locs, s1


def stage1_chain(repo, locs, s1, final):
    """Members in download order: 0, then each location's pair (s, s+1000), then the final stage-1 checkpoint."""
    steps = []
    for s in [0] + locs:
        for x in (s, s + 1000):
            if x not in steps:
                steps.append(x)
    if final not in steps:
        steps.append(final)
    return steps


# ---------------------------------------------------------------- checkpoints
CK = {}   # label -> dict


def add(label, family, stage, repo, branch, step, note=""):
    commit = R[repo]["branches"][branch]
    CK[label] = dict(label=label, family=family, stage=stage, repo=repo, branch=branch, commit=commit, step=step,
                     note=note)
    return label


def tree(repo, branch):
    p = f"{M}/trees/{repo.replace('/', '__')}__{branch}.json"
    return json.load(open(p)) if os.path.exists(p) else None


def build(args):
    loc = {}
    # 32B ---------------------------------------------------------------------------------------------------
    n32 = 12 if args.cut32 else 25
    locs32, s1_32 = stage1_locations(B32, n32, 4 if args.cut32 else 2)
    final32 = max(s1_32)
    loc["32B"] = {"n": n32, "early_factor": 4 if args.cut32 else 2, "locations": locs32, "final": final32}
    c32_s1 = [add(f"32B/s1/{s}", "32B", "stage1", B32, s1_32[s][0], s) for s in stage1_chain(B32, locs32, s1_32, final32)]
    i1 = branches(B32, r"stage2-ingredient1-step(\d+)")
    i2 = branches(B32, r"stage2-ingredient2-step(\d+)")
    c32_i1 = [add(f"32B/s2i1/{s}", "32B", "stage2", B32, b, s) for s, (b, _) in i1.items()]
    i2_keep = list(i2)[3::4] if not args.drop_i2 else []
    c32_i2 = [add(f"32B/s2i2/{s}", "32B", "stage2", B32, i2[s][0], s) for s in i2_keep]
    m2 = add("32B/s2merge", "32B", "stage2", B32, "stage2-ingredient1+2-step23842", 23842,
             "merge of the two stage-2 ingredients (model card; paper sec. 3.5)")
    s3 = branches(B32, r"stage3-step(\d+)")
    c32_s3 = [add(f"32B/s3/{s}", "32B", "stage3", B32, b, s) for s, (b, _) in s3.items()]
    m3 = add("32B/s3merge", "32B", "stage3", B32, "stage3-step11921+11000+10000-nooptim", 11921,
             "merge of stage-3 steps 10,000 / 11,000 / 11,921 (paper sec. 3.6); = base main by shard hash")
    SFT = "allenai/Olmo-3-32B-Think-SFT"
    sft = {lr: branches(SFT, re.escape(lr) + r"-step(\d+)") for lr in ("1e-4", "5e-5")}
    c32_sft = {lr: [add(f"32B/sft{lr}/{s}", "32B", "sft", SFT, b, s) for s, (b, _) in d.items()] for lr, d in sft.items()}
    dpo32 = add("32B/dpo", "32B", "dpo", "allenai/Olmo-3-32B-Think-DPO", "main", None)
    RL = "allenai/Olmo-3.1-32B-Think"
    rl = branches(RL, r"step_(\d+)")
    c32_rl = [add(f"32B/rl/{s}", "32B", "rl", RL, b, s) for s, (b, _) in rl.items()]
    # 7B ----------------------------------------------------------------------------------------------------
    n7 = 15 if args.cut7 else 30
    locs7, s1_7 = stage1_locations(B7, n7, 4 if args.cut7 else 2)
    final7 = max(s1_7)
    loc["7B"] = {"n": n7, "early_factor": 4 if args.cut7 else 2, "locations": locs7, "final": final7}
    c7_s1 = [add(f"7B/s1/{s}", "7B", "stage1", B7, s1_7[s][0], s) for s in stage1_chain(B7, locs7, s1_7, final7)]
    c7_s2 = [add(f"7B/s2/{s}", "7B", "stage2", B7, b, s) for s, (b, _) in branches(B7, r"stage2-step(\d+)").items()]
    c7_s3 = [add(f"7B/s3/{s}", "7B", "stage3", B7, b, s) for s, (b, _) in branches(B7, r"stage3-step(\d+)").items()]
    SFT7 = "allenai/Olmo-3-7B-Think-SFT"
    c7_sft = [add(f"7B/sft/{s}", "7B", "sft", SFT7, b, s) for s, (b, _) in branches(SFT7, r"step(\d+)").items()]
    sft7m = add("7B/sftmain", "7B", "sft", SFT7, "main", None, "SFT main; equals no branch by shard hash")
    dpo7 = add("7B/dpo", "7B", "dpo", "allenai/Olmo-3-7B-Think-DPO", "main", None)
    RL7 = "allenai/Olmo-3-7B-Think"
    c7_rl = [add(f"7B/rl/{s}", "7B", "rl", RL7, b, s) for s, (b, _) in branches(RL7, r"step_(\d+)").items()]
    rl7m = add("7B/rlmain", "7B", "rl", RL7, "main", None, "RL main; equals no branch by shard hash")
    z = {}
    for k in ["IF", "Math", "Code"]:
        if k == "Code" and args.drop_zcode:
            continue
        repo = f"allenai/Olmo-3-7B-RL-Zero-{k}"
        z[k] = [add(f"7B/z{k.lower()}/{s}", "7B", f"rlzero-{k.lower()}", repo, b, s)
                for s, (b, _) in branches(repo, r"step_(\d+)").items()]
        if k != "Code":   # Code main = step_300 by shard hash: not downloaded twice
            z[k].append(add(f"7B/z{k.lower()}main", "7B", f"rlzero-{k.lower()}", repo, "main", None,
                            "main; equals no branch by shard hash"))
    base7 = "7B/s3/11921"   # = base main by shard hash
    # jobs ----------------------------------------------------------------------------------------------------
    J = {}

    def chain(members, start=None, name="main"):
        return {"name": name, "members": members, "start": start or members[0]}
    J["b32_s1"] = {"chains": [chain(c32_s1, name="stage1-sampled")]}
    J["b32_s2"] = {"chains": [chain([c32_s1[-1]] + c32_i1 + [m2], name="ingredient1")]
                   + ([chain([c32_s1[-1]] + c32_i2 + [m2], name="ingredient2")] if c32_i2 else []),
                   "gram": [[c32_i1[-1]] + ([c32_i2[-1]] if c32_i2 else []) + [m2]]}
    J["b32_s3"] = {"chains": [chain([m2] + c32_s3 + [m3], name="stage3")],
                   "pairs": [[c32_s1[-1], c32_s3[0]]],          # does stage 3 start from the merge or from 656000?
                   "gram": [[f"32B/s3/{s}" for s in (9000, 10000, 11000, 11921)] + [m3]]}
    J["p32_sft"] = {"chains": [chain([m3] + c32_sft["1e-4"], name="sft-1e-4"),
                               chain([m3] + c32_sft["5e-5"], name="sft-5e-5"),
                               chain(["32B/sft5e-5/8000", dpo32], name="sftmain-to-dpo")],
                    "gram": [["32B/sft5e-5/8000"] + [x for x in c32_sft["5e-5"] + c32_sft["1e-4"]
                                                     if x != "32B/sft5e-5/8000"] + [dpo32]]}
    J["p32_rl"] = {"chains": [chain([dpo32] + c32_rl, name="rl")], "lora": True}
    J["b7_s1"] = {"chains": [chain(c7_s1, name="stage1-sampled")]}
    J["b7_s2"] = {"chains": [chain([c7_s1[-1]] + c7_s2, name="stage2")]}
    J["b7_s3"] = {"chains": [chain([c7_s2[-1]] + c7_s3, name="stage3")]}
    alt7 = "7B/s3/11000"   # an alternative start 921 steps before base main: is the first checkpoint nearer to main?
    J["p7_sft"] = {"chains": [chain([base7] + c7_sft + [sft7m, dpo7], name="sft-dpo")],
                   "pairs": [[c7_sft[-1], dpo7], [alt7, c7_sft[0]]]}
    J["p7_rl"] = {"chains": [chain([dpo7] + c7_rl + [rl7m], name="rl")]}
    for k, mem in z.items():
        # duplicate branch names (shard hash) are resolved from the chain's distances to base main (start statistics)
        J[f"z7_{k.lower()}"] = {"chains": [chain([base7] + mem, name=f"rlzero-{k.lower()}")],
                                "pairs": [[alt7, mem[0]]]}
    for j, d in J.items():
        mem = []
        for c in d["chains"]:
            for x in c["members"]:
                if x not in mem:
                    mem.append(x)
        for g in d.get("gram", []) + d.get("pairs", []):
            for x in g:
                if x not in mem:
                    mem.append(x)
        d["members"] = mem
    return loc, J


def main():
    ap = argparse.ArgumentParser()
    for k in ["--cut7", "--cut32", "--drop-i2", "--drop-zcode"]:
        ap.add_argument(k, type=int, default=0)
    ap.add_argument("--fetch", type=int, default=1, help="fetch missing trees from the Hub API")
    args = ap.parse_args()
    loc, J = build(args)
    missing = [(c["repo"], c["branch"]) for c in CK.values() if tree(c["repo"], c["branch"]) is None]
    if missing and args.fetch:
        open(f"{M}/fetch_missing.txt", "w").write("".join(f"{r} {b}\n" for r, b in missing))
        subprocess.run([sys.executable, "olmo_weights/fetch_trees.py", f"{M}/fetch_missing.txt"], check=True)
    rows = []
    for c in CK.values():
        t = tree(c["repo"], c["branch"])
        st = sorted([f for f in t["files"] if f["path"].endswith(".safetensors")], key=lambda f: f["path"])
        c.update(files=";".join(f["path"] for f in st), n_files=len(st), bytes=sum(f["size"] for f in st),
                 sha256=";".join(f["sha256"] for f in st), sizes=";".join(str(f["size"]) for f in st))
        rows.append(c)
    import csv
    cols = ["label", "family", "stage", "repo", "branch", "commit", "step", "n_files", "bytes", "files", "sizes",
            "sha256", "note"]
    with open(f"{M}/checkpoints.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for c in rows:
            w.writerow({k: c.get(k) for k in cols})
    json.dump(loc, open(f"{M}/stage1_locations.json", "w"), indent=1)
    json.dump(J, open(f"{M}/jobs.json", "w"), indent=1)
    tot = {}
    for j, d in J.items():
        b = sum(CK[x]["bytes"] for x in d["members"])
        tot[j] = (len(d["members"]), b)
        print(f"{j:9s} {len(d['members']):4d} downloads {b / 1e12:6.2f} TB")
    print("total", sum(n for n, _ in tot.values()), "downloads", round(sum(b for _, b in tot.values()) / 1e12, 2), "TB;",
          "distinct checkpoints", len(CK))
    print("32B stage-1 locations:", loc["32B"]["locations"])
    print("7B stage-1 locations:", loc["7B"]["locations"])


if __name__ == "__main__":
    main()
