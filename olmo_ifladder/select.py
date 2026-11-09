#!/usr/bin/env python3
"""Prompt sets, problem files and source candidates of run olmo-ifladder (pre-registration
preregistration/olmo-ifladder.md). VPS-side, standard library only; deterministic (SEED).

  python3 olmo_ifladder/select.py prompts      -> olmo_ifladder/prompts.csv, problems_{r1cal,r2,r3,plain}.jsonl
  python3 olmo_ifladder/select.py overlap      -> olmo_ifladder/overlap.csv (base-request overlap, see below)
  python3 olmo_ifladder/select.py candidates   -> olmo_ifladder/cand_exemplar.csv, cand_train.csv (what to hand-read)

Evaluation set (58): the 48 instruction-following reach prompts olmo-iffu hinted (42 IFBench = the review's 43 hand-reach
prompts less ifbench_281, 6 IFEval) and olmo-transplant's 10 calibration prompts (IFBench headline prompts both models
solve: dpo >= 8 / 16 and s2300 >= 4 / 8 strict in olmo-ifomega's fixed phase).
Binding constraint: olmo_ifomega/constraints.csv (binding = True) for reach prompts, else the first id.

Base-request overlap: constraint text is masked (a word 8-gram occurring in >= 3 prompts of the benchmark that all
carry one common instruction id); the longest common run of the remaining words (lower-cased, punctuation-stripped
tokens) is computed; a pair with a run >= OVERLAP_WORDS words shares its base request. Sources (exemplars, training and held-out prompts)
must not overlap their target / any evaluation prompt.
"""
import ast
import csv
import gzip
import json
import random
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from interventions import DESCRIPTIONS, DROP60, HINTS, suffix, rung1_suffix  # noqa: E402

SEED = 20261109
OVERLAP_WORDS = 8
O = Path("olmo_ifladder")
OM = Path("artifacts/olmo_ifomega")
L = lambda x: ast.literal_eval(x) if isinstance(x, str) else x  # noqa: E731
PROBS = {r["pid"]: r for r in map(json.loads, open("olmo_ifomega/problems.jsonl"))}
CAP_TOKENS = 16384  # training sequence cap (prompt + response tokens)


def ids_of(pid):
    return list(L(PROBS[pid]["instruction_id_list"]))


def kwargs_of(pid):
    return [{k: v for k, v in d.items() if v is not None} for d in L(PROBS[pid]["kwargs"])]


def eval_sets():
    st = list(csv.DictReader(open("olmo_iffu/status.csv")))
    reach = [r["pid"] for r in st if r["group"] == "ifeval" or (r["pid"].startswith("ifbench") and r["pid"] != "ifbench_281")]
    calib = [r["pid"] for r in csv.DictReader(open("olmo_transplant/prompts.csv")) if r["set"] == "calib"]
    assert len(reach) == 48 and len(calib) == 10
    return reach, calib, {r["pid"]: r for r in st}


def binding():
    b = {}
    for r in csv.DictReader(open("olmo_ifomega/constraints.csv")):
        if r["binding"] == "True":
            b[r["pid"]] = r["instruction_id"]
    return b


# ---------------------------------------------------------------- base-request overlap
# The constraint sentences are worded slightly differently from prompt to prompt ("Each word in your response must
# start with ..."), so they are masked by frequency, not by pattern: a word 8-gram that occurs in >= 3 prompts of the
# same benchmark, all of which carry one common instruction id, or that occurs in a constraint description
# (interventions.DESCRIPTIONS) is constraint text. What is left is base request.
GRAM = 8


def _words(pid):
    return re.findall(r"[a-z0-9']+", PROBS[pid]["prompt"].lower())


MASKED = None


def _masked():
    global MASKED
    if MASKED is None:
        from collections import defaultdict
        df = defaultdict(set)
        W = {p: _words(p) for p in PROBS if PROBS[p]["task"] in ("ifbench", "ifeval")}
        for p, w in W.items():
            for i in range(len(w) - GRAM + 1):
                df[(PROBS[p]["task"],) + tuple(w[i:i + GRAM])].add(p)
        tmpl = {g for g, ps in df.items() if len(ps) >= 3 and set.intersection(*(set(ids_of(q)) for q in ps))}
        # ... and every 8-gram of a constraint description itself (ids with only two prompts, e.g. repeat:repeat_simple)
        for d in DESCRIPTIONS.values():
            dw = re.findall(r"[a-z0-9']+", re.sub(r"\{[^}]*\}", " ", d).lower())
            for t in ("ifbench", "ifeval"):
                tmpl |= {(t,) + tuple(dw[i:i + GRAM]) for i in range(len(dw) - GRAM + 1)}
        MASKED = {}
        for p, w in W.items():
            keep = [True] * len(w)
            for i in range(len(w) - GRAM + 1):
                if (PROBS[p]["task"],) + tuple(w[i:i + GRAM]) in tmpl:
                    for j in range(i, i + GRAM):
                        keep[j] = False
            MASKED[p] = [x if k else f"\x00{p}|{j}" for j, (x, k) in enumerate(zip(w, keep))]
    return MASKED


def base_words(pid):
    """The prompt's words with constraint text replaced by unique placeholders (never matched)."""
    return _masked()[pid]


def lcs_words(a, b):
    wa, wb = base_words(a), base_words(b)
    m = SequenceMatcher(None, wa, wb, autojunk=False).find_longest_match(0, len(wa), 0, len(wb))
    return m.size, " ".join(wa[m.a:m.a + m.size])


# ---------------------------------------------------------------- stored samples
JOB_ORDER = ["F", "E1", "E2", "E3", "C1", "C2", "C3"]


def strict_rows(model, task):
    """{pid: [graded rows, strict successes only, in draw order (phase, job, chunk, i)]} for unhinted olmo-ifomega jobs."""
    out = {}
    for f in sorted(OM.glob("graded/*.jsonl")):
        job = f.stem
        if not job.split("_")[1:2] == [model]:
            continue
        for ln in open(f):
            r = json.loads(ln)
            if r.get("task") != task or not r["strict"]:
                continue
            out.setdefault(r["pid"], []).append(r)
    for v in out.values():
        v.sort(key=lambda r: (JOB_ORDER.index(r["job"].split("_")[0]) if r["job"].split("_")[0] in JOB_ORDER else 9,
                              r["job"], r["chunk"], r["i"]))
    return out


def prior_labels():
    """(job, pid, chunk, i) -> final label from earlier hand gates on unhinted olmo-ifomega samples."""
    lab = {}
    for r in csv.DictReader(open("olmo_ifomega/handcheck.csv")):
        lab[(r["job"], r["pid"], str(r["chunk"]), str(r["i"]))] = (r["final_label"], "olmo_ifomega/handcheck.csv " + r["item"])
    for r in csv.DictReader(open("olmo_transplant/handcheck_src.csv")):
        job, pid, chunk, i = r["key"].split("|")
        if r["final_label"]:
            lab[(job, pid, chunk, i)] = (r["final_label"], "olmo_transplant/handcheck_src.csv " + r["item"])
    return lab


# ---------------------------------------------------------------- commands
def cmd_prompts():
    reach, calib, st = eval_sets()
    b = binding()
    rows = []
    for pid in reach + calib:
        ids = ids_of(pid)
        bid = b.get(pid, ids[0])
        s = st.get(pid, {})
        rows.append({"pid": pid, "set": "reach" if pid in reach else "calib", "task": PROBS[pid]["task"],
                     "ids": " ".join(ids), "binding": bid, "family": bid.split(":")[0], "drop60": pid in DROP60,
                     "r1_dpo": s.get("t2", ""), "r1_s2300": s.get("t2_s2300", ""), "r1_label": s.get("t2_label", ""),
                     "r1_elicited": s.get("t2_label", "").startswith("prompt-elicitable"),
                     "t3_1024": s.get("t3", ""), "iffu_status": s.get("explanation", "")})
        for i in ids:
            assert i in HINTS, (pid, i)
    with open(O / "prompts.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    def rec(pid, **extra):
        p = PROBS[pid]
        r = {k: p[k] for k in ("pid", "task", "key", "prompt", "instruction_id_list", "kwargs")}
        r.update(extra)
        return r

    with open(O / "problems_r1cal.jsonl", "w") as f:
        for pid in calib:
            sfx = rung1_suffix(pid)
            if sfx is not None:
                f.write(json.dumps(rec(pid, prompt_sample=PROBS[pid]["prompt"] + sfx, rung=1)) + "\n")
    for rung in (2, 3):
        with open(O / f"problems_r{rung}.jsonl", "w") as f:
            for pid in reach + calib:
                f.write(json.dumps(rec(pid, prompt_sample=PROBS[pid]["prompt"] + suffix(pid, ids_of(pid), rung),
                                       rung=rung)) + "\n")
    print(f"prompts.csv {len(rows)} rows; r1cal {sum(1 for _ in open(O / 'problems_r1cal.jsonl'))}; "
          f"drop60 in set {sum(r['drop60'] for r in rows)}; r1 elicited {sum(r['r1_elicited'] for r in rows)}")


def cmd_overlap(pairs_from=None):
    """overlap.csv: every (source, evaluation) pair with a common base-request run >= 5 words (>= OVERLAP_WORDS = shared)."""
    reach, calib, _ = eval_sets()
    ev = reach + calib
    src = sorted({r["source"] for f in ("cand_exemplar.csv", "cand_train.csv") if (O / f).exists()
                  for r in csv.DictReader(open(O / f))} - set(ev)) if pairs_from is None else pairs_from
    out = []
    for s in src:
        for e in ev:
            if PROBS[s]["task"] != PROBS[e]["task"]:
                continue
            n, txt = lcs_words(s, e)
            if n >= 5:
                out.append({"source": s, "eval": e, "lcs_words": n, "shared": n >= OVERLAP_WORDS, "run": txt[:200]})
    for i, a in enumerate(ev):  # evaluation prompts among themselves (exemplars may come from other evaluation prompts)
        for e in ev[i + 1:]:
            if PROBS[a]["task"] != PROBS[e]["task"]:
                continue
            n, txt = lcs_words(a, e)
            if n >= 5:
                out.append({"source": a, "eval": e, "lcs_words": n, "shared": n >= OVERLAP_WORDS, "run": txt[:200]})
    with open(O / "overlap.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["source", "eval", "lcs_words", "shared", "run"])
        w.writeheader()
        w.writerows(out)
    print(f"overlap.csv: {len(out)} pairs with a run >= 5 words, {sum(r['shared'] for r in out)} >= {OVERLAP_WORDS}")
    return out


def shares_base(a, b):
    return lcs_words(a, b)[0] >= OVERLAP_WORDS


def cmd_candidates():
    """Candidate source prompts and the stored strict successes to hand-read for them (draw order)."""
    reach, calib, _ = eval_sets()
    ev = reach + calib
    b = binding()
    rng = random.Random(SEED)
    lab = prior_labels()
    s23 = {t: strict_rows("s2300", t) for t in ("ifbench", "ifeval")}
    dpo = strict_rows("dpo", "ifbench")
    ok = lambda r: r["finish"] == "stop"  # noqa: E731

    # exemplars (rung 4): per target, ranked candidates c != t of the same benchmark with a stored s2300 strict success
    ex_rows = []
    for t in ev:
        task = PROBS[t]["task"]
        idt = ids_of(t)
        bid = b.get(t, idt[0])
        cands = []
        for c in PROBS:
            if c == t or PROBS[c]["task"] != task or c == "ifbench_281":
                continue
            idc = ids_of(c)
            fam = bid.split(":")[0]
            if bid in idc:
                cls = 0 if sorted(set(idc)) == sorted(set(idt)) else 1
            elif any(i.split(":")[0] == fam for i in idc):
                cls = 2  # fallback: same family (id prefix), used only to fill the two slots
            else:
                continue
            succ = [r for r in s23[task].get(c, []) if ok(r)]
            if not succ:
                continue
            outside = c not in ev
            cands.append((cls, 0 if outside else 1, rng.random(), c, succ))
        cands.sort()
        k = 0
        for cls, out, _, c, succ in cands:
            if shares_base(c, t):
                continue
            k += 1
            for j, r in enumerate(succ):
                key = (r["job"], c, str(r["chunk"]), str(r["i"]))
                pl = lab.get(key, ("", ""))
                ex_rows.append({"target": t, "rank": k, "source": c, "match": ["same ids", "binding id", "family"][cls],
                                "outside_eval": out == 0,
                                "job": r["job"], "chunk": r["chunk"], "i": r["i"], "draw_rank": j,
                                "prior_label": pl[0], "prior_src": pl[1]})
    with open(O / "cand_exemplar.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(ex_rows[0]))
        w.writeheader()
        w.writerows(ex_rows)

    # training (LoRA): IFBench prompts outside the evaluation set and ifbench_281, both models with a stored strict
    # success that finished; ids taken in order of how many rung-1-unelicited reach prompts carry them, then all reach
    # prompts, then id name; candidates within an id in seeded order
    from collections import Counter
    st = {r["pid"]: r for r in csv.DictReader(open(O / "prompts.csv"))}
    evid = Counter(i for t in reach for i in set(ids_of(t)))
    unel = Counter(i for t in reach if st[t]["r1_elicited"] == "False" for i in set(ids_of(t)))
    order = sorted(evid, key=lambda i: (-unel[i], -evid[i], i))
    pool = {}
    for c in PROBS:
        if PROBS[c]["task"] != "ifbench" or c in ev or c == "ifbench_281":
            continue
        a = [r for r in s23["ifbench"].get(c, []) if ok(r)]
        d = [r for r in dpo.get(c, []) if ok(r)]
        if a and d and not any(shares_base(c, e) for e in ev):
            pool[c] = (a, d)
    tr_rows = []
    for iid in order:
        cs = sorted(c for c in pool if iid in ids_of(c))
        rng2 = random.Random(f"{SEED}-{iid}")
        rng2.shuffle(cs)
        for rank, c in enumerate(cs):
            a, d = pool[c]
            for who, rs, nmax in (("s2300", a, 2), ("dpo", d, 4)):
                for j, r in enumerate(rs[:nmax]):
                    key = (r["job"], c, str(r["chunk"]), str(r["i"]))
                    pl = lab.get(key, ("", ""))
                    tr_rows.append({"id": iid, "id_rank": order.index(iid), "cand_rank": rank, "source": c,
                                    "ids": " ".join(ids_of(c)), "model": who, "job": r["job"], "chunk": r["chunk"],
                                    "i": r["i"], "n_tok": r["n_tok"], "draw_rank": j, "prior_label": pl[0],
                                    "prior_src": pl[1]})
    with open(O / "cand_train.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(tr_rows[0]))
        w.writeheader()
        w.writerows(tr_rows)
    print(f"cand_exemplar.csv {len(ex_rows)} rows ({len({r['target'] for r in ex_rows})} targets); "
          f"cand_train.csv {len(tr_rows)} rows ({len({r['source'] for r in tr_rows})} prompts, "
          f"{len({r['id'] for r in tr_rows})} ids); id order {order}")


if __name__ == "__main__":
    {"prompts": cmd_prompts, "overlap": cmd_overlap, "candidates": cmd_candidates}[sys.argv[1]]()
