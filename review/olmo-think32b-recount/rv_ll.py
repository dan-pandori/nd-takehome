"""Likelihood recount (reviewer): items vs stored samples, prompt = olmo_thinker(problem), per-token lps -> per-item
mean / sum, fraction of RL items inside dpo's own 2.5-97.5 % per-token range (both reference sets), mean gaps."""
import base64, collections, gzip, json, os, sys
import numpy as np
from tokenizers import Tokenizer
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_core as C
LL = os.path.join(C.ROOT, "artifacts", "olmo32", "ll")
items = [json.loads(l) for l in open(os.path.join(LL, "items.jsonl"))]
scores = {json.loads(l)["key"]: json.loads(l) for l in open(os.path.join(LL, "scores_dpo.jsonl"))}
tok = Tokenizer.from_file(os.path.join(C.HERE, "out", "tokcfg", "tokenizer.json"))
probs = {p["pid"]: p for p in C.problems()}
# stored sample ids by key
need = collections.defaultdict(set)
for it in items:
    job, pid, c, i = it["key"].split("|"); need[job].add((pid, int(c), int(i)))
stored = {}
for job, ks in need.items():
    with gzip.open(os.path.join(C.ROOT, "artifacts", "olmo32", "samples", f"{job}.jsonl.gz"), "rt") as f:
        for l in f:
            r = json.loads(l)
            if (r["pid"], r["chunk"], r["i"]) in ks:
                stored[f"{job}|{r['pid']}|{r['chunk']}|{r['i']}"] = r["ids"]
grades = {(r["job"], r["pid"], r["chunk"], r["i"]): r for r in C.rows()}
def expected_prompt(problem):
    return ("<|im_start|>system\nYou are a helpful AI assistant.<|im_end|>\n<|im_start|>user\n" + problem +
            "<|im_end|>\n<|im_start|>assistant\n<think>")
chk = collections.Counter(); rows = []
for it in items:
    s = scores[it["key"]]
    lps = np.frombuffer(base64.b64decode(s["lps"]), dtype=np.float32)
    resp = np.frombuffer(base64.b64decode(it["resp_ids"]), dtype=np.int32)
    pr = np.frombuffer(base64.b64decode(it["prompt_ids"]), dtype=np.int32).tolist()
    chk["resp==stored"] += it["resp_ids"] == stored.get(it["key"])
    chk["prompt==template"] += tok.decode(pr, skip_special_tokens=False) == expected_prompt(probs[it["pid"]]["problem"])
    chk["prompt_no_bos"] += pr[0] != 100257
    chk["len(lps)==len(resp)"] += len(lps) == len(resp) == s["n_tok"]
    chk["sum matches"] += abs(float(lps.sum()) - s["sum_lp"]) < 1e-2 * max(1, abs(s["sum_lp"])) * 1e-3 + 0.5
    job, pid, c, i = it["key"].split("|")
    g = grades[(job, pid, int(c), int(i))]
    chk["rl-credited"] += g["rl"]
    rows.append({"key": it["key"], "group": it["group"], "model": it["gen_model"], "pid": it["pid"], "final": g["final"],
                 "n": len(lps), "mean": float(lps.mean()), "sum": float(lps.sum()), "cut": g["finish"] == "length"})
print("checks over", len(items), "items:", dict(chk))
print("groups:", collections.Counter((r["group"], r["model"]) for r in rows))
own = [r for r in rows if r["group"] == "dpo_on_candidate"]; ref = [r for r in rows if r["group"] == "dpo_reference"]
rl = [r for r in rows if r["group"] == "rl_on_candidate"]
out = {}
for name, base in (("dpo_on_candidate", own), ("dpo_reference", ref), ("both", own + ref)):
    lo, hi = np.percentile([r["mean"] for r in base], [2.5, 97.5])
    inside = [lo <= r["mean"] <= hi for r in rl]
    out[name] = {"n_base": len(base), "range": [float(lo), float(hi)], "rl_inside": int(sum(inside)), "rl_n": len(rl),
                 "share": float(np.mean(inside)), "base_mean": float(np.mean([r["mean"] for r in base])),
                 "rl_mean": float(np.mean([r["mean"] for r in rl])),
                 "gap_rl_minus_base": float(np.mean([r["mean"] for r in rl]) - np.mean([r["mean"] for r in base]))}
for m in ("s0100", "s0750", "s2300"):
    xs = [r for r in rl if r["model"] == m]
    out[f"rl_{m}"] = {"n": len(xs), "mean": float(np.mean([r["mean"] for r in xs])),
                      "median_sum": float(np.median([r["sum"] for r in xs])), "median_n": float(np.median([r["n"] for r in xs]))}
out["dpo_on_candidate_detail"] = sorted((round(r["mean"], 4), round(r["sum"], 1), r["n"], r["final"], r["cut"]) for r in own)
out["dpo_on_candidate_median_sum"] = float(np.median([r["sum"] for r in own]))
json.dump({"summary": out, "rows": rows}, open(os.path.join(C.HERE, "out", "ll_recount.json"), "w"), indent=1)
for k, v in out.items():
    print(k, v)
