"""My re-grade vs the run's per-row grades (artifacts/olmo_ifcurve/rows/*.csv: strict, loose, think_end, finish, n_tok,
think_tok, ans_tok, think_words, ans_words) for every row of every job the run uses. Writes out/gradecmp.txt."""
import collections
import gzip
import json

from rvc_core import ALL_JOBS, ART, OUT, Tee, load_csv

T = Tee("gradecmp.txt")
tot = collections.Counter()
ex = collections.defaultdict(list)
for job in ALL_JOBS:
    mine = {}
    with gzip.open(OUT / "regrade" / f"{job}.jsonl.gz", "rt") as f:
        for ln in f:
            r = json.loads(ln)
            mine[(r["pid"], int(r["chunk"]), int(r["i"]))] = r
    theirs = {(r["pid"], int(r["chunk"]), int(r["i"])): r for r in load_csv(ART / "rows" / f"{job}.csv")}
    c = collections.Counter()
    c["mine"], c["theirs"], c["both"] = len(mine), len(theirs), len(set(mine) & set(theirs))
    for k in set(mine) & set(theirs):
        a, b = mine[k], theirs[k]
        for f, x, y in (("strict", a["strict"], b["strict"] == "1"), ("loose", a["loose"], b["loose"] == "1"),
                        ("think_end", a["n_close"] > 0, b["think_end"] == "1"), ("finish", a["finish"], b["finish"]),
                        ("n_tok", a["n_ids"], int(b["n_tok"])),
                        ("ans_words", a["ans_words"], int(b["ans_words"]) if b["ans_words"] not in ("", None) else None),
                        ("think_words", a["think_words"], int(b["think_words"]) if b["think_words"] not in ("", None) else None),
                        ("think_tok", a["think_tok"], int(b["think_tok"]) if b["think_tok"] not in ("", None) else None),
                        ("ans_tok", a["ans_tok"], int(b["ans_tok"]) if b["ans_tok"] not in ("", None) else None)):
            if x != y:
                c[f"diff_{f}"] += 1
                if len(ex[f]) < 4:
                    ex[f].append((job, k, x, y))
    T(f"{job:12s} " + " ".join(f"{k}={v}" for k, v in sorted(c.items())))
    tot.update(c)
T("TOTAL", dict(tot))
for f, v in ex.items():
    T("examples", f, v)
