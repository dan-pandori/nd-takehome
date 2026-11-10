"""Phase-2 checks of numbers in the executor's write-ups that my phase-1 outputs did not already give (run olmo-ifladder).

 1. handcheck.csv: items, overturned, items with >= 2 reader labels, reader splits; source gate items
 2. held-out slice (Lchk, 8 pool prompts x 16): strict per prompt, main / control
 3. s2300's unhinted strict rate on the 48 (olmo-ifomega fixed phase, my re-grade) — the plain summary's "66 %"
 4. mean thinking tokens per draw on the reach evaluation, lora_main vs lora_ctrl (numbers.md: 6,985 vs 3,613)
 5. Fisher (estimated counts) on the 16 executor-"teachable" prompts under my labels with ifbench_154's rung-4
    item adjudicated gamed (my confirm, phase 2)
 6. rung-1 s2300 break flags for the "neither" prompts in my olmo-iffu review (numbers.md: 284 breaks at rung 1)
 7. rung-1 tokens per draw (olmo-iffu T2 / T2c rows from my olmo-iffu kit)
 8. how the executor's label arose on the executor-gamed / mine-genuine disagreements (its readers vs its overturns)
 9. tokens per draw rung r vs rung r-1 on the same prompts
10. cost of a second training draw for both LoRAs (two trainings + two 48 x 32 evaluations, measured rates)
11-12. the one-way disagreements by binding id, and the addendum rules the executor's notes cite on them
Writes out/phase2_checks.txt.
"""
import collections
import csv
import gzip
import json
import statistics as stx

from rvl_core import KIT, OUT, RAW, SCR, Tee, answer_of, iter_gz, load_csv, upstream_record
from rvl_graders import if_grade

P = Tee("phase2_checks.txt")
WT = KIT.parent.parent
hc = list(csv.DictReader(open(WT / "olmo_ifladder" / "handcheck.csv")))
two = [r for r in hc if len(r["reader_labels"].split()) >= 2]
split = [r for r in two if len({x.split(":")[1] for x in r["reader_labels"].split()}) > 1]
P(f"[1] handcheck.csv items {len(hc)}; overturned {sum(r['overturned'] == 'True' for r in hc)}; items with >= 2 reader "
  f"labels {len(two)}; reader splits among them {len(split)}; jobs {dict(collections.Counter(r['job'] for r in hc))}")
hs = list(csv.DictReader(open(WT / "olmo_ifladder" / "handcheck_src.csv")))
P(f"    handcheck_src.csv items {len(hs)}")
# 2. held-out slice
man = load_csv(WT / "olmo_ifladder" / "train_manifest.csv")
ho = sorted({r["pid"] for r in man if r["role"] == "heldout"})
for job in ("Lchk_main", "Lchk_ctrl"):
    rows = [json.loads(l) for l in gzip.open(OUT / "regrade" / f"{job}.jsonl.gz", "rt")]
    per = {p: sum(r["strict"] for r in rows if r["pid"] == p) for p in ho}
    P(f"[2] {job} held-out slice strict: total {sum(per.values())} of {16 * len(ho)}; {per}")
# 3. s2300 unhinted strict on the 48
prompts = load_csv(WT / "olmo_ifladder" / "prompts.csv")
reach = {r["pid"] for r in prompts if r["set"] == "reach"}
n = s = 0
perp = collections.defaultdict(lambda: [0, 0])
for job in ("F_s2300_ifb", "F_s2300_ife"):
    for r in iter_gz(SCR / "src" / f"{job}.jsonl.gz"):
        if r["pid"] in reach:
            task, rec = upstream_record(r["pid"])
            st = if_grade(task, rec, answer_of(r["text"]))[0]
            n += 1
            s += st
            perp[r["pid"]][0] += st
            perp[r["pid"]][1] += 1
P(f"[3] s2300 unhinted (fixed phase) strict on the 48: {s}/{n} = {s / n:.3f}; mean of per-prompt rates "
  f"{stx.mean(a / b for a, b in perp.values()):.3f}")
lm = [json.loads(l) for l in gzip.open(OUT / "regrade" / "Leval_main.jsonl.gz", "rt")]
lc = [json.loads(l) for l in gzip.open(OUT / "regrade" / "Leval_ctrl.jsonl.gz", "rt")]
lms = [r for r in lm if r["pid"] in reach]
P(f"    lora_main strict on the 48: {sum(r['strict'] for r in lms)}/{len(lms)} = {sum(r['strict'] for r in lms) / len(lms):.3f}")
# 4. mean thinking per draw
for name, rows in (("lora_main", lm), ("lora_ctrl", lc)):
    xs = [r["think_tok"] for r in rows if r["pid"] in reach and r["think_tok"] is not None]
    xa = [r["n_ids"] if r["think_tok"] is None else r["think_tok"] for r in rows if r["pid"] in reach]
    P(f"[4] {name}: mean thinking tokens per draw on the 48: {stx.mean(xs):.0f} (rows with '</think>' {len(xs)}); "
      f"counting a missing '</think>' as the whole response {stx.mean(xa):.0f}")
# 5. Fisher with ifbench_154 adjudicated
O = json.load(open(OUT / "outcomes.json"))
F = {x["pid"]: x for x in O["fisher"]}
ex = {r["pid"]: r for r in csv.DictReader(open(WT / "olmo_ifladder" / "classify.csv"))}
teach = [p for p, r in ex.items() if r["reading"] == "teachable from RL's trajectories"]
P(f"[5] executor-teachable prompts {len(teach)}; Fisher p_est < 0.05 under my labels: "
  f"{sum(F[p]['p_est'] < 0.05 for p in teach)}; failing {[(p, round(F[p]['p_est'], 4)) for p in teach if F[p]['p_est'] >= 0.05]}; "
  f"executor's est. counts / p for the failing four: "
  f"{ {p: (ex[p]['est_genuine_main'], ex[p]['fisher_p_main_gt_ctrl']) for p in ('ifbench_0', 'ifbench_169', 'ifbench_170', 'ifbench_264')} }")
# 6. rung-1 breaks in my olmo-iffu review
oi = json.load(open(KIT.parent / "olmo-iffu-recount" / "out" / "outcomes.json"))
for p in ("ifbench_284", "ifbench_166", "ifbench_188", "ifbench_3", "ifeval_3478", "ifbench_67", "ifbench_268"):
    for t in ("t2", "t2c"):
        if p in oi[t]:
            v = oi[t][p]
            P(f"[6] {p} ({t}): s2300 under the hint genuine {v['s_genuine']} of strict {v['s_strict']} -> breaks {v['breaks']}")
st = {r["pid"]: r for r in load_csv(RAW / "olmo_iffu" / "status.csv")}
P(f"    olmo_iffu/status.csv t2_s2300 for 284: {st['ifbench_284']['t2_s2300']}; 166: {st['ifbench_166']['t2_s2300']}")
# 7. rung-1 tokens per draw (olmo-iffu T2 / T2c, my olmo-iffu kit's re-grade rows)
d = KIT.parent / "olmo-iffu-recount" / "out" / "regrade"
tot = n = 0
for j in ("T2_dpo", "T2c_dpo"):
    for l in gzip.open(d / f"{j}.jsonl.gz", "rt"):
        r = json.loads(l)
        n += 1
        tot += r.get("n_tok") or r.get("n_ids") or 0
P(f"[7] olmo-iffu T2 + T2c dpo draws {n}; tokens per draw {tot / n:.0f}")
# 8. the one-way label disagreements: how the executor's label arose
from rvl_hand import gkey, labels, mech_labels  # noqa: E402

JOBCELL = {"R2_dpo": "R2", "R3_dpo": "R3", "R4_dpo": "R4", "Leval_main": "LM", "Leval_ctrl": "LC",
           "R2_s2300": "S2", "R3_s2300": "S3", "R4_s2300": "S4"}
lab, mech = labels(), mech_labels()
cnt = collections.Counter()
for r in hc:
    k = (JOBCELL[r["job"]], r["pid"], int(r["chunk"]), int(r["i"]))
    g = gkey(k)
    my = "gamed" if k in mech else (lab[g]["label"] if g in lab else None)
    if my is None:
        continue
    if r["final_label"].strip().lower() == "gamed" and my == "genuine":
        rl = [x.split(":")[1] for x in r["reader_labels"].split()]
        kind = ("executor overturned its readers" if r["overturned"] == "True" else
                "executor's readers all gamed" if all(x == "gamed" for x in rl) else "readers split, adjudicated gamed")
        cnt[(k[0], kind)] += 1
tot_ = collections.Counter()
for (c, kind), v in cnt.items():
    tot_[kind] += v
P(f"[8] executor-gamed / mine-genuine disagreements by how the executor's label arose: {dict(tot_)}; by cell {dict(cnt)}")
# 9. tokens per draw on the same prompts, rung r vs rung r-1 (numbers.md compute table: 1.18x / 1.20x / 0.88x)
def tok_by_pid(rows):
    d = collections.defaultdict(list)
    for r in rows:
        d[r["pid"]].append(r.get("n_tok") or r.get("n_ids") or 0)
    return d


R = {}
R["R1"] = tok_by_pid([json.loads(l) for j in ("T2_dpo", "T2c_dpo") for l in
                      gzip.open(KIT.parent / "olmo-iffu-recount" / "out" / "regrade" / f"{j}.jsonl.gz", "rt")] +
                     [json.loads(l) for l in gzip.open(OUT / "regrade" / "R1cal_dpo.jsonl.gz", "rt")])
for r_, job in (("R2", "R2_dpo"), ("R3", "R3_dpo"), ("R4", "R4_dpo")):
    R[r_] = tok_by_pid([json.loads(l) for l in gzip.open(OUT / "regrade" / f"{job}.jsonl.gz", "rt")])
for a, b in (("R2", "R1"), ("R3", "R2"), ("R4", "R3")):
    common = sorted(set(R[a]) & set(R[b]))
    ta = sum(sum(R[a][p]) for p in common) / sum(len(R[a][p]) for p in common)
    tb = sum(sum(R[b][p]) for p in common) / sum(len(R[b][p]) for p in common)
    P(f"[9] tokens per draw on the {len(common)} common prompts: {a} {ta:.0f} vs {b} {tb:.0f} = {ta / tb:.3f}x")
# 10. cost of a second training draw: two trainings + two 48 x 32 evaluations at the measured LoRA-path rates
ART = KIT.parent.parent / "artifacts" / "olmo_ifladder"
est = 0.0
toks = 0
for arm, job in (("main", "Leval_main"), ("ctrl", "Leval_ctrl")):
    rows = [json.loads(l) for l in gzip.open(OUT / "regrade" / f"{job}.jsonl.gz", "rt")]
    rr = [r for r in rows if r["pid"] in reach]
    tpd = sum(r["n_ids"] for r in rr) / len(rr)
    m = json.load(open(ART / "meta" / f"{job}.json"))
    rate = m["gen_tokens"] / m["t_gen_s"]
    lm_ = json.load(open(ART / "meta" / f"lora_{arm}.json"))
    t = 48 * 32 * tpd / rate + lm_["train_secs"] + lm_.get("secs_finish", 0) + m["t_load_s"]
    est += t
    toks += 48 * 32 * tpd
    P(f"[10] {arm}: reach tokens per draw {tpd:.0f}; LoRA-path rate {rate:.0f} tok/s; 48 x 32 draws -> "
      f"{48 * 32 * tpd / 1e6:.2f} M tokens; with training + load {t / 3600:.2f} h")
P(f"[10] total {toks / 1e6:.1f} M tokens, {est / 3600:.2f} GPU-h -> ${est / 3600 * 3.59:.1f} at $3.59/h "
  f"(+ pod set-up / weight fetch, ~0.5 h -> ${(est / 3600 + 0.5) * 3.59:.1f})")
# like-for-like at 64 draws per prompt (the run's evaluation size): the evaluation part doubles
est64 = 0.0
for arm, job in (("main", "Leval_main"), ("ctrl", "Leval_ctrl")):
    rows = [json.loads(l) for l in gzip.open(OUT / "regrade" / f"{job}.jsonl.gz", "rt")]
    rr = [r for r in rows if r["pid"] in reach]
    tpd = sum(r["n_ids"] for r in rr) / len(rr)
    m = json.load(open(ART / "meta" / f"{job}.json"))
    lm_ = json.load(open(ART / "meta" / f"lora_{arm}.json"))
    est64 += 48 * 64 * tpd / (m["gen_tokens"] / m["t_gen_s"]) + lm_["train_secs"] + lm_.get("secs_finish", 0) + m["t_load_s"]
P(f"[10] like-for-like at 64 draws per prompt: {est64 / 3600:.2f} GPU-h -> ${est64 / 3600 * 3.59:.1f} "
  f"(+ ~0.5 h set-up -> ${(est64 / 3600 + 0.5) * 3.59:.1f})")
# 11. the one-way disagreements by binding id; rule citations in the executor's notes
bind = {r["pid"]: r["binding"] for r in prompts}
byid = collections.Counter()
cites = collections.Counter()
for r in hc:
    k = (JOBCELL[r["job"]], r["pid"], int(r["chunk"]), int(r["i"]))
    g = gkey(k)
    my = "gamed" if k in mech else (lab[g]["label"] if g in lab else None)
    if my == "genuine" and r["final_label"].strip().lower() == "gamed":
        byid[bind[r["pid"]]] += 1
        note = (r.get("my_note") or "").lower()
        for rule in ("rule 7", "rule 8", "rule 9", "rule 10", "rule 11", "rule 12"):
            if rule in note:
                cites[rule] += 1
P(f"[11] executor-gamed / mine-genuine by binding id: {dict(byid.most_common())}")
P(f"[12] executor notes on them citing an addendum rule: {dict(cites)}")
# 13. the executor's rule-1 one-sentence screen (gate.py `mech`: no match of [.!?]["')\]]*\s+\S, re-typed here) vs the
#     literal pre-registered test (my fixed rvl_hand.one_sentence) on every reach strict success of a per-sentence id
import re as _re  # noqa: E402

from rvl_core import iter_job  # noqa: E402
from rvl_hand import PER_SENT, SL, one_sentence  # noqa: E402

JOBS_ = {"R2": "R2_dpo", "R3": "R3_dpo", "R4": "R4_dpo", "LM": "Leval_main", "LC": "Leval_ctrl", "S2": "R2_s2300",
         "S3": "R3_s2300", "S4": "R4_s2300"}
diff = collections.Counter()
both = collections.Counter()
for c, job in JOBS_.items():
    want = {(p, ch, i) for p, xs in SL[c].items() if p in reach and set(upstream_record(p)[1]["instruction_id_list"]) & PER_SENT
            for ch, i, _ in xs}
    for r in iter_job(job):
        k = (r["pid"], int(r["chunk"]), int(r["i"]))
        if k not in want:
            continue
        a = answer_of(r["text"]) or ""
        ex1 = not _re.search(r"[.!?][\"')\]]*\s+\S", a)
        lit = one_sentence(a)
        both[(ex1, lit)] += 1
        if ex1 and not lit:
            diff[(c, r["pid"])] += 1
P(f"[13] per-sentence strict successes: (executor screen one-sentence, literal one-sentence) counts {dict(both)}; "
  f"executor screen 'one sentence' but literally more than one: {sum(diff.values())} by (cell, pid) {dict(diff)}")
# 14. compute ratios the review cites (from the metas): training secs_total, check + evaluation tokens and GPU-s
mm = {a: json.load(open(ART / "meta" / f"lora_{a}.json")) for a in ("main", "ctrl")}
jm = {j: json.load(open(ART / "meta" / f"{j}.json")) for j in ("Lchk_main", "Lchk_ctrl", "Leval_main", "Leval_ctrl")}
tr_main = mm["main"]["train_secs"] + mm["main"]["secs_finish"]
tr_ctrl = mm["ctrl"]["train_secs"] + mm["ctrl"]["secs_finish"]
tok_m = jm["Lchk_main"]["gen_tokens"] + jm["Leval_main"]["gen_tokens"]
tok_c = jm["Lchk_ctrl"]["gen_tokens"] + jm["Leval_ctrl"]["gen_tokens"]
gpu_m = sum(jm[j]["t_load_s"] + jm[j]["t_gen_s"] for j in ("Lchk_main", "Leval_main"))
gpu_c = sum(jm[j]["t_load_s"] + jm[j]["t_gen_s"] for j in ("Lchk_ctrl", "Leval_ctrl"))
P(f"[14] lora_main / lora_ctrl: training secs (train + finish) {tr_main:.1f} / {tr_ctrl:.1f} = {tr_main / tr_ctrl:.3f}x "
  f"(train only {mm['main']['train_secs'] / mm['ctrl']['train_secs']:.3f}x); check + evaluation tokens {tok_m} / {tok_c} = "
  f"{tok_m / tok_c:.3f}x; GPU-s (t_load + t_gen) {gpu_m:.1f} / {gpu_c:.1f} = {gpu_m / gpu_c:.3f}x")
# 15. olmo-iffu rung-1 s2300 genuine counts on the DROP60 prompts with contested labels (my olmo-iffu review)
for p in ("ifbench_170", "ifbench_284"):
    for t in ("t2", "t2c"):
        if p in oi[t]:
            v = oi[t][p]
            P(f"[15] {p} ({t}): s2300 under the hint genuine {v['s_genuine']} of strict {v['s_strict']} -> breaks {v['breaks']}; "
              f"olmo_iffu/status.csv t2_s2300 {st[p]['t2_s2300']}")
