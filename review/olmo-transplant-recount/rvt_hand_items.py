"""Blinded hand-gate items for the reviewer's re-read (run olmo-transplant). My own selection and item texts.

Selection (deciding successes, reach prompts and F):
  D1  every strict success in T1, T3, T4, T0 (both writers), B<N> and P written by dpo, that is NOT a verbatim
      (whitespace-collapsed) copy of a labelled source answer on the same prompt (copies carry the source's
      olmo-ifomega label, which that run's review already re-read);
  D2  every item the executor's readers read in T2 and in the s2300 B / P cells (item-level agreement);
  D3  a seeded sample of 30 unread s2300 successes in each of B1024, B2048, B4096 and P, and 20 in T2 (tests the
      share-extrapolation rule);
  D4  F (fresh budget forcing): every strict success at F2048, every executor read, 15 unread each at F4096, F8192.
One item per distinct (prompt, answer); the key maps it back to every covered sample. Items show what the
pre-registered readers saw: the prompt, the constraints with the checker's verdicts (my re-grade), and the answer
with its word count; nothing about writer, condition, thinking or selection. Item ids are random (seed below).
Writes ~/review/otr_rv/items_A/<id>.md, hand/key_A.json (kept from readers), hand/batches_A.json.
Usage: rvt_hand_items.py A
"""
import collections
import gzip
import json
import random
import sys

from rvt_core import ART, KIT, OUT, RAW, SCR, answer_of, iter_gz
from rvt_labels import table

SEED = 7731
BATCH = 46
HAND = KIT / "hand"
HAND.mkdir(exist_ok=True)


def main():
    rnd = sys.argv[1]
    assert rnd == "A"
    rows = table()
    reach_jobs = {"R_dpo", "R_s2300", "F_s2300"}
    rng = random.Random(SEED)
    pick = {}  # key -> reason
    for r in rows:
        if r["job"] not in reach_jobs:
            continue
        w, c = r["writer"], r["cell"]
        if r["job"] == "F_s2300":
            if c == "F2048" or r["src"] == "read":
                pick[r["key"]] = "D4"
            continue
        dpo_cell = w == "dpo" and (c in ("T1", "T4", "T0", "P") or c.startswith("B"))
        s_cell = w == "s2300" and c in ("T3", "T0")
        if (dpo_cell or s_cell) and r["src"] != "inh_src":
            pick[r["key"]] = "D1"
        elif w == "s2300" and (c == "T2" or c == "P" or c.startswith("B")) and r["src"] == "read":
            pick[r["key"]] = "D2"
    # D3 / D4 samples of unread successes
    by = collections.defaultdict(list)
    for r in rows:
        if r["src"] == "unread" and r["key"] not in pick:
            by[(r["job"], r["cell"])].append(r["key"])
    for (job, cell), n in [(("R_s2300", "B1024"), 30), (("R_s2300", "B2048"), 30), (("R_s2300", "B4096"), 30),
                           (("R_s2300", "P"), 30), (("R_s2300", "T2"), 20), (("F_s2300", "F4096"), 15),
                           (("F_s2300", "F8192"), 15)]:
        ks = sorted(by[(job, cell)])
        for k in rng.sample(ks, min(n, len(ks))):
            pick[k] = "D3" if job == "R_s2300" else "D4"
    # one item per distinct (pid, answer)
    rows_by = {r["key"]: r for r in rows}
    groups = collections.defaultdict(list)
    for k in pick:
        r = rows_by[k]
        groups[(r["pid"], r["norm"])].append(k)
    # texts and per-constraint verdicts
    need = collections.defaultdict(set)
    for ks in groups.values():
        for k in ks:
            need[k.split("|")[0]].add(k)
    texts, per = {}, {}
    for job, ks in need.items():
        for r in iter_gz(ART / "samples" / f"{job}.jsonl.gz"):
            k = f"{job}|{r['rid']}|{r['i']}"
            if k in ks:
                texts[k] = (r["text"], r["finish"])
        with gzip.open(OUT / "regrade" / f"{job}.jsonl.gz", "rt") as f:
            for ln in f:
                g = json.loads(ln)
                if g["key"] in ks:
                    per[g["key"]] = g["per"]
    up = {str(json.loads(l)["key"]): json.loads(l) for l in open(SCR / "upstream" / "ifbench" / "IFBench_test.jsonl")}
    prob = {json.loads(l)["pid"]: json.loads(l) for l in open(RAW / "olmo_ifomega" / "problems.jsonl")}
    outdir = SCR / f"items_{rnd}"
    outdir.mkdir(exist_ok=True)
    key = {}
    used = set()
    glist = sorted(groups.items())
    rng.shuffle(glist)
    for (pid, norm), ks in glist:
        item = f"x{rng.randrange(16 ** 6):06x}"
        while item in used:
            item = f"x{rng.randrange(16 ** 6):06x}"
        used.add(item)
        k0 = sorted(ks)[0]
        text, finish = texts[k0]
        ans = answer_of("</think>" + text)
        u = up[str(prob[pid]["key"])]
        cons = "\n".join(
            f"- `{c}` {json.dumps({a: b for a, b in kw.items() if b is not None})}: checker says "
            f"{'followed' if ok else 'NOT followed'}" for c, kw, ok in zip(u["instruction_id_list"], u["kwargs"], per[k0]))
        cut = " The answer was cut off at the length limit." if finish == "length" else ""
        body = (f"# Item {item}\n\n## Prompt (sent to the model verbatim)\n\n{u['prompt']}\n\n"
                f"## Constraints checked (official checker)\n\n{cons}\n\n"
                f"## Answer (the text after the model's private reasoning, which is not shown; "
                f"{len(ans.split())} words){cut}\n\n{ans}\n")
        (outdir / f"{item}.md").write_text(body)
        key[item] = {"pid": pid, "keys": sorted(ks), "reasons": sorted({pick[k] for k in ks}),
                     "cells": sorted({f"{rows_by[k]['writer']}:{rows_by[k]['cell']}" for k in ks}),
                     "exec_labels": sorted({rows_by[k]["label"] or "-" for k in ks}),
                     "exec_src": sorted({rows_by[k]["src"] for k in ks})}
    items = list(key)
    rng.shuffle(items)
    batches = [items[i:i + BATCH] for i in range(0, len(items), BATCH)]
    json.dump(key, open(HAND / f"key_{rnd}.json", "w"), indent=1, sort_keys=True)
    json.dump(batches, open(HAND / f"batches_{rnd}.json", "w"), indent=0)
    print(f"round {rnd}: {len(pick)} samples -> {len(items)} distinct items in {len(batches)} batches; reasons "
          f"{dict(collections.Counter(v for v in pick.values()))}; items by cell "
          f"{dict(collections.Counter(c for v in key.values() for c in v['cells']))}")


if __name__ == "__main__":
    main()
