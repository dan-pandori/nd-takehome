"""Checkpoint manifest check for run olmo-ifcurve: my own Hub API query (huggingface_hub, no token needed).

For each revision of the pre-registration's table: commit sha, every file's blob id, LFS sha256 and size. Checks:
commit = the run's checkpoints.csv commit; 14 safetensors shards; weight bytes; tokenizer / config / template blobs;
main of Olmo-3.1-32B-Think vs step_2300 (per-shard LFS sha256 and the index weight map); every RL revision's weights
distinct; and the commit history of both repos' main (did main move after the stored draws of 2026-11-04 / 11-05?).
Writes out/hub.json and out/hub.txt. Run with ~/.local/share/uv/tools/huggingface-hub/bin/python.
"""
import csv
import hashlib
import json
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download

KIT = Path(__file__).resolve().parent
OUT = KIT / "out"
RAW = Path.home() / "review" / "olmo-ifcurve"
api = HfApi()
REVS = [("dpo", "allenai/Olmo-3-32B-Think-DPO", "main")] + [
    (f"s{s:04d}", "allenai/Olmo-3.1-32B-Think", f"step_{s:04d}") for s in (50, 100, 200, 350, 500, 750, 1100, 1600, 2300)
] + [("main", "allenai/Olmo-3.1-32B-Think", "main")]


def main():
    lines = []

    def say(*a):
        s = " ".join(str(x) for x in a)
        print(s)
        lines.append(s)

    info = {}
    for name, repo, rev in REVS:
        mi = api.model_info(repo, revision=rev, files_metadata=True)
        files = {}
        for s in mi.siblings:
            files[s.rfilename] = {"blob": s.blob_id, "size": s.size,
                                  "lfs_sha256": (s.lfs.sha256 if s.lfs else None)}
        info[name] = {"repo": repo, "rev": rev, "sha": mi.sha, "files": files,
                      "last_modified": str(mi.last_modified)}
    ex = {r["name"]: r for r in csv.DictReader(open(RAW / "olmo_ifcurve" / "checkpoints.csv"))}
    say("name rev | my commit | csv commit | shards | weight bytes (mine / csv) | tokenizer.json blob | match")
    for name, repo, rev in REVS:
        f = info[name]["files"]
        sh = sorted(k for k in f if k.endswith(".safetensors"))
        wb = sum(f[k]["size"] for k in sh)
        # candidate digests: sha256 over sorted "name sha" lines / concatenated shas
        c1 = hashlib.sha256("".join(f[k]["lfs_sha256"] for k in sh).encode()).hexdigest()
        c2 = hashlib.sha256("\n".join(f"{k} {f[k]['lfs_sha256']}" for k in sh).encode()).hexdigest()
        c3 = hashlib.sha256("\n".join(f[k]["lfs_sha256"] for k in sh).encode()).hexdigest()
        info[name]["weights_bytes"] = wb
        info[name]["n_shards"] = len(sh)
        info[name]["cand_digests"] = [c1, c2, c3]
        e = ex.get(name)
        if e is None:
            say(name, rev, info[name]["sha"][:12], "(not in csv)", len(sh), wb, f.get("tokenizer.json", {}).get("blob"))
            continue
        ok = (e["commit"] == info[name]["sha"] and int(e["n_shards"]) == len(sh) and int(e["weight_bytes"]) == wb
              and e["tokenizer_json_blob"] == f["tokenizer.json"]["blob"])
        dig = [i for i, c in enumerate((c1, c2, c3)) if c == e["weights_digest"]]
        say(name, rev, "|", info[name]["sha"][:12], "|", e["commit"][:12], "|", len(sh), "|", wb, "/", e["weight_bytes"],
            "|", f["tokenizer.json"]["blob"][:12], "| commit/shards/bytes/tok", ok, "| digest formula", dig or "none matched")
        for col, fn in (("tokenizer_config_blob", "tokenizer_config.json"), ("config_blob", "config.json"),
                        ("generation_config_blob", "generation_config.json"), ("chat_template_blob", "chat_template.jinja"),
                        ("index_blob", "model.safetensors.index.json")):
            mine = f.get(fn, {}).get("blob")
            if e.get(col) != mine:
                say("   ", name, col, "csv", e.get(col), "mine", mine)
    # main vs step_2300
    a, b = info["main"]["files"], info["s2300"]["files"]
    sh = sorted(k for k in a if k.endswith(".safetensors"))
    same = sh == sorted(k for k in b if k.endswith(".safetensors")) and all(a[k]["lfs_sha256"] == b[k]["lfs_sha256"] for k in sh)
    say("main vs step_2300: same shard names and LFS sha256:", same)
    diff = sorted(k for k in set(a) | set(b) if a.get(k, {}).get("blob") != b.get(k, {}).get("blob"))
    say("main vs step_2300: files whose blob differs:", diff)
    for rv in ("main", "step_2300"):
        p = hf_hub_download("allenai/Olmo-3.1-32B-Think", "model.safetensors.index.json", revision=rv)
        info[("main" if rv == "main" else "s2300")]["weight_map_sha"] = hashlib.sha256(
            json.dumps(json.load(open(p))["weight_map"], sort_keys=True).encode()).hexdigest()
    say("index weight_map identical:", info["main"]["weight_map_sha"] == info["s2300"]["weight_map_sha"])
    # distinct weights across RL revisions
    digs = {n: info[n]["cand_digests"][0] for n in info}
    say("distinct weight sets among the 11 revisions:", len(set(digs.values())), "(main = s2300 expected -> 10)")
    toks = {n: info[n]["files"]["tokenizer.json"]["blob"] for n in info}
    say("tokenizer.json blobs:", sorted(set(toks.values())))
    tmpl = {n: info[n]["files"].get("chat_template.jinja", {}).get("blob") for n in info}
    say("chat_template.jinja blobs:", {v: sorted(k for k in tmpl if tmpl[k] == v) for v in set(tmpl.values())})
    gen = {n: info[n]["files"].get("generation_config.json", {}).get("blob") for n in info}
    say("generation_config.json blobs:", {v: sorted(k for k in gen if gen[k] == v) for v in set(gen.values())})
    # history of main
    for repo in ("allenai/Olmo-3-32B-Think-DPO", "allenai/Olmo-3.1-32B-Think"):
        cs = api.list_repo_commits(repo, revision="main")
        say(f"{repo} main history (newest first, {len(cs)} commits):")
        for c in cs[:8]:
            say("   ", c.commit_id[:12], c.created_at, (c.title or "")[:80])
        info[f"history_{repo}"] = [(c.commit_id, str(c.created_at), c.title) for c in cs]
    json.dump(info, open(OUT / "hub.json", "w"), indent=1, default=str)
    open(OUT / "hub.txt", "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
