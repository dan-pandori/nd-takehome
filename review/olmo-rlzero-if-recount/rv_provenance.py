"""Provenance of the 450 evaluation prompts and the 64 Stage-0 prompts against my own fetches of the pinned datasets.
  IFBench: prompt / instruction list / kwargs equal the IFBench repo jsonl @ cd189a9c (the checker's input) and the HF
           parquet allenai/IFBench_test @ ed7c1245 (None kwargs dropped; ints compared numerically).
  IFEval : rows equal google/IFEval @ 966cd895; the 150 + 40 Stage-0 subset is olmo-ifomega's seeded draw
           (random.Random(int(sha256('20261104|ifeval')[:16], 16)).sample over the key-sorted 541, 190 drawn, first 150 =
           evaluation, rest = Stage 0) -- the rule my olmo-ifomega review verified; re-derived here.
  rows   : equal to olmo_ifomega/problems.jsonl (the brief: "the same 150"); ifomega_excl == olmo-ifomega's exclusions.
Output: out/provenance.txt"""
import csv
import hashlib
import json
import os
import random
from collections import Counter

import pyarrow.parquet as pq

import rv_core as C

D = os.path.expanduser("~/review/oif_rv/data")
lines = []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    lines.append(s)


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


def nn(kws):
    return [{k: v for k, v in dict(x or {}).items() if v is not None} for x in kws]


def main():
    P = C.load_problems()
    S0 = C.load_problems(stage0=True)
    say("problems:", len(P), dict(Counter(r["task"] for r in P.values())), "stage0:", len(S0),
        dict(Counter(r["task"] for r in S0.values())), "pid overlap:", len(set(P) & set(S0)),
        "prompt overlap:", len({r["prompt"] for r in P.values()} & {r["prompt"] for r in S0.values()}))
    repo = {str(r["key"]): r for r in map(json.loads, open(os.path.join(C.UP, "ifbench", "ifbench", "data",
                                                                         "IFBench_test.jsonl")))}
    hf = {str(r["key"]): r for r in pq.read_table(os.path.join(D, "ifbench_hf", "data",
                                                               "train-00000-of-00001.parquet")).to_pylist()}
    ifb = {p: r for p, r in P.items() if r["task"] == "ifbench"}
    ok_repo = sum(1 for r in ifb.values() if repo[r["key"]]["prompt"] == r["prompt"]
                  and repo[r["key"]]["instruction_id_list"] == r["instruction_id_list"]
                  and all(same_kwargs(x, y) for x, y in zip(nn(repo[r["key"]]["kwargs"]), nn(r["kwargs"]))))
    ok_hf = sum(1 for r in ifb.values() if hf[r["key"]]["prompt"] == r["prompt"]
                and list(hf[r["key"]]["instruction_id_list"]) == r["instruction_id_list"]
                and all(same_kwargs(x, y) for x, y in zip(nn(hf[r["key"]]["kwargs"]), nn(r["kwargs"]))))
    say(f"IFBench: {len(ifb)} prompts (keys distinct {len({r['key'] for r in ifb.values()})}); equal to the repo jsonl "
        f"{ok_repo}, to the HF parquet {ok_hf} (repo rows {len(repo)}, HF rows {len(hf)}); constraints per prompt "
        f"{dict(Counter(len(r['instruction_id_list']) for r in ifb.values()))}")
    ife_rows = [json.loads(x) for x in open(os.path.join(D, "ifeval", "ifeval_input_data.jsonl"))]
    by_key = {str(r["key"]): r for r in ife_rows}
    keys = sorted(by_key, key=int)
    h = hashlib.sha256(b"20261104|ifeval").hexdigest()
    draw = random.Random(int(h[:16], 16)).sample(keys, 190)
    ife = {p: r for p, r in P.items() if r["task"] == "ifeval"}
    s0e = {p: r for p, r in S0.items() if r["task"] == "ifeval"}
    say("IFEval: rows", len(ife_rows), "| eval subset == seeded first 150:", sorted(r["key"] for r in ife.values()) ==
        sorted(draw[:150]), "| stage0 == next 40:", sorted(r["key"] for r in s0e.values()) == sorted(draw[150:]))
    ok = sum(1 for r in list(ife.values()) + list(s0e.values()) if by_key[str(r["key"])]["prompt"] == r["prompt"]
             and by_key[str(r["key"])]["instruction_id_list"] == r["instruction_id_list"]
             and all(same_kwargs(x, y) for x, y in zip(nn(by_key[str(r["key"])]["kwargs"]), nn(r["kwargs"]))))
    say("IFEval rows equal to google/IFEval:", ok, "of", len(ife) + len(s0e))
    # the brief: same prompts as olmo-ifomega; rows copied unchanged
    oif = {r["pid"]: r for r in map(json.loads, open(os.path.join(C.WS, "olmo_ifomega", "problems.jsonl")))}
    same = sum(1 for p, r in P.items() if p in oif and {k: v for k, v in r.items() if k != "ifomega_excl"} == oif[p])
    say("rows equal to olmo_ifomega/problems.jsonl (minus ifomega_excl):", same, "of", len(P))
    ex = {r["pid"] for r in csv.DictReader(open(os.path.join(C.WS, "olmo_ifomega", "exclusions.csv")))
          if r.get("pid", "").startswith("ifbench")}
    flag = {p for p, r in ifb.items() if r.get("ifomega_excl")}
    say("ifomega_excl flagged:", len(flag), "| olmo_ifomega/exclusions.csv IFBench rows:", len(ex), "| equal:", flag == ex)
    if flag != ex:
        say("  flagged-not-excluded", sorted(flag - ex)[:10], "excluded-not-flagged", sorted(ex - flag)[:10])
    rl = {p: r for p, r in S0.items() if r["task"] != "ifeval"}
    say("Stage-0 RL prompts:", len(rl), dict(Counter(r["task"] for r in rl.values())))
    os.makedirs(C.OUT, exist_ok=True)
    open(os.path.join(C.OUT, "provenance.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
