#!/usr/bin/env python3
"""Reviewer (coe-dose01): stream a ladder's LEAN_GATE_DUMP from the bucket and keep
  * every row whose prompt is a strict sigma-covered held-out member (any verdict) -> the literal texts of counted proofs
  * a 1-in-50 sample of other rows that the run recorded as Lean-REJECTED after passing the prefilter (negative controls)
  * a 1-in-200 sample of prefilter-rejected rows (filter != null) -> sent to Lean to check the filter rejects only invalid texts
  python3 dumpfilter.py la_dose01_s0.jsonl.gz
"""
import collections, gzip, json, random, subprocess, sys
sys.path.insert(0, '/home/dan/work/coe-dose01/review_cd01')
from common import BIG, REPO, jl, strict_members

BK = 'hf://buckets/dan-pandori/nd-rl/coe-dose01/artifacts/coe/dump'


def main(fn):
    SM = strict_members()
    tr = {r['name']: r for r in jl(f'{REPO}/data/coe/transfer_track832.jsonl')}
    sp = {tr[n]['prompt']: n for n in SM}
    rng = random.Random(fn)
    p = subprocess.Popen(f'hf buckets cp {BK}/{fn} - 2>/dev/null | zcat', shell=True, stdout=subprocess.PIPE, text=True, bufsize=1 << 20)
    stem = fn.replace('.jsonl.gz', '')
    o_s = gzip.open(f'{BIG}/dump/{stem}_strict.jsonl.gz', 'wt')
    o_r = gzip.open(f'{BIG}/dump/{stem}_leanrej.jsonl.gz', 'wt')
    o_f = gzip.open(f'{BIG}/dump/{stem}_filterrej.jsonl.gz', 'wt')
    c = collections.Counter()
    for line in p.stdout:
        x = json.loads(line)
        st = 'lean_ok' if x.get('lean') is True else 'lean_rej' if x.get('lean') is False else 'filter' if x.get('filter') else 'other'
        c[st] += 1
        if x['prompt'] in sp:
            c['strict_' + st] += 1
            x['name'] = sp[x['prompt']]
            o_s.write(json.dumps(x) + '\n')
        elif st == 'lean_rej' and rng.random() < 0.02:
            o_r.write(json.dumps(x) + '\n')
        elif st == 'filter' and rng.random() < 0.005:
            o_f.write(json.dumps(x) + '\n')
    for o in (o_s, o_r, o_f):
        o.close()
    print(fn, dict(c), 'rc', p.wait())


if __name__ == '__main__':
    main(sys.argv[1])
