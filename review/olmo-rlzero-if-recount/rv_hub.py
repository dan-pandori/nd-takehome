#!/usr/bin/env python3
"""Reviewer: HF hub provenance for olmo-rlzero-if (stdlib only). Per branch: file blob ids, LFS sha256 of shards.
Writes ~/review/rzi_rv/hf/hub_tree.json and prints the shard-identity table."""
import json, os, sys, time, urllib.request
OUT = os.path.expanduser("~/review/rzi_rv/hf")
def get(url):
    for k in range(4):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            time.sleep(2 + 3 * k); err = e
    raise err
def tree(repo, rev):
    d = get(f"https://huggingface.co/api/models/{repo}/tree/{rev}?recursive=1&expand=1")
    files = {}
    for x in d:
        if x.get("type") != "file": continue
        files[x["path"]] = {"oid": x.get("oid"), "size": x.get("size"), "lfs": (x.get("lfs") or {}).get("oid")}
    return files
want = {"allenai/Olmo-3-7B-RL-Zero-IF": None, "allenai/Olmo-3-1025-7B": ["main", "stage3-step11921", "stage3-step11900", "stage3-step11000"],
        "allenai/Olmo-3-7B-RL-Zero-Math": ["main", "step_1900"]}
res = {}
for repo, revs in want.items():
    refs = json.load(open(f"{OUT}/refs_{repo.replace('/', '_')}.json"))
    commits = {b["name"]: b["targetCommit"] for b in refs["branches"]}
    if revs is None: revs = sorted(commits)
    for rev in revs:
        res[f"{repo}@{rev}"] = {"commit": commits[rev], "files": tree(repo, commits[rev])}
        print(repo, rev, commits[rev][:8], len(res[f"{repo}@{rev}"]["files"]), flush=True)
json.dump(res, open(f"{OUT}/hub_tree.json", "w"), indent=1)
