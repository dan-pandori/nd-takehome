"""Fetch the file tree (path, size, LFS sha256, git blob id) of given (repo, revision) pairs from the Hub API.

No weights are downloaded. Each tree is cached in olmo_weights/manifest/trees/<repo>__<revision>.json, so re-runs
only fetch what is missing. Usage: fetch_trees.py <listfile with 'repo revision' lines>
"""
import json, os, sys, time
from huggingface_hub import HfApi

api = HfApi()
D = "olmo_weights/manifest/trees"
os.makedirs(D, exist_ok=True)


def path_for(repo, rev):
    return f"{D}/{repo.replace('/', '__')}__{rev}.json"


def fetch(repo, rev):
    p = path_for(repo, rev)
    if os.path.exists(p):
        return "cached"
    for attempt in range(5):
        try:
            files = []
            for f in api.list_repo_tree(repo, revision=rev):
                lfs = getattr(f, "lfs", None)
                files.append({"path": f.path, "size": getattr(f, "size", None),
                              "sha256": lfs.sha256 if lfs else None, "blob_id": getattr(f, "blob_id", None)})
            json.dump({"repo": repo, "revision": rev, "files": files}, open(p + ".tmp", "w"))
            os.replace(p + ".tmp", p)
            return "fetched"
        except Exception as e:  # rate limits / transient errors
            print(f"retry {attempt} {repo}@{rev}: {str(e)[:120]}", flush=True)
            time.sleep(10 * (attempt + 1))
    return "FAILED"


if __name__ == "__main__":
    pairs = [ln.split() for ln in open(sys.argv[1]) if ln.strip()]
    n = {"cached": 0, "fetched": 0, "FAILED": 0}
    for repo, rev in pairs:
        r = fetch(repo, rev)
        n[r] += 1
        if r == "FAILED":
            print("FAILED", repo, rev, flush=True)
    print(n)
