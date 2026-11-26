#!/usr/bin/env python3
"""Stage 0 zero-delta check (pod): prompt log-probs of a fixed token sequence under the plain engine and under the
LoRA path with an all-zero adapter (Z8: B = 0). One engine per process; run twice, then compare.

  zero_check.py run  --model D --tokenizer D --problems P --out O.json [--lora DIR --lora_rank 8]
  zero_check.py diff A.json B.json
"""
import argparse
import json
import os
import sys

TEXT = ("Here is a careful answer. First, I restate the request in my own words, then I list each constraint and "
        "check it before writing. The final text follows the requested format exactly, with no extra commentary. ") * 6
PIDS = ["ifbench_0", "ifbench_19", "ifeval_2350", "ifbench_170"]


def run(a):
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "olmo_ifladder"))
    from sample import prompt_ids  # noqa: E402  (the sampler's olmo_thinker template, pad tokens stripped)
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    tok = AutoTokenizer.from_pretrained(a.tokenizer)
    probs = {json.loads(l)["pid"]: json.loads(l) for l in open(a.problems)}
    seqs = []
    for pid in PIDS:
        ids = prompt_ids(tok, probs[pid]["prompt"])
        seqs.append(list(ids) + tok.encode(TEXT, add_special_tokens=False))
    kw = {}
    lreq = None
    if a.lora:
        from vllm.lora.request import LoRARequest
        kw = dict(enable_lora=True, max_lora_rank=a.lora_rank, max_loras=1)
        lreq = LoRARequest("z", 1, os.path.abspath(a.lora))
    llm = LLM(model=a.model, tokenizer=a.tokenizer, dtype="bfloat16", generation_config="vllm", max_model_len=4096,
              gpu_memory_utilization=0.9, enable_prefix_caching=False, seed=1, **kw)
    sp = SamplingParams(max_tokens=1, temperature=0.0, prompt_logprobs=0)
    def lps(batch):
        outs = llm.generate([{"prompt_token_ids": s} for s in batch], sp, lora_request=lreq)
        return [[None] + [float(d[t].logprob) for t, d in zip(s[1:], o.prompt_logprobs[1:])] for s, o in zip(batch, outs)]
    res = lps(seqs)
    single = [lps([s])[0] for s in seqs]  # same engine, one sequence per batch: the batch-composition noise floor
    json.dump({"model": a.model, "lora": a.lora, "seqs": seqs, "logprobs": res, "logprobs_single": single},
              open(a.out, "w"))
    print("ZERO_CHECK_RUN_DONE", a.out, len(res), flush=True)


def diff(a):
    A, B = json.load(open(a.a)), json.load(open(a.b))
    if a.single:  # A's batched vs A's one-sequence-per-batch log-probs (same engine)
        B = {"logprobs": A["logprobs_single"]}
    ds = sorted(abs(u - v) for x, y in zip(A["logprobs"], B["logprobs"]) for u, v in zip(x[1:], y[1:]))
    n = len(ds)
    print(json.dumps({"tokens": n, "max_abs_logprob_diff": ds[-1], "identical": sum(1 for d in ds if d == 0),
                      "mean_abs": sum(ds) / n, "median_abs": ds[n // 2], "p99_abs": ds[int(0.99 * (n - 1))],
                      "frac_gt_0.01": sum(1 for d in ds if d > 0.01) / n}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "diff"])
    ap.add_argument("a", nargs="?")
    ap.add_argument("b", nargs="?")
    ap.add_argument("--model")
    ap.add_argument("--tokenizer")
    ap.add_argument("--problems")
    ap.add_argument("--out")
    ap.add_argument("--lora")
    ap.add_argument("--lora_rank", type=int, default=8)
    ap.add_argument("--single", action="store_true", help="diff: A batched vs A single-sequence")
    a = ap.parse_args()
    run(a) if a.cmd == "run" else diff(a)


if __name__ == "__main__":
    main()
