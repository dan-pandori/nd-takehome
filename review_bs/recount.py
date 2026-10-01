#!/usr/bin/env python3
"""Reviewer recount (best-state): per eval file, solved counts from the stored accepted-proof lists, consistency of
n_ok / n_tried / reasons, per-stratum truncation (env action/step caps), and the pre-registered headline quantities."""
import json, glob, os, collections, re, sys
R = os.path.expanduser('~/review/best-state')
E = f'{R}/artifacts/bs/eval'
def rd(fn): return [json.loads(l) for l in open(fn) if l.strip()]
rr600 = {r['name']: r for r in rd(f'{R}/data/ladder/transfer_long_rr600.jsonl')}
Q = {n for n, r in rr600.items() if r['source'] == 'gen' and 13 <= r['L_true'] <= 16}
assert len(Q) == 380
tb_dev = {json.loads(l)['prompt'] for l in open(f'{R}/data/eval_only/textbook72/textbook_dev.jsonl')}
def tb_bin(r):
    if r['prompt'] not in tb_dev: return 'train14'
    L = r['reference_lines']; return '1-5' if L <= 5 else '6-10' if L <= 10 else '11-15' if L <= 15 else '16+'
def reasons(r):
    rs = r['reasons']
    if isinstance(rs, dict): return rs
    return collections.Counter(rs)
def trunc(rs): return sum(v for k, v in rs.items() if 'truncated' in k or 'step cap' in k or 'step_cap' in k)
out = {}
for fn in sorted(glob.glob(f'{E}/*.jsonl')):
    tag = os.path.basename(fn)[:-6]
    rows = rd(fn)
    pool = tag.split('__')[1] if '__' in tag else 'held'
    d = dict(n=len(rows), solved=sum(1 for r in rows if r['proofs']), flag_solved=sum(1 for r in rows if r['solved']),
             n_ok=sum(r['n_ok'] for r in rows), n_tried=sum(r['n_tried'] for r in rows),
             distinct=sum(len(r['proofs']) for r in rows))
    # n_ok == n_tried - (# failure reasons)
    d['bad_rows'] = sum(1 for r in rows if r['n_ok'] != r['n_tried'] - sum(reasons(r).values()))
    d['flag_vs_proofs'] = sum(1 for r in rows if bool(r['solved']) != bool(r['proofs']))
    tr = collections.Counter(); tn = collections.Counter()
    for r in rows:
        if pool.startswith('tb72'): s = tb_bin(r)
        elif pool.startswith('rr600'): s = 'Q' if r['name'] in Q else 'other'
        else: s = 'all'
        tr[s] += trunc(reasons(r)); tn[s] += r['n_tried']
    d['trunc'] = {s: [tr[s], tn[s], round(tr[s] / tn[s], 5)] for s in tn}
    d['trunc_all'] = round(sum(tr.values()) / max(1, sum(tn.values())), 5)
    if pool.startswith('rr600'):
        d['Q'] = sum(1 for r in rows if r['name'] in Q and r['proofs'])
        d['nQ'] = sum(1 for r in rows if r['name'] in Q)
    if pool.startswith('tb72'):
        d['bins'] = dict(collections.Counter(tb_bin(r) for r in rows if r['proofs']))
        d['dev58'] = sum(1 for r in rows if r['proofs'] and r['prompt'] in tb_dev)
    if pool.startswith('h250'):
        # unbiased pass@k from n_ok of n_tried at k = n_tried is just solved; also pass@1 mean
        d['pass1'] = sum(r['n_ok'] / r['n_tried'] for r in rows) / len(rows)
    sj = fn[:-1]  # .json summary
    if os.path.exists(sj):
        s = json.load(open(sj)); d['summary_solved'] = s.get('solved'); d['batch'] = s.get('batch')
        d['peak'] = (s.get('env') or {}).get('peak_alloc_gb', s.get('peak_mem_gb'))
        d['args'] = {k: s.get(k) for k in ('k', 'temperature', 'seed', 'max_action', 'max_steps', 'ckpt')}
    out[tag] = d
json.dump(out, open(f'{R}/review_bs/recount.json', 'w'), indent=1)
for t, d in out.items():
    print(t, d['n'], d['solved'], d.get('summary_solved'), 'Q=%s' % d.get('Q') if 'Q' in d else '', 'bad', d['bad_rows'], d['flag_vs_proofs'],
          'trunc', d['trunc_all'], 'max_stratum', max(v[2] for v in d['trunc'].values()), d.get('batch'), d.get('args', {}).get('ckpt'))
