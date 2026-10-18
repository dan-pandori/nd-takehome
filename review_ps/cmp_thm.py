"""Compare reviewer theorem labels with executor artifacts/ps/theorem/<set>.jsonl.gz; print totals."""
import gzip
import json
import sys
from collections import Counter

for name in sys.argv[1:]:
    M = [json.loads(l) for l in gzip.open(f"out/thm_{name}.jsonl.gz", "rt")]
    n = len(M)
    tot = Counter()
    for m in M:
        for k in ("cv", "iv", "co", "dneg_syn", "dneg_sem", "inc", "sc_syn", "sc_sem"):
            tot[k] += bool(m[k])
    pr = lambda k: f"{k}={tot[k]} ({100 * tot[k] / n:.2f}%)"  # noqa: E731
    print(f"== {name} n={n}: " + " ".join(pr(k) for k in ("co", "dneg_syn", "dneg_sem", "sc_syn", "sc_sem", "inc")),
          "| not classically valid", n - tot["cv"])
    try:
        T = [json.loads(l) for l in gzip.open(f"../artifacts/ps/theorem/{name}.jsonl.gz", "rt")]
    except FileNotFoundError:
        print("   (no executor theorem file)")
        continue
    d = Counter()
    for m, t in zip(M, T):
        assert m["i"] == t["i"]
        if m["co"] != t["classical"]:
            d["classical-only"] += 1
        if m["dneg_sem"] != t["dneg"]:
            d["dneg(sem)"] += 1
        if m["sc_sem"] != t["sigma_cov"]:
            d["sigma_cov(sem)"] += 1
        if m["inc"] != t["inconsistent"]:
            d["inconsistent"] += 1
    print(f"   vs executor ({len(T)} rows): differences {dict(d) if d else 'none'}")
