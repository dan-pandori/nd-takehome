"""Every check made inline during the review, re-run in one place with saved output (out/phase2_checks.txt).

  1. hard constraints: nd_verify tree vs origin/main, TEST_RUN_DONE blob, judge use in the run's code, changed paths
  2. MANIFEST rows of the run vs local files (sha256) and the bucket listing
  3. timing: prereg commit, first pod (~/pods.log), first sample (JOB_START), 2c addition vs T2c start
  4. results.csv (executor) vs my re-grade, per (job, prompt)
  5. s2300's strict rate with the hint vs its olmo-ifomega rate (fixed phase = 8 draws; all draws)
  6. two-sided 95 % Clopper-Pearson intervals of test 1's sound rates
  7. test-1 length quartiles: nearest-rank (executor's q) vs interpolated
  8. test-3 per-constraint passes
  9. inherited / predecessor numbers from the predecessor reviewer's re-grade (review/olmo-ifomega-recount/out/
     regrade_all.jsonl.gz): s2300 omega / rl on 068 / 069 at 32k; dpo credits on 055 / 068 / 069 at 32k
"""
import collections
import csv
import gzip
import hashlib
import json
import math
import re
import statistics as st
import subprocess

import rvi_core as C

WT = C.KIT.parent.parent
LINES = []


def say(s=""):
    LINES.append(s)
    print(s)


def git(*a):
    return subprocess.run(["git", "-C", str(WT), *a], capture_output=True, text=True).stdout.strip()


def rows(job):
    return [json.loads(ln) for ln in gzip.open(C.OUT / "regrade" / f"{job}.jsonl.gz", "rt")]


def main():
    say("1. hard constraints")
    say(f"   nd_verify tree HEAD {git('rev-parse', 'HEAD:nd_verify')} origin/main {git('rev-parse', 'origin/main:nd_verify')}")
    say(f"   TEST_RUN_DONE HEAD {git('rev-parse', 'HEAD:artifacts/TEST_RUN_DONE')} origin/main "
        f"{git('rev-parse', 'origin/main:artifacts/TEST_RUN_DONE')} branch point {git('rev-parse', '671bf753:artifacts/TEST_RUN_DONE')}")
    hits = subprocess.run(["grep", "-rn", r"nd_verify\|verify_text\|lean_check", str(WT / "olmo_iffu"), str(WT / "pod" / "olmo_iffu")],
                          capture_output=True, text=True).stdout.strip().splitlines()
    say(f"   judge mentions in olmo_iffu/ and pod/olmo_iffu/: {hits if hits else 'none'}")
    changed = git("diff", "--name-only", "671bf753", "e57060d0").splitlines()
    other = [p for p in changed if not re.match(r"(olmo_iffu/|artifacts/olmo_iffu/|artifacts/olmo-iffu/|pod/olmo_iffu/|"
                                                r"preregistration/olmo-iffu.md|figures/olmo_iffu)", p)]
    say(f"   files changed by the run (branch point .. e57060d0): {len(changed)}; outside its own paths: {other}")
    say(f"   deletions in that diff: {git('diff', '--shortstat', '671bf753', 'e57060d0')}")

    say("\n2. MANIFEST and bucket")
    man = [json.loads(ln[1:]) for ln in git("diff", "671bf753", "e57060d0", "--", "artifacts/MANIFEST.jsonl").splitlines()
           if ln.startswith("+{")]
    ok = sum(hashlib.sha256((C.RAW / r["path"]).read_bytes()).hexdigest() == r["sha256"] for r in man)
    bls = {ln.split()[-1]: int(ln.split()[0]) for ln in (C.SCR / "bucket_ls.txt").read_text().splitlines()
           if ln.split() and ln.split()[0].isdigit()}
    inb = sum(bls.get("olmo-iffu/" + r["path"]) == r["bytes"] for r in man)
    say(f"   MANIFEST rows added {len(man)}; local sha256 match {ok}; in the bucket listing with the same size {inb}; "
        f"bucket files {len(bls)}")

    say("\n3. timing")
    say(f"   prereg first commit {git('log', '--format=%h %aI', '--reverse', '--', 'preregistration/olmo-iffu.md').splitlines()[0]}")
    pods = [ln for ln in open(C.KIT.parent.parent.parent.parent / "pods.log") if "olmo-iffu" in ln]
    say(f"   pods.log: {[ln.split()[0] + ' ' + ln.split()[1] for ln in pods]}")
    starts = {}
    for f in (C.ART / "logs").glob("q_*.log"):
        for ln in open(f, errors="replace"):
            m = re.match(r"JOB_START (\S+) (\S+)", ln)
            if m:
                starts[m.group(1)] = m.group(2)
    say(f"   JOB_START: {dict(sorted(starts.items(), key=lambda kv: kv[1]))}")
    say(f"   2c addition commit: {git('log', '--format=%h %aI %s', '-1', 'a9b234f1')}")

    say("\n4. results.csv vs my re-grade")
    mine = {}
    for j in C.JOBS:
        for r in rows(j):
            d = mine.setdefault((j, r["pid"]), collections.Counter())
            d["draws"] += 1
            d["cut"] += r["finish"] == "length"
            for k in ("strict", "loose", "omega", "rl"):
                d[k] += bool(r.get(k))
            d["doubly"] += bool(r.get("omega") and r.get("rl"))
            d["any"] += bool(r.get("omega") or r.get("rl"))
            d["no_answer"] += not r["think_end"]
    ex = list(csv.DictReader(open(WT / "olmo_iffu" / "results.csv")))
    diff = []
    for r in ex:
        m = mine.get((r["job"], r["pid"]))
        for col in ("draws", "cut", "strict", "loose", "omega", "rl", "doubly", "any", "no_answer"):
            if r.get(col) not in (None, "") and (m is None or int(float(r[col])) != m[col]):
                diff.append((r["job"], r["pid"], col, r[col], None if m is None else m[col]))
    say(f"   rows {len(ex)}; differences {diff if diff else 'none'}")

    say("\n5. s2300 strict rate with the hint vs olmo-ifomega")
    b = json.load(open(C.OUT / "before.json"))["cells"]
    s = json.load(open(C.OUT / "stats.json"))
    for t in ("test2", "test2c"):
        lf, la = [], []
        for p, v in s[t].items():
            c = b[f"s2300|{p}"]
            fix = sum(1 for d in c["succ"] if d[0].startswith("F_")) / 8
            h = v["s_strict"] / 16
            if h < fix:
                lf.append(f"{p} {v['s_strict']}/16 < {fix * 8:.0f}/8")
            if h < c["strict"] / c["draws"]:
                la.append(f"{p} {v['s_strict']}/16 < {c['strict']}/{c['draws']}")
        say(f"   {t}: below the fixed phase on {len(lf)}: {lf}")
        say(f"   {t}: below all olmo-ifomega draws on {len(la)}: {la}")

    say("\n6. test 1 sound-rate CP intervals (two-sided 95 %)")

    def cdf(k, n, p):
        return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))

    def bis(f):
        lo, hi = 0.0, 1.0
        for _ in range(200):
            m = (lo + hi) / 2
            lo, hi = (m, hi) if f(m) else (lo, m)
        return (lo + hi) / 2
    for k in (1, 3, 2):
        lo = 0.0 if k == 0 else bis(lambda p: 1 - cdf(k - 1, 64, p) < 0.025)
        hi = bis(lambda p: cdf(k, 64, p) > 0.025)
        say(f"   {k}/64 = {k / 64:.3f} [{lo:.4f}, {hi:.3f}]")

    say("\n7. test 1 finished-length quartiles")
    t1 = rows("T1_dpo")
    for p in ("055", "068", "069"):
        x = sorted(r["n_tok"] for r in t1 if r["pid"].endswith(p) and r["finish"] != "length")
        near = [x[min(len(x) - 1, int(f * len(x)))] for f in (.25, .5, .75)]
        say(f"   {p}: n {len(x)}; nearest-rank {near}; interpolated (inclusive) "
            f"{[round(q, 1) for q in st.quantiles(x, n=4, method='inclusive')]}; max {x[-1]}")

    say("\n8. test 3 per-constraint passes")
    t3 = rows("T3_dpo")
    for p in sorted({r["pid"] for r in t3}, key=lambda q: int(q.split("_")[1])):
        per = [r["per"] for r in t3 if r["pid"] == p]
        say(f"   {p}: {[sum(x[i] for x in per) for i in range(len(per[0]))]} of {len(per)}, jointly {sum(all(x) for x in per)}")

    say("\n9. predecessor re-grade (independent reviewer of olmo-ifomega)")
    cnt = collections.Counter()
    cred = []
    for ln in gzip.open(WT / "review" / "olmo-ifomega-recount" / "out" / "regrade_all.jsonl.gz", "rt"):
        r = json.loads(ln)
        pid = r.get("pid", "")
        if pid.startswith("omega_out_geometry_perpendicular") and pid[-3:] in ("055", "068", "069"):
            k = (r["model"], pid[-3:])
            cnt[k + ("n",)] += 1
            cnt[k + ("omega",)] += bool(r.get("omega"))
            cnt[k + ("rl",)] += bool(r.get("rl"))
            if r["model"] == "dpo" and (r.get("omega") or r.get("rl")):
                cred.append((pid[-3:], r["job"], r["chunk"], r["i"], r["n_tok"], r["finish"]))
    for m in ("dpo", "s2300"):
        say(f"   {m}: " + "; ".join(f"{p}: n {cnt[(m, p, 'n')]}, omega {cnt[(m, p, 'omega')]}, rl {cnt[(m, p, 'rl')]}"
                                     for p in ("055", "068", "069")))
    say(f"   dpo credited draws: {cred}")
    (C.OUT / "phase2_checks.txt").write_text("\n".join(LINES) + "\n")


if __name__ == "__main__":
    main()
