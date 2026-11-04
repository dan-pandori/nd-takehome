#!/usr/bin/env python3
"""Build the evaluation and Stage-0 problem sets of run olmo-ifomega (seeded; every input at a pinned revision).

  fetch <cache>          download the pinned inputs into <cache> (curl; ~760 MB, most of it Dolci-Think-RL-32B)
  build <cache>          write olmo_ifomega/problems.jsonl, stage0_problems.jsonl, families.csv, rl_if_ids.csv

Tasks (pid prefix):
  ifbench   allenai/IFBench_test, all 300 prompts (the user turn is `prompt` verbatim)
  ifeval    google/IFEval, a seeded 150-prompt subset of the 541 (`prompt` verbatim)
  omega_in / omega_out   allenai/omega-explorative test_in / test_out: 10 families x 10 problems per split. The user
            turn is the OMEGA problem with its "\\n\\nPresent the answer in LaTex format: \\boxed{Your answer}" suffix
            removed, which is exactly the form of RL's OMEGA prompts (Dolci-Think-RL-32B `omega-combined-no-boxed`:
            all 15,000 match an OMEGA train problem verbatim once "user: " and the suffix are dropped).
Family choice: eligible = explorative families with >= 100 distinct RL prompts (31 of 41); stratified by domain
(algebra 2, arithmetic 2, combinatory 2, geometry 2, logic 1, numbertheory 1), seeded draw within each domain.
Problem pools exclude, before the draw, any problem whose normalised text equals an RL prompt, any OMEGA train /
compositional / transformative problem, or another problem of the same split (OMEGA's own split overlap), and any
problem that equals one of those after renaming single-letter symbols in order of appearance (canon(): a relabelled
copy of the same instance, e.g. the same multiset and event with other letters).
Stage 0 (lengths and throughput only, never evaluated): 2 more problems per family x split from the same pools, 40
IFEval prompts outside the subset, and 24 RL IF prompts (Dolci IF multi-constraint; in RL's training set).
"""
import ast
import csv
import hashlib
import json
import random
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

SEED = 20261104
OUT = Path(__file__).resolve().parent
PINS = {  # repo -> (revision, files)
    "allenai/IFBench_test": ("ed7c12452594b7028b15807b86d3938150b663ae", ["data/train-00000-of-00001.parquet"]),
    "google/IFEval": ("966cd89545d6b6acfd7638bc708b98261ca58e84", ["ifeval_input_data.jsonl"]),
    "allenai/Dolci-Think-RL-32B": ("d581ecde5cb4bb2a550c2499a7408a3b8dca79f6",
                                   [f"data/train-0000{i}-of-00004.parquet" for i in range(4)]),
    "allenai/omega-explorative": ("b04ae8d4757a2229e8ed65ac6a923e502d0bbb95", None),
    "allenai/omega-compositional": ("fabf91c0e85ab3ba5ec2ecfc38a2f30a6d0fadb9", None),
    "allenai/omega-transformative": ("f188d999ef40f51843828d6d268c720feb3d355a", None),
}
# IFBench prompts come from the IFBench repo's bundled ifbench/data/IFBench_test.jsonl (the official checker's input;
# kwargs are ints there, while the HF parquet stores them as floats, which the checkers reject); build() asserts that
# it equals allenai/IFBench_test on every key, prompt, instruction list and kwargs value.
IFBENCH_JSONL = ("https://raw.githubusercontent.com/allenai/IFBench/cd189a9c2889526d8af901d2103fd3e1ffcea6df/"
                 "ifbench/data/IFBench_test.jsonl")
SUFFIX = "\n\nPresent the answer in LaTex format: \\boxed{Your answer}"
DOMAIN_K = {"algebra": 2, "arithmetic": 2, "combinatory": 2, "geometry": 2, "logic": 1, "numbertheory": 1}
MIN_RL = 100
N_EVAL, N_S0 = 10, 2
N_IFEVAL, N_IFEVAL_S0, N_RLIF_S0 = 150, 40, 24


def fetch(cache):
    cache = Path(cache)
    for repo, (rev, files) in PINS.items():
        if files is None:  # every parquet file of the repo at that revision
            api = f"https://huggingface.co/api/datasets/{repo}/tree/{rev}?recursive=true"
            tree = json.loads(subprocess.run(["curl", "-sL", api], capture_output=True, check=True).stdout)
            files = [x["path"] for x in tree if x["type"] == "file" and x["path"].endswith(".parquet")]
        for f in files:
            dst = cache / repo.split("/")[1] / f
            if dst.exists():
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            url = f"https://huggingface.co/datasets/{repo}/resolve/{rev}/{f}"
            subprocess.run(["curl", "-sfL", "-o", str(dst), url], check=True)
        print(repo, rev, len(files), "files")
    dst = cache / "IFBench_repo" / "IFBench_test.jsonl"  # the official checker's own input file
    if not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["curl", "-sfL", "-o", str(dst), IFBENCH_JSONL], check=True)


def norm(t):
    t = t.strip()
    if t.startswith("user: "):
        t = t[6:]
    if t.endswith(SUFFIX):
        t = t[: -len(SUFFIX)]
    return re.sub(r"\s+", " ", t).strip()


TOK = re.compile(r"[A-Za-z]+|\d+(?:\.\d+)?|\S")


def canon(t):
    """norm(t) with single-letter symbols renamed in order of appearance: {n: 4, y: 2} ... 'y' == {a: 4, b: 2} ... 'b'."""
    m, out = {}, []
    for x in TOK.findall(norm(t)):
        out.append(m.setdefault(x, f"#{len(m)}") if len(x) == 1 and x.isalpha() else x)
    return " ".join(out)


def rng_for(*keys):
    h = hashlib.sha256(("|".join(map(str, (SEED,) + keys))).encode()).hexdigest()
    return random.Random(int(h[:16], 16))


def build(cache):
    import pandas as pd
    import pyarrow.parquet as pq
    cache = Path(cache)
    # --- RL prompts (Dolci-Think-RL-32B): OMEGA rows and IF rows
    cols = ["dataset", "original_dataset", "prompt", "ground_truth", "constraint", "custom_id"]
    rl = pd.concat([pq.read_table(cache / "Dolci-Think-RL-32B" / f, columns=cols).to_pandas()
                    for f in PINS["allenai/Dolci-Think-RL-32B"][1]], ignore_index=True)
    assert len(rl) == 102026, len(rl)
    rl["key"] = rl.prompt.map(norm)
    rl_keys = set(rl.key)
    rl_om = rl[rl.original_dataset == "hamishivi/omega-combined-no-boxed_filtered"]
    rl_canon = set(rl_om.prompt.map(canon))
    rl_if = rl[rl.dataset.map(lambda x: x[0]) == "ifeval"]
    # --- OMEGA
    rows = []
    for ds in ("omega-explorative", "omega-compositional", "omega-transformative"):
        for f in sorted((cache / ds).glob("*/*.parquet")):
            d = pq.read_table(f).to_pandas()
            d["ds"], d["family"], d["split"] = ds, f.parent.name, f.name.split("-")[0]
            rows.append(d)
    om = pd.concat(rows, ignore_index=True)
    om["text"] = om.messages.map(lambda m: m[0]["content"])
    om["key"] = om.text.map(norm)
    om["canon"] = om.text.map(canon)
    ex = om[om.ds == "omega-explorative"]
    train_keys = set(om[(om.ds != "omega-explorative") | (om.split == "train")].key)
    train_canon = set(om[(om.ds != "omega-explorative") | (om.split == "train")].canon)
    fam_of = defaultdict(set)  # RL OMEGA prompt key -> explorative train families it matches
    for r in ex[ex.split == "train"].itertuples():
        fam_of[r.key].add(r.family)
    rl_fam = defaultdict(set)
    for k in set(rl_om.key):
        for f in fam_of.get(k, ()):
            rl_fam[f].add(k)
    fams = sorted(set(ex.family))
    by_dom = defaultdict(list)
    for f in fams:
        if len(rl_fam[f]) >= MIN_RL:
            by_dom[f.split("_")[0]].append(f)
    chosen = []
    for dom, k in DOMAIN_K.items():
        chosen += sorted(rng_for("families", dom).sample(sorted(by_dom[dom]), k))
    with open(OUT / "families.csv", "w", newline="") as g:
        w = csv.writer(g)
        w.writerow(["family", "domain", "rl_distinct_prompts", "rl_rows", "eligible", "selected",
                    "test_in", "test_out", "pool_in", "pool_out"])
        rl_rows = Counter()
        for k in rl_om.key:
            for f in fam_of.get(k, ()):
                rl_rows[f] += 1
        pools = {}
        for f in fams:
            for sp in ("test_in", "test_out"):
                s = ex[(ex.family == f) & (ex.split == sp)]
                dup = set(s.canon[s.canon.duplicated(keep=False)])
                ok = s[~s.key.isin(rl_keys) & ~s.key.isin(train_keys) & ~s.canon.isin(rl_canon)
                       & ~s.canon.isin(train_canon) & ~s.canon.isin(dup)]
                pools[(f, sp)] = ok.sort_values("id")
            w.writerow([f, f.split("_")[0], len(rl_fam[f]), rl_rows[f], int(len(rl_fam[f]) >= MIN_RL),
                        int(f in chosen), int((ex.family == f).mul(ex.split == "test_in").sum()),
                        int((ex.family == f).mul(ex.split == "test_out").sum()),
                        len(pools[(f, "test_in")]), len(pools[(f, "test_out")])])
    probs, s0 = [], []
    for f in chosen:
        for sp in ("test_in", "test_out"):
            pool = pools[(f, sp)]
            pick = rng_for("problems", f, sp).sample(range(len(pool)), N_EVAL + N_S0)
            for j, ix in enumerate(pick):
                r = pool.iloc[ix]
                task = "omega_in" if sp == "test_in" else "omega_out"
                rec = {"pid": f"{task}_{r.id}", "task": task, "family": f, "split": sp, "omega_id": r.id,
                       "prompt": r.text[: -len(SUFFIX)] if r.text.endswith(SUFFIX) else r.text,
                       "prompt_original": r.text, "answer": str(r.ground_truth).strip()}
                (probs if j < N_EVAL else s0).append(rec)
    # --- IFBench (all 300) and IFEval (seeded subset)
    ifb = pq.read_table(cache / "IFBench_test" / PINS["allenai/IFBench_test"][1][0]).to_pandas()
    hf = {str(r.key): (r.prompt, list(r.instruction_id_list),
                       [{a: b for a, b in dict(k).items() if b is not None} for k in r.kwargs]) for r in ifb.itertuples()}
    rows = [json.loads(ln) for ln in open(cache / "IFBench_repo" / "IFBench_test.jsonl")]
    assert len(rows) == len(hf) == 300
    for r in sorted(rows, key=lambda r: int(r["key"])):
        kw = [{a: b for a, b in k.items() if b is not None} for k in r["kwargs"]]
        assert hf[str(r["key"])] == (r["prompt"], r["instruction_id_list"], kw), r["key"]
        probs.append({"pid": f"ifbench_{r['key']}", "task": "ifbench", "key": str(r["key"]), "prompt": r["prompt"],
                      "instruction_id_list": r["instruction_id_list"], "kwargs": r["kwargs"]})
    ife = [json.loads(ln) for ln in open(cache / "IFEval" / "ifeval_input_data.jsonl")]
    ife = sorted(ife, key=lambda r: r["key"])
    perm = rng_for("ifeval").sample(range(len(ife)), N_IFEVAL + N_IFEVAL_S0)
    for j, ix in enumerate(perm):
        r = ife[ix]
        rec = {"pid": f"ifeval_{r['key']}", "task": "ifeval", "key": str(r["key"]), "prompt": r["prompt"],
               "instruction_id_list": r["instruction_id_list"], "kwargs": r["kwargs"]}
        (probs if j < N_IFEVAL else s0).append(rec)
    # --- RL IF prompts for Stage 0 (lengths only)
    rif = rl_if.reset_index(drop=True)
    for ix in rng_for("rl_if").sample(range(len(rif)), N_RLIF_S0):
        r = rif.iloc[ix]
        gt = ast.literal_eval(r.ground_truth[0])[0]
        s0.append({"pid": f"rlif_{ix}", "task": "rlif", "prompt": r.prompt[6:] if r.prompt.startswith("user: ")
                   else r.prompt, "instruction_id_list": gt["instruction_id"], "kwargs": gt["kwargs"],
                   "rl_custom_id": r.custom_id})
    for name, rs in (("problems.jsonl", probs), ("stage0_problems.jsonl", s0)):
        assert len({r["pid"] for r in rs}) == len(rs), name
        with open(OUT / name, "w") as g:
            for r in rs:
                g.write(json.dumps(r, ensure_ascii=False) + "\n")
    # RL IF constraint ids (for the per-constraint analysis)
    ids = Counter(x for gt in rl_if.ground_truth for x in ast.literal_eval(gt[0])[0]["instruction_id"])
    with open(OUT / "rl_if_ids.csv", "w", newline="") as g:
        w = csv.writer(g)
        w.writerow(["instruction_id", "rl_prompts"])
        for k, v in sorted(ids.items(), key=lambda t: (-t[1], t[0])):
            w.writerow([k, v])
    print("families:", chosen)
    print("problems:", Counter(r["task"] for r in probs), "stage0:", Counter(r["task"] for r in s0))


if __name__ == "__main__":
    {"fetch": fetch, "build": build}[sys.argv[1]](sys.argv[2])
