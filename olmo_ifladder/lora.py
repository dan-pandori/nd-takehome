#!/usr/bin/env python3
"""LoRA fine-tunes of dpo for run olmo-ifladder (pre-registration preregistration/olmo-ifladder.md, Teachability).

  lora.py steptest --base /workspace/models/dpo --tok /workspace/models/tok --out <json>
      two optimizer steps on a 16,384-token sequence: peak memory and step time (stage 0).
  lora.py train --base /workspace/models/dpo --tok /workspace/models/tok --manifest olmo_ifladder/train_manifest.jsonl
                --arm main|ctrl --adapter_out <dir> --merged_out <dir> --report <json> [--lr 1e-4]
      one process: held-out NLL under dpo; LoRA training (the pre-registered recipe); held-out NLL under the PEFT
      model; merge into bf16 weights; merge check (NLL of two training trajectories, merged vs PEFT); save the adapter
      and the merged model (the merged weights stay on the pod).

Manifest rows (built on the VPS by olmo_ifladder/sources.py): {"role": "train" | "heldout", "writer": "s2300" | "dpo",
"slot": training slot 0-15 (train rows), "pid", "prompt" (the user turn), "ids" (base64 int32 stored response ids,
thinking + answer + EOS), "key", "sha256"}. Arm main trains on the train rows written by s2300, ctrl on those written by
dpo; both see the slots in the same per-epoch order (seed). Held-out NLL is reported for both writers.
"""
import argparse
import base64
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sample import TEMPLATE  # noqa: E402  (the sampler's olmo_thinker template, verbatim)

TARGETS = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
RECIPE = {"r": 16, "alpha": 32, "dropout": 0.05, "targets": TARGETS, "lr": 1e-4, "betas": [0.9, 0.999], "eps": 1e-8,
          "weight_decay": 0.0, "warmup_steps": 4, "final_lr_frac": 0.1, "grad_clip": 1.0, "epochs": 4, "batch": 1,
          "seq_cap": 16384, "seed": 20261109, "loss": "mean token CE over response tokens"}


def prompt_ids(tok, prompt):
    ids = tok.apply_chat_template([{"role": "user", "content": prompt}], add_generation_prompt=True, tokenize=True,
                                  return_dict=False, chat_template=TEMPLATE)
    if tok.pad_token_id is not None:
        ids = [x for x in ids if x != tok.pad_token_id]
    return ids


def load_model(base):
    import torch
    from transformers import AutoModelForCausalLM
    t0 = time.time()
    m = AutoModelForCausalLM.from_pretrained(base, dtype=torch.bfloat16, device_map={"": 0}, attn_implementation="sdpa")
    m.config.use_cache = False
    print(f"loaded {base} in {time.time() - t0:.0f}s", flush=True)
    return m


def seqs(tok, rows):
    out = []
    for r in rows:
        p = prompt_ids(tok, r["prompt"])
        resp = np.frombuffer(base64.b64decode(r["ids"]), dtype=np.int32).tolist()
        assert len(p) + len(resp) <= RECIPE["seq_cap"], (r["pid"], len(p), len(resp))
        out.append((p, resp))
    return out


def nll(model, data):
    """Mean per-token NLL of each response given its prompt (no grad)."""
    import torch
    res = []
    model.eval()
    with torch.no_grad():
        for p, resp in data:
            x = torch.tensor([p + resp], device="cuda")
            lab = torch.tensor([[-100] * len(p) + resp], device="cuda")
            res.append(float(model(input_ids=x, labels=lab).loss))
    return res


def lora_wrap(model, recipe):
    from peft import LoraConfig, get_peft_model
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.enable_input_require_grads()
    cfg = LoraConfig(r=recipe["r"], lora_alpha=recipe["alpha"], lora_dropout=recipe["dropout"],
                     target_modules=recipe["targets"], bias="none", task_type="CAUSAL_LM")
    return get_peft_model(model, cfg)


def train(model, data, recipe, log):
    import torch
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=recipe["lr"], betas=tuple(recipe["betas"]), eps=recipe["eps"],
                            weight_decay=recipe["weight_decay"])
    total = recipe["epochs"] * len(data)
    w = recipe["warmup_steps"]

    def lr_at(s):  # s = 0-based step
        if s < w:
            return (s + 1) / w
        f = (s - w) / max(1, total - 1 - w)
        return recipe["final_lr_frac"] + (1 - recipe["final_lr_frac"]) * 0.5 * (1 + math.cos(math.pi * f))

    sched = torch.optim.lr_scheduler.LambdaLR(opt, lr_at)
    rng = np.random.default_rng(recipe["seed"])
    step = 0
    model.train()
    n_tok = 0
    t0 = time.time()
    for ep in range(recipe["epochs"]):
        order = rng.permutation(len(data)).tolist()
        for slot in order:
            p, resp = data[slot]
            x = torch.tensor([p + resp], device="cuda")
            lab = torch.tensor([[-100] * len(p) + resp], device="cuda")
            ts = time.time()
            loss = model(input_ids=x, labels=lab).loss
            loss.backward()
            gn = float(torch.nn.utils.clip_grad_norm_(params, recipe["grad_clip"]))
            opt.step()
            sched.step()
            opt.zero_grad(set_to_none=True)
            n_tok += len(p) + len(resp)
            rec = {"step": step, "epoch": ep, "slot": slot, "loss": float(loss), "grad_norm": gn,
                   "lr": sched.get_last_lr()[0], "tokens": len(p) + len(resp), "resp_tokens": len(resp),
                   "secs": round(time.time() - ts, 2), "peak_gb": round(torch.cuda.max_memory_allocated() / 2**30, 2)}
            log.append(rec)
            print(json.dumps(rec), flush=True)
            step += 1
    return {"steps": step, "train_tokens": n_tok, "train_secs": round(time.time() - t0, 1)}


def cmd_steptest(a):
    import torch
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(a.tok)
    model = lora_wrap(load_model(a.base), RECIPE)
    rng = np.random.default_rng(0)
    L = RECIPE["seq_cap"]
    p = prompt_ids(tok, "Write a short poem.")
    resp = rng.integers(1000, 90000, size=L - len(p)).tolist()
    log = []
    r = dict(RECIPE, lr=1e-6, epochs=1)
    torch.cuda.reset_peak_memory_stats()
    info = train(model, [(p, resp)] * 2, r, log)
    out = {"seq_tokens": L, "log": log, "peak_gb": max(x["peak_gb"] for x in log), **info,
           "trainable": sum(p.numel() for p in model.parameters() if p.requires_grad),
           "gpu": torch.cuda.get_device_name(0)}
    json.dump(out, open(a.out, "w"), indent=1)
    print("STEPTEST", json.dumps({k: v for k, v in out.items() if k != "log"}), flush=True)


def cmd_train(a):
    import torch
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(a.tok)
    rows = [json.loads(x) for x in open(a.manifest)]
    writer = {"main": "s2300", "ctrl": "dpo"}[a.arm]
    tr = sorted([r for r in rows if r["role"] == "train" and r["writer"] == writer], key=lambda r: r["slot"])
    assert [r["slot"] for r in tr] == list(range(len(tr))), "train slots must be 0..n-1"
    ho = {w: [r for r in rows if r["role"] == "heldout" and r["writer"] == w] for w in ("s2300", "dpo")}
    data = seqs(tok, tr)
    hdata = {w: seqs(tok, v) for w, v in ho.items()}
    recipe = dict(RECIPE, lr=a.lr)
    rep = {"arm": a.arm, "writer": writer, "recipe": recipe, "manifest": a.manifest,
           "train": [{"slot": r["slot"], "pid": r["pid"], "key": r["key"], "sha256": r["sha256"],
                      "tokens": len(d[0]) + len(d[1])} for r, d in zip(tr, data)],
           "heldout": {w: [r["key"] for r in v] for w, v in ho.items()}}
    model = load_model(a.base)
    t0 = time.time()
    rep["nll_heldout_base"] = {w: nll(model, v) for w, v in hdata.items()}
    rep["nll_train2_base"] = nll(model, data[:2])
    model = lora_wrap(model, recipe)
    torch.cuda.reset_peak_memory_stats()
    log = []
    rep.update(train(model, data, recipe, log))
    rep["log"] = log
    rep["peak_gb"] = max(x["peak_gb"] for x in log)
    model.save_pretrained(a.adapter_out)
    rep["nll_heldout_peft"] = {w: nll(model, v) for w, v in hdata.items()}
    rep["nll_train2_peft"] = nll(model, data[:2])
    merged = model.merge_and_unload()
    rep["nll_train2_merged"] = nll(merged, data[:2])
    rep["nll_heldout_merged"] = {w: nll(merged, v) for w, v in hdata.items()}
    m = lambda xs: float(np.mean(xs))  # noqa: E731
    rep["summary"] = {
        "heldout_s2300_nll": {"base": m(rep["nll_heldout_base"]["s2300"]), "peft": m(rep["nll_heldout_peft"]["s2300"]),
                              "merged": m(rep["nll_heldout_merged"]["s2300"])},
        "heldout_dpo_nll": {"base": m(rep["nll_heldout_base"]["dpo"]), "peft": m(rep["nll_heldout_peft"]["dpo"]),
                            "merged": m(rep["nll_heldout_merged"]["dpo"])},
        "merge_check_rel": max(abs(x - y) / y for x, y in zip(rep["nll_train2_merged"], rep["nll_train2_peft"])),
        "train_loss_first4": m([x["loss"] for x in log[:4]]), "train_loss_last4": m([x["loss"] for x in log[-4:]])}
    s = rep["summary"]["heldout_s2300_nll"]
    rep["summary"]["heldout_s2300_drop_rel"] = (s["base"] - s["peft"]) / s["base"]
    merged.config.use_cache = True
    merged.save_pretrained(a.merged_out, safe_serialization=True, max_shard_size="5GB")
    rep["secs_total"] = round(time.time() - t0, 1)
    rep["gpu"] = torch.cuda.get_device_name(0)
    json.dump(rep, open(a.report, "w"), indent=1)
    print("TRAIN_DONE", json.dumps(rep["summary"]), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["steptest", "train"])
    ap.add_argument("--base", required=True)
    ap.add_argument("--tok", required=True)
    ap.add_argument("--out")
    ap.add_argument("--manifest")
    ap.add_argument("--arm", choices=["main", "ctrl"])
    ap.add_argument("--adapter_out")
    ap.add_argument("--merged_out")
    ap.add_argument("--report")
    ap.add_argument("--lr", type=float, default=RECIPE["lr"])
    a = ap.parse_args()
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
    {"steptest": cmd_steptest, "train": cmd_train}[a.cmd](a)


if __name__ == "__main__":
    main()
