#!/usr/bin/env python3
"""state-readouts part B: independent Lean re-check of the dead-schema solves (VPS; own Lean process per text).

  python3 sr_recheck_b.py [--workers 2]     # -> artifacts/state-readouts/recheck_b.json (+ a printed table)

For every re-read (artifacts/state-readouts/rr/<label>__<tb|tbl>.jsonl) and every theorem of a dead schema it counts as
solved (n_ok >= 1), take the first Lean-accepted literal text for that prompt from the pod's LEAN_GATE_DUMP
(dump/rr_<label>__<pool>.jsonl.gz) and check it with sr_recheck.py's statement builder and Lean call. Accounting:
a counted solve without an accepted literal text in the dump is reported. Negative controls: the same texts with one
connective of the first `have` type flipped must be rejected.
"""
import argparse, glob, gzip, json, os, collections
from concurrent.futures import ThreadPoolExecutor
from sr_recheck import statement, lean_ok, mutate, LEAN
import subprocess

DEAD = {'demorgan_and_to_nor', 'demorgan_nor_to_and', 'demorgan_or_to_nand', 'dist_and_over_or', 'dist_and_over_or_conv',
        'dist_or_over_and', 'excluded_middle', 'import', 'negated_conditional', 'negated_conditional_conv', 'peirce',
        'peirce_sequent'}
D = 'artifacts/state-readouts'


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--workers', type=int, default=2); a = ap.parse_args()
    pool = {json.loads(l)['name']: json.loads(l) for f in ('data/sr/textbook_transfer.jsonl', 'data/sr/textbook_long.jsonl')
            for l in open(f) if l.strip()}
    jobs, missing = [], []
    for f in sorted(glob.glob(f'{D}/rr/*__tb*.jsonl')):
        tag = os.path.basename(f)[:-6]
        acc = {}
        for l in gzip.open(f'{D}/dump/rr_{tag}.jsonl.gz', 'rt'):
            d = json.loads(l)
            if d.get('lean_ok') and d['prompt'] not in acc:
                acc[d['prompt']] = d['lean_text']
        for l in open(f):
            r = json.loads(l)
            if r['n_ok'] > 0 and pool[r['name']]['schema'] in DEAD:
                if r['prompt'] not in acc:
                    missing.append((tag, r['name'])); continue
                jobs.append((tag, r['name'], acc[r['prompt']]))
    neg = [(t, n, m) for t, n, tx in jobs for m in [mutate(tx)] if m]
    src = lambda n, tx: statement(pool[n]['prompt']) + ' ' + tx
    with ThreadPoolExecutor(a.workers) as ex:
        res = list(ex.map(lambda j: lean_ok(src(j[1], j[2])), jobs))
        nres = list(ex.map(lambda j: lean_ok(src(j[1], j[2])), neg))
    by = collections.defaultdict(lambda: [0, 0])
    for (t, n, tx), ok in zip(jobs, res):
        by[t][0] += ok; by[t][1] += 1
    for t in sorted(by):
        print(f'{t:14s} {by[t][0]:4d} / {by[t][1]:4d} accepted')
    print(f'total {sum(res)} / {len(res)} accepted; counted solves with no accepted literal text in the dump: {len(missing)}')
    print(f'negative controls (one connective flipped): {len(nres) - sum(nres)} / {len(nres)} rejected')
    json.dump({'lean': subprocess.run([LEAN, '--version'], capture_output=True, text=True).stdout.strip(),
               'by_reread': {t: {'accepted': v[0], 'checked': v[1]} for t, v in sorted(by.items())},
               'rejected': [(t, n, tx) for (t, n, tx), ok in zip(jobs, res) if not ok], 'missing_in_dump': missing,
               'negative_controls': {'checked': len(nres), 'rejected': len(nres) - sum(nres),
                                     'accepted': [(t, n, m) for (t, n, m), ok in zip(neg, nres) if ok]}},
              open(f'{D}/recheck_b.json', 'w'), indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main()
