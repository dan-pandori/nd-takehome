"""Compute axis (pre-registered definitions, my own lengths) and per-job compute from the raw rows.

Axis (olmo_pilot/compute_axis.py's definitions, re-implemented): pretraining 6ND, N 7.3e9, D 6.08e12; RL per step
32 prompts x 8 samples x [L 2N over + (L + prompt) 6N + (L + prompt) 2N extra]; L linear between measured checkpoints.
  low  = L on RL training prompts (Stage 0's 24 Dolci prompts: base s0_base_a+b, s0_s0100, s0_s0500, s0_main),
         over 1, extra 0, no prompt tokens;
  high = L on the evaluation prompts (fixed phase, all 450), over 1 (pre-registered: no active sampling), extra 1,
         prompt tokens = my mean templated length of the 13,179 Dolci prompts (RL-Zero-IF tokenizer, olmo_thinker).
main at step 2,000 (bracket 1,900-2,100, from the executor's weight distances; not re-derivable on the VPS).
Per job: samples and generated tokens counted from the rows (not meta), meta t_load_s + t_gen_s, GPU.
Output: out/compute.txt, out/compute.json"""
import json
import os

import numpy as np
import pyarrow.parquet as pq
from tokenizers import Tokenizer

import rv_core as C

N, D = 7.3e9, 6.08e12
PRE = 6 * N * D
SYS = ("<|im_start|>system\nYou are OLMo, a helpful function-calling AI assistant built by Ai2. Your date cutoff is "
       "November 2024, and your model weights are available at https://huggingface.co/allenai. You do not currently "
       "have access to any functions. <functions></functions><|im_end|>\n")


def render(content):
    return SYS + "<|im_start|>user\n" + content + "<|im_end|>\n" + "<|im_start|>assistant\n<think>"


def cum(steps, lens, q, over, extra, ptok):
    grid = np.arange(0, max(q) + 1)
    L = np.interp(grid, steps, lens)
    per = 32 * 8 * (L * 2 * N * over + (L + ptok) * 6 * N + (L + ptok) * 2 * N * extra)
    c = np.concatenate([[0.0], np.cumsum(per[1:])])
    return {s: float(c[s]) for s in q}


def main():
    out, lines = {}, []
    rg = {}
    for fn in os.listdir(os.path.join(C.OUT, "regrade")):
        if fn.endswith(".jsonl"):
            rg[fn[:-6]] = [json.loads(x) for x in open(os.path.join(C.OUT, "regrade", fn))]
    tr = {0: [r["n_tok"] for j in ("s0_base_a", "s0_base_b") for r in rg[j] if r["task"] == "rlzif"],
          100: [r["n_tok"] for r in rg["s0_s0100"] if r["task"] == "rlzif"],
          500: [r["n_tok"] for r in rg["s0_s0500"] if r["task"] == "rlzif"],
          2000: [r["n_tok"] for r in rg["s0_main"] if r["task"] == "rlzif"]}
    ev = {0: [r["n_tok"] for j in ("F_base_ifb", "F_base_ife") for r in rg[j]],
          100: [r["n_tok"] for r in rg["F_s0100"]], 500: [r["n_tok"] for r in rg["F_s0500"]],
          2000: [r["n_tok"] for r in rg["F_main"]]}
    tok = Tokenizer.from_file(os.path.join(C.BIG, "hf", "allenai_Olmo-3-7B-RL-Zero-IF@main", "tokenizer.json"))
    dol = pq.read_table(os.path.join(C.BIG, "data", "dolci_rlzero_if.parquet"), columns=["prompt"]).to_pylist()
    # Dolci prompts start "user: "; RL's transform builds the chat from messages -- I strip the prefix
    pl = [len(tok.encode(render(r["prompt"][6:] if r["prompt"].startswith("user: ") else r["prompt"]),
                         add_special_tokens=False).ids) for r in dol]
    ptok = float(np.mean(pl))
    steps = sorted(tr)
    lt = [float(np.mean(tr[s])) for s in steps]
    le = [float(np.mean(ev[s])) for s in steps]
    lines.append(f"pretraining 6ND = {PRE:.4e}; mean templated Dolci prompt = {ptok:.1f} tokens (median "
                 f"{np.median(pl):.0f})")
    lines.append("step  n_train  L_train  n_eval  L_eval")
    for s, a, b in zip(steps, lt, le):
        lines.append(f"{s:5d} {len(tr[s]):7d} {a:8.1f} {len(ev[s]):7d} {b:7.1f}")
    q = [100, 500, 1900, 2000, 2100]
    lo = cum(steps + [2100], lt + [lt[-1]], q, 1.0, 0, 0.0)
    hi = cum(steps + [2100], le + [le[-1]], q, 1.0, 1, ptok)
    out["axis"] = {}
    for s in q:
        r_lo, r_hi = lo[s] / PRE, hi[s] / PRE
        out["axis"][s] = {"low": r_lo, "high": r_hi, "geomean": (r_lo * r_hi) ** 0.5}
        lines.append(f"step {s:5d}: RL/pretrain low {r_lo:.3e} high {r_hi:.3e} geomean {(r_lo * r_hi) ** 0.5:.3e}")
    # per-job compute
    lines.append("job            samples  gen_tokens  meta_samples meta_tokens  load_s   gen_s   gpu")
    tot_s = tot_t = 0
    jobs = {}
    for j in sorted(rg):
        mp = os.path.join(C.ART, "meta", f"{j}.json")
        metas = [json.loads(x) for x in open(mp)] if os.path.exists(mp) else []
        m = metas[-1] if metas else {}
        ns, nt = len(rg[j]), sum(r["n_tok"] for r in rg[j])
        ld = sum(x.get("t_load_s", 0) for x in metas)
        gs = sum(x.get("t_gen_s", 0) for x in metas)
        jobs[j] = {"samples": ns, "gen_tokens": nt, "meta_rows": len(metas), "meta_samples": sum(x.get("samples", 0) for x in metas),
                   "meta_tokens": sum(x.get("gen_tokens", 0) for x in metas), "load_s": ld, "gen_s": gs,
                   "gpu": (m.get("gpus") or ["?"])[0]}
        tot_s += ns
        tot_t += nt
        lines.append(f"{j:14s} {ns:7d} {nt:11d} {jobs[j]['meta_samples']:12d} {jobs[j]['meta_tokens']:11d} {ld:7.0f} "
                     f"{gs:7.0f}   {jobs[j]['gpu']}  (meta rows {len(metas)})")
    lines.append(f"TOTAL samples {tot_s} generated tokens {tot_t}")
    out["jobs"] = jobs
    out["lengths"] = {"train": dict(zip(steps, lt)), "eval": dict(zip(steps, le)), "prompt_tok": ptok}
    json.dump(out, open(os.path.join(C.OUT, "compute.json"), "w"), indent=1)
    open(os.path.join(C.OUT, "compute.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
