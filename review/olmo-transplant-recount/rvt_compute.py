"""Compute record of run olmo-transplant, re-derived by the reviewer from the job logs, meta files and sample rows.

Per job: wall-clock GPU-seconds from every JOB_START / JOB_DONE pair in the job logs (killed and failed attempts
included), the sampler's own t_load / t_gen (meta; covers only the last attempt), samples, generated tokens (sum of
n_tok; F adds the phase-1 thinking tokens), input tokens (prompt + prefix per request, as submitted; prefix caching
means fewer were computed), checker calls (graded rows). Pods: billed hours and dollars from ~/runs/<run>/reap_*.log
and the rates in poll_*.log. No training (0 steps / tokens), no Lean.
Output: out/compute.txt, out/compute.json
"""
import collections
import datetime as dt
import json
import re
from pathlib import Path

from rvt_core import ART, OUT, Tee, iter_gz, load_jsonl, unb64

P = Tee("compute.txt")
RUNS = Path.home() / "runs" / "olmo-transplant"


def ts(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


starts = collections.defaultdict(list)
dones = collections.defaultdict(list)
for f in sorted((ART / "logs").glob("q_*.log")):
    for ln in open(f, errors="replace"):
        m = re.match(r"(JOB_START|JOB_DONE) (\S+) (?:rc=(\d+) )?(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)", ln)
        if m:
            kind, job, rc, t = m.groups()
            (starts if kind == "JOB_START" else dones)[job].append((ts(t), rc, f.name))
res = {}
tot_wall = tot_gen = 0
for job in ("R_dpo", "R_s2300", "C_dpo", "C_s2300", "F_s2300"):
    s = sorted(set(starts[job]))
    d = sorted(set(dones[job]))
    walls = []
    for (t0, _, f0), (t1, rc, f1) in zip(s, d):
        walls.append(((t1 - t0).total_seconds(), rc))
    wall = sum(w for w, _ in walls)
    meta = load_jsonl(ART / "meta" / f"{job}.json")[-1]
    rows = list(iter_gz(ART / "samples" / f"{job}.jsonl.gz"))
    gen = sum(r["n_tok"] for r in rows)
    think = sum(r.get("think_n_tok", 0) for r in rows)
    if job.startswith("F"):
        # phase 1: one n=16 request per (pid, N) on the prompt; phase 2: one request per sample on prompt + prefix
        inp = sum(r["prompt_len"] + r["prefix_len"] for r in rows) + sum(
            {(r["pid"], r["cut"]): r["prompt_len"] for r in rows}.values())
    else:
        seen = {}
        for r in rows:
            seen[r["rid"]] = r["prompt_len"] + r["prefix_len"]
        inp = sum(seen.values())
    graded = sum(1 for _ in open(ART / "graded" / f"{job}.jsonl"))
    cut = sum(r["finish"] == "length" for r in rows)
    P(f"{job}: attempts {[(round(w), rc) for w, rc in walls]} -> wall GPU-s {wall:.0f}; meta t_load {meta.get('t_load_s')} "
      f"t_gen {meta.get('t_gen_s', meta.get('t_phase1_s'))}{'' if not job.startswith('F') else ' + ' + str(meta.get('t_phase2_s'))}; "
      f"samples {len(rows)}; generated tokens {gen + think:,} (answers {gen:,}, F thinking {think:,}); input tokens as "
      f"submitted {inp:,}; meta warm-up tokens {meta.get('warm_tok')}; checker calls {graded}; cut at budget {cut}")
    res[job] = {"wall_s": wall, "attempts": walls, "samples": len(rows), "gen_tokens": gen + think, "answer_tokens": gen,
                "think_tokens": think, "input_tokens": inp, "checker_calls": graded, "meta": {k: meta.get(k) for k in (
                    "t_load_s", "t_gen_s", "t_phase1_s", "t_phase2_s", "gen_tok", "samples", "warm_tok", "input_tok",
                    "requests", "gpus", "tp")}}
    tot_wall += wall
    tot_gen += gen + think
P(f"total job wall GPU-s {tot_wall:.0f} ({tot_wall / 3600:.2f} GPU-h, H200); generated tokens {tot_gen:,}")
# pods
tot_usd = tot_h = 0
for name in ("ot-1", "ot-2"):
    created = (RUNS / f"{name}.created").read_text().strip()
    rate = None
    for ln in open(RUNS / f"poll_{name}.log"):
        m = re.search(r"pod %s ready: .*\$(\d+\.\d+)/h" % name, ln)
        if m:
            rate = float(m.group(1))
    rem = None
    for ln in open(RUNS / f"reap_{name}.log"):
        m = re.search(r"removed %s \((\S+)\) \(([\d.]+)h, \$([\d.]+)\)" % name, ln)
        if m:
            rem = (float(m.group(2)), float(m.group(3)))
    P(f"pod {name}: {created}; rate ${rate}/h; removed after {rem[0]} h, ${rem[1]} (rate x hours = ${rate * rem[0]:.2f})")
    tot_h += rem[0] * (2 if "|2|" in created else 1)
    tot_usd += rem[1]
    res[f"pod_{name}"] = {"created": created, "rate": rate, "hours": rem[0], "usd": rem[1]}
P(f"pods: billed GPU-h {tot_h:.2f}; dollars ${tot_usd:.2f} of the $60 budget")
res["total"] = {"wall_s": tot_wall, "gen_tokens": tot_gen, "billed_gpu_h": tot_h, "usd": tot_usd}
json.dump(res, open(OUT / "compute.json", "w"), indent=1, default=str)
