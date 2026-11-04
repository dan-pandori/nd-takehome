"""Phase 2 (reviewer): my per-cell table (out/cells.csv, from my re-grade) vs the executor's olmo32/results.csv,
field by field on every model x problem cell."""
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
mine = {(r["model"], r["pid"]): r for r in csv.DictReader(open(os.path.join(HERE, "out", "cells.csv")))}
ex = {(r["model"], r["pid"]): r for r in csv.DictReader(open(os.path.join(ROOT, "olmo32", "results.csv")))}
pairs = [("n_fixed", "n_fixed"), ("n_all", "attempts"), ("all_rl", "succ_rl"), ("fixed_rl", "succ_fixed_rl"),
         ("all_final", "succ_final"), ("fixed_final", "succ_fixed_final"), ("all_doubly", "succ_doubly"),
         ("fixed_doubly", "succ_fixed_doubly"), ("first_rl", "first_rl"), ("second_rl", "second_rl"),
         ("first_final", "first_final"), ("second_final", "second_final"), ("first_doubly", "first_doubly"),
         ("second_doubly", "second_doubly")]
norm = lambda v: "" if v in ("", "None", None) else str(int(float(v)))
diff = []
for k in sorted(set(mine) | set(ex)):
    if k not in mine or k not in ex:
        diff.append((k, "missing", k in mine, k in ex)); continue
    for a, b in pairs:
        if norm(mine[k][a]) != norm(ex[k][b]):
            diff.append((k, a, mine[k][a], ex[k][b]))
print(f"cells mine {len(mine)}, executor {len(ex)}; fields compared {len(pairs)} per cell; differences {len(diff)}")
for d in diff[:20]:
    print(" ", d)
