#!/usr/bin/env python3
"""Sample completions from one Olmo 3 / 3.1 Think 32B checkpoint with vLLM at the Think RL rollout settings.

Run olmo-ifomega: olmo32/sample.py (run olmo-think32b) with three changes. The user turn is the problem's `prompt`
field verbatim (IF prompts as in IFBench / IFEval; OMEGA problems in RL's "no-boxed" form, see build_problems.py);
the sequential stopping rule counts grade.success() (IF: official strict; OMEGA: OMEGA exact match and RL's
MathVerifier); the default order runs the long tasks (OMEGA) first. Template, decoding and output format unchanged.

Settings (open-instruct scripts/train/olmo3/32b_think_rl.sh at 7e780f2fea, 2025-11-22):
  chat template olmo_thinker (dataset_transformation.py at 7e780f2fea; applied with add_generation_prompt=True, no
  BOS, the user turn is the bare problem, as Dolci-Think-RL's math prompts are); temperature 1.0; top_p 1.0
  (vllm_top_p default); max_tokens 32768 (--response_length); no stop strings (stop at EOS <|endoftext|> only);
  bf16 weights and KV cache. generation_config="vllm": the checkpoint's generation_config.json (T 0.6, top_p 0.95)
  supplies no defaults; its EOS id (100257) equals the tokenizer's.

Requests are (problem, chunk) pairs of `--chunk` samples each; finished requests are appended to a gzip JSONL as they
complete, so a killed job resumes where it stopped. Output rows: pid, model, rev, job, chunk, i, n_tok, finish, text
(decoded with skip_special_tokens=True, the text the RL reward saw) and ids (base64 int32 response token ids).

Sequential mode (--stop_after K): chunks of a problem run in index order with at most --inflight in flight; after
each completed chunk the job counts successes (olmo_ifomega/grade.success) over the completed
prefix of chunks (index order; plus --prior counts) and submits no further chunk for that problem once the count is
>= K. Chunks already in flight finish and are kept (reported as overshoot by the analysis).

Usage: sample.py --model <dir> --name <label> --rev <revision> --problems <jsonl> [--pids a,b|a:n,b:n|@file] --n 8
                 --chunk 8 --seed S --job J --out <samples.jsonl.gz> [--meta <json>] [--tp 4]
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

# open_instruct/dataset_transformation.py CHAT_TEMPLATES["olmo_thinker"] at 7e780f2fea, verbatim
TEMPLATE = (
    "{% set has_system = messages|selectattr('role', 'equalto', 'system')|list|length > 0 %}"
    "{% if not has_system %}"
    "{{ '<|im_start|>system\nYou are a helpful AI assistant.<|im_end|>\n' }}"
    "{% endif %}"
    "{% for message in messages %}"
    "{% if message['role'] == 'system' %}"
    "{{ '<|im_start|>system\n' + message['content'] }}"
    "{% if message.get('functions', none) is not none %}"
    "{{ ' <functions>' + message['functions'] + '</functions><|im_end|>\n' }}"
    "{% else %}"
    "{{ ' You do not currently have access to any functions. <functions></functions><|im_end|>\n' }}"
    "{% endif %}"
    "{% elif message['role'] == 'user' %}"
    "{% if message.get('functions', none) is not none %}"
    "{{ '<|im_start|>user\n' + message['content'] + '\n' + '<functions>' + message['functions'] + '</functions><|im_end|>\n' }}"
    "{% else %}"
    "{{ '<|im_start|>user\n' + message['content'] + '<|im_end|>\n' }}"
    "{% endif %}"
    "{% elif message['role'] == 'assistant' %}"
    "{{ '<|im_start|>assistant\n' }}"
    "{% if message.get('content', none) is not none %}"
    "{{ message['content'] }}"
    "{% endif %}"
    "{% if message.get('function_calls', none) is not none %}"
    "{{ '<function_calls>' + message['function_calls'] + '</function_calls>' }}"
    "{% endif %}"
    "{% if not loop.last %}"
    "{{ '<|im_end|>' + '\n' }}"
    "{% else %}"
    "{{ eos_token }}"
    "{% endif %}"
    "{% elif message['role'] == 'environment' %}"
    "{{ '<|im_start|>environment\n' + message['content'] + '<|im_end|>\n' }}"
    "{% endif %}"
    "{% if loop.last and add_generation_prompt %}"
    "{{ '<|im_start|>assistant\n<think>' }}"
    "{% endif %}"
    "{% endfor %}"
)
MAX_TOKENS = 32768
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


TASK_ORDER = {"omega_out": 0, "omega_in": 1, "rlif": 2, "ifbench": 3, "ifeval": 4}


def read_rows(out):
    rows = []
    if os.path.exists(out):
        try:
            with gzip.open(out, "rt") as f:
                for ln in f:
                    try:
                        rows.append(json.loads(ln))
                    except json.JSONDecodeError:
                        break  # truncated tail of a killed job
        except (EOFError, OSError):
            pass
    return rows


def parse_spec(spec, default):
    """'a,b' | 'a:n,b:n' | '@file' (whitespace-separated) -> {pid: n}."""
    toks = open(spec[1:]).read().split() if spec.startswith("@") else spec.split(",")
    out = {}
    for s in toks:
        pid, _, n = s.partition(":")
        out[pid] = int(n) if n else default
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tokenizer", default=None)
    ap.add_argument("--name", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--problems", required=True)
    ap.add_argument("--pids", default=None)
    ap.add_argument("--n", type=int, required=True, help="samples per problem (or per-pid counts via --pids pid:n)")
    ap.add_argument("--chunk", type=int, default=8)
    ap.add_argument("--chunk0", type=int, default=0, help="first chunk index (extensions continue numbering)")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--job", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--meta", default=None)
    ap.add_argument("--tp", type=int, default=1)
    ap.add_argument("--gpu_mem", type=float, default=0.92)
    ap.add_argument("--max_num_seqs", type=int, default=512)
    ap.add_argument("--max_tokens", type=int, default=MAX_TOKENS)
    ap.add_argument("--order", default="long_first", choices=["long_first", "given"])
    ap.add_argument("--stop_after", type=int, default=0,
                    help="sequential mode: stop a problem once its success count reaches this (0 = off)")
    ap.add_argument("--inflight", type=int, default=1, help="sequential mode: chunks in flight per problem")
    ap.add_argument("--prior", default=None, help="sequential mode: pid:count already credited before this job")
    args = ap.parse_args()

    from transformers import AutoTokenizer
    import vllm
    from vllm import LLM, SamplingParams
    from vllm.sampling_params import RequestOutputKind

    probs = load_problems(args.problems)
    want = parse_spec(args.pids, args.n) if args.pids else {pid: args.n for pid in probs}
    prior = parse_spec(args.prior, 0) if args.prior else {}
    tok = AutoTokenizer.from_pretrained(args.tokenizer or args.model)
    old = read_rows(args.out)
    # a killed job can leave a chunk with only part of its rows written: drop such chunks so they rerun whole
    size = {(pid, c): min(args.chunk, n - (c - args.chunk0) * args.chunk)
            for pid, n in want.items() for c in range(args.chunk0, args.chunk0 + (n + args.chunk - 1) // args.chunk)}
    cnt = {}
    for r in old:
        cnt[(r["pid"], r["chunk"])] = cnt.get((r["pid"], r["chunk"]), 0) + 1
    partial = {k for k, v in cnt.items() if k in size and v != size[k]}
    if partial:
        old = [r for r in old if (r["pid"], r["chunk"]) not in partial]
        with gzip.open(args.out, "wt") as g0:
            for r in old:
                g0.write(json.dumps(r) + "\n")
        print(f"dropped {len(partial)} partial chunks before resuming", flush=True)
    done = {(r["pid"], r["chunk"]) for r in old}
    reqs = []
    for pid, n in want.items():
        ids = prompt_ids(tok, probs[pid]["prompt"])
        nch = (n + args.chunk - 1) // args.chunk
        for c in range(args.chunk0, args.chunk0 + nch):
            if (pid, c) in done:
                continue
            m = min(args.chunk, n - (c - args.chunk0) * args.chunk)
            reqs.append((pid, c, m, ids))
    if args.order == "long_first":
        # OMEGA runs longest; starting it first shortens the end-of-job tail (sampling unaffected)
        reqs.sort(key=lambda r: (TASK_ORDER.get(probs[r[0]]["task"], 9), r[0], r[1]))
    print(f"{len(reqs)} requests to run ({len(done)} chunks already done)", flush=True)
    if not reqs:
        return

    seq = args.stop_after > 0
    if seq:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from grade import success
        # chunk -> list of success flags, for chunks of this job's pids done before a resume
        chunk_res = {}
        for r in old:
            if r["pid"] in want:
                p = probs[r["pid"]]
                chunk_res.setdefault((r["pid"], r["chunk"]), []).append(success(p["task"], r["text"], p))
        pending = {}
        for r in reqs:
            pending.setdefault(r[0], []).append(r)
        for pid in pending:
            pending[pid].sort(key=lambda r: r[1])

        def credited(pid):
            """Success count over the completed prefix of this job's chunks, in chunk order."""
            k = prior.get(pid, 0)
            for c in range(args.chunk0, args.chunk0 + (want[pid] + args.chunk - 1) // args.chunk):
                if (pid, c) not in chunk_res:
                    break
                k += sum(chunk_res[(pid, c)])
            return k

    t0 = time.time()
    llm = LLM(model=args.model, tokenizer=args.tokenizer or args.model, dtype="bfloat16",
              tensor_parallel_size=args.tp, generation_config="vllm",
              max_model_len=max(len(r[3]) for r in reqs) + args.max_tokens + 8, gpu_memory_utilization=args.gpu_mem,
              enable_prefix_caching=True, seed=args.seed, max_num_seqs=args.max_num_seqs, disable_log_stats=False)
    t_load = time.time() - t0
    eng = llm.llm_engine
    inflight = {}

    def submit(req):
        pid, c, m, ids = req
        sp = SamplingParams(n=m, temperature=TEMPERATURE, top_p=TOP_P, max_tokens=args.max_tokens,
                            detokenize=False, output_kind=RequestOutputKind.FINAL_ONLY)
        eng.add_request(f"{pid}|{c}", {"prompt_token_ids": ids}, sp)
        inflight[pid] = inflight.get(pid, 0) + 1

    def top_up(pid):
        while pending.get(pid) and inflight.get(pid, 0) < args.inflight and credited(pid) < args.stop_after:
            submit(pending[pid].pop(0))

    if seq:
        for pid in list(pending):
            top_up(pid)
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
                flags = []
                for comp in o.outputs:
                    tids = list(comp.token_ids)
                    rec = {"pid": pid, "model": args.name, "rev": args.rev, "job": args.job, "chunk": c,
                           "i": comp.index, "n_tok": len(tids), "finish": comp.finish_reason,
                           "stop_reason": comp.stop_reason,
                           "text": tok.decode(tids, skip_special_tokens=True),
                           "ids": base64.b64encode(np.asarray(tids, dtype=np.int32).tobytes()).decode()}
                    f.write(json.dumps(rec) + "\n")
                    n_tok += len(tids)
                    n_samp += 1
                    n_len += comp.finish_reason == "length"
                    if seq:
                        flags.append(success(probs[pid]["task"], rec["text"], probs[pid]))
                f.flush()
                inflight[pid] -= 1
                if seq:
                    chunk_res[(pid, c)] = flags
                    top_up(pid)
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
            "max_tokens": args.max_tokens, "temperature": TEMPERATURE, "top_p": TOP_P, "tp": args.tp,
            "stop_after": args.stop_after, "inflight": args.inflight, "chunk": args.chunk, "chunk0": args.chunk0,
            "problems": args.problems, "pids": args.pids, "prior": args.prior,
            "template_sha256": hashlib.sha256(TEMPLATE.encode()).hexdigest(),
            "vllm": vllm.__version__, "torch": torch.__version__,
            "gpus": [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())],
            "utc_end": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if seq:
        meta["credited_end"] = {pid: credited(pid) for pid in want}
    print(json.dumps(meta), flush=True)
    if args.meta:
        with open(args.meta, "a") as g:
            g.write(json.dumps(meta) + "\n")


if __name__ == "__main__":
    sys.exit(main())
