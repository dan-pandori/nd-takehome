"""Provenance checks for run olmo-transplant (reviewer's own code; no executor module imported).

1. problems: the run's IFBench prompts vs my upstream fetch (prompt, instruction ids, kwargs), by key.
2. prompt sets: reach-41 vs the olmo-ifomega review's 43; brief20; required 6; calibration criteria are checked in
   rvt_sets.py (needs the re-grade).
3. traces: every trace's stored sample (my bucket copy) -> my sha256 of the ids, my `</think>` position, closing ids,
   my pre-draft cut; rl reach traces genuine in olmo_ifomega/handcheck.csv; counts; thinking-length statistics.
4. requests: my own enumeration of the pre-registered requests from the trace rows, each prefix rebuilt from the
   stored ids and compared with the request file's prefix.
5. samples: my prompt ids (template text written out by me, tokenised with `tokenizers`) vs the job meta's; every
   sample row's input_sha256 vs sha256(my prompt ids + request prefix); 8 rows per request; budgets; F rows' prefixes.
6. a seeded sample of decoded boundaries for reading by hand (out/boundary_sample.txt).
Outputs: out/provenance.txt, out/provenance.json, out/traces_mine.csv, out/boundary_sample.txt
"""
import collections
import csv
import json
import random
import re
import statistics
import subprocess

from tokenizers import Tokenizer

from rvt_core import ART, OUT, RAW, SCR, TOKJ, Pieces, Tee, iter_gz, load_jsonl, sha_int32, sha_json, unb64, wsnorm

P = Tee("provenance.txt")
pc = Pieces()
CLOSE = [524, 27963, 1363]
NL = 198
CUTS = [1024, 2048, 4096, 8192, 16384]
SYSTEM = "You are a helpful AI assistant."
res = {}


def q(xs, f):
    """quantile by linear interpolation (numpy default) on sorted xs"""
    xs = sorted(xs)
    pos = f * (len(xs) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


# ------------------------------------------------------------------ 1. problems vs upstream
up = {str(json.loads(l)["key"]): json.loads(l) for l in open(SCR / "upstream" / "ifbench" / "IFBench_test.jsonl")}
prob = {}
for ln in open(RAW / "olmo_ifomega" / "problems.jsonl"):
    r = json.loads(ln)
    if r["task"] == "ifbench":
        prob[r["pid"]] = r
prompts = list(csv.DictReader(open(RAW / "olmo_transplant" / "prompts.csv")))
used = [p["pid"] for p in prompts if p["set"] in ("reach", "calib")]
bad = []
for pid in used:
    pr, u = prob[pid], up[str(prob[pid]["key"])]
    if pid != f"ifbench_{u['key']}":
        bad.append((pid, "pid/key"))
    if pr["prompt"] != u["prompt"] or pr["instruction_id_list"] != u["instruction_id_list"] or \
            [{a: b for a, b in k.items() if b is not None} for k in pr["kwargs"]] != \
            [{a: b for a, b in k.items() if b is not None} for k in u["kwargs"]]:
        bad.append((pid, "content"))
P(f"[1] problems: {len(used)} used IFBench prompts compared with upstream IFBench_test.jsonl @ cd189a9c: "
  f"{len(bad)} differ {bad[:5]}")
res["problems_differ"] = bad

# ------------------------------------------------------------------ 2. prompt sets
rev = subprocess.run(["git", "-C", str(RAW.parent.parent / "work" / "olmo-transplant"), "show",
                      "HEAD:review_olmo-ifomega.md"], capture_output=True, text=True).stdout
line = [l for l in rev.splitlines() if l.startswith("IFBench hand-reach prompts (strict mapping, 43)")][0]
reach43 = re.findall(r"`(ifbench_\d+)`", line)
sets = collections.defaultdict(list)
for p in prompts:
    sets[p["set"]].append(p["pid"])
reach = sets["reach"]
P(f"[2] review's list: {len(reach43)} prompts; run sets {dict((k, len(v)) for k, v in sets.items())}")
P(f"    reach-41 = 43 minus {sorted(set(reach43) - set(reach))}; extra in run reach: {sorted(set(reach) - set(reach43))};"
  f" reach_no_trace = {sets['reach_no_trace']}")
hc = list(csv.DictReader(open(RAW / "olmo_ifomega" / "handcheck.csv")))
gen_by_pid = collections.Counter(r["pid"] for r in hc if r["model"] == "s2300" and r["final_label"] == "genuine")
P(f"    s2300 genuine final labels in olmo_ifomega/handcheck.csv: 226 -> {gen_by_pid.get('ifbench_226', 0)}, "
  f"252 -> {gen_by_pid.get('ifbench_252', 0)}; reach-41 prompts with 0 genuine: "
  f"{[p for p in reach if gen_by_pid.get(p, 0) == 0]}")
fam = {}
for pid in used:
    fam[pid] = prob[pid]["instruction_id_list"][0].split(":")[0]
fam_reach = collections.Counter(fam[p] for p in reach)
P(f"    reach-41 families (prefix of first instruction id): {dict(fam_reach.most_common())}")
fam_run = {p["pid"]: p["family"] for p in prompts}
P(f"    family column vs mine: {sum(fam_run[p] != fam[p] for p in used)} differ")
b20 = [p["pid"] for p in prompts if p["brief20"] == "True"]
req6 = [p["pid"] for p in prompts if p["required6"] == "True"]
st = {r["pid"]: r for r in csv.DictReader(open(RAW / "olmo_iffu" / "status.csv"))}
surv = [p for p, r in st.items() if p.startswith("ifbench") and r["t3"] == "0/1024"]
not_hint = [p for p in surv if "prompt-elicitable" not in st[p]["explanation"]]
P(f"    brief20: {len(b20)} prompts, all in reach-41: {set(b20) <= set(reach)}; families "
  f"{dict(collections.Counter(fam[p] for p in b20).most_common())}")
P(f"    olmo-iffu: survived 1,024 dpo draws: {sorted(surv, key=lambda s: int(s.split('_')[1]))}; of them not "
  f"prompt-elicitable: {sorted(not_hint, key=lambda s: int(s.split('_')[1]))}; run's required6 = {req6}; "
  f"equal: {sorted(not_hint) == sorted(req6)}; all in brief20: {set(req6) <= set(b20)}")
res.update({"reach43": reach43, "reach41": reach, "brief20": b20, "required6": req6, "calib": sets["calib"],
            "family": fam})

# ------------------------------------------------------------------ 3. traces
traces = list(csv.DictReader(open(RAW / "olmo_transplant" / "traces.csv")))
need = {(t["job"], t["pid"], int(t["chunk"]), int(t["i"])) for t in traces}
stored = {}
for job in sorted({k[0] for k in need}):
    for r in iter_gz(SCR / "src" / f"{job}.jsonl.gz"):
        k = (job, r["pid"], r["chunk"], r["i"])
        if k in need:
            stored[k] = r
P(f"[3] traces.csv: {len(traces)} rows, {collections.Counter((t['set'], t['kind']) for t in traces)}; "
  f"stored rows found in my bucket copies: {len(stored)} / {len(need)} (distinct)")


def draft_cut(ids, k, answer):
    """My pre-draft cut: index t of the token holding the first character of the first occurrence of the answer's
    first 40 whitespace-collapsed characters inside the thinking content ids[:k-3]; None if absent (or the
    collapsed answer is shorter than 8 characters)."""
    a = wsnorm(answer)[:40]
    if len(a) < 8:
        return None
    pieces = [pc.piece[i] for i in ids[:k - 3]]
    # character -> token map over the decoded thinking (decode token by token on a byte stream)
    raw = b"".join(pieces)
    txt = raw.decode("utf-8", errors="replace")
    # collapsed text with offsets back into txt
    col, off, prev = [], [], False
    for j, ch in enumerate(txt):
        if ch.isspace():
            if not prev and col:
                col.append(" ")
                off.append(j)
            prev = True
        else:
            col.append(ch)
            off.append(j)
            prev = False
    h = "".join(col)
    m = h.find(a)
    if m < 0:
        return None
    byte_pos = len(txt[:off[m]].encode("utf-8", errors="replace"))
    acc = 0
    for t, p in enumerate(pieces):
        if acc + len(p) > byte_pos:
            return t
        acc += len(p)
    return None


mine = []
issues = collections.Counter()
before_close_nl = 0
for t in traces:
    s = stored[(t["job"], t["pid"], int(t["chunk"]), int(t["i"]))]
    ids = unb64(s["ids"])
    if sha_json(ids) != t["ids_sha256"]:
        issues["ids_sha"] += 1
    if pc.text(ids) != s["text"]:
        issues["text!=decode"] += 1
    k = pc.first_close(ids)
    if k is None:
        issues["no_close"] += 1
        continue
    if k != int(t["think_k"]):
        issues["think_k"] += 1
    if sha_json(ids[:k]) != t["prefix_sha256"]:
        issues["prefix_sha"] += 1
    if ids[k - 3:k - 1] != [524, 27963] or ids[k - 1] not in (1363, 397):
        issues["close_ids"] += 1
    before_close_nl += pc.piece[ids[k - 4]].endswith(b"\n")
    if int(t["c"]) != k - 3:
        issues["c"] += 1
    if s["model"] != t["src_model"] or int(t["n_tok"]) != len(ids):
        issues["model/n_tok"] += 1
    ans = s["text"].split("</think>", 1)[1].strip()
    d = draft_cut(ids, k, ans) if t["kind"] == "rl" else None
    run_d = int(t["draft_k"]) if t["draft_k"] else None
    if d != run_d:
        issues["draft_k"] += 1
    mine.append({"trace": t["trace"], "set": t["set"], "pid": t["pid"], "kind": t["kind"], "job": t["job"],
                 "chunk": t["chunk"], "i": t["i"], "k": k, "c": k - 3, "draft": d, "run_draft": run_d,
                 "close": ids[k - 1], "n_tok": len(ids)})
P(f"    per-trace issues (ids sha, text==decode, my </think> position, prefix sha, closing ids, c, model, draft cut): "
  f"{dict(issues) or 'none'}")
P(f"    token before `</` ends in a newline: {before_close_nl} / {len(mine)}; closing token counts "
  f"{dict(collections.Counter(m['close'] for m in mine))}")

# rl reach traces: genuine in olmo_ifomega/handcheck.csv, at most 4, all of them if <= 4 available
genkeys = collections.defaultdict(set)
for r in hc:
    if r["model"] == "s2300" and r["final_label"] == "genuine" and r["job"] in ("F_s2300_ifb", "C1_s2300_ifb",
                                                                               "C2_s2300_ifb"):
        genkeys[r["pid"]].add((r["job"], r["pid"], int(r["chunk"]), int(r["i"])))
tr_by = collections.defaultdict(list)
for t in traces:
    tr_by[(t["set"], t["pid"], t["kind"])].append(t)
bad_rl, short = [], []
for pid in reach:
    ts = tr_by[("reach", pid, "rl")]
    keys = {(t["job"], t["pid"], int(t["chunk"]), int(t["i"])) for t in ts}
    if not keys <= genkeys[pid]:
        bad_rl.append(pid)
    if len(ts) != min(4, len(genkeys[pid])):
        short.append((pid, len(ts), len(genkeys[pid])))
n_rl = sum(len(tr_by[("reach", p, "rl")]) for p in reach)
P(f"    reach rl traces: {n_rl}; not genuine-labelled: {bad_rl}; count != min(4, available): {short}; "
  f"per-prompt counts {dict(collections.Counter(len(tr_by[('reach', p, 'rl')]) for p in reach))}")
# dpo traces: F_dpo_ifb rows; strictness checked in rvt_sets.py against my re-grade
nd = collections.Counter(len(tr_by[(st_, p, "dpo")]) for st_ in ("reach", "calib") for p in sets[st_])
P(f"    dpo traces per prompt (reach + calib): {dict(nd)}; jobs {collections.Counter(t['job'] for t in traces if t['kind'] == 'dpo')}")

rlr = [m for m in mine if m["set"] == "reach" and m["kind"] == "rl"]
dpr = [m for m in mine if m["set"] == "reach" and m["kind"] == "dpo"]
cs = [m["c"] for m in rlr]
P(f"    rl reach thinking c = think_k - 3: median {statistics.median(cs)}, mean {statistics.mean(cs):.0f}, "
  f"max {max(cs)}, min {min(cs)}; think_k median {statistics.median([m['k'] for m in rlr])}")
P(f"    dpo reach thinking c: median {statistics.median([m['c'] for m in dpr])}, think_k median "
  f"{statistics.median([m['k'] for m in dpr])}")
cut_counts = {N: sum(m["c"] > N for m in rlr) for N in CUTS}
P(f"    reach rl traces cut (c > N): {cut_counts}")
dr = [m for m in rlr if m["draft"] is not None]
fr = [m["draft"] / m["c"] for m in dr]
P(f"    pre-draft: {len(dr)} / {len(rlr)} reach rl traces contain the answer opening; position draft/c median "
  f"{statistics.median(fr):.3f}, deciles 10% {q(fr, 0.1):.3f} 90% {q(fr, 0.9):.3f}; draft == 0: "
  f"{sum(m['draft'] == 0 for m in dr)}")
P(f"    my draft cut vs traces.csv draft_k: {sum(m['draft'] != m['run_draft'] for m in mine)} differ")
cal_rl = [m for m in mine if m["set"] == "calib" and m["kind"] == "rl"]
P(f"    calib rl traces: {len(cal_rl)}, with draft {sum(m['draft'] is not None for m in cal_rl)}; per prompt "
  f"{dict(collections.Counter(m['pid'] for m in cal_rl))}")
res["trace_issues"] = dict(issues)
res["cut_counts_reach"] = cut_counts
res["draft_reach"] = len(dr)
with open(OUT / "traces_mine.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(mine[0].keys()))
    w.writeheader()
    w.writerows(mine)

# ------------------------------------------------------------------ 4. requests
mine_by = {m["trace"]: m for m in mine}
idsof = {m["trace"]: unb64(stored[(m["job"], m["pid"], int(m["chunk"]), int(m["i"]))]["ids"]) for m in mine}


def closing(last):
    return ([] if pc.piece[last].endswith(b"\n") else [NL]) + CLOSE


def expected(st, w):
    """{rid: (pid, cond, cut, trace, prefix)} by the pre-registration."""
    full = {"dpo": {"rl": "T1", "dpo": "T4"}, "s2300": {"rl": "T2", "dpo": "T3"}}[w]
    e = {}
    for m in mine:
        if m["set"] != st:
            continue
        ids = idsof[m["trace"]]
        e[f"{m['trace']}|full"] = (m["pid"], full[m["kind"]], "full", m["trace"], ids[:m["k"]])
        if m["kind"] != "rl":
            continue
        for N in CUTS:
            if m["c"] > N:
                e[f"{m['trace']}|B{N}"] = (m["pid"], "B", N, m["trace"], ids[:N] + closing(ids[N - 1]))
        if m["draft"] is not None:
            d = m["draft"]
            e[f"{m['trace']}|P"] = (m["pid"], "P", "P", m["trace"], ids[:d] + (closing(ids[d - 1]) if d else [NL] + CLOSE))
    t0 = [NL] + CLOSE  # after the template's '<think>' ('>' does not end in a newline)
    for pid in sets[st]:
        for j in range(4):
            e[f"{pid}|T0|{j}"] = (pid, "T0", 0, "", t0)
    return e


reqs = {}
for w in ("dpo", "s2300"):
    for st in ("reach", "calib"):
        rows = list(iter_gz(ART / "requests" / f"{w}_{st}.jsonl.gz"))
        e = expected(st, w)
        got = {r["rid"]: r for r in rows}
        miss = sorted(set(e) - set(got))
        extra = sorted(set(got) - set(e))
        badp = []
        for rid, r in got.items():
            reqs[(w, rid)] = r
            if rid not in e:
                continue
            pid, cond, cut, trace, pre = e[rid]
            if (r["pid"], r["cond"], r["cut"], r["trace"], r["n"]) != (pid, cond, cut, trace, 8) or \
                    unb64(r["prefix"]) != pre or r["prefix_len"] != len(pre) or r["writer"] != w:
                badp.append(rid)
        P(f"[4] requests {w}_{st}: {len(rows)} rows (expected {len(e)}), missing {len(miss)} {miss[:3]}, extra "
          f"{len(extra)} {extra[:3]}, prefix/field mismatches {len(badp)} {badp[:3]}; conds "
          f"{dict(collections.Counter(r['cond'] for r in rows))}; samples {sum(r['n'] for r in rows)}")
        res[f"requests_{w}_{st}"] = {"rows": len(rows), "expected": len(e), "missing": len(miss), "extra": len(extra),
                                     "mismatch": len(badp)}

# ------------------------------------------------------------------ 5. prompt ids and sample input hashes
tk = Tokenizer.from_file(str(TOKJ))


def my_prompt_ids(pid):
    u = up[str(prob[pid]["key"])]
    text = (f"<|im_start|>system\n{SYSTEM}<|im_end|>\n<|im_start|>user\n{u['prompt']}<|im_end|>\n"
            f"<|im_start|>assistant\n<think>")
    return tk.encode(text, add_special_tokens=False).ids


myp = {pid: my_prompt_ids(pid) for pid in used}
P(f"[5] my prompt ids: last tokens of one prompt {myp[used[0]][-6:]} -> {pc.text(myp[used[0]][-6:], False)!r}; "
  f"'<think>' last token is 29? {myp[used[0]][-1] == 29} ({pc.piece[29]!r})")
metas = {}
for job in ("R_dpo", "R_s2300", "C_dpo", "C_s2300", "F_s2300"):
    ms = load_jsonl(ART / "meta" / f"{job}.json")
    metas[job] = ms[-1]
    pi = {p: unb64(v) for p, v in ms[-1]["prompt_ids"].items()}
    nd = [p for p, v in pi.items() if v != myp[p]]
    P(f"    {job}: meta lines {len(ms)}; prompt ids for {len(pi)} pids; differ from mine: {nd}")
writer_of = {"R_dpo": "dpo", "R_s2300": "s2300", "C_dpo": "dpo", "C_s2300": "s2300"}
seen_rid = collections.Counter()
for job, w in writer_of.items():
    cnt = collections.Counter()
    probs_ = collections.Counter()
    per_rid = collections.defaultdict(set)
    for r in iter_gz(ART / "samples" / f"{job}.jsonl.gz"):
        q_ = reqs.get((w, r["rid"]))
        if q_ is None:
            probs_["no_request"] += 1
            continue
        pre = unb64(q_["prefix"])
        x = myp[r["pid"]] + pre
        if sha_int32(x) != r["input_sha256"]:
            probs_["input_sha"] += 1
        if (r["pid"], r["cond"], r["cut"], r["trace"], r["writer"]) != (q_["pid"], q_["cond"], q_["cut"], q_["trace"], w):
            probs_["fields"] += 1
        if r["prefix_len"] != len(pre) or r["budget"] != 32768 - len(pre) or r["prompt_len"] != len(myp[r["pid"]]):
            probs_["lens"] += 1
        ids = unb64(r["ids"])
        if r["n_tok"] != len(ids):
            probs_["n_tok"] += 1
        if r["finish"] == "length" and r["n_tok"] != r["budget"]:
            probs_["length_not_at_budget"] += 1
        if r["finish"] == "stop" and (not ids or ids[-1] != 100257):
            probs_["stop_without_eos"] += 1
        per_rid[r["rid"]].add(r["i"])
        cnt[r["cond"]] += 1
    bad8 = [rid for rid, s in per_rid.items() if s != set(range(8))]
    nreq = sum(1 for (w_, rid) in reqs if w_ == w and reqs[(w_, rid)]["pid"] in (sets["reach"] if job[0] == "R" else sets["calib"]))
    P(f"    {job}: rows by cond {dict(cnt)}; requests with rows {len(per_rid)} of {nreq}; requests without i = 0..7: "
      f"{len(bad8)}; problems {dict(probs_) or 'none'}")
    res[f"samples_{job}"] = {"rows": sum(cnt.values()), "problems": dict(probs_), "bad8": len(bad8)}

# F rows: phase-1 thinking -> prefix
fprob = collections.Counter()
fcnt = collections.Counter()
for r in iter_gz(ART / "samples" / "F_s2300.jsonl.gz"):
    th = unb64(r["think_ids"])
    pre = unb64(r["prefix_ids"])
    k = pc.first_close(th)
    if k is not None:
        want, nat = th[:k], True
    else:
        t2 = [x for x in th if x != 100257]
        want, nat = t2 + closing(t2[-1]) if t2 else [NL] + CLOSE, False
    if pre != want:
        fprob["prefix"] += 1
    if r["natural"] != nat:
        fprob["natural_flag"] += 1
    if len(th) > r["cut"] or r["think_n_tok"] != len(th):
        fprob["think_len"] += 1
    if sha_int32(myp[r["pid"]] + pre) != r["input_sha256"]:
        fprob["input_sha"] += 1
    if r["budget"] != 32768 - len(pre) or r["prefix_len"] != len(pre):
        fprob["budget"] += 1
    if r["finish"] == "length" and r["n_tok"] != r["budget"]:
        fprob["length_not_at_budget"] += 1
    fcnt[(r["pid"], r["cut"])] += 1
    fcnt[("natural", r["cut"])] += nat
P(f"    F_s2300: rows {sum(v for k, v in fcnt.items() if k[0] != 'natural')}; per (pid, N) counts "
  f"{sorted(set(v for k, v in fcnt.items() if k[0] != 'natural'))}; natural </think> by N "
  f"{ {k[1]: v for k, v in fcnt.items() if k[0] == 'natural'} }; problems {dict(fprob) or 'none'}")
P(f"    F meta: seed {metas['F_s2300']['seed']}, pids {metas['F_s2300'].get('pids')}, budgets "
  f"{metas['F_s2300'].get('budgets')}, natural_end {metas['F_s2300'].get('natural_end')}")
for job, m in metas.items():
    P(f"    meta {job}: seed {m.get('seed')} rev {m.get('rev')} vllm {m.get('vllm')} gpus {m.get('gpus')} tp {m.get('tp')} "
      f"T {m.get('temperature')} top_p {m.get('top_p')} cap {m.get('response_cap')} groups {m.get('groups_in_flight')} "
      f"samples {m.get('samples')} gen_tok {m.get('gen_tok', m.get('answer_gen_tokens'))} t_gen {m.get('t_gen_s')} "
      f"max_mem {m.get('max_mem_alloc_gb')} end {m.get('utc_end')}")

# ------------------------------------------------------------------ 6. boundary sample for reading
rng = random.Random(20261108)
picks = collections.defaultdict(list)
for job, w in writer_of.items():
    for r in iter_gz(ART / "samples" / f"{job}.jsonl.gz"):
        if r["i"] == 0:
            picks[(job, r["cond"])].append(r)
with open(OUT / "boundary_sample.txt", "w") as f:
    for key in sorted(picks):
        for r in rng.sample(picks[key], min(2, len(picks[key]))):
            pre = unb64(reqs[(writer_of[key[0]], r["rid"])]["prefix"])
            x = myp[r["pid"]] + pre
            ans = unb64(r["ids"])
            pl = len(myp[r["pid"]])
            f.write(f"===== {key[0]} {r['rid']} cond={r['cond']} cut={r['cut']} prompt_len={pl} prefix_len={len(pre)}\n")
            f.write(f"--- prompt tail : {pc.text(x[pl - 8:pl], False)!r}\n")
            f.write(f"--- prefix head : {pc.text(pre[:16], False)!r}\n")
            f.write(f"--- prefix tail : {pc.text(pre[-14:], False)!r}  ids {pre[-5:]}\n")
            f.write(f"--- answer head : {pc.text(ans[:24], False)!r}\n")
            f.write(f"--- answer tail : {pc.text(ans[-6:], False)!r} finish={r['finish']}\n")
P("[6] boundary sample written to out/boundary_sample.txt")
json.dump(res, open(OUT / "provenance.json", "w"), indent=1, default=str)
