"""Build the reviewer's Lean re-check sample: >=100 counted proofs per arm, deliberately
over-weighting the long proofs that carry the run's claims."""
import sys, os, json, glob, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '/home/dan/review/cap-horizon')
import rvlib

ROOT = '/home/dan/review/cap-horizon'
ARMS = {'K6': 'c0', 'K8flat': 'a3', 'K8add': 'k8add', 'K10': 'k10', 'K12': 'k12', 'K14': 'k14'}
TR = {r['name']: r for r in rvlib.rd(f'{ROOT}/data/ladder/transfer.jsonl')}
PROMPTS = {}
for fn in ('data/p2/targets_reductio_req.jsonl', 'data/r3_1/depth3_req.jsonl'):
    for r in rvlib.rd(f'{ROOT}/{fn}'):
        PROMPTS[r['name']] = r['prompt']

cov = collections.defaultdict(list)
for r in rvlib.rd(f'{ROOT}/rv/out_cov_proofs.jsonl'):
    cov[r['src']].append(r)

rng = random.Random(20260924)
os.makedirs(f'{ROOT}/rv/leansample', exist_ok=True)
manifest = {}
for arm, tag in ARMS.items():
    pool = []
    for src, rows in cov.items():
        if src.startswith('covd'):
            continue
        parts = src.split('_')
        if tag == 'k8add' and '_k8add_' not in src:
            continue
        if tag not in ('k8add',) and f'_{tag}_' not in src:
            continue
        for r in rows:
            pool.append({'name': r['name'], 'prompt': PROMPTS[r['name']], 'proof': r['proof'],
                         'src': src, 'pruned': r['pruned']})
    # ladder transfer proofs for this arm (cumulative found pools)
    lad = []
    for d in glob.glob(f'{ROOT}/artifacts/kh/la_*_{tag}_s0') + glob.glob(f'{ROOT}/artifacts/dsc_inherited/la_*_{tag}_s0'):
        fn = f'{d}/found_transfer_8.jsonl'
        if not os.path.exists(fn):
            continue
        for r in rvlib.rd(fn):
            lad.append({'name': r['name'], 'prompt': r['prompt'], 'proof': r['proof'],
                        'src': os.path.basename(d), 'pruned': rvlib.pruned_length(r['proof']),
                        'L_true': TR[r['name']]['L_true']})
    pool.sort(key=lambda r: -r['pruned'])
    sel = pool[:40]                                   # the 40 longest counted coverage proofs
    rest = [r for r in pool[40:]]
    sel += rng.sample(rest, min(40, len(rest)))       # 40 random coverage proofs
    hard = [r for r in lad if r['L_true'] >= 12]      # every counted proof of an L_true >= 12 theorem
    seen = set()
    hard2 = []
    for r in hard:
        if r['name'] not in seen:
            seen.add(r['name']); hard2.append(r)
    sel += hard2[:40]
    other = [r for r in lad if r['L_true'] < 12]
    sel += rng.sample(other, min(40, len(other)))
    fn = f'{ROOT}/rv/leansample/{arm}.jsonl'
    with open(fn, 'w') as f:
        for r in sel:
            f.write(json.dumps(r) + '\n')
    manifest[arm] = {'file': fn, 'n': len(sel),
                     'max_pruned': max(r['pruned'] for r in sel),
                     'sources': dict(collections.Counter(r['src'] for r in sel))}
    print(arm, manifest[arm])
json.dump(manifest, open(f'{ROOT}/rv/leansample/manifest.json', 'w'), indent=1)
