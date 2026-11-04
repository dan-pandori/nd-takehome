"""Hub checks (reviewer): revision commits, tokenizer blob identity, main == step_2300 shard hashes, generation
config EOS. Metadata only; no weights downloaded."""
import json
from huggingface_hub import HfApi, hf_hub_download

api = HfApi()
out = {}
specs = [("dpo", "allenai/Olmo-3-32B-Think-DPO", "main"), ("s0100", "allenai/Olmo-3.1-32B-Think", "step_0100"),
         ("s0750", "allenai/Olmo-3.1-32B-Think", "step_0750"), ("s2300", "allenai/Olmo-3.1-32B-Think", "main"),
         ("s2300_branch", "allenai/Olmo-3.1-32B-Think", "step_2300")]
for lab, repo, rev in specs:
    try:
        mi = api.model_info(repo, revision=rev, files_metadata=True)
    except Exception as e:
        out[lab] = {"error": repr(e)[:200]}
        continue
    files = {s.rfilename: {"blob": s.blob_id, "lfs": (s.lfs.sha256 if s.lfs else None), "size": s.size}
             for s in mi.siblings}
    tok = {k: v["blob"] for k, v in files.items() if "token" in k or k.endswith("vocab.json") or k.endswith("merges.txt")
           or k == "chat_template.jinja"}
    shards = {k: v["lfs"] for k, v in files.items() if k.endswith(".safetensors")}
    gc = json.load(open(hf_hub_download(repo, "generation_config.json", revision=rev)))
    cfg = json.load(open(hf_hub_download(repo, "config.json", revision=rev)))
    out[lab] = {"repo": repo, "rev": rev, "sha": mi.sha, "tok_blobs": tok, "n_shards": len(shards), "shards": shards,
                "gen_config": gc, "arch": cfg.get("architectures"), "layers": cfg.get("num_hidden_layers"),
                "kv_heads": cfg.get("num_key_value_heads"), "rope_scaling": cfg.get("rope_scaling"),
                "max_pos": cfg.get("max_position_embeddings"), "sliding_window": cfg.get("sliding_window"),
                "layer_types": (sorted(set(cfg["layer_types"])) if cfg.get("layer_types") else None),
                "n_full": (sum(1 for t in cfg.get("layer_types", []) if t == "full_attention")),
                "torch_dtype": cfg.get("torch_dtype")}
refs = api.list_repo_refs("allenai/Olmo-3.1-32B-Think")
out["think_branches"] = sorted(b.name for b in refs.branches)
json.dump(out, open("out/hub.json", "w"), indent=1)
for lab in [s[0] for s in specs]:
    o = out[lab]
    if "error" in o:
        print(lab, o["error"]); continue
    print(lab, o["rev"], o["sha"][:12], "shards", o["n_shards"], "eos", o["gen_config"].get("eos_token_id"),
          "T", o["gen_config"].get("temperature"), "top_p", o["gen_config"].get("top_p"), o["arch"], o["layers"],
          "kv", o["kv_heads"], "full", o["n_full"], o["rope_scaling"], o["max_pos"], o["sliding_window"], o["torch_dtype"])
base = out["dpo"]["tok_blobs"]
for lab in ["s0100", "s0750", "s2300"]:
    print("tokenizer blobs equal dpo vs", lab, out[lab]["tok_blobs"] == base, sorted(base))
if "error" not in out["s2300_branch"]:
    print("main shards == step_2300 shards:", out["s2300"]["shards"] == out["s2300_branch"]["shards"],
          "sha equal:", out["s2300"]["sha"] == out["s2300_branch"]["sha"])
print("branches:", [b for b in out["think_branches"] if b in ("main", "step_0100", "step_0750", "step_2300")], len(out["think_branches"]))
