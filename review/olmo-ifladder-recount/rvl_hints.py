"""Rung-3 procedure hints of run olmo-ifladder: answer-content and timing checks.

1. Every HINTS entry (interventions.py, pre-registered hash) printed with its constraint description.
2. Mechanical answer-content screen: for every prompt that received a hint (all 58), the hint's content words
   (>= 4 letters, not in a small stop list) that occur in the prompt's BASE request (constraint text removed as in
   rvl_overlap.py) but not in that constraint's own description; and any number in a hint that occurs in the prompt.
3. Timing: the git commit of interventions.py vs the first rung-3 sample (job metas / logs).
Writes out/hints.txt.
"""
import ast
import json
import re
import subprocess
from pathlib import Path

from rvl_core import ART, CODE, Tee, load_csv, upstream_record

P = Tee("hints.txt")
src = (CODE / "interventions.py").read_text()
consts = {}
for node in ast.parse(src).body:
    if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
        try:
            consts[node.targets[0].id] = ast.literal_eval(node.value)
        except ValueError:
            pass
H, D = consts["HINTS"], consts["DESCRIPTIONS"]
P(f"[1] {len(H)} hints; ids with a description {sum(i in D for i in H)}")
for i, h in H.items():
    P(f"  {i}\n     description: {D.get(i)}\n     hint: {h}")
STOP = set("that this with from your each every then them they their there than into word words letter letters "
           "sentence sentences answer response draft check write before after first last line lines more most "
           "same until only number numbers count counts list least exactly times time make keep give using used "
           "other none text".split())
from rvl_overlap import base_of  # my constraint-text removal  # noqa: E402

prompts = load_csv(CODE / "prompts.csv")
flags = []
stats = {}
import collections  # noqa: E402

stats = collections.Counter()
for r in prompts:
    pid = r["pid"]
    task, rec = upstream_record(pid)
    base = set(t for t in base_of(pid, stats) if not t.startswith("\x00"))
    for iid in dict.fromkeys(rec["instruction_id_list"]):
        h = H[iid]
        dw = set(re.findall(r"[a-z']+", (D.get(iid) or "").lower()))
        hw = set(w for w in re.findall(r"[a-z']+", h.lower()) if len(w) >= 4 and w not in STOP)
        common = sorted((hw & base) - dw)
        nums = sorted(set(re.findall(r"\d+", h)) & set(re.findall(r"\d+", rec["prompt"])))
        if common or nums:
            flags.append((pid, iid, common, nums))
P(f"[2] hint content words found in a prompt's base request (not in the constraint's description): {len(flags)} "
  f"(prompt, id) pairs")
for f in flags:
    P(f"    {f[0]} {f[1]}: words {f[2]} numbers {f[3]}")
# 3. timing
wt = Path.home() / "work" / "olmo-ifladder"
log = subprocess.run(["git", "-C", str(wt), "log", "--format=%h %cI", "--", "olmo_ifladder/interventions.py"],
                     capture_output=True, text=True).stdout.strip()
starts = []
for f in sorted((ART / "logs").glob("q_*.log")):
    for m in re.finditer(r"JOB_START (\S+) (\S+) .*problems=(\S+)", open(f, errors="replace").read()):
        if "r3" in m.group(3) or "r4" in m.group(3):
            starts.append((m.group(2), m.group(1), m.group(3)))
P(f"[3] interventions.py commits: {log}; first sampling jobs that used hints: {sorted(starts)[:3]}")
