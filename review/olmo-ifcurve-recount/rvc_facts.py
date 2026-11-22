"""Times and facts cited in the review of run olmo-ifcurve: pre-registration and amendment commits, budget
registration, first pod, first JOB_START of every job (and whether each job started after the amendment that
admitted it), executor start / done, cancelled s0350. Writes out/facts.txt."""
import re
import subprocess
from pathlib import Path

from rvc_core import ART, Tee

T = Tee("facts.txt")
WT = Path.home() / "work" / "olmo-ifcurve"
RUNS = Path.home() / "runs" / "olmo-ifcurve"
log = subprocess.run(["git", "-C", str(WT), "log", "--format=%h %ad %s", "--date=format-local:%Y-%m-%dT%H:%M:%SZ", "--",
                      "preregistration/olmo-ifcurve.md"], capture_output=True, text=True, env={"TZ": "UTC"}).stdout
T("pre-registration commits (UTC):")
for l in reversed(log.strip().splitlines()):
    T("   " + l)
T("executor.started:", (RUNS / "executor.started").read_text().strip(), "| executor.done mtime:",
  subprocess.run(["date", "-u", "-r", str(RUNS / "executor.done"), "+%FT%TZ"], capture_output=True, text=True).stdout.strip())
for l in open(Path.home() / "podbudget.log"):
    if "olmo-ifcurve" in l:
        T("podbudget:", l.strip())
first = sorted(l.split()[0] for l in open(Path.home() / "podhours.log") if " olmo-ifcurve " in l)
T("first ~/podhours.log line:", first[0] if first else None)
pods = [l.strip() for l in open(Path.home() / "pods.log") if "ifc-" in l or "olmo-ifcurve" in l]
T("first ~/pods.log line for the run:", pods[0][:160] if pods else None)
starts = {}
for lg in sorted((ART / "logs").glob("q_*.log")):
    for l in open(lg, errors="replace"):
        m = re.match(r"JOB_START (\S+) (\S+Z)", l)
        if m:
            starts.setdefault(m.group(1), []).append(m.group(2))
T("first JOB_START per job:")
for j, s in sorted(starts.items(), key=lambda x: min(x[1])):
    T(f"   {min(s)}  {j}  ({len(s)} start{'s' if len(s) > 1 else ''})")
T("any log mentioning M_s0350:", [p.name for p in (ART / "logs").glob("*0350*")])
