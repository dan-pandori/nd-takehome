#!/usr/bin/env python3
"""Sample answers after a supplied thinking prefix (run olmo-transplant; pre-registration
preregistration/olmo-transplant.md).

Built on olmo_iffu/sample.py: the same chat template and prompt ids (TEMPLATE and prompt_ids are imported from it),
T 1.0, top-p 1.0, no stop strings (EOS only), bf16, vLLM, prefix caching, generation_config="vllm". What changes:
  - each request is (pid, prefix ids): the model input is prompt_ids(user turn) + prefix, where the prefix is the
    assistant-side token ids after the template's `<think>` (a stored trace through `</think>`, a cut trace plus the
    forced closing, or the closing alone); the requests file is built on the VPS by build_requests.py;
  - the answer budget is 32,768 - len(prefix) (RL's response cap on thinking + answer);
  - requests that share a trace (`group`) run after a one-token warm-up on the group's longest prefix, so the n
    sub-requests of every request in the group read the prefill from the prefix cache instead of each computing it;
    at most --groups groups are in flight. Warm-up outputs are discarded (they do not change any sampled answer's
    distribution);
  - rows carry the request's condition fields, prompt_len, prefix_len, budget and the sha256 of the exact input ids;
    the meta records every pid's prompt ids (base64) and a decoded dump of the first requests' boundaries.
Output rows (gzip JSONL, appended as requests finish; a killed job resumes, dropping partially written requests):
  rid, pid, cond, writer, trace, cut, i, n_tok, finish, stop_reason, prompt_len, prefix_len, budget, input_sha256,
  text (generated tokens decoded with skip_special_tokens=True), ids (base64 int32 generated ids).
Usage: sample_prefix.py --model <dir> --tokenizer <dir> --name <label> --rev <rev> --requests <jsonl.gz>
                        --problems olmo_ifomega/problems.jsonl --seed S --job J --out <jsonl.gz> --meta <json>
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

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "olmo_iffu"))
from sample import TEMPLATE, prompt_ids, read_rows  # noqa: E402  (olmo_iffu/sample.py, unchanged)

RESPONSE_CAP = 32768
TEMPERATURE = 1.0
TOP_P = 1.0


def b64ids(ids):
    return base64.b64encode(np.asarray(ids, dtype=np.int32).tobytes()).decode()


def unb64(s):
    return np.frombuffer(base64.b64decode(s), dtype=np.int32).tolist()


def sha_ids(ids):
    return hashlib.sha256(np.asarray(ids, dtype=np.int32).tobytes()).hexdigest()


def load_requests(path):
    op = gzip.open if path.endswith(".gz") else open
    return [json.loads(ln) for ln in op(path, "rt")]


def make_engine(args, max_len):
    from vllm import LLM
    return LLM(model=args.model, tokenizer=args.tokenizer or args.model, dtype="bfloat16",
               tensor_parallel_size=args.tp, generation_config="vllm", max_model_len=max_len,
               gpu_memory_utilization=args.gpu_mem, enable_prefix_caching=True, seed=args.seed,
               max_num_seqs=args.max_num_seqs, disable_log_stats=False)


def kv_info(eng):
    try:
        cc = eng.vllm_config.cache_config
        return {"num_gpu_blocks": cc.num_gpu_blocks, "block_size": cc.block_size}
    except Exception as e:  # recorded, never fatal
        return {"error": repr(e)[:200]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tokenizer", default=None)
    ap.add_argument("--name", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--requests", required=True)
    ap.add_argument("--problems", default="olmo_ifomega/problems.jsonl")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--job", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--meta", default=None)
    ap.add_argument("--tp", type=int, default=1)
    ap.add_argument("--gpu_mem", type=float, default=0.92)
    ap.add_argument("--max_num_seqs", type=int, default=512)
    ap.add_argument("--groups", type=int, default=8, help="trace groups in flight")
    ap.add_argument("--limit_groups", type=int, default=0, help="run only the first K groups (0 = all)")
    ap.add_argument("--dump", type=int, default=3, help="boundary dumps per condition")
    args = ap.parse_args()

    from transformers import AutoTokenizer
    import vllm
    from vllm import SamplingParams
    from vllm.sampling_params import RequestOutputKind

    probs = {json.loads(l)["pid"]: json.loads(l) for l in open(args.problems)}
    tok = AutoTokenizer.from_pretrained(args.tokenizer or args.model)
    reqs = load_requests(args.requests)
    assert all(r["writer"] == args.name for r in reqs), "requests file is for another writer"
    old = read_rows(args.out)
    cnt = {}
    for r in old:
        cnt[r["rid"]] = cnt.get(r["rid"], 0) + 1
    want = {r["rid"]: r["n"] for r in reqs}
    partial = {k for k, v in cnt.items() if v != want.get(k)}
    if old:  # always rewrite on resume (a killed job leaves a truncated gzip member)
        old = [r for r in old if r["rid"] not in partial]
        with gzip.open(args.out, "wt") as g0:
            for r in old:
                g0.write(json.dumps(r) + "\n")
        print(f"rewrote {len(old)} rows, dropped {len(partial)} partial requests before resuming", flush=True)
    done = {r["rid"] for r in old}
    pids = sorted({r["pid"] for r in reqs})
    pids_ids = {p: prompt_ids(tok, probs[p]["prompt"]) for p in pids}
    groups = {}
    order = []
    for r in reqs:
        if r["group"] not in groups:
            groups[r["group"]] = []
            order.append(r["group"])
        groups[r["group"]].append(r)
    if args.limit_groups:
        order = order[: args.limit_groups]
    todo = [g for g in order if any(r["rid"] not in done for r in groups[g])]
    print(f"{len(reqs)} requests in {len(groups)} groups; {len(todo)} groups to run ({len(done)} requests done)",
          flush=True)
    if not todo:
        return
    max_len = max(len(v) for v in pids_ids.values()) + RESPONSE_CAP + 8

    t0 = time.time()
    llm = make_engine(args, max_len)
    t_load = time.time() - t0
    eng = llm.llm_engine
    kv = kv_info(eng)
    print(f"kv_cache {kv} max_model_len {eng.vllm_config.model_config.max_model_len}", flush=True)

    dumps = {}
    dump_txt = []
    left = {}  # group -> requests still running
    queue = list(todo)
    stats = {"samples": 0, "gen_tok": 0, "length_cut": 0, "input_tok": 0, "warm_tok": 0, "requests": 0}

    def inp(r):
        return pids_ids[r["pid"]] + unb64(r["prefix"])

    def submit_real(g):
        rs = [r for r in groups[g] if r["rid"] not in done]
        left[g] = len(rs)
        for r in rs:
            x = inp(r)
            sp = SamplingParams(n=r["n"], temperature=TEMPERATURE, top_p=TOP_P,
                                max_tokens=RESPONSE_CAP - len(unb64(r["prefix"])), detokenize=False,
                                output_kind=RequestOutputKind.FINAL_ONLY)
            eng.add_request("r|" + r["rid"], {"prompt_token_ids": x}, sp)
            c = r["cond"]
            if dumps.get(c, 0) < args.dump:
                dumps[c] = dumps.get(c, 0) + 1
                pl = len(pids_ids[r["pid"]])
                dump_txt.append(f"===== {r['rid']} cond={c} prompt_len={pl} prefix_len={len(x) - pl}\n"
                                f"--- prompt tail: {tok.decode(x[max(0, pl - 12):pl])!r}\n"
                                f"--- prefix head: {tok.decode(x[pl:pl + 24])!r}\n"
                                f"--- input tail: {tok.decode(x[-24:])!r}\n"
                                f"--- input tail ids: {x[-6:]}\n")
                if args.meta:  # written at once, so the boundary can be read before the job ends
                    with open(args.meta.replace(".json", "_boundary.txt"), "a") as g:
                        g.write(dump_txt[-1])
        if not rs:
            left.pop(g)

    def start(g):
        base = max(groups[g], key=lambda r: len(unb64(r["prefix"])))
        x = inp(base)
        if len(x) - len(pids_ids[base["pid"]]) < 512:
            submit_real(g)
            return
        sp = SamplingParams(n=1, temperature=TEMPERATURE, top_p=TOP_P, max_tokens=1, detokenize=False,
                            output_kind=RequestOutputKind.FINAL_ONLY)
        eng.add_request("w|" + g, {"prompt_token_ids": x}, sp)
        stats["warm_tok"] += len(x)
        left[g] = -1  # warming

    def fill():
        while queue and len(left) < args.groups:
            start(queue.pop(0))

    by_rid = {r["rid"]: r for r in reqs}
    fill()
    t1 = time.time()
    last = t1
    with gzip.open(args.out, "at") as f:
        while eng.has_unfinished_requests() or queue:
            if not eng.has_unfinished_requests():
                fill()
                continue
            for o in eng.step():
                if not o.finished:
                    continue
                kind, key = o.request_id.split("|", 1)
                if kind == "w":
                    submit_real(key)
                    continue
                r = by_rid[key]
                x = inp(r)
                pl = len(pids_ids[r["pid"]])
                sh = sha_ids(x)
                for comp in o.outputs:
                    tids = list(comp.token_ids)
                    rec = {"rid": r["rid"], "pid": r["pid"], "cond": r["cond"], "writer": args.name,
                           "trace": r["trace"], "cut": r["cut"], "i": comp.index, "n_tok": len(tids),
                           "finish": comp.finish_reason, "stop_reason": comp.stop_reason, "prompt_len": pl,
                           "prefix_len": len(x) - pl, "budget": RESPONSE_CAP - (len(x) - pl), "input_sha256": sh,
                           "job": args.job, "text": tok.decode(tids, skip_special_tokens=True), "ids": b64ids(tids)}
                    f.write(json.dumps(rec) + "\n")
                    stats["samples"] += 1
                    stats["gen_tok"] += len(tids)
                    stats["length_cut"] += comp.finish_reason == "length"
                f.flush()
                stats["input_tok"] += len(x)
                stats["requests"] += 1
                g = r["group"]
                left[g] -= 1
                if left[g] == 0:
                    left.pop(g)
                    fill()
            now = time.time()
            if now - last > 60:
                el = now - t1
                print(f"[{time.strftime('%H:%M:%S')}] {el:.0f}s requests={stats['requests']} samples={stats['samples']} "
                      f"gen_tok={stats['gen_tok']} gen_tok/s={stats['gen_tok'] / el:.0f} "
                      f"input_tok={stats['input_tok']} warm_tok={stats['warm_tok']} groups_left={len(queue)} "
                      f"length_cut={stats['length_cut']}", flush=True)
                last = now
    t_gen = time.time() - t1
    import torch
    meta = {"job": args.job, "name": args.name, "rev": args.rev, "model_dir": args.model, "seed": args.seed,
            "requests_file": args.requests, "n_groups_run": len(todo), **stats,
            "t_load_s": round(t_load, 1), "t_gen_s": round(t_gen, 1),
            "gen_tok_per_s": round(stats["gen_tok"] / max(t_gen, 1e-9), 1), "kv_cache": kv,
            "temperature": TEMPERATURE, "top_p": TOP_P, "response_cap": RESPONSE_CAP, "tp": args.tp,
            "groups_in_flight": args.groups, "max_num_seqs": args.max_num_seqs, "gpu_mem": args.gpu_mem,
            "template_sha256": hashlib.sha256(TEMPLATE.encode()).hexdigest(),
            "prompt_ids": {p: b64ids(v) for p, v in pids_ids.items()},
            "vllm": vllm.__version__, "torch": torch.__version__,
            "gpus": [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())],
            "max_mem_alloc_gb": round(torch.cuda.max_memory_allocated() / 2 ** 30, 2) if torch.cuda.is_available() else None,
            "utc_end": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    print(json.dumps({k: v for k, v in meta.items() if k != "prompt_ids"}), flush=True)
    if args.meta:
        with open(args.meta, "a") as g:
            g.write(json.dumps(meta) + "\n")


if __name__ == "__main__":
    sys.exit(main())
