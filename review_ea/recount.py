"""Reviewer (evidence-atlas, phase 1): independent recount of the whole-proof re-score from the stored per-theorem files.
Own counter: a theorem is solved iff its row stores >= 1 accepted proof string; checks k, pool membership, args, truncation."""
import json, glob, os, collections
E = 'artifacts/atlas'
POOL = {'tb72': ('data/bs/textbook72.jsonl', 256), 'dev': ('data/bs/dev1108.jsonl', 64), 'h250': ('data/bs/holdout250.jsonl', 256)}
pools = {r: [json.loads(l) for l in open(p)] for r, (p, _) in POOL.items()}
out = {}
def read(d, name):
    rows = [json.loads(l) for l in open(f'{d}/{name}.jsonl')]
    model, r = name.split('__'); pf, k = POOL[r]
    assert [x['prompt'] for x in rows] == [x['prompt'] for x in pools[r]], name
    assert all(x['n_tried'] == k for x in rows), name
    solved = [x['name'] for x in rows if len(x['proofs']) > 0]
    assert all(x['solved'] == (len(x['proofs']) > 0) for x in rows)
    nok = sum(x['n_ok'] for x in rows)
    summ = json.load(open(f'{d}/{name}.json')); a = json.load(open(f'{d}/{name}.jsonl.args.json')); g = json.load(open(f'{d}/{name}.jsonl.genstats.json'))
    reasons = collections.Counter(z.split(':')[0] for x in rows for z in x['reasons'] if z)
    return dict(n=len(rows), solved=len(solved), summary_solved=summ['solved'], n_ok_samples=nok, samples=len(rows) * k,
                k=a['k'], T=a['temperature'], seed=a['seed'], batch=a['batch'], max_new=g['max_new'], rows=g['rows'],
                trunc=g['truncated'], trunc_frac=g['truncated'] / g['rows'], peak_alloc_gb=g.get('peak_alloc_gb'),
                sample_wall_s=g.get('sample_wall_s'), utc=a['_meta']['utc'], host=a['_meta']['host'],
                reasons=dict(reasons.most_common(6)), solved_set=sorted(solved))
for d in ('eval', 'eval_mn1024', 'b4096_partial/eval'):
    for f in sorted(glob.glob(f'{E}/{d}/*__*.jsonl')):
        name = os.path.basename(f)[:-6]
        try:
            out[f'{d}/{name}'] = read(f'{E}/{d}', name)
        except Exception as e:
            out[f'{d}/{name}'] = {'error': repr(e)}
json.dump(out, open('review_ea/recount.json', 'w'), indent=1)
print(f'{"read":34s} {"n":>5s} {"solv":>5s} {"summ":>5s} {"k":>4s} {"T":>4s} {"sd":>2s} {"batch":>5s} {"mxn":>5s} {"trunc%":>7s} {"peakGB":>6s} {"wall":>6s}')
for n, v in out.items():
    if 'error' in v: print(n, v['error']); continue
    print(f'{n:34s} {v["n"]:5d} {v["solved"]:5d} {v["summary_solved"]:5d} {v["k"]:4d} {v["T"]:4.1f} {v["seed"]:2d} {v["batch"]:5d} {v["max_new"]:5d} {100*v["trunc_frac"]:7.3f} {v["peak_alloc_gb"] or 0:6.2f} {v["sample_wall_s"] or 0:6.0f}')
# seed table
print('\ncell table (eval, max_new 512): per seed solved')
for m in ('c0fz', 'c0t1', 'k12fz', 'k12t1'):
    print(m, {r: [out[f'eval/{m}_s{s}__{r}']['solved'] for s in (0, 1)] for r in ('tb72', 'h250', 'dev')})
# truncation re-reads
print('\nmax_new 512 vs 1024 (same seed/batch)')
for n, v in out.items():
    if n.startswith('eval_mn1024/') and 'error' not in v:
        a = out['eval/' + n.split('/')[1]]
        A, B = set(a['solved_set']), set(v['solved_set'])
        print(f'{n:34s} 512:{a["solved"]:5d} trunc {100*a["trunc_frac"]:.3f}%  1024:{v["solved"]:5d} trunc {100*v["trunc_frac"]:.3f}%  only512 {len(A-B)} only1024 {len(B-A)}')
