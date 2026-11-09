"""Compute behind every arm of run olmo-ifladder (one pod, one H200; jobs ran one after another).

Per job: wall seconds from the pod worker's LINE_START / LINE_END and from every JOB_START / JOB_DONE (failed
attempts included), the meta's t_load + t_gen, samples, generated tokens (meta, and my sum of the rows' response
lengths), prompt tokens; LoRA training steps / tokens / seconds from the training metas; pod hours and dollars from
podbudget (rate 3.59 $/h, community H200). Matched-axis ratios between compared arms.
Writes out/compute.{txt,json}.
"""
import collections
import datetime as dt
import gzip
import json
import re
import subprocess

from rvl_core import ART, OUT, Tee, dump

P = Tee("compute.txt")


def t(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


lines = open(ART / "logs" / "worker0.log").read().splitlines()
starts, wall = {}, {}
for ln in lines:
    m = re.match(r"LINE_START 0 (\d+) (\S+) :: (.*)", ln)
    if m:
        jm = re.search(r"job\.sh (\S+)|lora\.py (\w+) .*--arm (\w+)", m.group(3))
        name = jm.group(1) if jm and jm.group(1) else (f"lora_{jm.group(3)}_{jm.group(2)}" if jm else "other")
        starts[m.group(1)] = (name, t(m.group(2)))
    m = re.match(r"LINE_END 0 (\d+) rc=(\d+) (\S+)", ln)
    if m and m.group(1) in starts:
        name, a = starts[m.group(1)]
        wall.setdefault(name, []).append(((t(m.group(3)) - a).total_seconds(), int(m.group(2))))
jobsd = collections.defaultdict(list)
for f in sorted((ART / "logs").glob("q_*.log")):
    s = open(f, errors="replace").read()
    for a, b in zip(re.findall(r"JOB_START (\S+) (\S+)", s), re.findall(r"JOB_DONE (\S+) rc=(\d+) (\S+)", s)):
        jobsd[a[0]].append(((t(b[2]) - t(a[1])).total_seconds(), int(b[1])))
res = {"jobs": {}}
tot = collections.Counter()
for job in ["S0r2", "S0r3", "R1cal_dpo", "R2_dpo", "R3_dpo", "R4_dpo", "R2_s2300", "R3_s2300", "R4_s2300",
            "Lchk_main", "Lchk_ctrl", "Leval_main", "Leval_ctrl"]:
    m = json.load(open(ART / "meta" / f"{job}.json"))
    rows = [json.loads(l) for l in gzip.open(OUT / "regrade" / f"{job}.jsonl.gz", "rt")]
    gen = sum(r["n_ids"] for r in rows)
    ptok = sum(r["prompt_tokens"] for r in rows)
    w = wall.get(job, [])
    jd = jobsd.get(job, [])
    o = {"samples": len(rows), "gen_tokens_meta": m["gen_tokens"], "gen_tokens_rows": gen, "prompt_tokens_rows": ptok,
         "t_load_gen": round(m["t_load_s"] + m["t_gen_s"], 1), "wall_lines": w, "job_runs": jd,
         "gpu_s": sum(x[0] for x in jd)}
    res["jobs"][job] = o
    tot["gpu_s"] += o["gpu_s"]
    tot["gen"] += gen
    tot["samples"] += len(rows)
    P(f"{job}: samples {len(rows)}; gen tokens meta {m['gen_tokens']} rows {gen}; prompt tokens {ptok}; t_load+t_gen "
      f"{o['t_load_gen']} s; job runs (s, rc) {jd}; worker lines {w}")
for arm in ("main", "ctrl"):
    m = json.load(open(ART / "meta" / f"lora_{arm}.json"))
    w = wall.get(f"lora_{arm}_train", []) + wall.get(f"lora_{arm}_finish", [])
    res["jobs"][f"lora_{arm}"] = {"steps": m["steps"], "train_tokens": m["train_tokens"], "train_secs": m["train_secs"],
                                  "secs_finish": m.get("secs_finish"), "wall_lines": w}
    P(f"lora_{arm}: steps {m['steps']}, train tokens {m['train_tokens']}, train secs {m['train_secs']}, finish secs "
      f"{m.get('secs_finish')}, worker lines {w}")
other = {k: v for k, v in wall.items() if k not in res["jobs"] and not k.startswith("lora_")}
P(f"other worker lines: {other}")
P(f"sampling jobs total: {tot['samples']} samples, {tot['gen']} generated tokens, {tot['gpu_s'] / 3600:.2f} GPU-h "
  f"(JOB_START->JOB_DONE incl. failed starts)")
pb = subprocess.run(["podbudget", "olmo-ifladder"], capture_output=True, text=True).stdout.strip().splitlines()[-1]
P(f"podbudget: {pb}")
J = res["jobs"]
pairs = [("Leval_main", "Leval_ctrl"), ("Lchk_main", "Lchk_ctrl")]
for a, b in pairs:
    P(f"{a} / {b}: gen tokens {J[a]['gen_tokens_rows'] / J[b]['gen_tokens_rows']:.3f}, GPU-s "
      f"{J[a]['gpu_s'] / J[b]['gpu_s']:.3f}, samples {J[a]['samples'] / J[b]['samples']:.3f}")
P(f"lora_main / lora_ctrl: train tokens {J['lora_main']['train_tokens'] / J['lora_ctrl']['train_tokens']:.3f}, train "
  f"secs {J['lora_main']['train_secs'] / J['lora_ctrl']['train_secs']:.3f}, steps equal "
  f"{J['lora_main']['steps'] == J['lora_ctrl']['steps']}")
for a, b in (("R3_dpo", "R2_dpo"), ("R4_dpo", "R3_dpo")):
    pa = J[a]["gen_tokens_rows"] / J[a]["samples"]
    pb_ = J[b]["gen_tokens_rows"] / J[b]["samples"]
    P(f"tokens per draw {a} {pa:.0f} vs {b} {pb_:.0f} ({pa / pb_:.3f}x)")
res["total"] = dict(tot)
res["podbudget"] = pb
dump(res, "compute.json")
