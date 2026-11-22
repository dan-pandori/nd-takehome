"""Provenance checks for run olmo-ifcurve (reviewer code; no executor module imported).

1. vendored checkers (olmo_ifomega/vendor) = my upstream fetch, byte for byte;
2. olmo_ifomega/problems.jsonl now = the olmo-ifomega bucket copy of 2026-11-04 (before the stored F_* jobs), and every
   used pid's prompt / instruction ids / kwargs = the upstream dataset record;
3. prompt sets: arm A = pids_ifbench - exclusions (mine) vs pids_armA.txt; reach = olmo_ifladder/classify.csv vs
   pids_reach.txt; classes from classify.csv's `reading`; families (prefix of the first instruction id);
4. every job's meta: template sha, vLLM / torch, T, top-p, max_tokens, TP, LoRA, fill_context, stop_after, problems file,
   GPU, rev and seed; JOB_START sha = the Hub commit of the rev (out/hub.json);
5. every new job's prompt_sha256_by_pid vs my own template rendering + tokenisation (DPO tokenizer.json), and every row's
   prompt_tokens vs my length; the stored jobs' rows' prompt_tokens where present;
6. plan specs (pid:n) vs the rows present per (job, pid): complete chunks, chunk numbering.
Writes out/provenance.txt / .json. Python: ~/review/oiffu_venv (tokenizers).
"""
import collections
import filecmp
import hashlib
import json
import re

from tokenizers import Tokenizer

from rvc_core import (ALL_JOBS, ART, CODE, NEW_JOBS, OLD_JOBS, OUT, RAW, SCR, SRC, TOKJ, STEP, Tee, dump, iter_job,
                      load_csv, load_jsonl, sha_int32, upstream_record)

P = Tee("provenance.txt")
res = {}

# ------------------------------------------------------------------ 1. vendored = upstream
UP = SCR / "upstream"
V = RAW / "olmo_ifomega" / "vendor"
pairs = [(V / "ifbench_evaluation_lib.py", UP / "ifbench" / "evaluation_lib.py")]
for sub, up in (("ifbench", UP / "ifbench" / "ifbench"), ("instruction_following_eval", UP / "ife" / "instruction_following_eval")):
    for f in sorted((V / sub).glob("*.py")):
        pairs.append((f, up / f.name))
bad = [str(a.relative_to(RAW)) for a, b in pairs if not (b.exists() and filecmp.cmp(a, b, shallow=False))]
P(f"[1] vendored checker files compared with my upstream fetch: {len(pairs)}; differing or missing: {bad}")
res["vendor_diff"] = bad

# ------------------------------------------------------------------ 2. problems file
cur = RAW / "olmo_ifomega" / "problems.jsonl"
old = SCR / "ifomega" / "problems.jsonl"
h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
P(f"[2] problems.jsonl sha now {h(cur)[:16]} / olmo-ifomega bucket copy (2026-11-04 19:52) {h(old)[:16]} "
  f"identical: {h(cur) == h(old)}")
probs = {r["pid"]: r for r in load_jsonl(cur)}


def norm_kw(kws):
    return [{a: b for a, b in dict(k).items() if b is not None} for k in kws]


# ------------------------------------------------------------------ 3. sets
pidsb = open(RAW / "olmo_ifomega" / "pids_ifbench.txt").read().split()
excl = {r["pid"] for r in load_csv(RAW / "olmo_ifomega" / "exclusions.csv")}
armA_mine = [p for p in pidsb if p not in excl]
armA_ex = open(CODE / "pids_armA.txt").read().split()
P(f"[3] pids_ifbench {len(pidsb)}, exclusions {len(excl)} (of them in pids_ifbench {len(excl & set(pidsb))}); "
  f"arm A mine {len(armA_mine)}; pids_armA.txt {len(armA_ex)}; same set {set(armA_mine) == set(armA_ex)}")
cls = load_csv(RAW / "olmo_ifladder" / "classify.csv")
reach = [r["pid"] for r in cls]
reach_ex = open(CODE / "pids_reach.txt").read().split()
P(f"    reach: classify.csv {len(reach)} ({sum(p.startswith('ifbench') for p in reach)} IFBench), pids_reach.txt "
  f"{len(reach_ex)}, same set {set(reach) == set(reach_ex)}; IFBench reach inside arm A: "
  f"{sum(p in set(armA_mine) for p in reach if p.startswith('ifbench'))}")


def klass(reading):
    s = reading.lower()
    if s.startswith("prompt-elicitable") or s.startswith("prompt-recoverable"):
        return "P"
    if s.startswith("teachable"):
        return "T"
    if s.startswith("neither"):
        return "N"
    return "?" + reading


readings = collections.Counter(r["reading"] for r in cls)
P(f"    classify.csv `reading` values: {dict(readings)}")
CLS = {r["pid"]: klass(r["reading"]) for r in cls}
for c in "PTN":
    ps = sorted((p for p in CLS if CLS[p] == c), key=lambda p: (p.split('_')[0], int(p.split('_')[1])))
    P(f"    class {c}: {len(ps)}: {' '.join(p.replace('ifbench_', 'b').replace('ifeval_', 'e') for p in ps)}")
unk = [p for p in CLS if CLS[p].startswith("?")]
P(f"    unclassified: {unk}")
fam = collections.Counter(probs[p]["instruction_id_list"][0].split(":")[0] if "instruction_id_list" in probs[p]
                          else upstream_record(p)[1]["instruction_id_list"][0].split(":")[0] for p in armA_mine)
P(f"    arm-A families (prefix of the first instruction id): {dict(fam.most_common())}")
res["sets"] = {"armA": armA_mine, "reach": reach, "cls": CLS}

# prompt text vs upstream for every pid any job uses
used = set()
for job in ALL_JOBS:
    for r in iter_job(job):
        used.add(r["pid"])
mism = []
for p in sorted(used):
    task, rec = upstream_record(p)
    pr = probs[p]
    if pr["prompt"] != rec["prompt"]:
        mism.append((p, "prompt"))
    if "instruction_id_list" in pr and list(pr["instruction_id_list"]) != list(rec["instruction_id_list"]):
        mism.append((p, "ids"))
    if "kwargs" in pr and norm_kw(pr["kwargs"]) != norm_kw(rec["kwargs"]):
        mism.append((p, "kwargs"))
    if any(k in pr for k in ("prompt_sample", "messages_sample")):
        mism.append((p, "hinted field"))
P(f"[2b] pids used by any job: {len(used)}; problems.jsonl vs upstream mismatches: {mism}")
res["prompt_mismatch"] = mism
P(f"    pids used outside arm A and reach: {sorted(used - set(armA_mine) - set(reach))[:10]} "
  f"(count {len(used - set(armA_mine) - set(reach))})")

# ------------------------------------------------------------------ 4. metas
hub = json.load(open(OUT / "hub.json"))
HUBSHA = {(v["repo"], v["rev"]): v["sha"] for k, v in hub.items() if isinstance(v, dict) and "repo" in v}
EXP_REV = {n: ("main" if n in ("dpo", "s2300") else f"step_{STEP[n]:04d}") for n in STEP}
REPO = lambda n: "allenai/Olmo-3-32B-Think-DPO" if n == "dpo" else "allenai/Olmo-3.1-32B-Think"
TEMPLATE_SHA = "eba6e269f669706e5c788e370160dad953137f3fa7014fa69d03c7b3ad9f0e72"


def metas_of(job):
    if job in OLD_JOBS:
        return [(job, json.load(open(SRC / "meta" / f"{job}.json")))]
    out = [(job, json.load(open(ART / "meta" / f"{job}.json")))]
    st = ART / "meta" / f"{job}_stage0.json"
    if st.exists():
        out.append((job + "_stage0", json.load(open(st))))
    return out


def job_starts(job):
    p = (SRC / "meta" / f"q_{job}.log") if job in OLD_JOBS else (ART / "logs" / f"q_{job}.log")
    outs = []
    for q in [p] + ([ART / "logs" / f"q_{job}_s0.log"] if job not in OLD_JOBS else []):
        if q.exists():
            outs += [ln.strip() for ln in open(q, errors="replace") if ln.startswith("JOB_START")]
    return outs


P("[4] job metas: job | name rev seed | samples | T top_p max_tok tp | stop_after lora fill | template ok | vllm torch | gpus | JOB_START sha ok")
issues = []
metainfo = {}
for job in ALL_JOBS:
    for mj, m in metas_of(job):
        name, rev = m["name"], m["rev"]
        ok_t = m.get("template_sha256") == TEMPLATE_SHA
        set_ok = (m.get("temperature") == 1.0 and m.get("top_p") == 1.0 and m.get("max_tokens") == 32768 and m.get("tp") == 1
                  and not m.get("lora") and not m.get("fill_context") and m.get("problems") == "olmo_ifomega/problems.jsonl")
        rev_ok = rev == EXP_REV[name]
        shas = [re.search(r"sha=(\w+)", s).group(1) for s in job_starts(job) if "sha=" in s]
        hub_sha = HUBSHA.get((REPO(name), rev))
        sha_ok = (all(s == hub_sha for s in shas) if shas else None)
        line = (f"    {mj:16s} | {name} {rev} {m.get('seed')} | {m.get('samples')} | {m.get('temperature')} {m.get('top_p')} "
                f"{m.get('max_tokens')} {m.get('tp')} | {m.get('stop_after')} {m.get('lora')} {m.get('fill_context')} | "
                f"{ok_t} | {m.get('vllm')} {m.get('torch')} | {m.get('gpus')} | {sha_ok} ({len(shas)} starts)")
        P(line)
        if not (ok_t and set_ok and rev_ok and m.get("vllm") == "0.11.0" and m.get("torch") == "2.8.0+cu128" and sha_ok is not False):
            issues.append(mj)
        metainfo[mj] = {k: m.get(k) for k in ("name", "rev", "seed", "samples", "stop_after", "chunk", "chunk0", "pids",
                                                "gen_tokens", "t_load_s", "t_gen_s", "tok_per_s", "length_cut", "utc_end", "gpus")}
P(f"    metas with a setting / rev / version / sha problem: {issues}")
res["meta_issues"] = issues
seeds = collections.defaultdict(list)
for mj, m in metainfo.items():
    seeds[(m["name"], m["seed"])].append(mj)
P(f"    (checkpoint, engine seed) used by more than one meta: {[(k, v) for k, v in seeds.items() if len(v) > 1]}")

# ------------------------------------------------------------------ 5. prompt ids
tk = Tokenizer.from_file(str(TOKJ))
SYSTEM = "You are a helpful AI assistant."


def my_ids(prompt):
    s = f"<|im_start|>system\n{SYSTEM}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n<think>"
    return tk.encode(s, add_special_tokens=False).ids


MY = {p: my_ids(upstream_record(p)[1]["prompt"]) for p in used}
MYSHA = {p: sha_int32(v) for p, v in MY.items()}
n_ok = n_bad = 0
badp = []
for job in NEW_JOBS:
    for mj, m in metas_of(job):
        for p, s in (m.get("prompt_sha256_by_pid") or {}).items():
            if s == MYSHA[p]:
                n_ok += 1
            else:
                n_bad += 1
                badp.append((mj, p))
        for p, n in (m.get("prompt_tokens_by_pid") or {}).items():
            if n != len(MY[p]):
                badp.append((mj, p, "len"))
P(f"[5] new jobs' prompt_sha256_by_pid vs my rebuild: {n_ok} match, {n_bad} differ {badp[:5]}")
rowlen = collections.Counter()
for job in ALL_JOBS:
    for r in iter_job(job):
        if r.get("prompt_tokens") is None:
            rowlen[(job, "no field")] += 1
        elif r["prompt_tokens"] == len(MY[r["pid"]]):
            rowlen[(job, "ok")] += 1
        else:
            rowlen[(job, "DIFF")] += 1
P(f"    rows' prompt_tokens vs my length: {dict(sorted(rowlen.items()))}")
s = tk.decode(MY["ifeval_2247"], skip_special_tokens=False)
P(f"    template boundary (ifeval_2247, my rebuild, decoded with specials): {s!r}")
res["prompt_sha_ok"] = n_ok
res["prompt_sha_bad"] = badp

# ------------------------------------------------------------------ 6. specs vs rows
P("[6] plan spec vs rows present (job: pids, spec draws, rows, complete chunks, chunks numbered from)")


def spec_of(job):
    pf = None
    for mj, m in metas_of(job)[:1]:  # the job's main meta (stage-0 metas hold the stage-0 spec)
        if m.get("pids", "").startswith("@"):
            pf = RAW / m["pids"][1:]
    if pf is None or not pf.exists():
        return None
    out = {}
    for t in open(pf).read().split():
        a, _, n = t.partition(":")
        out[a] = int(n) if n else None
    return out


specinfo = {}
for job in NEW_JOBS:
    sp = spec_of(job)
    rows = collections.defaultdict(lambda: collections.defaultdict(int))
    for r in iter_job(job):
        rows[r["pid"]][int(r["chunk"])] += 1
    tot = sum(sum(v.values()) for v in rows.values())
    want = sum(sp.values()) if sp else None
    short = {p: (sum(rows[p].values()), n) for p, n in (sp or {}).items() if sum(rows[p].values()) != n}
    extra = sorted(set(rows) - set(sp or {}))
    part = {(p, c): k for p, d in rows.items() for c, k in d.items() if k != 4}
    c0 = collections.Counter(min(d) for d in rows.values())
    P(f"    {job:10s} pids {len(rows):3d} spec {want} rows {tot} | short {short} extra {extra} | chunks != 4 rows {part} | min chunk {dict(c0)}")
    specinfo[job] = {"spec": sp, "rows": {p: dict(d) for p, d in rows.items()}}
res["spec"] = {j: {"want": sum(v['spec'].values()) if v['spec'] else None} for j, v in specinfo.items()}
dump(res, "provenance.json")
dump(specinfo, "specinfo.json")
