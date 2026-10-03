#!/usr/bin/env python3
"""step_check_validate.py -- the gate on `step_check.check` (run `guided-tts`): its verdict against Lean's on distinct
(state, step) pairs dumped by `guided_eval.py --dump` (each step as a standalone Lean theorem whose binders are the
state's hypotheses).

  python3 step_check_validate.py --out artifacts/gt/validate.json artifacts/gt/eval/*.steps.jsonl.gz

Prints and writes the 2 x 2 table.  A false reject (checker rejects, Lean accepts) disqualifies the checker
(brief: >= 50,000 steps, 0 false rejects); every false reject is written out in full.  Checker-pass / Lean-reject
steps are harmless (Lean judges the finished proof) and are counted by the checker's coverage.
"""
import argparse, collections, gzip, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lean_gate import check_sources


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    seen = {}
    for fn in a.files:
        for l in gzip.open(fn, 'rt'):
            d = json.loads(l)
            seen.setdefault(d['src'], d['verdict'])
    srcs = list(seen)
    ok, wall, cpu = check_sources(srcs)
    tab = collections.Counter()
    by_reason = collections.defaultdict(collections.Counter)
    false_rej = []
    for s, lean_ok in zip(srcs, ok):
        v = seen[s]
        tab[('checker_reject' if v else 'checker_pass', 'lean_accept' if lean_ok else 'lean_reject')] += 1
        if v:
            by_reason[v]['lean_accept' if lean_ok else 'lean_reject'] += 1
        if v and lean_ok:
            false_rej.append(dict(src=s, verdict=v))
    out = dict(files=a.files, n_steps=len(srcs), table={f'{x}/{y}': n for (x, y), n in tab.items()},
               by_reason={k: dict(v) for k, v in by_reason.items()}, false_rejects=len(false_rej),
               false_reject_examples=false_rej[:200], lean_wall_s=wall, lean_proc_s=cpu,
               gate_passed=len(srcs) >= 50000 and not false_rej)
    json.dump(out, open(a.out, 'w'), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ('false_reject_examples', 'files')}, indent=1))


if __name__ == '__main__':
    main()
