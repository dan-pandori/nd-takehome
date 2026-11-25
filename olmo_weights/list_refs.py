"""List every branch (revision) and its commit of the Olmo 3 repos used by olmo-weights (Hub API, no downloads).

Writes olmo_weights/manifest/refs.json: {repo: {"branches": {name: commit}, "main": commit}} and prints a summary
of branch-name patterns per repo.
"""
import json, re, sys
from collections import Counter
from huggingface_hub import HfApi

REPOS = ["allenai/Olmo-3-1125-32B", "allenai/Olmo-3-32B-Think-SFT", "allenai/Olmo-3-32B-Think-DPO",
         "allenai/Olmo-3.1-32B-Think", "allenai/Olmo-3-32B-Think",
         "allenai/Olmo-3-1025-7B", "allenai/Olmo-3-7B-Think-SFT", "allenai/Olmo-3-7B-Think-DPO",
         "allenai/Olmo-3-7B-Think", "allenai/Olmo-3-7B-RL-Zero-IF", "allenai/Olmo-3-7B-RL-Zero-Math",
         "allenai/Olmo-3-7B-RL-Zero-Code"]
api = HfApi()
out = {}
for r in REPOS:
    refs = api.list_repo_refs(r)
    br = {b.name: b.target_commit for b in refs.branches}
    out[r] = {"branches": br, "tags": {t.name: t.target_commit for t in refs.tags}}
    pat = Counter(re.sub(r"\d+", "#", n) for n in br)
    print(f"{r}: {len(br)} branches, {len(out[r]['tags'])} tags; patterns: " +
          "; ".join(f"{p} x{c}" for p, c in pat.most_common(12)))
json.dump(out, open("olmo_weights/manifest/refs.json", "w"), indent=1, sort_keys=True)
