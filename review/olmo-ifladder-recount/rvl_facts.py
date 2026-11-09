"""Facts cited in the review that are not sample counts: commit times of the design files, the executor transcript's
Write times for them, pod creation, worker job lines, model revisions, stated writing times in the documents.
Writes out/facts.txt."""
import json
import re
import subprocess
from pathlib import Path

from rvl_core import ART, CODE, RAW, Tee

P = Tee("facts.txt")
WT = Path.home() / "work" / "olmo-ifladder"
RUN = Path.home() / "runs" / "olmo-ifladder"


def git(*a):
    return subprocess.run(["git", "-C", str(WT), *a], capture_output=True, text=True).stdout.strip()


for f in ["preregistration/olmo-ifladder.md", "olmo_ifladder/interventions.py", "olmo_ifladder/prompts.csv",
          "olmo_ifladder/problems_r2.jsonl", "olmo_ifladder/problems_r3.jsonl", "olmo_ifladder/train_manifest.jsonl",
          "olmo_ifladder/exemplars.csv", "olmo_ifladder/problems_r4.jsonl", "olmo_ifladder/order_r3.txt",
          "olmo_ifladder/order_r4.txt", "olmo_ifladder/lora.py", "olmo_ifladder/handcheck_prompt_if.md"]:
    P(f"commits of {f}: {git('log', '--format=%h %cI', '--', f).replace(chr(10), ' | ')}")
P(f"executor started: {(RUN / 'executor.started').read_text().strip()}")
P(f"pod: {(RUN / 'ifl-a.created').read_text().strip()}; poll log last line: "
  f"{open(RUN / 'poll_ifl-a.log').read().strip().splitlines()[-1][:120]}")
# transcript write times
wt = {}
for line in open(RUN / "executor.claude_1.jsonl"):
    try:
        r = json.loads(line)
    except json.JSONDecodeError:
        continue
    m = r.get("message", {})
    if not isinstance(m, dict) or not isinstance(m.get("content"), list):
        continue
    for x in m["content"]:
        if x.get("type") == "tool_use" and x.get("name") == "Write":
            fp = x["input"].get("file_path", "")
            if fp.endswith(("interventions.py", "preregistration/olmo-ifladder.md", "select.py")):
                wt.setdefault(fp.split("olmo-ifladder/")[-1], []).append(r.get("timestamp"))
P(f"executor transcript Write calls: {wt}")
pre = (RAW / "preregistration" / "olmo-ifladder.md").read_text()
P(f"preregistration states: '{re.search(r'Written [^,]*,', pre).group(0)}'")
iv = (CODE / "interventions.py").read_text()
P(f"interventions.py states: '{re.search(r'Written [^,]*,', iv).group(0)}'")
for ln in open(ART / "logs" / "worker0.log"):
    if ln.startswith(("LINE_START", "LINE_END")):
        s = re.sub(r":: .*job\.sh (\S+).*", r":: job \1", ln.strip())
        s = re.sub(r":: .*lora\.py (\w+).*--arm (\w+).*", r":: lora \1 \2", s)
        s = re.sub(r":: .*fetch\.sh.*steptest.*", ":: fetch + steptest", s)
        P("worker " + s[:100])
for f in ("fetch_dpo.log", "fetch_s2300.log"):
    P(f"{f}: {open(ART / 'logs' / f).read().strip().splitlines()[-1][:140]}")
