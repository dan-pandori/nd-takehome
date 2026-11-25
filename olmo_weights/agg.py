"""Load the engine's per-tensor statistics and aggregate them (VPS-side; csv + numpy only).

load(job) -> dict of row lists per kind (iv, lag, st, gram, lora) and lora_norms.
group_of(tensor) -> (module, layer) with module in MODULES and layer an int or None.
"""
import csv, glob, gzip, io, json, os, re

STATS = "artifacts/olmo_weights/stats"
MODULES = ["embed", "q", "k", "v", "o", "gate", "up", "down", "q_norm", "k_norm", "attn_norm", "ffn_norm",
           "final_norm", "lm_head"]
_PAT = [("embed", r"model\.embed_tokens\.weight"), ("lm_head", r"lm_head\.weight"), ("final_norm", r"model\.norm\.weight"),
        ("q", r"self_attn\.q_proj"), ("k", r"self_attn\.k_proj"), ("v", r"self_attn\.v_proj"), ("o", r"self_attn\.o_proj"),
        ("q_norm", r"self_attn\.q_norm"), ("k_norm", r"self_attn\.k_norm"), ("gate", r"mlp\.gate_proj"),
        ("up", r"mlp\.up_proj"), ("down", r"mlp\.down_proj"), ("attn_norm", r"post_attention_layernorm"),
        ("ffn_norm", r"post_feedforward_layernorm")]


def group_of(t):
    m = re.search(r"model\.layers\.(\d+)\.", t)
    layer = int(m.group(1)) if m else None
    for name, p in _PAT:
        if re.search(p, t):
            return name, layer
    raise ValueError(t)


def _open(p):
    if p.endswith(".gz"):
        return io.TextIOWrapper(gzip.open(p, "rb"), newline="")
    return open(p, newline="")


def load(job, root=STATS):
    out = {k: [] for k in ("iv", "lag", "st", "gram", "lora")}
    shards = sorted(glob.glob(os.path.join(root, job, "shard_*")), key=lambda p: int(p.rsplit("_", 1)[1]))
    for sd in shards:
        if not os.path.exists(os.path.join(sd, "DONE")):
            continue
        for k in out:
            for p in (os.path.join(sd, f"{k}.csv"), os.path.join(sd, f"{k}.csv.gz")):
                if os.path.exists(p):
                    out[k] += list(csv.DictReader(_open(p)))
                    break
    out["n_shards_done"] = sum(os.path.exists(os.path.join(sd, "DONE")) for sd in shards)
    ln = [p for p in (os.path.join(root, job, "lora_norms.csv"), os.path.join(root, job, "lora_norms.csv.gz"))
          if os.path.exists(p)]
    out["lora_norms"] = list(csv.DictReader(_open(ln[0]))) if ln else []
    return out


def sums(rows, keys, by=None, num_int=("numel", "n_eq", "n_ulp", "n_nonfinite", "n_eq_s", "n_ulp_s")):
    """Sum columns `keys` over rows, grouped by the tuple of columns `by` (plus 'module'/'layer' if requested)."""
    acc = {}
    for r in rows:
        g = []
        for b in (by or []):
            if b == "module":
                g.append(group_of(r["tensor"])[0])
            elif b == "layer":
                g.append(group_of(r["tensor"])[1])
            else:
                g.append(r[b])
        g = tuple(g)
        d = acc.setdefault(g, {k: 0 for k in keys})
        for k in keys:
            d[k] += int(r[k]) if k in num_int else float(r[k])
    return acc
