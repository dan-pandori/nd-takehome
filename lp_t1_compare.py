"""lean-prefilter test (c): accepted sets of the T1-round arms from their gate dumps and found files.
    python3 lp_t1_compare.py   -> table on stdout, artifacts/lp/t1/compare.json"""
import gzip, json, collections
R = {}
for a in 'ABCD':
    acc = collections.defaultdict(set); n = collections.Counter()
    with gzip.open(f'artifacts/lp/t1/dump_{a}.jsonl.gz', 'rt') as f:
        for i, l in enumerate(f):
            d = json.loads(l); n['distinct_rows'] += 1
            if d['lean_ok']: acc['all'].add((d['prompt'], d['lean_text']))
    found = {(json.loads(l)['name'], json.loads(l)['norm']) for l in open(f'artifacts/lp/t1/t1_{a}/found_1.jsonl')}
    rnd = json.load(open(f'artifacts/lp/t1/t1_{a}/round_1.json'))
    gl = [json.loads(l) for l in open(f'artifacts/lp/t1/gate_{a}.jsonl')]
    exposed = sum(g['lean_wall_s'] for g in gl)
    R[a] = {'accepted_texts': acc['all'], 'found': found, 'secs': rnd['secs'], 'phase_s': rnd['phase_s'],
            'gate_exposed_s': exposed, 'gate_share': exposed / rnd['secs'], 'lean_proc_s': sum(g['lean_proc_s'] for g in gl),
            'filter_s': sum(g['filter_s'] for g in gl), 'lean_texts': sum(g['lean_texts'] for g in gl),
            'distinct': sum(g['distinct_checked'] for g in gl), 'workers': gl[0]['workers'], 'batch': json.load(open(f'artifacts/lp/t1/t1_{a}/args.json'))['batch']}
out = {}
print('| arm | batch | workers | round s | / A | gate exposed s | gate share | Lean texts | Lean proc s | distinct accepted texts | found_1 proofs |')
print('|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|')
for a, r in R.items():
    print(f"| {a} | {r['batch']} | {r['workers']} | {r['secs']:.0f} | {r['secs'] / R['A']['secs']:.3f} | {r['gate_exposed_s']:.1f} | {100 * r['gate_share']:.1f} % | {r['lean_texts']:,} | {r['lean_proc_s']:.0f} | {len(r['accepted_texts']):,} | {len(r['found']):,} |")
    out[a] = {k: v for k, v in r.items() if k not in ('accepted_texts', 'found')}
    out[a].update(n_accepted_texts=len(r['accepted_texts']), n_found=len(r['found']))
for x, y in (('A', 'B'), ('C', 'D')):
    same = R[x]['accepted_texts'] == R[y]['accepted_texts']; samef = R[x]['found'] == R[y]['found']
    out[f'{x}_vs_{y}'] = {'accepted_texts_identical': same, 'sym_diff': len(R[x]['accepted_texts'] ^ R[y]['accepted_texts']),
                         'found_identical': samef, 'found_sym_diff': len(R[x]['found'] ^ R[y]['found'])}
    print(f'{x} vs {y}:', out[f'{x}_vs_{y}'])
json.dump(out, open('artifacts/lp/t1/compare.json', 'w'), indent=1)
