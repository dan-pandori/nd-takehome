#!/usr/bin/env python3
"""Fresh budget forcing F(N) for s2300 (run olmo-transplant; pre-registration preregistration/olmo-transplant.md).

Phase 1: per (pid, N), one request of --n samples from the templated prompt (olmo_iffu/sample.py's prompt_ids) with
max_tokens = N: the thinking, capped at N tokens. Phase 2: for every phase-1 sample, the thinking prefix is
  - natural end: the sample's ids through the token that completes `</think>` (tok.think_end), if `</think>` occurs;
  - forced: otherwise its ids (EOS dropped) + `\\n` (198, if the last token does not end in a newline) + `</` `think`
    `>\\n\\n` (524, 27963, 1363) -- the same closing as the B cuts;
and one answer is sampled after it (budget 32,768 - prefix length). Same template and decoding as sample_prefix.py.
Rows: rid (pid|F<N>), pid, cond "F", cut N, i, natural (bool), think_n_tok, prefix_len, input_sha256, think_text, think_ids, then the
answer as n_tok, finish, text, ids. Phase-1 answer tokens after a natural `</think>` are discarded (the answer is
re-drawn in phase 2 from the same conditional distribution).
Usage: fresh_bf.py --model <dir> --tokenizer <dir> --name s2300 --rev main --pids a,b --budgets 2048,4096,8192 --n 16
                   --seed 8103 --job J --out <jsonl.gz> --meta <json>   (one engine seed covers both phases)
"""
import argparse
import gzip
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sample_prefix import RESPONSE_CAP, TEMPERATURE, TOP_P, b64ids, kv_info, make_engine, prompt_ids, sha_ids  # noqa
from tok import Tok, think_end  # noqa: E402

CLOSE = [524, 27963, 1363]
NL = 198


def run(eng, items, sp_of):
    """items: list of (key, input_ids); returns {key: RequestOutput}."""
    out = {}
    for key, x in items:
        eng.add_request(key, {"prompt_token_ids": x}, sp_of(key, x))
    while eng.has_unfinished_requests():
        for o in eng.step():
            if o.finished:
                out[o.request_id] = o
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tokenizer", default=None)
    ap.add_argument("--name", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--problems", default="olmo_ifomega/problems.jsonl")
    ap.add_argument("--pids", required=True)
    ap.add_argument("--budgets", default="2048,4096,8192")
    ap.add_argument("--n", type=int, default=16)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--job", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--meta", default=None)
    ap.add_argument("--tp", type=int, default=1)
    ap.add_argument("--gpu_mem", type=float, default=0.92)
    ap.add_argument("--max_num_seqs", type=int, default=512)
    args = ap.parse_args()

    from transformers import AutoTokenizer
    import vllm
    from vllm import SamplingParams
    from vllm.sampling_params import RequestOutputKind

    probs = {json.loads(l)["pid"]: json.loads(l) for l in open(args.problems)}
    tok = AutoTokenizer.from_pretrained(args.tokenizer or args.model)
    btok = Tok(os.path.join(args.tokenizer or args.model, "tokenizer.json"))
    pids = args.pids.split(",")
    budgets = [int(b) for b in args.budgets.split(",")]
    pp = {p: prompt_ids(tok, probs[p]["prompt"]) for p in pids}
    t0 = time.time()
    llm = make_engine(args, max(len(v) for v in pp.values()) + RESPONSE_CAP + 8)
    eng = llm.llm_engine
    t_load = time.time() - t0
    t1 = time.time()
    fin = RequestOutputKind.FINAL_ONLY
    ph1 = run(eng, [(f"{p}|{N}", pp[p]) for N in budgets for p in pids],
              lambda k, x: SamplingParams(n=args.n, temperature=TEMPERATURE, top_p=TOP_P,
                                          max_tokens=int(k.split("|")[1]), detokenize=False, output_kind=fin))
    t_ph1 = time.time() - t1
    items, info = [], {}
    for key, o in ph1.items():
        p, N = key.split("|")
        for comp in o.outputs:
            ids = [t for t in comp.token_ids if t != 100257]
            te = think_end(btok, ids)
            if te:
                pref, nat = ids[:te[0]], True
            else:
                pref = ids + ([] if btok.piece[ids[-1]].endswith(b"\n") else [NL]) + CLOSE
                nat = False
            k2 = f"{p}|{N}|{comp.index}"
            items.append((k2, pp[p] + pref))
            info[k2] = (p, int(N), comp.index, nat, list(comp.token_ids), pref, comp.finish_reason)
    t2 = time.time()
    ph2 = run(eng, items, lambda k, x: SamplingParams(
        n=1, temperature=TEMPERATURE, top_p=TOP_P, max_tokens=RESPONSE_CAP - (len(x) - len(pp[k.split("|")[0]])),
        detokenize=False, output_kind=fin))
    t_ph2 = time.time() - t2
    n_tok1 = n_tok2 = 0
    with gzip.open(args.out, "wt") as f:
        for k2, (p, N, i, nat, tids1, pref, fr1) in sorted(info.items()):
            comp = ph2[k2].outputs[0]
            tids = list(comp.token_ids)
            x = pp[p] + pref
            rec = {"rid": f"{p}|F{N}", "pid": p, "cond": "F", "writer": args.name, "cut": N, "i": i, "natural": nat,
                   "think_n_tok": len(tids1), "think_finish": fr1, "prefix_len": len(pref), "prompt_len": len(pp[p]),
                   "budget": RESPONSE_CAP - len(pref), "input_sha256": sha_ids(x), "job": args.job,
                   "think_text": tok.decode(tids1, skip_special_tokens=True), "think_ids": b64ids(tids1),
                   "prefix_ids": b64ids(pref), "n_tok": len(tids), "finish": comp.finish_reason,
                   "stop_reason": comp.stop_reason, "text": tok.decode(tids, skip_special_tokens=True),
                   "ids": b64ids(tids)}
            f.write(json.dumps(rec) + "\n")
            n_tok1 += len(tids1)
            n_tok2 += len(tids)
    import torch
    meta = {"job": args.job, "name": args.name, "rev": args.rev, "model_dir": args.model, "seed": args.seed,
            "pids": pids, "budgets": budgets, "n": args.n, "samples": len(info), "think_gen_tokens": n_tok1,
            "answer_gen_tokens": n_tok2, "natural_end": sum(v[3] for v in info.values()),
            "t_load_s": round(t_load, 1), "t_phase1_s": round(t_ph1, 1), "t_phase2_s": round(t_ph2, 1),
            "kv_cache": kv_info(eng), "tp": args.tp, "vllm": vllm.__version__, "torch": torch.__version__,
            "gpus": [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())],
            "prompt_ids": {p: b64ids(v) for p, v in pp.items()},
            "utc_end": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    print(json.dumps({k: v for k, v in meta.items() if k != "prompt_ids"}), flush=True)
    if args.meta:
        with open(args.meta, "a") as g:
            g.write(json.dumps(meta) + "\n")


if __name__ == "__main__":
    sys.exit(main())
