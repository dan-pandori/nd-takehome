"""Render the per-claim (Task 4) and per-sentence (Task 5) tables for LIT_AUDIT.md from the verdict TSVs.
Writes s7_tables.md."""
from common import OUT


def cell(s, n=None):
    s = s.replace("\\|", "|")
    if n and len(s) > n:
        s = s[: n - 1].rstrip() + "…"
    return s.replace("|", "\\|")


MATCH = {"exact": "verbatim", "markup": "verbatim modulo math markup", "paraphrase": "paraphrase-level",
         "notfound": "not found", "nosource": "source missing"}
rows = [l.rstrip("\n").split("\t") for l in open(f"{OUT}/s4_verdicts.tsv", encoding="utf-8")][1:]
out = ["| # | reader | ledger row | id | quote (abridged) | stated location | finding | line(s) | verdict |",
       "|---|---|---|---|---|---|---|---|---|"]
for k, reader, n, pid, q, loc, m, line, locv, note in rows:
    verdict = f"{MATCH[m]}; location {'OK' if locv == 'OK' else 'WRONG'}"
    out.append(f"| S{k} | {reader} | #{n} | {cell(pid)} | {cell(q, 95)} | {cell(loc, 45)} | {cell(note, 150)} | "
               f"{cell(line)} | {verdict} |")
out.append("")
rows5 = [l.rstrip("\n").split("\t") for l in open(f"{OUT}/s5_verdicts.tsv", encoding="utf-8")][1:]
out += ["| cand. | REVIEW.md line | sentence (abridged) | traced to (ledger rows, all status V) | verdict | note |",
        "|---|---|---|---|---|---|"]
for k, ln, sent, v, trace, note in rows5:
    out.append(f"| R{k} | {ln} | {cell(sent, 160)} | {cell(trace, 170)} | {v} | {cell(note, 230)} |")
open(f"{OUT}/s7_tables.md", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out[:4]))
print("...", len(out), "lines")
