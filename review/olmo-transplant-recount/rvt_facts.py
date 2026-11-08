"""Facts the review cites that live outside the sample files: git hashes and commit times, pod and job times, template
hashes per job meta, the R_dpo resume line. Output: out/facts.txt"""
import json
import re
import subprocess
from pathlib import Path

from rvt_core import ART, RAW, Tee, load_jsonl

P = Tee("facts.txt")
WT = Path.home() / "work" / "olmo-transplant"


def git(*a):
    return subprocess.run(["git", "-C", str(WT), *a], capture_output=True, text=True).stdout.strip()


P(f"nd_verify tree: HEAD {git('rev-parse', '1b7fcebe:nd_verify')} origin/main {git('rev-parse', 'origin/main:nd_verify')} "
  f"base {git('rev-parse', 'c0c6e053:nd_verify')}")
P(f"TEST_RUN_DONE blob: HEAD {git('rev-parse', '1b7fcebe:artifacts/TEST_RUN_DONE')} origin/main "
  f"{git('rev-parse', 'origin/main:artifacts/TEST_RUN_DONE')}")
for c in ("0fea68ab", "15a4522d", "1b7fcebe"):
    P(f"commit {c}: {git('show', '-s', '--format=%cI %s', c)[:120]}")
for f, pat in ((Path.home() / "podbudget.log", "olmo-transplant"), (Path.home() / "pods.log", "ot-1|ot-2")):
    for ln in open(f, errors="replace"):
        if re.search(pat, ln) and "2026-11-08" in ln:
            P(f"{f.name}: {ln.strip()[:160]}")
for ln in open(Path.home() / "runs" / "olmo-transplant" / "poll_ot-1.log"):
    if "ready" in ln:
        P(f"poll_ot-1.log: {ln.strip()[:160]}")
        break
for job in ("R_dpo", "R_s2300", "C_dpo", "C_s2300", "F_s2300"):
    m = load_jsonl(ART / "meta" / f"{job}.json")[-1]
    P(f"meta {job}: template_sha256 {m.get('template_sha256', 'absent')}")
for ln in open(ART / "logs" / "q_R_dpo.log", errors="replace"):
    if "rewrote" in ln or "groups to run" in ln:
        P(f"q_R_dpo.log: {ln.strip()[:160]}")
for ln in open(ART / "logs" / "q_R_dpo_part1.log", errors="replace"):
    if "JOB_START" in ln:
        P(f"q_R_dpo_part1.log: {ln.strip()[:160]}")
