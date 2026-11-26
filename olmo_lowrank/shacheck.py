#!/usr/bin/env python3
"""sha256 of every *.safetensors file of local checkpoint dirs against olmo_weights/manifest/checkpoints.csv (pod side).
  shacheck.py <dir> <label> [<dir> <label> ...]   -> one line per file and a PASS / FAIL line per checkpoint"""
import csv, os, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ckpt import sha256_file  # noqa: E402
M = {r["label"]: r for r in csv.DictReader(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                                              "olmo_weights", "manifest", "checkpoints.csv")))}
a = sys.argv[1:]
for d, label in zip(a[0::2], a[1::2]):
    r = M[label]
    want = dict(zip(r["files"].split(";"), r["sha256"].split(";")))
    have = sorted(f for f in os.listdir(d) if f.endswith(".safetensors"))
    with ThreadPoolExecutor(8) as ex:
        got = dict(zip(have, ex.map(lambda f: sha256_file(os.path.join(d, f)), have)))
    bad = [f for f in want if got.get(f) != want[f]] + [f for f in got if f not in want]
    for f in sorted(set(want) | set(got)):
        print(label, f, "ok" if got.get(f) == want.get(f) else f"MISMATCH have={got.get(f)} want={want.get(f)}")
    print(f"SHA_{'PASS' if not bad else 'FAIL'} {label} {d} files={len(got)} expected={len(want)}", flush=True)
