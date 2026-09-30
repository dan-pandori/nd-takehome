#!/usr/bin/env python3
import json, glob, os, random, collections, sys, time
sys.path.insert(0, os.path.dirname(__file__)); import rlean
R = os.path.expanduser('~/review/search-expert'); A = f'{R}/artifacts/sx'
rnd = random.Random(20260930)
def load(f): return [json.loads(l) for l in open(f) if l.strip()]
prompts = {}
for f in ['data/ladder/rl_targets.jsonl', 'data/ladder/transfer_long2_91.jsonl', 'data/ladder/rr600_13to16.jsonl']:
    for r in load(f'{R}/{f}'): prompts[r['name']] = r['prompt']
# counted read-out proofs per arm
S = collections.defaultdict(list)
for f in glob.glob(f'{A}/rr/*.jsonl'):
    tag = os.path.basename(f).split('__')[0]; arm = tag.rsplit('_s', 1)[0]
    for r in load(f):
        for p in r['proofs']: S[('rr', arm)].append((r['prompt'], p, tag, r['name']))
for d in glob.glob(f'{A}/*_s[0-9]'):
    tag = os.path.basename(d); arm = tag.rsplit('_s', 1)[0]
    for f in glob.glob(f'{d}/found_[0-9]*.jsonl'):
        for r in load(f): S[('found', arm)].append((r['prompt'], r['proof'], tag + '/' + os.path.basename(f), r['name']))
items = []
for key in sorted(S):
    n = 150 if key[0] == 'rr' else 100
    pool = S[key]; pick = rnd.sample(pool, min(n, len(pool)))
    items += [dict(kind='pos', src=key, prompt=p, nd=nd, where=w, name=nm) for p, nd, w, nm in pick]
    print(key, len(pool), 'sampled', len(pick))
pos = [it for it in items]
# controls
ctrl = []
rej = []
import itertools
for f in sorted(glob.glob(f'{A}/gate_rr_*.leanrej.jsonl'))[::3]:
    with open(f) as fh: rej += [json.loads(l) for l in itertools.islice(fh, 5000, 7000)]
lit = rnd.sample(rej, 300)
ctrl += [dict(kind='neg_leanrej', prompt=r['prompt'], body=r['lean_text'], filt=r.get('filter')) for r in lit]
for it in rnd.sample(pos, 200):
    for fl in (('Or.inl', 'Or.inr'), ('.1', '.2')):
        b = rlean.render(it['prompt'], it['nd'], flip=fl)
        if b != rlean.render(it['prompt'], it['nd']):
            ctrl.append(dict(kind='neg_flip', prompt=it['prompt'], body=b, fl=fl[0])); break
byk = collections.defaultdict(list)
for it in pos: byk[len(rlean.stmt(it['prompt'])[0])].append(it)
for it in rnd.sample(pos, 150):
    others = [o for o in byk[len(rlean.stmt(it['prompt'])[0])] if o['prompt'] != it['prompt']]
    o = rnd.choice(others)
    ctrl.append(dict(kind='neg_swap', prompt=o['prompt'], body=rlean.render(it['prompt'], it['nd'])))
ctrl += [dict(kind='neg_sorry', prompt=it['prompt'], body='sorry') for it in pos[:5]]
for it in pos: it['body'] = rlean.render(it['prompt'], it['nd'])
allit = pos + ctrl
t = time.time()
res = rlean.check([(x['prompt'], x['body']) for x in allit], per_file=150, size=True)
print('lean secs', round(time.time() - t))
for x, (ok, info, sz) in zip(allit, res):
    x['ok'] = ok; x['info'] = info; x['size'] = sz
    x.pop('body', None)
json.dump(allit, open(f'{R}/rv/recheck_results.json', 'w'))
tab = collections.Counter((x['kind'], str(x.get('src')), x['ok']) for x in allit)
for k in sorted(tab): print(k, tab[k])
for x in allit:
    if x['kind'] == 'pos' and not x['ok']: print('POS FAIL', x['where'], x['name'], x['info'], x['nd'][:200])
    if x['kind'] == 'neg_leanrej' and x['ok']: print('LEANREJ PASSED', x.get('filt'), x['prompt'][:100])
