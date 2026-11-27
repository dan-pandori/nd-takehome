"""Compute and cost of run olmo-lowrank from the job logs (my own parse): per arm the job wall time on its GPU
(JOB_START -> JOB_DONE in artifacts/olmo_lowrank/logs/**/q_*.log, every attempt), generated tokens summed over the
arm's rows (n_tok), draws, cut share; Part-1 jobs from logs/lr-e/spectra_*.log; pod-hours and dollars from
~/podhours.log (deleted pods of the run) with the billed rate each implies. -> out/compute.json, out/compute.txt"""
import glob
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from rvr_core import ARMS, ART, OUT, Tee, iter_job


def ts(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


def main():
    T = Tee("compute.txt")
    jobs = defaultdict(list)
    for f in sorted(glob.glob(str(ART / "logs" / "**" / "q_*.log"), recursive=True)):
        txt = open(f, errors="replace").read()
        st = re.findall(r"^JOB_START (\S+) (\S+Z)", txt, re.M)
        dn = re.findall(r"^JOB_DONE (\S+) rc=(\d+) (\S+Z)", txt, re.M)
        for (j, a), (j2, rc, b) in zip(st, dn):
            jobs[(j, f.split("/logs/")[1])].append((a, b, int(rc), (ts(b) - ts(a)).total_seconds()))
    # de-duplicate the same attempt seen in two copies of a log (logs/q_X.log and logs/lr-?/q_X.log)
    att = defaultdict(set)
    for (j, f), v in jobs.items():
        for a, b, rc, s in v:
            att[j].add((a, b, rc, s, "stage0" if "stage0" in f else "main"))
    res = {"arms": {}}
    dpo_tok = None
    for arm in ARMS:
        n = tok = cut = 0
        for r in iter_job(arm):
            n += 1
            tok += r["n_tok"]
            cut += r["finish"] == "length"
        a = sorted(att.get(arm, set()))
        secs = sum(x[3] for x in a)
        res["arms"][arm] = {"draws": n, "gen_tokens": tok, "cut": cut, "cut_share": round(cut / n, 5), "attempts": a,
                            "gpu_seconds": secs, "gpu": "NVIDIA H200"}
        if arm == "dpo":
            dpo_tok = tok
    for arm, d in res["arms"].items():
        d["tokens_vs_dpo"] = round(d["gen_tokens"] / dpo_tok, 3)
        d["flag_1.25x"] = d["gen_tokens"] > 1.25 * dpo_tok
    # Part 1 jobs (lr-e, one GPU)
    p1 = {}
    for f in glob.glob(str(ART / "logs" / "lr-e" / "spectra_*.log")):
        txt = open(f, errors="replace").read()
        m = re.search(r"job (\S+) done in (\d+) s", txt)
        p1[Path(f).stem] = int(m.group(2)) if m else None
    res["part1_jobs_wall_s"] = p1
    res["part1_gpu"] = json.load(open(ART / "spectra" / "R32" / "summary.json")).get("gpu")
    # pod ledger
    led = []
    for ln in open(Path.home() / "podhours.log"):
        x = ln.split()
        if len(x) >= 5 and x[1] == "olmo-lowrank":
            led.append({"utc": x[0], "pod": x[2], "hours": float(x[3]), "usd": float(x[4]), "gpu": " ".join(x[5:]),
                        "rate": round(float(x[4]) / float(x[3]), 3) if float(x[3]) else None})
    res["ledger"] = led
    ex = [l for l in led if not l["pod"].startswith("rv-")]
    res["executor_total"] = {"hours": round(sum(l["hours"] for l in ex), 4), "usd": round(sum(l["usd"] for l in ex), 2)}
    res["reviewer_total"] = {"hours": round(sum(l["hours"] for l in led if l["pod"].startswith("rv-")), 4),
                             "usd": round(sum(l["usd"] for l in led if l["pod"].startswith("rv-")), 2)}
    json.dump(res, open(OUT / "compute.json", "w"), indent=1, default=str)
    for arm, d in res["arms"].items():
        T(f"{arm:5s} draws {d['draws']} gen_tokens {d['gen_tokens']:>9,} ({d['tokens_vs_dpo']:.2f}x dpo{' FLAG' if d['flag_1.25x'] else ''}) "
          f"cut {d['cut']} ({d['cut_share']:.4f}) GPU-s {d['gpu_seconds']:.0f} attempts {[(x[0], x[1], x[2], x[4]) for x in d['attempts']]}")
    T("part1 jobs (s):", p1, res["part1_gpu"])
    for l in led:
        T("ledger", l)
    T("executor total", res["executor_total"], "reviewer", res["reviewer_total"])


if __name__ == "__main__":
    main()
