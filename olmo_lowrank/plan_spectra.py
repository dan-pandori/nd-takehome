#!/usr/bin/env python3
"""VPS side: the Part-1 job plan (olmo_lowrank/plan/spectra_jobs.json) from olmo_weights/manifest/checkpoints.csv.
Members are manifest labels (repo, branch, commit, files, sha256 pinned there); the pre-registered model names map to
labels with identical shard hashes: 32B base main = 32B/s3merge, 32B SFT main = 32B/sft5e-5/8000, 7B base main =
7B/s3/11921, 7B SFT main = 7B/sftmain, 7B RL-Zero-IF main = 7B/zifmain, s2300 = 32B/rl/2300."""
import csv, json
M = {r["label"]: r for r in csv.DictReader(open("olmo_weights/manifest/checkpoints.csv"))}


def mem(label, name):
    r = M[label]
    return {"name": name, "label": label, "repo": r["repo"], "branch": r["branch"], "commit": r["commit"],
            "files": r["files"].split(";"), "sha256": r["sha256"].split(";"), "bytes": int(r["bytes"])}


def rl32(t):
    return mem(f"32B/rl/{t}", f"s{t:04d}")


def rl7(t):
    return mem(f"7B/rl/{t}", f"r{t:04d}")


J = {}
J["R32"] = {"family": "32B", "steps": "shard", "start": "dpo", "lora": True, "subset_mod": 8,
            "members": [mem("32B/dpo", "dpo")] + [rl32(t) for t in (50, 100, 500, 750, 1100, 1150, 1600, 2100, 2250, 2300)],
            "changes": [{"id": f"N{t}", "a": "dpo", "b": f"s{t:04d}", "kind": "net"} for t in (50, 100, 500, 750, 1100, 1600, 2300)]
            + [{"id": "I_early", "a": "s0050", "b": "s0100", "kind": "interval"},
               {"id": "I_mid", "a": "s1100", "b": "s1150", "kind": "interval"},
               {"id": "I_late", "a": "s2250", "b": "s2300", "kind": "interval"},
               {"id": "K", "a": "s1100", "b": "s2100", "kind": "chord"}],
            "floorA": {"on": "dpo", "intervals": ["I_early", "I_mid", "I_late"]}}
J["S32"] = {"family": "32B", "steps": "all", "lora": False, "subset_mod": 8,
            "members": [mem("32B/s3merge", "base"), mem("32B/sft5e-5/8000", "sft"), mem("32B/dpo", "dpo")],
            "changes": [{"id": "SFT", "a": "base", "b": "sft", "kind": "total"},
                        {"id": "DPO", "a": "sft", "b": "dpo", "kind": "total"}], "floorA": None}
J["R7"] = {"family": "7B", "steps": "shard", "lora": False, "subset_mod": 8,
           "members": [mem("7B/s3/11921", "base"), mem("7B/sftmain", "sft"), mem("7B/dpo", "dpo")]
           + [rl7(t) for t in (25, 50, 100, 500, 525, 1000, 1350, 1375)] + [mem("7B/zifmain", "zif")],
           "changes": [{"id": f"N{t}", "a": "dpo", "b": f"r{t:04d}", "kind": "net"} for t in (25, 100, 500, 1000, 1375)]
           + [{"id": "I_early", "a": "r0025", "b": "r0050", "kind": "interval"},
              {"id": "I_mid", "a": "r0500", "b": "r0525", "kind": "interval"},
              {"id": "I_late", "a": "r1350", "b": "r1375", "kind": "interval"},
              {"id": "K", "a": "r0500", "b": "r1375", "kind": "chord"},
              {"id": "SFT", "a": "base", "b": "sft", "kind": "total"},
              {"id": "DPO", "a": "sft", "b": "dpo", "kind": "total"},
              {"id": "ZIF", "a": "base", "b": "zif", "kind": "total"}],
           "floorA": {"on": "dpo", "intervals": ["I_early", "I_mid", "I_late"]}}
for j in J.values():
    names = {m["name"] for m in j["members"]}
    assert all(c["a"] in names and c["b"] in names for c in j["changes"])
    j["GB"] = round(sum(m["bytes"] for m in j["members"]) / 1e9, 1)
json.dump(J, open("olmo_lowrank/plan/spectra_jobs.json", "w"), indent=1)
print({k: (len(v["members"]), len(v["changes"]), v["GB"]) for k, v in J.items()})
