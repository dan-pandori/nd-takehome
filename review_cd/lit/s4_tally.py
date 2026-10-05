"""Tally Task 4 (manual sample verdicts) and the supplementary population scans; checks that the manual resolution
file covers exactly the rows the location heuristic flagged or could not locate. Writes s4_tally.txt."""
import re
from collections import Counter

from common import OUT

out = []
rows = [l.rstrip("\n").split("\t") for l in open(f"{OUT}/s4_verdicts.tsv", encoding="utf-8")][1:]
out.append(f"sampled V claims: {len(rows)}; per reader {dict(sorted(Counter(r[1] for r in rows).items()))}")
m = Counter(r[6] for r in rows)
out.append(f"match: exact/punctuation-only {m['exact']}, math-markup-only {m['markup']}, paraphrase {m['paraphrase']}, "
           f"not found {m['notfound']}, source missing {m['nosource']}")
out.append(f"found verbatim (exact + markup-only): {m['exact'] + m['markup']} / {len(rows)}")
loc = Counter(r[8] for r in rows)
out.append(f"stated location: OK {loc['OK']}, WRONG {loc['WRONG']}")

# population scan buckets
pop = [l.rstrip("\n").split("\t") for l in open(f"{OUT}/s4b_population.tsv", encoding="utf-8")][1:]
b = Counter(r[6] for r in pop)
out.append(f"population scan (all V rows): {len(pop)}; " + "; ".join(f"{k}: {v}" for k, v in b.most_common()))
fz = open(f"{OUT}/s4c_fuzzy_diffs.txt").readline().strip()
out.append("fuzzy-diff pass: " + fz)

# location heuristic + manual resolutions
txt = open(f"{OUT}/s4d_location.txt").read()
counts = dict(re.findall(r"^  (consistent|FLAG|n/a [^:]+): (\d+)$", txt, re.M))
flag_rows = set(re.findall(r"^  (L\d) #(\d+) .*\| hits", txt, re.M))
unloc = txt.split("rows with no fragment located")[1]
unloc_rows = set(re.findall(r"^  (L\d) #(\d+) ", unloc, re.M))
res = [l.rstrip("\n").split("\t") for l in open(f"{OUT}/s4d_resolutions.tsv", encoding="utf-8")][1:]
res_rows = {(r[0], r[1]) for r in res}
need = flag_rows | unloc_rows
out.append(f"location heuristic: {counts}; flagged {len(flag_rows)}, unlocated {len(unloc_rows)}; manual resolutions "
           f"{len(res_rows)}; missing resolutions {sorted(need - res_rows)}; extra resolutions {sorted(res_rows - need)}")
rc = Counter(r[2] for r in res)
consistent_total = int(counts.get("consistent", 0)) + rc["consistent"]
out.append(f"after manual resolution: consistent {consistent_total}, inconsistent {rc.get('inconsistent', 0)}; "
           f"not checkable by the heuristic {len(pop) - consistent_total - rc.get('inconsistent', 0)}")
open(f"{OUT}/s4_tally.txt", "w").write("\n".join(out) + "\n")
print("\n".join(out))
