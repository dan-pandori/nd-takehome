"""Task 3 (reproducibility): redraw the executor's re-check sample with GNU shuf and compare row-by-row with
_executor_recheck.md. Two variants: all numbered ledger rows, and rows whose status is exactly 'V'.
Seeds/sizes from the file: L1 'yes 42' n=7; L2-L6 'yes 7' n=5. Writes s3_recheck_reproduce.txt."""
import json
import re
import subprocess

from common import LIT, OUT, table_rows

ledger = json.load(open(f"{OUT}/s2_claims.json"))
by = {(r["reader"], r["n"]): r for r in ledger}
rc = [c for _, c in table_rows(f"{LIT}/_executor_recheck.md") if c and re.fullmatch(r"\d+", c[0])]
plan = [("L1", 42, 7)] + [(t, 7, 5) for t in ["L2", "L3", "L4", "L5", "L6"]]
out = []
for variant, pattern in [("all rows", r"^\| [0-9]"), ("status exactly V", r"\| V \|\s*$")]:
    drawn = []
    for tag, seed, k in plan:
        cmd = f"shuf -n {k} --random-source=<(yes {seed}) <(grep -E '{pattern}' {LIT}/_claims_{tag}.md)"
        res = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, check=True).stdout
        for line in res.strip().split("\n"):
            n = int(line.split("|")[1])
            drawn.append((tag, n))
    match = 0
    for (tag, n), c in zip(drawn, rc):
        r = by[(tag, n)]
        frag = re.findall(r'"([^"]{12,})', c[3])
        frag = frag[0].split("…")[0][:40].strip().lower() if frag else ""
        ok = c[1] == tag and r["pid"].startswith(c[2]) and frag in r["claim"].lower()
        match += ok
    out.append(f"{variant}: drawn {len(drawn)}; same reader/id/claim as the executor's row in the same position: "
               f"{match} / {len(rc)}")
    out.append("   drawn rows: " + ", ".join(f"{t} #{n}" for t, n in drawn))
open(f"{OUT}/s3_recheck_reproduce.txt", "w").write("\n".join(out) + "\n")
print("\n".join(out))
