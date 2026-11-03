#!/usr/bin/env python3
"""Sample completions from one Olmo checkpoint with vLLM at Olmo 3.1 RL-Zero-Math's RL rollout settings.

Settings (open-instruct scripts/train/olmo3/7b_rlzero_math.sh, Olmo 3.1 recipe, PR #1261 at bb58c66):
  chat template olmo_thinker_rlzero (applied with add_generation_prompt=True, no BOS, pad ids removed, as
  open-instruct's rlvr tokenization does); temperature 1.0; top_p 1.0 (vllm_top_p default); max_tokens 16384
  (--response_length); no stop strings (stop at EOS only); bf16 weights and KV cache.

Requests are (problem, chunk) pairs of `--chunk` samples each; finished requests are appended to a gzip JSONL as they
complete, so a killed job resumes where it stopped. Output rows: pid, model, rev, job, chunk, i, n_tok, finish, text
(decoded with skip_special_tokens=True, the text the RL reward saw) and ids (base64 int32 response token ids).

Usage: sample.py --model <dir> --name <label> --rev <revision> --problems <jsonl> [--pids a,b|@file] --n 64
                 --chunk 16 --seed S --out <samples.jsonl.gz> [--meta <json>]
"""
import argparse
import base64
import gzip
import hashlib
import json
import os
import sys
import time

import numpy as np

TEMPLATE = (
    "Solve the following problem step by step. "
    "The last line of your response should be the answer to the problem in form Answer: $Answer (without quotes) where $Answer is the answer to the problem."
    "\n\n"
    "{% for message in messages %}"
    "{{ '\n\n' if not loop.first else '' }}"
    "{{ message['content'] + '\n' }}"
    "{% if loop.last and add_generation_prompt %}"
    "{{ '\nRemember to put your answer on its own line after \"Answer:\"' }}"
    "{% endif %}"
    "{% endfor %}"
)
MAX_TOKENS = 16384
TEMPERATURE = 1.0
TOP_P = 1.0


def prompt_ids(tok, problem):
    ids = tok.apply_chat_template([{"role": "user", "content": problem}], add_generation_prompt=True,
                                  tokenize=True, return_dict=False, chat_template=TEMPLATE)
    if tok.pad_token_id is not None:
        ids = [x for x in ids if x != tok.pad_token_id]
    return ids


def load_problems(path):
    return {r["pid"]: r for r in (json.loads(ln) for ln in open(path))}


def done_keys(out):
    keys = set()
    if os.path.exists(out):
        try:
            with gzip.open(out, "rt") as f:
                for ln in f:
                    try:
                        r = json.loads(ln)
                    except json.JSONDecodeError:
                        break  # truncated tail of a killed job
                    keys.add((r["pid"], r["chunk"]))
        except (EOFError, OSError):
            pass
    return keys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tokenizer", default=None)
    ap.add_argument("--name", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--problems", required=True)
    ap.add_argument("--pids", default=None)
    ap.add_argument("--n", type=int, required=True, help="samples per problem (or per-pid counts via --pids pid:n)")
    ap.add_argument("--chunk", type=int, default=16)
    ap.add_argument("--chunk0", type=int, default=0, help="first chunk index (extensions continue numbering)")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--job", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--meta", default=None)
    ap.add_argument("--gpu_mem", type=float, default=0.92)
    ap.add_argument("--max_num_seqs", type=int, default=512)
    ap.add_argument("--max_tokens", type=int, default=MAX_TOKENS)
    ap.add_argument("--order", default="hard_first", choices=["hard_first", "given"])
    ap.add_argument("--seq_stop", action="store_true",
                    help="extension mode: one chunk in flight per problem; stop a problem at its first chunk with a "
                         "sample the RL verifier accepts, else continue to its --pids budget")
    ap.add_argument("--spec_ngram", type=int, default=0,
                    help="n-gram prompt-lookup speculative decoding with this many draft tokens (0 = off)")
    args = ap.parse_args()

    from transformers import AutoTokenizer
    import vllm
    from vllm import LLM, SamplingParams
    from vllm.sampling_params import RequestOutputKind

    probs = load_problems(args.problems)
    want = {}
    if args.pids:
        spec = open(args.pids[1:]).read().split() if args.pids.startswith("@") else args.pids.split(",")
        for s in spec:
            pid, _, n = s.partition(":")
            want[pid] = int(n) if n else args.n
    else:
        want = {pid: args.n for pid in probs}
    tok = AutoTokenizer.from_pretrained(args.tokenizer or args.model)
    done = done_keys(args.out)
    reqs = []
    for pid, n in want.items():
        ids = prompt_ids(tok, probs[pid]["problem"])
        nch = (n + args.chunk - 1) // args.chunk
        for c in range(args.chunk0, args.chunk0 + nch):
            if (pid, c) in done:
                continue
            m = min(args.chunk, n - (c - args.chunk0) * args.chunk)
            reqs.append((pid, c, m, ids))
    if args.order == "hard_first":
        # AIME problems later in a paper run longer; starting them first shortens the end-of-job tail where only a
        # few long sequences are left running. Sampling is unaffected (requests are independent).
        reqs.sort(key=lambda r: (-((int(r[0].rsplit("_", 1)[1]) - 1) % 15), r[0], r[1]))
    print(f"{len(reqs)} requests to run ({len(done)} chunks already done)", flush=True)
    if not reqs:
        return

    t0 = time.time()
    llm = LLM(model=args.model, tokenizer=args.tokenizer or args.model, dtype="bfloat16",
              max_model_len=max(len(r[3]) for r in reqs) + args.max_tokens + 8, gpu_memory_utilization=args.gpu_mem,
              enable_prefix_caching=True, seed=args.seed, max_num_seqs=args.max_num_seqs, disable_log_stats=False,
              **({"speculative_config": {"method": "ngram", "num_speculative_tokens": args.spec_ngram,
                                         "prompt_lookup_max": 4, "prompt_lookup_min": 2}} if args.spec_ngram else {}))
    t_load = time.time() - t0
    eng = llm.llm_engine

    def submit(req):
        pid, c, m, ids = req
        sp = SamplingParams(n=m, temperature=TEMPERATURE, top_p=TOP_P, max_tokens=args.max_tokens,
                            detokenize=False, output_kind=RequestOutputKind.FINAL_ONLY)
        eng.add_request(f"{pid}|{c}", {"prompt_token_ids": ids}, sp)

    pending = {}
    if args.seq_stop:
        from grade import grade_rl
        for r in reqs:
            pending.setdefault(r[0], []).append(r)
        for pid in pending:
            pending[pid].sort(key=lambda r: r[1])
        # a problem already solved in an earlier extension chunk of this job (resume) is not continued
        if os.path.exists(args.out):
            with gzip.open(args.out, "rt") as f0:
                for ln in f0:
                    try:
                        r0 = json.loads(ln)
                    except json.JSONDecodeError:
                        break
                    if r0["pid"] in pending and grade_rl(r0["text"], probs[r0["pid"]]["answer"]):
                        pending[r0["pid"]] = []
        for pid in list(pending):
            if pending[pid]:
                submit(pending[pid].pop(0))
    else:
        for req in reqs:
            submit(req)
    t1 = time.time()
    n_tok = n_samp = n_len = 0
    last = t1
    with gzip.open(args.out, "at") as f:
        while eng.has_unfinished_requests():
            for o in eng.step():
                if not o.finished:
                    continue
                pid, c = o.request_id.split("|")
                c = int(c)
                for comp in o.outputs:
                    tids = list(comp.token_ids)
                    rec = {"pid": pid, "model": args.name, "rev": args.rev, "job": args.job, "chunk": c,
                           "i": comp.index, "n_tok": len(tids), "finish": comp.finish_reason,
                           "text": tok.decode(tids, skip_special_tokens=True),
                           "ids": base64.b64encode(np.asarray(tids, dtype=np.int32).tobytes()).decode()}
                    f.write(json.dumps(rec) + "\n")
                    n_tok += len(tids)
                    n_samp += 1
                    n_len += comp.finish_reason == "length"
                    if args.seq_stop and grade_rl(rec["text"], probs[pid]["answer"]):
                        pending[pid] = []  # first correct chunk: stop this problem
                f.flush()
                if args.seq_stop and pending.get(pid):
                    submit(pending[pid].pop(0))
            now = time.time()
            if now - last > 60:
                print(f"[{time.strftime('%H:%M:%S')}] {now - t1:.0f}s samples={n_samp} gen_tok={n_tok} "
                      f"tok/s={n_tok / (now - t1):.0f} length_cut={n_len}", flush=True)
                last = now
    t_gen = time.time() - t1
    import torch
    meta = {"job": args.job, "name": args.name, "rev": args.rev, "model_dir": args.model, "seed": args.seed,
            "n_requests": len(reqs), "samples": n_samp, "gen_tokens": n_tok, "length_cut": n_len,
            "t_load_s": round(t_load, 1), "t_gen_s": round(t_gen, 1), "tok_per_s": round(n_tok / max(t_gen, 1e-9), 1),
            "max_tokens": args.max_tokens, "temperature": TEMPERATURE, "top_p": TOP_P, "spec_ngram": args.spec_ngram,
            "problems": args.problems,
            "template_sha256": hashlib.sha256(TEMPLATE.encode()).hexdigest(),
            "vllm": vllm.__version__, "torch": torch.__version__, "gpu": torch.cuda.get_device_name(0),
            "max_mem_alloc_gb": round(torch.cuda.max_memory_allocated() / 2**30, 2),
            "utc_end": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    print(json.dumps(meta), flush=True)
    if args.meta:
        with open(args.meta, "a") as g:
            g.write(json.dumps(meta) + "\n")


if __name__ == "__main__":
    sys.exit(main())
