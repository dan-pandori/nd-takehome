"""Provenance of run olmo-ifladder's inputs and samples, from my own rebuilds.

 1. upstream checkers (my fetch) vs the run's vendored copies, byte for byte
 2. prompt sets: reach = olmo-iffu's hinted IF prompts less ifbench_281; calibration = olmo-transplant's set
 3. problems files: `prompt` / ids / kwargs vs upstream; the user turn sent (`prompt_sample`) vs MY rung text built
    from the pre-registered rule (BREVITY, CHECK, HINTS by instruction id, DROP60 from the pre-registration's text)
 4. rung 4: messages_sample = two (user, assistant) exemplar turns + the rung-3 turn; exemplar user turns = the
    source's upstream prompt; exemplar answers = the stored olmo-ifomega s2300 sample's answer (bucket copies),
    sha256 vs exemplars.csv; source != target; source carries the target's binding id
 5. my prompt ids (template text written out by me, tokenised with `tokenizers`) vs each job meta's
    prompt_sha256_by_pid and prompt_tokens_by_pid, and every row's prompt_tokens
 6. per job: pids, draws per pid, chunks, seeds, decoding, template sha vs open-instruct's olmo_thinker, LoRA sha
"""
import ast
import collections
import hashlib
import json
import re

from tokenizers import Tokenizer

from rvl_core import (ART, CODE, JOBS, OUT, RAW, SCR, TOKJ, Tee, dump, iter_gz, iter_job, load_csv, load_jsonl,
                      sha_int32, upstream_record, answer_of, wsnorm)

P = Tee("provenance.txt")
res = {}

# ------------------------------------------------------------------ 1. upstream vs vendored
V = RAW / "olmo_ifomega" / "vendor"
pairs = [(V / "ifbench_evaluation_lib.py", SCR / "upstream/ifbench/evaluation_lib.py")]
for f in ["__init__.py", "classic_instructions.py", "instructions.py", "instructions_registry.py",
          "instructions_util.py"]:
    pairs.append((V / "ifbench" / f, SCR / "upstream/ifbench/ifbench" / f))
for f in ["evaluation_lib.py", "instructions.py", "instructions_registry.py", "instructions_util.py"]:
    pairs.append((V / "instruction_following_eval" / f, SCR / "upstream/ife/instruction_following_eval" / f))
same = [a.read_bytes() == b.read_bytes() for a, b in pairs]
P(f"[1] vendored vs my upstream fetch: {sum(same)}/{len(same)} byte-identical "
  f"{[str(a.relative_to(V)) for (a, b), s in zip(pairs, same) if not s]}")
res["vendor_identical"] = [sum(same), len(same)]

# ------------------------------------------------------------------ 2. prompt sets
prompts = load_csv(CODE / "prompts.csv")
reach = [r["pid"] for r in prompts if r["set"] == "reach"]
cal = [r["pid"] for r in prompts if r["set"] != "reach"]
st = load_csv(RAW / "olmo_iffu" / "status.csv")
iffu_if = [r["pid"] for r in st if r["group"] != "geometry"]
tp = load_csv(RAW / "olmo_transplant" / "prompts.csv")
tp_cal = [r["pid"] for r in tp if r["set"] != "reach"]
P(f"[2] prompts.csv: reach {len(reach)} (ifbench {sum(p.startswith('ifbench') for p in reach)}, ifeval "
  f"{sum(p.startswith('ifeval') for p in reach)}), other sets {collections.Counter(r['set'] for r in prompts if r['set'] != 'reach')}")
P(f"    olmo-iffu IF prompts {len(iffu_if)}; reach == iffu IF less ifbench_281: "
  f"{sorted(reach) == sorted(p for p in iffu_if if p != 'ifbench_281')}; 281 in reach: {'ifbench_281' in reach}")
P(f"    olmo-transplant calibration {sorted(tp_cal, key=lambda x: int(x.split('_')[1]))}; == run's: {sorted(cal) == sorted(tp_cal)}")
PRE_CAL = [f"ifbench_{k}" for k in (25, 29, 52, 58, 85, 115, 239, 259, 295, 298)]
P(f"    calibration == pre-registered list: {sorted(cal) == sorted(PRE_CAL)}")
res["sets"] = {"reach": len(reach), "cal": len(cal)}

# ------------------------------------------------------------------ 3. rung texts
src = (CODE / "interventions.py").read_text()
P(f"[3] interventions.py sha256 {hashlib.sha256(src.encode()).hexdigest()[:16]} (pre-registered e3c284741c25d84c)")
tree = ast.parse(src)
consts = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        try:
            consts[node.targets[0].id] = ast.literal_eval(node.value)
        except ValueError:
            pass
HINTS = consts["HINTS"]
# the pre-registration's own text for rungs 1-2 and DROP60 (not the file's)
BREV = "Answer in at most 60 words."
CHK = "Before answering, check each constraint against your draft."
DROP60 = {f"ifbench_{k}" for k in (52, 58, 0, 1, 3, 4, 166, 170, 188, 284)}
P(f"    file BREVITY == prereg: {consts['BREVITY'] == BREV}; CHECK == prereg: {consts['CHECK'] == CHK}; "
  f"DROP60 == prereg: {set(consts['DROP60']) == DROP60}")


def my_rung_text(pid, rung):
    task, rec = upstream_record(pid)
    base = rec["prompt"]
    if rung == 1:
        return None if pid in DROP60 else base + "\n\n" + BREV
    head = CHK if pid in DROP60 else BREV + " " + CHK
    if rung == 2:
        return base + "\n\n" + head
    ids = []
    for i in rec["instruction_id_list"]:
        if i not in ids:
            ids.append(i)
    return base + "\n\n" + head + "\n\n" + " ".join(HINTS[i] for i in ids)


def norm_kwargs(kw):
    if isinstance(kw, str):
        kw = ast.literal_eval(kw)
    return [{a: b for a, b in dict(k).items() if b is not None} for k in kw]


probs = {}
for name, rung in [("problems_r1cal.jsonl", 1), ("problems_r2.jsonl", 2), ("problems_r3.jsonl", 3),
                   ("problems_r4.jsonl", 4), ("problems_plain.jsonl", 0)]:
    rows = load_jsonl(CODE / name)
    probs[name] = {r["pid"]: r for r in rows}
    bad = collections.Counter()
    for r in rows:
        task, rec = upstream_record(r["pid"])
        if r["prompt"] != rec["prompt"]:
            bad["prompt!=upstream"] += 1
        if list(r["instruction_id_list"]) != list(rec["instruction_id_list"]):
            bad["ids!=upstream"] += 1
        if norm_kwargs(r["kwargs"]) != norm_kwargs(rec["kwargs"]):
            bad["kwargs!=upstream"] += 1
        if rung == 0:
            if "prompt_sample" in r or "messages_sample" in r:
                bad["plain has a sample field"] += 1
            continue
        want = my_rung_text(r["pid"], 3 if rung == 4 else rung)
        if r.get("prompt_sample") != want:
            bad["prompt_sample!=mine"] += 1
        if rung == 4:
            ms = r.get("messages_sample")
            if not ms or ms[-1]["content"] != want or ms[-1]["role"] != "user":
                bad["final turn!=mine"] += 1
    P(f"    {name}: {len(rows)} rows; mismatches {dict(bad) or 'none'}")
    res[f"problems_{name}"] = dict(bad)

# ------------------------------------------------------------------ 4. rung-4 exemplars
ex = load_csv(CODE / "exemplars.csv")
P(f"[4] exemplars.csv: {len(ex)} rows, targets {len({e['target'] for e in ex})}, jobs "
  f"{dict(collections.Counter(e['job'] for e in ex))}")
need = collections.defaultdict(set)
for e in ex:
    need[e["job"]].add((e["source"], int(e["chunk"]), int(e["i"])))
ans = {}
for job, keys in need.items():
    f = SCR / "src" / f"{job}.jsonl.gz"
    for r in iter_gz(f):
        k = (r["pid"], int(r["chunk"]), int(r["i"]))
        if k in keys:
            ans[(job,) + k] = (answer_of(r["text"]), r.get("finish"), r.get("model"))
P(f"    stored source rows found {len(ans)} of {sum(len(v) for v in need.values())}")
cons = {r["pid"]: r for r in load_csv(RAW / "olmo_ifomega" / "constraints.csv")} if (RAW / "olmo_ifomega" / "constraints.csv").exists() else {}
bind = {r["pid"]: r["binding"] for r in prompts}
P4 = collections.Counter()
r4 = probs["problems_r4.jsonl"]
ex_by_t = collections.defaultdict(list)
for e in sorted(ex, key=lambda e: (e["target"], int(e["slot"]))):
    ex_by_t[e["target"]].append(e)
detail = []
for t, es in ex_by_t.items():
    ms = r4[t]["messages_sample"]
    if len(ms) != 5 or [m["role"] for m in ms] != ["user", "assistant", "user", "assistant", "user"]:
        P4["turn structure"] += 1
        continue
    for j, e in enumerate(es):
        a, fin, model = ans.get((e["job"], e["source"], int(e["chunk"]), int(e["i"])), (None, None, None))
        if a is None:
            P4["source row or answer missing"] += 1
            continue
        if hashlib.sha256(a.encode()).hexdigest() != e["answer_sha256"]:
            P4["answer sha != csv (raw stripped)"] += 1
        if ms[2 * j + 1]["content"] != a:
            P4["assistant turn != stored answer"] += 1
        task, rec = upstream_record(e["source"])
        if ms[2 * j]["content"] != rec["prompt"]:
            P4["user turn != source upstream prompt"] += 1
        if e["source"] == t:
            P4["source == target"] += 1
        if bind[t] not in rec["instruction_id_list"]:
            P4["source lacks target binding id"] += 1
        if model != "s2300" and "s2300" not in e["job"]:
            P4["not s2300"] += 1
        if fin != "stop":
            P4["source not finished"] += 1
        if (e["source"].split("_")[0]) != t.split("_")[0]:
            P4["other benchmark"] += 1
        P4["exemplar turns checked"] += 1
        detail.append({"target": t, "slot": e["slot"], "source": e["source"], "same_ids":
                       sorted(set(rec["instruction_id_list"])) == sorted(set(upstream_record(t)[1]["instruction_id_list"]))})
P(f"    rung-4 exemplar checks: {dict(P4)}")
P(f"    exemplar sources with an identical id set: {sum(d['same_ids'] for d in detail)} / {len(detail)}; "
  f"sources that are among the 58: {sum(d['source'] in set(reach) | set(cal) for d in detail)}")
res["exemplars"] = dict(P4)

# ------------------------------------------------------------------ 5. prompt ids vs metas
tk = Tokenizer.from_file(str(TOKJ))
SYSTEM = "You are a helpful AI assistant."


def my_ids(msgs):
    s = f"<|im_start|>system\n{SYSTEM}<|im_end|>\n"
    for m in msgs:
        s += f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n"
    s += "<|im_start|>assistant\n<think>"
    return tk.encode(s, add_special_tokens=False).ids


def msgs_for(job, pid):
    if job.startswith("L"):
        return [{"role": "user", "content": upstream_record(pid)[1]["prompt"]}]
    rung = 1 if job.startswith("R1") else int(job[1]) if job.startswith("R") else int(job[3])  # S0r2 / S0r3
    if rung == 4:
        r = r4[pid]
        es = ex_by_t[pid]
        out = []
        for e in es:
            a = ans[(e["job"], e["source"], int(e["chunk"]), int(e["i"]))][0]
            out += [{"role": "user", "content": upstream_record(e["source"])[1]["prompt"]},
                    {"role": "assistant", "content": a}]
        return out + [{"role": "user", "content": my_rung_text(pid, 3)}]
    return [{"role": "user", "content": my_rung_text(pid, rung)}]


jobinfo = {}
for job in JOBS:
    m = json.load(open(ART / "meta" / f"{job}.json"))
    psha = m["prompt_sha256_by_pid"]
    plen = m["prompt_tokens_by_pid"]
    if isinstance(psha, str):
        psha = ast.literal_eval(psha)
    if isinstance(plen, str):
        plen = ast.literal_eval(plen)
    diff, lendiff = [], []
    for pid, h in psha.items():
        ids = my_ids(msgs_for(job, pid))
        if sha_int32(ids) != h:
            diff.append(pid)
        if len(ids) != plen[pid]:
            lendiff.append(pid)
    # rows
    per = collections.Counter()
    chunks = collections.defaultdict(set)
    fin = collections.Counter()
    ptok_bad = 0
    models = collections.Counter()
    for r in iter_job(job):
        per[r["pid"]] += 1
        chunks[r["pid"]].add((r["chunk"], r["i"]))
        fin[r["finish"]] += 1
        models[r["model"]] += 1
        if r.get("prompt_tokens") != plen.get(r["pid"]):
            ptok_bad += 1
    nd = collections.Counter(per.values())
    dup = sum(per[p] - len(chunks[p]) for p in per)
    info = {"seed": m.get("seed"), "pids": len(per), "draws_per_pid": dict(nd), "dup_keys": dup,
            "finish": dict(fin), "models": dict(models), "T": m.get("temperature"), "top_p": m.get("top_p"),
            "max_tokens": m.get("max_tokens"), "tp": m.get("tp"), "chunk": m.get("chunk"),
            "stop_after": m.get("stop_after"), "vllm": m.get("vllm"), "template": (m.get("template_sha256") or "")[:12],
            "lora_sha": (m.get("lora_sha256") or "")[:16], "prompt_sha_diff": diff, "prompt_len_diff": lendiff,
            "row_prompt_tokens_bad": ptok_bad, "gen_tokens": m.get("gen_tokens"), "samples": m.get("samples"),
            "gpus": m.get("gpus"), "utc_end": m.get("utc_end"), "problems": m.get("problems"), "pids_spec": m.get("pids")}
    jobinfo[job] = info
    P(f"[5/6] {job}: seed {info['seed']} pids {info['pids']} draws/pid {info['draws_per_pid']} dup {dup} finish "
      f"{info['finish']} model {info['models']} T {info['T']} top_p {info['top_p']} max {info['max_tokens']} tp "
      f"{info['tp']} chunk {info['chunk']} stop_after {info['stop_after']} vllm {info['vllm']} tmpl {info['template']} "
      f"lora {info['lora_sha'] or '-'} | prompt sha != mine: {len(diff)} {diff[:4]}; len != mine {len(lendiff)}; "
      f"row prompt_tokens != meta {ptok_bad}")
res["jobs"] = jobinfo

# template vs open-instruct's olmo_thinker (my fetch @ 7e780f2fea)
dt = (SCR / "upstream" / "oi" / "dataset_transformation.py").read_text()
tree = ast.parse(dt)
tmpl = None
for node in ast.walk(tree):
    if isinstance(node, ast.Dict):
        for k, v in zip(node.keys, node.values):
            if isinstance(k, ast.Constant) and k.value == "olmo_thinker":
                tmpl = ast.literal_eval(v)
sha_up = hashlib.sha256(tmpl.encode()).hexdigest()[:12] if tmpl else None
P(f"    open-instruct olmo_thinker template sha {sha_up}; jobs' template sha set "
  f"{sorted({v['template'] for v in jobinfo.values()})}")
res["template_upstream"] = sha_up

# LoRA adapter files vs metas
for arm in ("main", "ctrl"):
    h = hashlib.sha256((ART / "lora" / arm / "adapter_model.safetensors").read_bytes()).hexdigest()[:16]
    P(f"    adapter {arm}: sha256 {h}; metas using it: "
      f"{[j for j, v in jobinfo.items() if v['lora_sha'] == h]}")
    cfg = json.load(open(ART / "lora" / arm / "adapter_config.json"))
    P(f"      config r {cfg.get('r')} alpha {cfg.get('lora_alpha')} dropout {cfg.get('lora_dropout')} targets "
      f"{sorted(cfg.get('target_modules') or [])} base {cfg.get('base_model_name_or_path')}")
dump(res, "provenance.json")
