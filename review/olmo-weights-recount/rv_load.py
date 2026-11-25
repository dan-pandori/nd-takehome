"""Reviewer (olmo-weights): load the executor's raw per-tensor statistics (stats/<job>/shard_*/*.csv.gz) into sums
per (job, chain, idx) overall, per module and per layer. Checks completeness on the way: every shard DONE, each
(chain, idx, tensor) row exactly once, every interval covers the full tensor set of its family."""
import csv, glob, gzip, json, os, re
from collections import defaultdict

MODULES = {
    "model.embed_tokens.weight": "embed", "lm_head.weight": "lm_head", "model.norm.weight": "final_norm",
}
PAT = re.compile(r"model\.layers\.(\d+)\.(self_attn|mlp)?\.?([a-z_]+)\.weight$")


def module_of(t):
    if t in MODULES:
        return MODULES[t], None
    m = re.match(r"model\.layers\.(\d+)\.(.+)\.weight$", t)
    assert m, t
    L, rest = int(m.group(1)), m.group(2)
    short = {"self_attn.q_proj": "q", "self_attn.k_proj": "k", "self_attn.v_proj": "v", "self_attn.o_proj": "o",
             "self_attn.q_norm": "q_norm", "self_attn.k_norm": "k_norm", "mlp.gate_proj": "gate", "mlp.up_proj": "up",
             "mlp.down_proj": "down", "post_attention_layernorm": "post_attn_norm",
             "post_feedforward_layernorm": "post_ff_norm"}[rest]
    return short, L


def rows(job_dir, kind):
    out = []
    shards = sorted(glob.glob(os.path.join(job_dir, "shard_*")))
    for s in shards:
        assert os.path.exists(os.path.join(s, "DONE")), s
        with gzip.open(os.path.join(s, f"{kind}.csv.gz"), "rt") as f:
            for r in csv.DictReader(f):
                r["_shard"] = os.path.basename(s)
                out.append(r)
    return out


def load(root):
    S = os.path.join(root, "artifacts/olmo_weights/stats")
    J = json.load(open(os.path.join(root, "olmo_weights/manifest/jobs.json")))
    D = {}
    for job in sorted(J):
        jd = os.path.join(S, job)
        iv, st, lag = rows(jd, "iv"), rows(jd, "st"), rows(jd, "lag")
        lora = rows(jd, "lora") if J[job].get("lora") else []
        gram = rows(jd, "gram") if J[job].get("gram") else []
        # uniqueness and coverage
        seen = set()
        tensors = set()
        for r in iv:
            k = (r["chain"], int(r["idx"]), r["a"], r["b"], r["tensor"])
            assert k not in seen, ("dup iv", job, k)
            seen.add(k)
            tensors.add(r["tensor"])
        per = defaultdict(set)
        for r in iv:
            per[(r["chain"], int(r["idx"]), r["a"], r["b"])].add(r["tensor"])
        for k, v in per.items():
            assert v == tensors, ("missing tensors", job, k, len(v), len(tensors))
        for kind, rr, key in (("st", st, lambda r: (r["chain"], int(r["idx"]), r["tensor"])),
                              ("lag", lag, lambda r: (r["chain"], int(r["idx"]), int(r["lag"]), r["tensor"]))):
            ss = set()
            for r in rr:
                k = key(r)
                assert k not in ss, ("dup", kind, job, k)
                ss.add(k)
        D[job] = dict(iv=iv, st=st, lag=lag, lora=lora, gram=gram, tensors=tensors, job=J[job])
        if J[job].get("lora"):
            with open(os.path.join(jd, "lora_norms.csv")) as f:
                D[job]["lora_norms"] = list(csv.DictReader(f))
    return D, J


def agg(rr, keyf, fields, group=lambda t: "all"):
    """sum float/int fields of rows by (keyf(row), group(tensor))."""
    out = defaultdict(lambda: defaultdict(float))
    for r in rr:
        k = (keyf(r), group(r["tensor"]))
        o = out[k]
        for f in fields:
            o[f] += float(r[f])
    return out
