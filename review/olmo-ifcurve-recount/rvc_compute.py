"""Compute and cost of run olmo-ifcurve from the job logs, metas, my re-grade rows and ~/podhours.log.

Per job: every JOB_START / JOB_DONE pair in its queue logs (q_<job>.log, q_<job>_s0.log), wall seconds (GPU-seconds at
TP 1, one H200 per job), the sampler's own t_load_s + t_gen_s (meta), generated tokens (sum of my rows' n_ids) vs the
meta's gen_tokens, draws, checker calls (one strict + one loose grade per draw). Per arm: arm A's own draws (M-job
non-reach chunks, T_s0500), arm B base (M-job reach draws + B jobs), extension (X / X2 / X3 / X4); mixed M jobs are
split by generated tokens. Reused stored draws (olmo-ifomega F_*, olmo-iffu T4 / T4b) are listed with their own
metas (their compute belongs to those runs). Pod dollars and hours: every ~/podhours.log line for the run.
Writes out/compute.txt / .json.
"""
import collections
import datetime as dt
import gzip
import json
import re
from pathlib import Path

from rvc_cells import build
from rvc_core import ART, NEW_JOBS, OLD_JOBS, OUT, SRC, Tee, dump

T = Tee("compute.txt")


def ts(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


def pairs(job):
    logs = [ART / "logs" / f"q_{job}.log", ART / "logs" / f"q_{job}_s0.log"] if job not in OLD_JOBS else [SRC / "meta" / f"q_{job}.log"]
    out = []
    for lg in logs:
        if not lg.exists():
            continue
        st = None
        for ln in open(lg, errors="replace"):
            m = re.match(r"JOB_START \S+ (\S+Z)", ln)
            if m:
                st = ts(m.group(1))
            m = re.match(r"JOB_DONE \S+ rc=(\d+) (\S+Z)", ln)
            if m:
                out.append((st, ts(m.group(2)), int(m.group(1)), lg.name))
                st = None
            if ln.startswith("FETCH_FAIL"):
                out.append((st, None, "fetch_fail", lg.name))
        if st is not None:
            out.append((st, None, "no JOB_DONE", lg.name))
    return out


def main():
    rows, armA, reach, A, B, XC, J = build()
    rset = set(reach)
    res = {"jobs": {}}
    T("job | starts (rc) | wall s | meta t_load+t_gen s | gen tokens mine / meta | draws | tok/s (meta) | cut")
    tot = collections.Counter()
    for job in NEW_JOBS + OLD_JOBS:
        ps = pairs(job)
        wall = sum((b - a).total_seconds() for a, b, rc, _ in ps if a and b)
        mfiles = [ART / "meta" / f"{job}.json", ART / "meta" / f"{job}_stage0.json"] if job not in OLD_JOBS else [SRC / "meta" / f"{job}.json"]
        ms = [json.load(open(f)) for f in mfiles if f.exists()]
        tl = sum(m.get("t_load_s", 0) + m.get("t_gen_s", 0) for m in ms)
        mtok = sum(m.get("gen_tokens", 0) for m in ms)
        ks = [k for k in rows if k[0] == job]
        mytok = sum(rows[k]["n_ids"] for k in ks)
        cut = sum(rows[k]["finish"] == "length" for k in ks)
        tps = [m.get("tok_per_s") for m in ms]
        res["jobs"][job] = {"starts": [(str(a), str(b), rc, f) for a, b, rc, f in ps], "wall_s": wall, "meta_s": tl,
                            "tokens": mytok, "meta_tokens": mtok, "draws": len(ks), "cut": cut, "tok_per_s": tps}
        T(f"   {job:12s} | {len(ps)} ({','.join(str(p[2]) for p in ps)}) | {wall:8.0f} | {tl:8.0f} | {mytok:9d} / {mtok:9d} "
          f"| {len(ks):5d} | {tps} | {cut}")
        if job in NEW_JOBS:
            tot["wall_s"] += wall
            tot["meta_s"] += tl
            tot["tokens"] += mytok
            tot["draws"] += len(ks)
    T(f"new jobs total: wall {tot['wall_s']:.0f} s = {tot['wall_s'] / 3600:.2f} GPU-h (H200, TP 1); sampler-own "
      f"{tot['meta_s'] / 3600:.2f} h; tokens {tot['tokens']:,}; draws {tot['draws']:,}; checker calls {2 * tot['draws']:,} "
      f"(strict + loose per draw; plus my re-grade)")
    res["total_new"] = dict(tot)
    # per arm: token shares within jobs
    arm = collections.Counter()
    armd = collections.Counter()
    for k, r in rows.items():
        job = k[0]
        if job not in NEW_JOBS:
            continue
        if job.startswith("X"):
            a = "B extension"
        elif job.startswith("B_"):
            a = "B base"
        elif job.startswith("T_"):
            a = "A"
        else:  # M jobs
            a = "B base" if k[1] in rset else "A"
        arm[a] += r["n_ids"]
        armd[a] += 1
    jobtok = {j: res["jobs"][j]["tokens"] for j in NEW_JOBS}
    armgs = collections.Counter()
    for k, r in rows.items():
        job = k[0]
        if job not in NEW_JOBS or jobtok[job] == 0:
            continue
        a = ("B extension" if job.startswith("X") else "B base" if job.startswith("B_") else "A" if job.startswith("T_")
             else ("B base" if k[1] in rset else "A"))
        armgs[a] += res["jobs"][job]["wall_s"] * r["n_ids"] / jobtok[job]
    T("per arm (new draws only; M jobs split by tokens; the 42 IFBench reach prompts' arm-A draws are inside 'B base'):")
    for a in ("A", "B base", "B extension"):
        T(f"   {a:12s} draws {armd[a]:6d} tokens {arm[a]:11,d} GPU-s {armgs[a]:9.0f} ({armgs[a] / 3600:.2f} h)")
    res["arms"] = {a: {"draws": armd[a], "tokens": arm[a], "gpu_s": armgs[a]} for a in arm}
    # pods
    ph = [ln.split() for ln in open(Path.home() / "podhours.log") if " olmo-ifcurve " in ln]
    usd = sum(float(x[4]) for x in ph)
    hrs = sum(float(x[3]) for x in ph)
    T(f"~/podhours.log lines for olmo-ifcurve: {len(ph)}; pod-hours {hrs:.2f}; dollars {usd:.2f}")
    by = collections.defaultdict(lambda: [0.0, 0.0])
    for x in ph:
        kind = "orphan pods (amendment 1)" if x[2].startswith("orphan") else x[2]
        by[kind][0] += float(x[3])
        by[kind][1] += float(x[4])
    for kk, (h, u) in sorted(by.items()):
        T(f"   {kk:28s} {h:7.3f} h  ${u:7.2f}  rate {u / h if h else float('nan'):.2f} $/h")
    res["pods"] = {"lines": ph, "usd": usd, "hours": hrs}
    sampled_pods = [x for x in ph if x[2].startswith("ifc-") and x[2] != "ifc-t"]
    sh = sum(float(x[3]) for x in sampled_pods)
    T(f"sampling pods ifc-a..h: {sh:.2f} pod-hours vs new-job wall {tot['wall_s'] / 3600:.2f} GPU-h "
      f"(utilisation {tot['wall_s'] / 3600 / sh:.2f})")
    dump(res, "compute.json")


if __name__ == "__main__":
    main()
