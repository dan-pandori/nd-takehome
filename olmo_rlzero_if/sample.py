#!/usr/bin/env python3
"""Sample completions from one Olmo 3 7B checkpoint with vLLM at Olmo 3 7B RL-Zero-IF's RL rollout settings.

Run olmo-rlzero-if: olmo_ifomega/sample.py (run olmo-ifomega) with the RL-Zero-IF recipe in place of the Think one.
Settings = the recorded RL-Zero-IF run (open-instruct scripts/train/olmo3/README.md "RL Zero chat templates", #1929 at
e25a27b8; launch-script snapshot scripts/train/olmo3/7b_rlzero_instruction_following.sh at 7e780f2fea):
  chat template olmo_thinker at d928a7c (open_instruct/dataset_transformation.py CHAT_TEMPLATES["olmo_thinker"], 1652
  bytes, sha256 6d549883...; byte-identical to the chat_template.jinja shipped with allenai/Olmo-3-7B-RL-Zero-IF),
  applied with add_generation_prompt=True, no BOS, pad ids removed, the user turn = the prompt verbatim, no system
  turn given (so the template's default system turn is used); temperature 1.0; top_p 1.0 (vllm_top_p default);
  max_tokens 16384 (--response_length); stop strings ["</answer>"] with include_stop_str_in_output=True and
  skip_special_tokens=False (grpo_fast.create_generation_configs at d928a7c); EOS <|endoftext|> (100257); bf16
  weights and KV cache. generation_config="vllm": the checkpoint's generation_config.json supplies no defaults (it
  holds none besides the EOS id, which equals the tokenizer's). Every model is run with ONE tokenizer, the one shipped
  with the RL-Zero-IF checkpoints (--tokenizer): in it <think>, </think>, <answer>, </answer>, <functions>, ... are
  single added tokens (ids 100268-100275 that the base repository's tokenizer names <|extra_id_k|>), so the prompt ids
  are the ones RL itself fed the base at step 0.

Requests are (problem, chunk) pairs of `--chunk` samples each; finished requests are appended to a gzip JSONL as they
complete, so a killed job resumes where it stopped. Output rows: pid, model, rev, job, chunk, i, n_tok, finish,
stop_reason, text (decoded with skip_special_tokens=True: the text RL's reward saw) and ids (base64 int32 response
token ids).

Sequential mode (--stop_after K): chunks of a problem run in index order with at most --inflight in flight; after
each completed chunk the job counts successes (olmo_rlzero_if/grade.success: official strict on RL's answer
extraction) over the completed prefix of chunks (index order; plus --prior counts) and submits no further chunk for
that problem once the count is >= K. Chunks already in flight finish and are kept (reported as overshoot by the
analysis). --stop_file: pids listed there get no further chunks (a budget stop that keeps the job and its in-flight
chunks). --spec_ngram N: n-gram prompt-lookup speculative decoding (olmo-rlzero-pilot's configuration).

Usage: sample.py --model <dir> --tokenizer <dir> --name <label> --rev <revision> --problems <jsonl>
                 [--pids a,b|a:n,b:n|@file] --n 8 --chunk 8 --seed S --job J --out <samples.jsonl.gz> [--meta <json>]
"""
import argparse
import base64
import gzip
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

# open_instruct/dataset_transformation.py CHAT_TEMPLATES["olmo_thinker"] at d928a7cd29, verbatim
TEMPLATE = "{% set has_system = messages|selectattr('role', 'equalto', 'system')|list|length > 0 %}{% if not has_system %}{{ '<|im_start|>system\nYou are OLMo, a helpful function-calling AI assistant built by Ai2. Your date cutoff is November 2024, and your model weights are available at https://huggingface.co/allenai. You do not currently have access to any functions. <functions></functions><|im_end|>\n' }}{% endif %}{% for message in messages %}{% if message['role'] == 'system' %}{{ '<|im_start|>system\n' + message['content'] }}{% if message.get('functions', none) is not none %}{{ ' <functions>' + message['functions'] + '</functions><|im_end|>\n' }}{% else %}{{ ' You do not currently have access to any functions. <functions></functions><|im_end|>\n' }}{% endif %}{% elif message['role'] == 'user' %}{% if message.get('functions', none) is not none %}{{ '<|im_start|>user\n' + message['content'] + '\n' + '<functions>' + message['functions'] + '</functions><|im_end|>\n' }}{% else %}{{ '<|im_start|>user\n' + message['content'] + '<|im_end|>\n' }}{% endif %}{% elif message['role'] == 'assistant' %}{{ '<|im_start|>assistant\n' }}{% if message.get('content', none) is not none %}{{ message['content'] }}{% endif %}{% if message.get('function_calls', none) is not none %}{{ '<function_calls>' + message['function_calls'] + '</function_calls>' }}{% endif %}{% if not loop.last %}{{ '<|im_end|>' + '\n' }}{% else %}{{ eos_token }}{% endif %}{% elif message['role'] == 'environment' %}{{ '<|im_start|>environment\n' + message['content'] + '<|im_end|>\n' }}{% endif %}{% if loop.last and add_generation_prompt %}{{ '<|im_start|>assistant\n<think>' }}{% endif %}{% endfor %}"
TEMPLATE_SHA256 = "6d549883b5ed12879e191845c256a30c7dfd4eced0a4f160060a3ea0199d9e3a"
MAX_TOKENS = 16384
STOP_STRINGS = ["</answer>"]
TURN_IDS = (100257, 100264, 100265)  # <|endoftext|>, <|im_start|>, <|im_end|> (same ids in both tokenizers)
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


TASK_ORDER = {"ifbench": 0, "ifeval": 1, "rlzif": 2}


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
    ap.add_argument("--spec_ngram", type=int, default=0,
                    help="n-gram prompt-lookup speculative decoding with this many draft tokens (0 = off)")
    ap.add_argument("--stop_after", type=int, default=0,
                    help="sequential mode: stop a problem once its success count reaches this (0 = off)")
    ap.add_argument("--inflight", type=int, default=1, help="sequential mode: chunks in flight per problem")
    ap.add_argument("--prior", default=None, help="sequential mode: pid:count already credited before this job")
    ap.add_argument("--stop_file", default=None,
                    help="sequential mode: pids listed in this file (re-read at every chunk completion) get no further "
                         "chunks; chunks in flight finish (budget stops without killing the job)")
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
    if old:
        # always rewrite on resume: a killed job leaves a truncated gzip member, and appending a new member after it
        # makes the file unreadable past the junction (olmo-ifomega 2026-11-05; repaired by repair_gz.py)
        old = [r for r in old if (r["pid"], r["chunk"]) not in partial]
        with gzip.open(args.out, "wt") as g0:
            for r in old:
                g0.write(json.dumps(r) + "\n")
        print(f"rewrote {len(old)} rows, dropped {len(partial)} partial chunks before resuming", flush=True)
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
        # task order, then pid, then chunk (sampling unaffected)
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

    assert hashlib.sha256(TEMPLATE.encode()).hexdigest() == TEMPLATE_SHA256
    t0 = time.time()
    llm = LLM(model=args.model, tokenizer=args.tokenizer or args.model, dtype="bfloat16",
              tensor_parallel_size=args.tp, generation_config="vllm",
              max_model_len=max(len(r[3]) for r in reqs) + args.max_tokens + 8, gpu_memory_utilization=args.gpu_mem,
              enable_prefix_caching=True, seed=args.seed, max_num_seqs=args.max_num_seqs, disable_log_stats=False,
              **({"speculative_config": {"method": "ngram", "num_speculative_tokens": args.spec_ngram,
                                         "prompt_lookup_max": 4, "prompt_lookup_min": 2}} if args.spec_ngram else {}))
    t_load = time.time() - t0
    eng = llm.llm_engine
    inflight = {}

    def submit(req):
        pid, c, m, ids = req
        # as RL's rollouts: stop at "</answer>" (kept in the output) or EOS; stop strings need detokenize=True
        sp = SamplingParams(n=m, temperature=TEMPERATURE, top_p=TOP_P, max_tokens=args.max_tokens,
                            stop=STOP_STRINGS, include_stop_str_in_output=True, skip_special_tokens=False,
                            detokenize=True, output_kind=RequestOutputKind.FINAL_ONLY)
        eng.add_request(f"{pid}|{c}", {"prompt_token_ids": ids}, sp)
        inflight[pid] = inflight.get(pid, 0) + 1

    def stopped(pid):
        if not args.stop_file:
            return False
        try:
            return pid in Path(args.stop_file).read_text().split()
        except OSError:
            return False

    def top_up(pid):
        while (pending.get(pid) and inflight.get(pid, 0) < args.inflight and credited(pid) < args.stop_after
               and not stopped(pid)):
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
                    text = tok.decode(tids, skip_special_tokens=True)
                    # first-turn cut (grade `t1`): characters of `text` before the first turn-ending special token
                    k = next((j for j, x in enumerate(tids) if x in TURN_IDS), None)
                    t1 = None
                    if k is not None:
                        pre = tok.decode(tids[:k], skip_special_tokens=True)
                        t1 = len(pre) if text.startswith(pre) else -1
                    rec = {"pid": pid, "model": args.name, "rev": args.rev, "job": args.job, "chunk": c,
                           "i": comp.index, "n_tok": len(tids), "finish": comp.finish_reason,
                           "stop_reason": comp.stop_reason, "t1_chars": t1,
                           "n_im_start": sum(x == 100264 for x in tids), "n_im_end": sum(x == 100265 for x in tids),
                           "text": text,
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
            "stop_strings": STOP_STRINGS, "spec_ngram": args.spec_ngram, "tokenizer": args.tokenizer,
            "stop_after": args.stop_after, "inflight": args.inflight, "chunk": args.chunk, "chunk0": args.chunk0,
            "problems": args.problems, "pids": args.pids, "prior": args.prior, "stop_file": args.stop_file,
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
