"""Hand-gate label table for run olmo-transplant (reviewer's own implementation of the pre-registered rules).

Every strict success of this run (my re-grade) gets a label source:
  read      : the item key (job|rid|i) is in the executor's olmo_transplant/handcheck.csv (its final_label);
  inh_src   : its whitespace-collapsed answer equals a labelled source answer on the same prompt
              (olmo_ifomega/handcheck.csv final_label on stored s2300 samples, olmo_transplant/handcheck_src.csv);
  inh_run   : equals an answer read in this run (handcheck.csv) on the same prompt;
  unread    : none of these; the (prompt, run-condition) share applies.
Labels can be overridden by a reviewer label file (my blind re-read): labels_override(path) -> {key: label}.
A run-condition (cell) is (writer, cond, cut): T0..T4, B<N>, P, F<N>.
Exposes: table(override=None, r6_strict=False) -> list of dict rows; shares(rows) -> {(set?)...}.
"""
import collections
import csv
import gzip
import json

from rvt_core import ART, OUT, RAW, SCR, answer_of, iter_gz, wsnorm

RUN_JOBS = ["R_dpo", "R_s2300", "C_dpo", "C_s2300", "F_s2300"]


def cell_of(r):
    c = r["cond"]
    if c in ("B", "F"):
        return f"{c}{r['cut']}"
    return c


def _src_texts():
    out = {}
    for job in ("F_s2300_ifb", "C1_s2300_ifb", "C2_s2300_ifb"):
        for r in iter_gz(SCR / "src" / f"{job}.jsonl.gz"):
            out[(job, r["pid"], r["chunk"], r["i"])] = r["text"]
    return out


def source_labels():
    """(pid, norm answer) -> set of labels, from olmo-ifomega's hand gate and this run's calibration source reads."""
    src = _src_texts()
    lab = collections.defaultdict(set)
    n = collections.Counter()
    for r in csv.DictReader(open(RAW / "olmo_ifomega" / "handcheck.csv")):
        k = (r["job"], r["pid"], int(r["chunk"]), int(r["i"]))
        if k in src and r["final_label"]:
            a = answer_of(src[k])
            if a is not None:
                lab[(r["pid"], wsnorm(a))].add(r["final_label"])
                n["ifomega"] += 1
    for r in csv.DictReader(open(RAW / "olmo_transplant" / "handcheck_src.csv")):
        job, pid, ch, i = r["key"].split("|")
        if r["final_label"]:
            a = answer_of(src[(job, pid, int(ch), int(i))])
            lab[(pid, wsnorm(a))].add(r["final_label"])
            n["src_reads"] += 1
    return lab, n


def run_reads():
    rows = list(csv.DictReader(open(RAW / "olmo_transplant" / "handcheck.csv")))
    return {r["key"]: r for r in rows}


def strict_successes():
    """All strict successes of the run under my re-grade: key -> dict(job, writer, pid, cell, trace, norm, finish)."""
    out = {}
    for job in RUN_JOBS:
        g = {}
        with gzip.open(OUT / "regrade" / f"{job}.jsonl.gz", "rt") as f:
            for ln in f:
                r = json.loads(ln)
                g[r["key"]] = r
        for r in iter_gz(ART / "samples" / f"{job}.jsonl.gz"):
            k = f"{job}|{r['rid']}|{r['i']}"
            if not g[k]["strict"]:
                continue
            a = answer_of("</think>" + r["text"])
            out[k] = {"key": k, "job": job, "writer": r["writer"], "pid": r["pid"], "cell": cell_of(r),
                      "trace": r.get("trace", ""), "norm": wsnorm(a), "finish": r["finish"], "rid": r["rid"]}
    return out


def table(override=None, r6_strict=False, ignore_run_reads=False, mine=None):
    """Label every strict success. override: {key: label} replaces the executor's label on its read items.
    mine: {key: label} from the reviewer's own re-read (every covered sample key); it takes precedence and propagates
    to identical answers on the same prompt; then the executor's reads, source labels, run-read identity, unread.
    r6_strict: items the executor's table flags r6 become gamed (with mine: items my readers flag all-caps)."""
    ss = strict_successes()
    slab, _ = source_labels()
    reads = {} if ignore_run_reads else run_reads()
    # labels of this run's reads, by key and by (pid, norm)
    rlab = {}
    for k, r in reads.items():
        lab = r["final_label"]
        if override and k in override:
            lab = override[k]
        if r6_strict and r.get("r6") == "True":
            lab = "gamed"
        if lab:
            rlab[k] = lab
    run_by_norm = collections.defaultdict(set)
    for k, lab in rlab.items():
        if k in ss:
            run_by_norm[(ss[k]["pid"], ss[k]["norm"])].add(lab)
    mine_key, mine_norm = {}, collections.defaultdict(set)
    if mine:
        for k, lab in mine.items():
            if k in ss:
                mine_key[k] = lab
                mine_norm[(ss[k]["pid"], ss[k]["norm"])].add(lab)
    rows = []
    for k, s in ss.items():
        pn = (s["pid"], s["norm"])
        if k in mine_key:
            src, lab = "mine", mine_key[k]
        elif pn in mine_norm:
            src, lab = "mine_inh", sorted(mine_norm[pn])[0] if len(mine_norm[pn]) == 1 else "conflict"
        elif k in rlab:
            src, lab = "read", rlab[k]
        elif pn in slab:
            src, lab = "inh_src", sorted(slab[pn])[0] if len(slab[pn]) == 1 else "conflict"
        elif pn in run_by_norm:
            src, lab = "inh_run", sorted(run_by_norm[pn])[0] if len(run_by_norm[pn]) == 1 else "conflict"
        else:
            src, lab = "unread", ""
        rows.append({**s, "src": src, "label": lab})
    return rows


def genuine_counts(rows):
    """{(job, pid, cell): (strict, labelled, labelled_genuine, unread)} for the share rule."""
    c = collections.defaultdict(lambda: [0, 0, 0, 0])
    for r in rows:
        x = c[(r["job"], r["pid"], r["cell"])]
        x[0] += 1
        if r["label"] in ("genuine", "gamed"):
            x[1] += 1
            x[2] += r["label"] == "genuine"
        else:
            x[3] += 1
    return {k: tuple(v) for k, v in c.items()}


if __name__ == "__main__":
    rows = table()
    slab, n = source_labels()
    conf = [r for r in rows if r["label"] == "conflict"]
    by = collections.Counter((r["job"], r["src"]) for r in rows)
    print("source labels:", dict(n), "distinct (pid, answer) labelled:", len(slab),
          "with conflicting labels:", sum(len(v) > 1 for v in slab.values()))
    print("strict successes:", len(rows), "label sources:", dict(sorted(by.items())))
    print("conflicts:", len(conf))
    gc = genuine_counts(rows)
    nolab = [(k, v) for k, v in gc.items() if v[1] == 0]
    print("cells with strict successes but no labelled success:", len(nolab))
    for (job, pid, cell), v in sorted(nolab):
        print("  ", job, pid, cell, v)
    reads = run_reads()
    ss = {r["key"] for r in rows}
    print("run reads:", len(reads), "of which strict successes of the run (my re-grade):", sum(k in ss for k in reads),
          "final labels", dict(collections.Counter(r["final_label"] for r in reads.values())),
          "r6 flagged", sum(r["r6"] == "True" for r in reads.values()))
