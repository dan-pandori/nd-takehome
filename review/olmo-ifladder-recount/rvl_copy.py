"""Copy checks for run olmo-ifladder: does a strict success copy text it was shown or trained on?

 - rung 4 (R4_dpo, R4_s2300): every strict success vs the target's two exemplar answers (word 3-gram Jaccard,
   whitespace-collapsed exact match);
 - LoRAs (Leval_main / Leval_ctrl): every strict success on the 48 vs the 16 training answers of its arm.
Exact = identical whitespace-collapsed text; near = Jaccard >= 0.5. Writes out/copy.txt."""
import collections
import gzip
import json

from rvl_core import CODE, OUT, SCR, Tee, answer_of, iter_gz, iter_job, load_csv, wsnorm

P = Tee("copy.txt")


def grams(s):
    w = s.lower().split()
    return {tuple(w[i:i + 3]) for i in range(len(w) - 2)} or {tuple(w)}


def jac(a, b):
    return len(a & b) / max(1, len(a | b))


reach = {r["pid"] for r in load_csv(CODE / "prompts.csv") if r["set"] == "reach"}
ex = load_csv(CODE / "exemplars.csv")
need = collections.defaultdict(set)
for e in ex:
    need[e["job"]].add((e["source"], int(e["chunk"]), int(e["i"])))
src_ans = {}
for job, ks in need.items():
    for r in iter_gz(SCR / "src" / f"{job}.jsonl.gz"):
        k = (r["pid"], int(r["chunk"]), int(r["i"]))
        if k in ks:
            src_ans[(job,) + k] = answer_of(r["text"])
exa = collections.defaultdict(list)
for e in ex:
    exa[e["target"]].append(src_ans[(e["job"], e["source"], int(e["chunk"]), int(e["i"]))])
man = [r for r in load_csv(CODE / "train_manifest.csv") if r["role"] == "train"]
tneed = collections.defaultdict(set)
for r in man:
    tneed[r["job"]].add((r["pid"], int(r["chunk"]), int(r["i"]), r["writer"]))
tr = {"s2300": [], "dpo": []}
for job, ks in tneed.items():
    want = {(a, b, c): w for a, b, c, w in ks}
    for x in iter_gz(SCR / "src" / f"{job}.jsonl.gz"):
        k = (x["pid"], int(x["chunk"]), int(x["i"]))
        if k in want:
            tr[want[k]].append((x["pid"], answer_of(x["text"])))


def strict_keys(job):
    return {(r["pid"], r["chunk"], r["i"]) for r in (json.loads(l) for l in gzip.open(OUT / "regrade" / f"{job}.jsonl.gz", "rt"))
            if r["strict"]}


for job in ("R4_dpo", "R4_s2300"):
    sk = strict_keys(job)
    n = exact = near = 0
    hits = collections.Counter()
    for r in iter_job(job):
        if (r["pid"], r["chunk"], r["i"]) not in sk or r["pid"] not in reach:
            continue
        a = answer_of(r["text"])
        n += 1
        g = grams(a)
        best = max(jac(g, grams(x)) for x in exa[r["pid"]])
        ex_ = any(wsnorm(a) == wsnorm(x) for x in exa[r["pid"]])
        exact += ex_
        near += best >= 0.5
        if best >= 0.5:
            hits[r["pid"]] += 1
    P(f"{job}: reach strict successes {n}; exact copies of an exemplar answer {exact}; near (J >= 0.5) {near}; by pid {dict(hits)}")
for job, w in (("Leval_main", "s2300"), ("Leval_ctrl", "dpo")):
    sk = strict_keys(job)
    TG = [(p, grams(a), wsnorm(a)) for p, a in tr[w]]
    n = exact = near = 0
    hits = collections.Counter()
    for r in iter_job(job):
        if (r["pid"], r["chunk"], r["i"]) not in sk or r["pid"] not in reach:
            continue
        a = answer_of(r["text"])
        n += 1
        g = grams(a)
        best, bp = max((jac(g, t[1]), t[0]) for t in TG)
        exact += any(wsnorm(a) == t[2] for t in TG)
        if best >= 0.5:
            near += 1
            hits[(r["pid"], bp)] += 1
    P(f"{job}: reach strict successes {n}; exact copies of a training answer ({w}) {exact}; near (J >= 0.5) {near}; "
      f"(eval pid, training pid) {dict(hits)}")
