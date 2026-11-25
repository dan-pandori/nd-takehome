"""Reviewer (olmo-weights): check the checkpoint manifest against the Hugging Face Hub API, fetched independently.

1. refs: every manifest branch exists and points at the manifest commit;
2. trees: at each manifest commit, the safetensors file names, sizes and LFS sha256 equal the manifest's;
3. byte identity (equal multisets of shard sha256) for the pre-registered hash checks: base / SFT / RL mains,
   Olmo-3-32B-Think's branches against Olmo-3.1-32B-Think's, duplicate RL-Zero names, the stage-3 reshard branch;
4. stage-1 locations re-derived from the pre-registered rule with my own code.
Writes rv_manifest_check.json. stdlib only (urllib); the HF token, if set in the environment, is sent and never printed.
Usage: python3 rv_manifest_check.py ROOT OUTDIR
"""
import csv, json, math, os, sys, time, urllib.error, urllib.parse, urllib.request

ROOT, OUT = sys.argv[1], sys.argv[2]
TOK = os.environ.get("HF_TOKEN", "")
CACHE = os.path.join(OUT, "hub_cache")
os.makedirs(CACHE, exist_ok=True)


def get(url):
    fn = os.path.join(CACHE, urllib.parse.quote(url, safe="") [:240] + ".json")
    if os.path.exists(fn):
        return json.load(open(fn))
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOK}"} if TOK else {})
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.loads(r.read().decode())
            json.dump(d, open(fn, "w"))
            time.sleep(0.25)
            return d
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(10 * (attempt + 1))
                continue
            raise
        except Exception:
            time.sleep(10 * (attempt + 1))
    raise RuntimeError(url)


def refs(repo):
    d = get(f"https://huggingface.co/api/models/{repo}/refs")
    return {b["name"]: b["targetCommit"] for b in d["branches"]}


def tree(repo, rev):
    d = get(f"https://huggingface.co/api/models/{repo}/tree/{urllib.parse.quote(rev, safe='')}")
    out = {}
    for e in d:
        if e.get("type") == "file" and e["path"].endswith(".safetensors"):
            lfs = e.get("lfs") or {}
            out[e["path"]] = (lfs.get("oid") or lfs.get("sha256"), e.get("size"))
    return out


def sig(t):
    return tuple(sorted(v[0] for v in t.values()))


ck = list(csv.DictReader(open(f"{ROOT}/olmo_weights/manifest/checkpoints.csv")))
repos = sorted({r["repo"] for r in ck} | {"allenai/Olmo-3-32B-Think"})
R = {repo: refs(repo) for repo in repos}
res = dict(repos={repo: len(v) for repo, v in R.items()})

# 1-2. refs and trees
bad_ref, bad_tree, n_files = [], [], 0
T = {}
for r in ck:
    commit = R[r["repo"]].get(r["branch"])
    if commit != r["commit"]:
        bad_ref.append((r["label"], r["branch"], r["commit"], commit))
    t = tree(r["repo"], r["commit"])
    T[r["label"]] = t
    want = dict(zip(r["files"].split(";"), zip(r["sha256"].split(";"), [int(x) for x in r["sizes"].split(";")])))
    n_files += len(want)
    if t != want:
        bad_tree.append((r["label"], sorted(set(t) ^ set(want))[:4],
                         [f for f in want if f in t and t[f] != want[f]][:4]))
res.update(n_checkpoints=len(ck), n_files=n_files, bad_ref=bad_ref, bad_tree=bad_tree,
           bytes=sum(int(r["bytes"]) for r in ck))

# 3. byte identity
lab_of = {}
for r in ck:
    lab_of.setdefault((r["repo"], sig(T[r["label"]])), []).append(r["label"])


def ident(repo, rev):
    t = tree(repo, R[repo][rev] if rev in R[repo] else rev)
    same = [lab for (rp, s), labs in lab_of.items() if rp == repo and s == sig(t) for lab in labs]
    same_branches = sorted(b for b, c in R[repo].items() if b != rev and sig(tree(repo, c)) == sig(t)) \
        if len(R[repo]) < 80 else None
    return dict(rev=rev, commit=R[repo].get(rev), files=len(t), same_manifest_labels=same, same_branches=same_branches)


checks = {}
for repo in repos:
    if repo != "allenai/Olmo-3-32B-Think":
        checks[f"{repo}@main"] = ident(repo, "main")
# base repos have hundreds of branches: compare main against the stage-3 branches only
for repo in ("allenai/Olmo-3-1125-32B", "allenai/Olmo-3-1025-7B"):
    mt = sig(tree(repo, R[repo]["main"]))
    checks[f"{repo}@main"]["same_stage3_branches"] = sorted(
        b for b, c in R[repo].items() if b.startswith("stage3") and sig(tree(repo, c)) == mt)
    checks[f"{repo}@stage3_branches"] = sorted(b for b in R[repo] if b.startswith("stage3"))
# Olmo-3-32B-Think against the 3.1 run
th = R["allenai/Olmo-3-32B-Think"]
s31 = {b: sig(tree("allenai/Olmo-3.1-32B-Think", c)) for b, c in R["allenai/Olmo-3.1-32B-Think"].items()}
checks["Olmo-3-32B-Think"] = {b: sorted(x for x, s in s31.items() if s == sig(tree("allenai/Olmo-3-32B-Think", c)))
                              for b, c in sorted(th.items())}
# duplicate signatures among manifest labels of one repo
dups = [labs for (rp, s), labs in lab_of.items() if len(labs) > 1]
# duplicates among all branches of the RL / RL-Zero / SFT repos
alldups = {}
for repo in repos:
    if len(R[repo]) >= 80 or repo == "allenai/Olmo-3-32B-Think":
        continue
    g = {}
    for b, c in R[repo].items():
        g.setdefault(sig(tree(repo, c)), []).append(b)
    alldups[repo] = sorted(sorted(v) for v in g.values() if len(v) > 1)
res.update(checks=checks, manifest_duplicate_labels=dups, branch_duplicates=alldups)

# 4. stage-1 locations from the pre-registered rule
def stage1_locs(repo, n_loc):
    steps = sorted(int(b[len("stage1-step"):]) for b in R[repo] if b.startswith("stage1-step")
                   and b[len("stage1-step"):].isdigit())
    st = set(steps)
    starts = sorted(s for s in steps if s + 1000 in st)
    early = []
    for tgt in [0] + [1000 * 2 ** k for k in range(0, 7)]:
        if tgt == 0:
            c = 0 if 0 in starts else None
        else:
            c = min((s for s in starts if s > 0), key=lambda s: (abs(math.log(s / tgt)), s))
        if c is not None and c not in early:
            early.append(c)
    last = max(starts)
    m = n_loc - len(early)
    even = []
    for j in range(1, m + 1):
        x = 64000 + (last - 64000) * j / m
        c = min((s for s in starts if s > 64000), key=lambda s: (abs(s - x), s))
        even.append(c)
    return dict(steps=len(steps), pair_starts=len(starts), last_pair_start=last, final_step=max(steps),
                early=early, even=even, all=early + even, n=len(early + even), n_unique=len(set(early + even)))


res["stage1"] = {"32B": stage1_locs("allenai/Olmo-3-1125-32B", 25), "7B": stage1_locs("allenai/Olmo-3-1025-7B", 30)}
J = json.load(open(f"{ROOT}/olmo_weights/manifest/stage1_locations.json"))
res["stage1_manifest"] = J
json.dump(res, open(os.path.join(OUT, "rv_manifest_check.json"), "w"), indent=1)
print("checkpoints", len(ck), "files", n_files, "bad_ref", len(bad_ref), "bad_tree", len(bad_tree))
for k, v in res["stage1"].items():
    print(k, v["n"], v["n_unique"], v["all"])
print("manifest stage1:", J)
