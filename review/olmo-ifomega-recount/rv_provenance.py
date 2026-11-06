"""Provenance of the 650 evaluation prompts (and the 104 Stage-0 prompts) against the pinned datasets, my own fetch
(~/review/oif_rv/data, fetch.sh). Checks, each printed with its count:
  IFBench: every prompt / instruction list / kwargs equals the IFBench repo jsonl @ cd189a9c (the checker's input) and
           the HF parquet allenai/IFBench_test @ ed7c1245 (None kwargs dropped, float ints compared numerically).
  IFEval : rows equal google/IFEval @ 966cd895; the 150 + 40 subset is the seeded draw the pre-registration names
           (random.Random(int(sha256('20261104|ifeval')[:16], 16)).sample over the key-sorted 541).
  OMEGA  : every problem is an omega-explorative @ b04ae8d4 row of its family / split (prompt = text minus the boxed
           suffix, answer = ground_truth); family eligibility (>= 100 distinct RL prompts) and the seeded family and
           problem draws re-derived with my own normaliser; pool filters re-checked (RL prompt, OMEGA train /
           compositional / transformative, same-split duplicates, single-letter renaming).
Output: out/provenance.txt"""
import hashlib
import json
import os
import random
import re
from collections import Counter, defaultdict

import pyarrow.parquet as pq

import rv_core as C

D = os.path.join(C.BIG, "data")
SUFFIX = "\n\nPresent the answer in LaTex format: \\boxed{Your answer}"
lines = []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    lines.append(s)


def rng_for(*keys):
    h = hashlib.sha256(("|".join(map(str, (20261104,) + keys))).encode()).hexdigest()
    return random.Random(int(h[:16], 16))


def same_kwargs(a, b):
    if a.keys() != b.keys():
        return False
    for k in a:
        x, y = a[k], b[k]
        if isinstance(x, (int, float)) and isinstance(y, (int, float)) and not isinstance(x, bool):
            if float(x) != float(y):
                return False
        elif x != y:
            return False
    return True


def my_norm(t):
    t = t.strip()
    if t.startswith("user: "):
        t = t[len("user: "):]
    if t.endswith(SUFFIX):
        t = t[: -len(SUFFIX)]
    return " ".join(t.split())


def my_canon(t):
    """my own renaming class: every standalone single ASCII letter renamed in order of first appearance."""
    toks = re.findall(r"[A-Za-z]+|\d+(?:\.\d+)?|\S", my_norm(t))
    m = {}
    return " ".join(m.setdefault(x, f"@{len(m)}") if len(x) == 1 and x.isalpha() else x for x in toks)


def main():
    P = C.load_problems()
    S0 = C.load_problems(stage0=True)
    say("problems:", len(P), Counter(r["task"] for r in P.values()), "stage0:", len(S0),
        Counter(r["task"] for r in S0.values()), "overlap:", len(set(P) & set(S0)))
    # ---------------- IFBench
    repo = [json.loads(x) for x in open(os.path.join(C.HERE, "upstream", "ifbench", "ifbench", "data", "IFBench_test.jsonl"))]
    repo = {str(r["key"]): r for r in repo}
    hf = pq.read_table(os.path.join(D, "ifbench_hf", "data", "train-00000-of-00001.parquet")).to_pylist()
    hf = {str(r["key"]): r for r in hf}
    ok_repo = ok_hf = 0
    ifb = {p: r for p, r in P.items() if r["task"] == "ifbench"}
    for p, r in ifb.items():
        a = repo[r["key"]]
        if (a["prompt"] == r["prompt"] and a["instruction_id_list"] == r["instruction_id_list"]
                and all(same_kwargs(x, y) for x, y in zip(a["kwargs"], r["kwargs"]))):
            ok_repo += 1
        b = hf[r["key"]]
        kb = [{k: v for k, v in dict(x).items() if v is not None} for k_ in [0] for x in b["kwargs"]]
        kr = [{k: v for k, v in x.items() if v is not None} for x in r["kwargs"]]
        if (b["prompt"] == r["prompt"] and list(b["instruction_id_list"]) == r["instruction_id_list"]
                and len(kb) == len(kr) and all(same_kwargs(x, y) for x, y in zip(kb, kr))):
            ok_hf += 1
    nids = Counter(len(r["instruction_id_list"]) for r in ifb.values())
    types = {i for r in ifb.values() for i in r["instruction_id_list"]}
    say(f"IFBench: {len(ifb)} prompts; equal to repo jsonl {ok_repo}, to HF parquet {ok_hf}; constraints per prompt {dict(nids)};"
        f" {len(types)} instruction ids; repo rows {len(repo)}, HF rows {len(hf)}")
    # ---------------- IFEval
    ife = [json.loads(x) for x in open(os.path.join(D, "ifeval", "ifeval_input_data.jsonl"))]
    ife_sorted = sorted(ife, key=lambda r: r["key"])
    perm = rng_for("ifeval").sample(range(len(ife_sorted)), 190)
    want_eval = {f"ifeval_{ife_sorted[i]['key']}" for i in perm[:150]}
    want_s0 = {f"ifeval_{ife_sorted[i]['key']}" for i in perm[150:]}
    have_eval = {p for p, r in P.items() if r["task"] == "ifeval"}
    have_s0 = {p for p, r in S0.items() if r["task"] == "ifeval"}
    byk = {f"ifeval_{r['key']}": r for r in ife}
    eq = sum(1 for p in have_eval if byk[p]["prompt"] == P[p]["prompt"] and byk[p]["instruction_id_list"] ==
             P[p]["instruction_id_list"] and byk[p]["kwargs"] == P[p]["kwargs"])
    say(f"IFEval: {len(ife)} rows; subset == seeded draw: eval {have_eval == want_eval}, stage0 {have_s0 == want_s0};"
        f" rows equal to google/IFEval {eq}/{len(have_eval)}")
    # ---------------- OMEGA
    rows = []
    for ds in ("omega-explorative", "omega-compositional", "omega-transformative"):
        base = os.path.join(D, ds)
        for fam in sorted(os.listdir(base)):
            if not os.path.isdir(os.path.join(base, fam)):
                continue
            for f in sorted(os.listdir(os.path.join(base, fam))):
                if not f.endswith(".parquet"):
                    continue
                for r in pq.read_table(os.path.join(base, fam, f)).to_pylist():
                    rows.append({"ds": ds, "family": fam, "split": f.split("-")[0], "id": r["id"],
                                 "text": r["messages"][0]["content"], "gt": r["ground_truth"]})
    say("OMEGA rows read:", Counter((r["ds"]) for r in rows))
    ex = [r for r in rows if r["ds"] == "omega-explorative"]
    exid = {(r["family"], r["split"], r["id"]): r for r in ex}
    om = {p: r for p, r in P.items() if r["task"].startswith("omega")}
    om0 = {p: r for p, r in S0.items() if r["task"].startswith("omega")}
    good = 0
    bad = []
    for p, r in list(om.items()) + list(om0.items()):
        x = exid.get((r["family"], r["split"], r["omega_id"]))
        if x and x["text"] == r["prompt_original"] and (x["text"][: -len(SUFFIX)] if x["text"].endswith(SUFFIX)
                                                      else x["text"]) == r["prompt"] and str(x["gt"]).strip() == r["answer"]:
            good += 1
        else:
            bad.append(p)
    ws = sum(1 for p, r in list(om.items()) + list(om0.items())
             if str(exid[(r["family"], r["split"], r["omega_id"])]["gt"]) != str(exid[(r["family"], r["split"], r["omega_id"])]["gt"]).strip())
    say(f"OMEGA: {good}/{len(om) + len(om0)} problems equal their explorative row (prompt, original, answer); bad {bad[:5]};"
        f" labels with surrounding whitespace in the dataset: {ws}")
    # RL prompts
    rl = []
    for i in range(4):
        t = pq.read_table(os.path.join(D, "dolci_rl", "data", f"train-0000{i}-of-00004.parquet"),
                          columns=["dataset", "original_dataset", "prompt"]).to_pylist()
        rl += t
    say("RL rows:", len(rl))
    rl_keys = {my_norm(r["prompt"]) for r in rl}
    rl_om = [r for r in rl if r["original_dataset"] == "hamishivi/omega-combined-no-boxed_filtered"]
    rl_om_keys = {my_norm(r["prompt"]) for r in rl_om}
    rl_om_canon = {my_canon(r["prompt"]) for r in rl_om}
    train_like = [r for r in rows if r["ds"] != "omega-explorative" or r["split"] == "train"]
    train_keys = {my_norm(r["text"]) for r in train_like}
    train_canon = {my_canon(r["text"]) for r in train_like}
    ex_train_fam = defaultdict(set)
    for r in ex:
        if r["split"] == "train":
            ex_train_fam[my_norm(r["text"])].add(r["family"])
    matched = sum(1 for k in rl_om_keys if k in ex_train_fam)
    say(f"RL OMEGA prompts: {len(rl_om)} rows, {len(rl_om_keys)} distinct; distinct ones equal to an explorative train"
        f" problem: {matched}")
    fam_rl = defaultdict(set)
    for k in rl_om_keys:
        for f in ex_train_fam.get(k, ()):
            fam_rl[f].add(k)
    fams = sorted({r["family"] for r in ex})
    elig = [f for f in fams if len(fam_rl[f]) >= 100]
    say(f"explorative families {len(fams)}; with >= 1 RL prompt {sum(1 for f in fams if fam_rl[f])}; eligible (>= 100) {len(elig)}")
    dom_k = {"algebra": 2, "arithmetic": 2, "combinatory": 2, "geometry": 2, "logic": 1, "numbertheory": 1}
    by_dom = defaultdict(list)
    for f in elig:
        by_dom[f.split("_")[0]].append(f)
    chosen = []
    for dom, k in dom_k.items():
        chosen += sorted(rng_for("families", dom).sample(sorted(by_dom[dom]), k))
    have_f = sorted({r["family"] for r in om.values()})
    say("family draw reproduces:", sorted(chosen) == have_f, have_f)
    # pools and the problem draw
    reprod = 0
    viol = Counter()
    for f in chosen:
        for sp in ("test_in", "test_out"):
            s = sorted([r for r in ex if r["family"] == f and r["split"] == sp], key=lambda r: r["id"])
            cnt = Counter(my_canon(r["text"]) for r in s)
            pool = [r for r in s if my_norm(r["text"]) not in rl_keys and my_norm(r["text"]) not in train_keys
                    and my_canon(r["text"]) not in rl_om_canon and my_canon(r["text"]) not in train_canon
                    and cnt[my_canon(r["text"])] == 1]
            pick = rng_for("problems", f, sp).sample(range(len(pool)), 12)
            want = [pool[i]["id"] for i in pick]
            task = "omega_in" if sp == "test_in" else "omega_out"
            have = [P.get(f"{task}_{i}") or S0.get(f"{task}_{i}") for i in want]
            if all(h is not None for h in have) and [h["omega_id"] for h in have[:10]] == want[:10] \
                    and all(f"{task}_{i}" in P for i in want[:10]) and all(f"{task}_{i}" in S0 for i in want[10:]):
                reprod += 1
            for r in [x for x in s if f"{task}_{x['id']}" in P]:
                if my_norm(r["text"]) in rl_keys:
                    viol["rl_prompt"] += 1
                if my_norm(r["text"]) in train_keys:
                    viol["train_like"] += 1
                if my_canon(r["text"]) in rl_om_canon or my_canon(r["text"]) in train_canon:
                    viol["renamed_copy"] += 1
                if cnt[my_canon(r["text"])] > 1:
                    viol["same_split_dup"] += 1
            say(f"  {f} {sp}: split {len(s)} pool {len(pool)}")
    say(f"problem draws reproduced (my normaliser): {reprod}/20 family-splits; filter violations among chosen: {dict(viol)}")
    open(os.path.join(C.OUT, "provenance.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
