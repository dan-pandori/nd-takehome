"""Rule-1 vacuous satisfaction of format:sub-bullets, counted mechanically (run olmo-transplant; reviewer's check).
IFBench's SubBulletPointsChecker splits on '*' and requires a '-' in every chunk after the first, so an answer with no
'*' at all passes ("every * bullet has a sub-bullet" over zero bullets) -- the pre-registered rule 1's own example
of a gamed answer. For every strict success on the three sub-bullet prompts: does the answer contain a '*'? And how
did each label source (executor read / inherited / unread share; my blinded label) treat the ones without.
Output: out/vacuous.txt"""
import collections
import csv
import gzip
import json

from rvt_core import ART, OUT, RAW, Tee, answer_of, iter_gz
from rvt_labels import table

P = Tee("vacuous.txt")
prompts = list(csv.DictReader(open(RAW / "olmo_transplant" / "prompts.csv")))
SB = {p["pid"] for p in prompts if "format:sub-bullets" in p["instruction_ids"]}
mine = json.load(open(OUT / "my_labels.json"))
ex = {r["key"]: r for r in table()}
c = collections.defaultdict(collections.Counter)
for job in ("R_dpo", "R_s2300", "C_dpo", "C_s2300", "F_s2300"):
    for r in iter_gz(ART / "samples" / f"{job}.jsonl.gz"):
        if r["pid"] not in SB:
            continue
        k = f"{job}|{r['rid']}|{r['i']}"
        if k not in ex:  # not a strict success
            continue
        a = answer_of("</think>" + r["text"])
        vac = "*" not in a
        cell = r["cond"] + (str(r["cut"]) if r["cond"] in ("B", "F") else "")
        e = ex[k]
        c[(job, r["pid"], cell)]["strict"] += 1
        if vac:
            c[(job, r["pid"], cell)]["vacuous"] += 1
            c[(job, r["pid"], cell)][f"vac_exec_{e['src']}:{e['label'] or '-'}"] += 1
            if k in mine:
                c[(job, r["pid"], cell)][f"vac_mine:{mine[k]}"] += 1
tot = collections.Counter()
for key, v in sorted(c.items()):
    if v["vacuous"]:
        P(f"{key[0]:8s} {key[1]:12s} {key[2]:7s} strict {v['strict']:3d} vacuous {v['vacuous']:3d}  " +
          " ".join(f"{k}={n}" for k, n in sorted(v.items()) if k.startswith("vac_")))
    for k, n in v.items():
        tot[(key[0], k)] += n
P("totals by job: " + "; ".join(f"{j} {k} {n}" for (j, k), n in sorted(tot.items()) if k in ("strict", "vacuous")))
