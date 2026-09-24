"""Recount 7a — build a reviewer's sample of counted proofs per arm (>=100 each,
spread over held-out, dial, ladder and all three coverage pools) for nd_verify +
Lean re-checking."""
import sys, os, json, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rv

HO = {r['name']: r for r in rv.load('data/p2/heldout.jsonl')}
T = {r['name']: r for r in rv.load('data/p2/targets_depth3.jsonl')}
TRD = {r['name']: r for r in rv.load('data/p2/transfer_depth3.jsonl')}
LTR = {r['name']: r for r in rv.load('data/ladder/transfer.jsonl')}
POOL = {}
for p in ['data/dsc/targets_depth3_sub250.jsonl', 'data/r3_1/depth3_req.jsonl', 'data/p2/targets_reductio_req.jsonl']:
    for r in rv.load(p):
        POOL[r['name']] = r

os.makedirs('recount/leansample', exist_ok=True)
tot = 0
for arm in ['c0', 'a1', 'a2', 'a3', 'a4']:
    cand = []
    for s in [0, 1]:
        f = 'artifacts/dsc/heldout_%s_s%d.jsonl' % (arm, s)
        for r in rv.load(f):
            for pf in (r.get('proofs') or []):
                cand.append(('heldout_s%d' % s, HO[r['name']]['prompt'], pf))
        for pool in ['d3sub', 'd3req', 'redreq']:
            f = 'artifacts/dsc/cov_%s_s%d_%s.s0.jsonl' % (arm, s, pool)
            if os.path.exists(f):
                for r in rv.load(f):
                    for pf in r['proofs']:
                        cand.append(('cov_%s_s%d' % (pool, s), r['prompt'], pf['proof']))
        for mode in ['ei', 'frozen']:
            f = 'artifacts/dsc/%s_%s_s%d/found_4.jsonl' % (mode, arm, s)
            if os.path.exists(f):
                for r in rv.load(f):
                    cand.append(('dial_%s_s%d' % (mode, s), T[r['name']]['prompt'], r['proof']))
        for mode in ['T1', 'frozen']:
            d = 'artifacts/dsc/la_%s_%s_s%d' % (mode, arm, s)
            if os.path.isdir(d):
                for f in sorted(os.listdir(d)):
                    if f.startswith('found_transfer_'):
                        for r in rv.load(os.path.join(d, f)):
                            cand.append(('ladder_%s_s%d' % (mode, s), LTR[r['name']]['prompt'], r['proof']))
    bysrc = collections.defaultdict(list)
    for c in cand:
        bysrc[c[0]].append(c)
    rnd = random.Random(20260924)
    pick = []
    per = max(1, 220 // max(1, len(bysrc)))
    for k in sorted(bysrc):
        v = bysrc[k]
        rnd.shuffle(v)
        pick += v[:per]
    with open('recount/leansample/%s.jsonl' % arm, 'w') as fh:
        for src, prompt, proof in pick:
            fh.write(json.dumps({'src': src, 'prompt': prompt, 'proof': proof}) + '\n')
    tot += len(pick)
    print(arm, len(pick), 'from', len(cand), 'candidates across', len(bysrc), 'sources',
          dict(collections.Counter(p[0] for p in pick)), flush=True)
print('total', tot)
