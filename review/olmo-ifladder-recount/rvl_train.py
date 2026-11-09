"""The LoRA training manifest and recipe of run olmo-ifladder, checked from the stored source samples (my bucket copies).

 1. manifest rows vs my copies of the olmo-ifomega sample files: ids, text sha, n_tok, finish, my strict grade on the
    ORIGINAL prompt, prompt + response tokens <= 16,384 (my prompt tokenisation)
 2. prompt sets: training / held-out pids are IFBench, outside the 58 and ifbench_281, distinct; one constraint id per
    slot; the reach set's ids covered
 3. LoRA metas: training list == manifest (key, sha) per arm; same per-epoch slot order in both arms; steps, epochs,
    learning-rate schedule (4 warm-up steps, cosine to 10 %), recipe fields vs the pre-registration; tokens per arm
 4. the pre-registered checks: held-out NLL (base / peft / merged), the 2 % guard, the merge check
Writes out/train.{txt,json}.
"""
import collections
import hashlib
import json
import math

from tokenizers import Tokenizer

from rvl_core import (ART, CODE, OUT, SCR, TOKJ, Tee, answer_of, dump, iter_gz, load_csv, load_jsonl, sha_int32,
                      unb64, upstream_record)
from rvl_graders import if_grade

P = Tee("train.txt")
res = {}
man = load_csv(CODE / "train_manifest.csv")
manj = load_jsonl(CODE / "train_manifest.jsonl")
prompts = load_csv(CODE / "prompts.csv")
P58 = {r["pid"] for r in prompts}
REACH = [r["pid"] for r in prompts if r["set"] == "reach"]
tk = Tokenizer.from_file(str(TOKJ))


def my_prompt_ids(text):
    s = (f"<|im_start|>system\nYou are a helpful AI assistant.<|im_end|>\n<|im_start|>user\n{text}<|im_end|>\n"
         f"<|im_start|>assistant\n<think>")
    return tk.encode(s, add_special_tokens=False).ids


# ---------------------------------------------------------------- 1. rows vs source files
need = collections.defaultdict(set)
for r in man:
    need[r["job"]].add((r["pid"], int(r["chunk"]), int(r["i"])))
src = {}
for job, ks in need.items():
    for x in iter_gz(SCR / "src" / f"{job}.jsonl.gz"):
        k = (x["pid"], int(x["chunk"]), int(x["i"]))
        if k in ks:
            src[(job,) + k] = x
P(f"[1] manifest rows {len(man)} (jsonl {len(manj)}); source rows found {len(src)} of {sum(len(v) for v in need.values())}")
jkey = {(x["role"], x["writer"], x["pid"]): x for x in manj}
bad = collections.Counter()
rows = []
for r in man:
    x = src[(r["job"], r["pid"], int(r["chunk"]), int(r["i"]))]
    ids = unb64(x["ids"])
    j = jkey[(r["role"], r["writer"], r["pid"])]
    jids = unb64(j["ids"])
    ans = answer_of(x["text"])
    task, rec = upstream_record(r["pid"])
    st, per, lo = if_grade(task, rec, ans)
    pids_ = my_prompt_ids(rec["prompt"])
    tsha = hashlib.sha256(x["text"].encode()).hexdigest()
    isha = sha_int32(ids)
    o = {"role": r["role"], "writer": r["writer"], "pid": r["pid"], "id": r["id"], "job": r["job"],
         "strict": st, "finish": x.get("finish"), "n_tok": x.get("n_tok"), "len_ids": len(ids),
         "prompt_tok": len(pids_), "total": len(pids_) + len(ids), "text_sha_ok": tsha == r["text_sha256"],
         "ids_sha_ok": isha == r["text_sha256"], "jsonl_ids_eq": jids == ids, "jsonl_sha_eq": j["sha256"] == r["text_sha256"],
         "jsonl_prompt_eq": j["prompt"] == rec["prompt"], "model": x.get("model"), "n_close": x["text"].count("</think>"),
         "ans_words": None if ans is None else len(ans.split())}
    for f in ("strict", "text_sha_ok", "jsonl_ids_eq", "jsonl_sha_eq", "jsonl_prompt_eq"):
        if not o[f]:
            bad[f"not {f}"] += 1
    if o["finish"] != "stop":
        bad["not finished"] += 1
    if o["total"] > 16384:
        bad["over 16,384 tokens"] += 1
    if o["n_tok"] != len(ids):
        bad["n_tok != len(ids)"] += 1
    if (o["writer"] == "s2300") != (o["model"] == "s2300"):
        bad["writer != row model"] += 1
    rows.append(o)
P(f"    problems: {dict(bad) or 'none'} (text sha convention: sha256(text) "
  f"{sum(o['text_sha_ok'] for o in rows)}/{len(rows)}, sha_int32(ids) {sum(o['ids_sha_ok'] for o in rows)}/{len(rows)})")
res["rows"] = rows

# ---------------------------------------------------------------- 2. sets
tr = [o for o in rows if o["role"] == "train"]
ho = [o for o in rows if o["role"] == "heldout"]
trp = sorted({o["pid"] for o in tr})
hop = sorted({o["pid"] for o in ho})
P(f"[2] training pids {len(trp)}, held-out pids {len(hop)}; in the 58: {[p for p in trp + hop if p in P58]}; "
  f"ifbench_281: {'ifbench_281' in trp + hop}; non-IFBench: {[p for p in trp + hop if not p.startswith('ifbench_')]}; "
  f"train & held-out overlap: {sorted(set(trp) & set(hop))}")
slots = collections.defaultdict(set)
for o in tr:
    slots[o["id"]].add(o["pid"])
P(f"    slot ids {len(slots)} (distinct); pids per slot {sorted(len(v) for v in slots.values())}; each slot pid carries its id: "
  f"{all(i in upstream_record(p)[1]['instruction_id_list'] for i, ps in slots.items() for p in ps)}")
reach_ids = collections.Counter()
for p in REACH:
    for i in set(upstream_record(p)[1]["instruction_id_list"]):
        reach_ids[i] += 1
cov = [i for i in reach_ids if i in slots]
P(f"    reach-set ids {len(reach_ids)}; covered by a training slot {len(cov)}; uncovered "
  f"{sorted(i for i in reach_ids if i not in slots)}")
train_ids_all = collections.Counter(i for p in trp for i in set(upstream_record(p)[1]["instruction_id_list"]))
P(f"    ids carried by training prompts (all, incl. second ids): {dict(train_ids_all)}")
res["train_pids"], res["heldout_pids"] = trp, hop
res["slots"] = {i: sorted(v) for i, v in slots.items()}
res["reach_ids_uncovered"] = sorted(i for i in reach_ids if i not in slots)
for w in ("s2300", "dpo"):
    xs = [o for o in tr if o["writer"] == w]
    P(f"    train {w}: response tokens sum {sum(o['len_ids'] for o in xs)}, with prompts {sum(o['total'] for o in xs)}; "
      f"median response {sorted(o['len_ids'] for o in xs)[len(xs) // 2]}; answer words median "
      f"{sorted(o['ans_words'] for o in xs)[len(xs) // 2]}; strict {sum(o['strict'] for o in xs)}/{len(xs)}")

# ---------------------------------------------------------------- 3. LoRA metas
metas = {a: json.load(open(ART / "meta" / f"lora_{a}.json")) for a in ("main", "ctrl")}
for a, w in (("main", "s2300"), ("ctrl", "dpo")):
    m = metas[a]
    mk = {(x["pid"], x["sha256"]) for x in m["train"]}
    want = {(o["pid"], next(r["text_sha256"] for r in man if r["role"] == "train" and r["writer"] == w and
                            r["pid"] == o["pid"])) for o in tr if o["writer"] == w}
    order = [x["slot"] for x in m["log"]]
    lrs = [x["lr"] for x in m["log"]]
    # my schedule: linear warm-up over 4 steps (step s -> (s+1)/4), then cosine from 1 to 0.1 at the last step
    exp = []
    for s in range(64):
        if s < 4:
            exp.append(1e-4 * (s + 1) / 4)
        else:
            t = (s - 4) / (63 - 4)
            exp.append(1e-4 * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * t))))
    dev = max(abs(a_ - b_) / b_ for a_, b_ in zip(lrs, exp))
    P(f"[3] lora_{a}: writer {m['writer']}; train set == manifest ({w}): {mk == want}; steps {m['steps']} log rows "
      f"{len(m['log'])}; epochs {m['recipe']['epochs']}; slots per epoch distinct: "
      f"{all(len(set(order[e * 16:(e + 1) * 16])) == 16 for e in range(4))}; lr max rel. deviation from my schedule {dev:.3g}; "
      f"train_tokens {m['train_tokens']} (resp tokens in log {sum(x['resp_tokens'] for x in m['log'])}); secs "
      f"{m.get('train_secs')} + finish {m.get('secs_finish')}; peak {m.get('peak_gb')} GB")
    res[f"lora_{a}"] = {"order": order, "train_tokens": m["train_tokens"], "lr_dev": dev,
                        "resp_tokens_log": sum(x["resp_tokens"] for x in m["log"])}
P(f"    same per-epoch order in both arms: {res['lora_main']['order'] == res['lora_ctrl']['order']}; "
  f"train tokens main / ctrl = {metas['main']['train_tokens'] / metas['ctrl']['train_tokens']:.3f}")
rec_pre = {"r": 16, "alpha": 32, "dropout": 0.05, "lr": 1e-4, "betas": [0.9, 0.999], "eps": 1e-8, "weight_decay": 0.0,
           "warmup_steps": 4, "final_lr_frac": 0.1, "grad_clip": 1.0, "epochs": 4, "batch": 1, "seq_cap": 16384,
           "seed": 20261109}
for a in ("main", "ctrl"):
    rc = metas[a]["recipe"]
    P(f"    recipe {a} vs pre-registration: {[k for k, v in rec_pre.items() if rc.get(k) != v] or 'all equal'}; targets "
      f"{sorted(rc['targets']) == sorted(['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj'])}")

# ---------------------------------------------------------------- 4. NLL checks
for a in ("main", "ctrl"):
    m = metas[a]
    mean = lambda xs: sum(xs) / len(xs)
    hb, hp, hm = (mean(m[f"nll_heldout_{t}"]["s2300"]) for t in ("base", "peft", "merged"))
    db, dp, dm = (mean(m[f"nll_heldout_{t}"]["dpo"]) for t in ("base", "peft", "merged"))
    mc = max(abs(a_ - b_) / b_ for a_, b_ in zip(m["nll_train2_merged"], m["nll_train2_peft"]))
    l4 = [x["loss"] for x in m["log"]]
    P(f"[4] lora_{a}: training loss mean of first 4 steps {sum(l4[:4]) / 4:.3f}, last 4 {sum(l4[-4:]) / 4:.3f}; NLL change "
      f"held-out s2300 {(hp - hb) / hb:+.1%} (positive = rises), held-out dpo {(dp - db) / db:+.1%}")
    P(f"[4] lora_{a}: held-out s2300 NLL base {hb:.4f} peft {hp:.4f} ({(hb - hp) / hb:+.1%} drop) merged {hm:.4f}; "
      f"held-out dpo NLL base {db:.4f} peft {dp:.4f} ({(db - dp) / db:+.1%} drop); merge check max rel. "
      f"{mc:.4f} (mean-based {m['summary']['merge_check_rel']:.4f})")
dump(res, "train.json")
