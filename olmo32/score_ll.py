#!/usr/bin/env python3
"""Teacher-forced log-likelihood of given responses under one checkpoint (vLLM prompt_logprobs, bf16).

Input JSONL rows: key, prompt_ids, resp_ids (base64 int32). Output JSONL rows: key, model, n_tok, sum_lp, mean_lp,
min_lp, n_lt_1e3 / n_lt_1e6 (tokens with p < 1e-3 / 1e-6), p10_lp, and lps (base64 float32 per-token log-probs).
The log-probs are of the raw model distribution, which is the sampling distribution here (temperature 1, top_p 1).

Usage: score_ll.py --model <dir> --tokenizer <dir> --name <label> --items <jsonl> --out <jsonl>
"""
import argparse
import base64
import json
import time

import numpy as np


def b64i(s):
    return np.frombuffer(base64.b64decode(s), dtype=np.int32).tolist()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--items", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--gpu_mem", type=float, default=0.85)
    args = ap.parse_args()
    from vllm import LLM, SamplingParams

    items = [json.loads(ln) for ln in open(args.items)]
    seqs = [(it["key"], b64i(it["prompt_ids"]), b64i(it["resp_ids"])) for it in items]
    t0 = time.time()
    llm = LLM(model=args.model, tokenizer=args.tokenizer, dtype="bfloat16",
              max_model_len=max(len(p) + len(r) for _, p, r in seqs) + 8, gpu_memory_utilization=args.gpu_mem,
              enable_prefix_caching=False, max_num_batched_tokens=4096, seed=0)
    t_load = time.time() - t0
    sp = SamplingParams(max_tokens=1, prompt_logprobs=0, detokenize=False)
    t1 = time.time()
    outs = llm.generate([{"prompt_token_ids": p + r} for _, p, r in seqs], sp, use_tqdm=False)
    t_score = time.time() - t1
    ntot = 0
    with open(args.out, "w") as f:
        for (key, p, r), o in zip(seqs, outs):
            plp = o.prompt_logprobs
            full = p + r
            lps = np.array([plp[j][full[j]].logprob for j in range(len(p), len(full))], dtype=np.float32)
            ntot += len(lps)
            f.write(json.dumps({"key": key, "model": args.name, "n_tok": int(len(lps)), "sum_lp": float(lps.sum()),
                                "mean_lp": float(lps.mean()), "min_lp": float(lps.min()),
                                "n_lt_1e3": int((lps < np.log(1e-3)).sum()), "n_lt_1e6": int((lps < np.log(1e-6)).sum()),
                                "p10_lp": float(np.percentile(lps, 10)),
                                "lps": base64.b64encode(lps.tobytes()).decode()}) + "\n")
    print(json.dumps({"name": args.name, "items": len(seqs), "tokens": ntot, "t_load_s": round(t_load, 1),
                      "t_score_s": round(t_score, 1), "tok_per_s": round(ntot / max(t_score, 1e-9))}), flush=True)


if __name__ == "__main__":
    main()
