"""Rung-4 exemplars of run olmo-ifladder: every exemplar answer re-graded (strict, my grader) on its SOURCE prompt;
the three same-family fills (no binding id); exemplars whose answer would also pass the TARGET's constraints (a
fixed-output leak check: the target's own checker run on the exemplar answer). Writes out/exemplars.txt."""
import collections

from rvl_core import CODE, SCR, Tee, answer_of, iter_gz, load_csv, upstream_record
from rvl_graders import if_grade

P = Tee("exemplars.txt")
ex = load_csv(CODE / "exemplars.csv")
need = collections.defaultdict(set)
for e in ex:
    need[e["job"]].add((e["source"], int(e["chunk"]), int(e["i"])))
ans = {}
for job, ks in need.items():
    for r in iter_gz(SCR / "src" / f"{job}.jsonl.gz"):
        k = (r["pid"], int(r["chunk"]), int(r["i"]))
        if k in ks:
            ans[(job,) + k] = answer_of(r["text"])
bind = {r["pid"]: r["binding"] for r in load_csv(CODE / "prompts.csv")}
bad, fills, leaks = [], [], []
for e in ex:
    a = ans[(e["job"], e["source"], int(e["chunk"]), int(e["i"]))]
    task, rec = upstream_record(e["source"])
    if not if_grade(task, rec, a)[0]:
        bad.append((e["target"], e["source"]))
    if bind[e["target"]] not in rec["instruction_id_list"]:
        fills.append((e["target"], e["slot"], e["source"], rec["instruction_id_list"]))
    tt, trec = upstream_record(e["target"])
    if if_grade(tt, trec, a)[0]:
        leaks.append((e["target"], e["source"], bind[e["target"]], len(a.split())))
P(f"exemplars {len(ex)}; answers strict on their own source prompt: {len(ex) - len(bad)}; failing {bad}")
P(f"same-family fills (source lacks the target's binding id): {fills}")
P(f"exemplar answers that pass the TARGET's own checker as they stand: {len(leaks)}")
for l in leaks:
    P(f"    target {l[0]} ({l[2]}) <- source {l[1]} answer ({l[3]} words)")
