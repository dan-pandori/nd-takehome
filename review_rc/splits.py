#!/usr/bin/env python3
"""Reviewer (rl-continue): renaming-class disjointness (24 atom permutations, F = falsum not renamed, premise-order
insensitive) between every training file and every evaluation pool; plus whether the r9-r16 fine-tune mixes contain
any eval-pool prompt (mix_16 from the bucket for each seed, if present).  Own code (key from the tj6 reviewer kit)."""
import json, itertools, os, sys
R = os.path.expanduser('~/review/rl-continue'); D = os.path.expanduser('~/review/rc_data')
AT = 'PQRS'
def parse(prompt):
    body = prompt.split('THM', 1)[1].rsplit('PRF', 1)[0]
    prem, concl = body.split(' SEQ ')
    ps, cur, d = [], [], 0
    for t in prem.split():
        if t == ',' and d == 0: ps.append(cur); cur = []; continue
        d += (t == '(') - (t == ')'); cur.append(t)
    if cur: ps.append(cur)
    return ps, concl.split()
def key(prompt):
    ps, c = parse(prompt); best = None
    for perm in itertools.permutations(AT):
        m = dict(zip(AT, perm)); rn = lambda f: ' '.join(m.get(t, t) for t in f)
        k = (tuple(sorted(rn(p) for p in ps)), rn(c))
        best = k if best is None or k < best else best
    return best
def rd(f): return [json.loads(l) for l in open(f) if l.strip()]
train = {'train_k12 (replay)': '/home/dan/work/best-state/data/kh/train_k12.jsonl', 'rl_targets (trained)': f'{R}/data/ladder/rl_targets.jsonl'}
ev = {'textbook72': f'{R}/data/bs/textbook72.jsonl', 'holdout250': f'{R}/data/bs/holdout250.jsonl', 'transfer2285': f'{R}/data/ladder/transfer.jsonl',
      'transfer_long2': f'{R}/data/ladder/transfer_long2.jsonl', 'rr600_13_16': f'{R}/data/rc/rr600_13_16.jsonl'}
TK = {}; TP = {}
for n, f in train.items():
    recs = rd(f); TK[n] = {key(r['prompt']) for r in recs}; TP[n] = {r['prompt'] for r in recs}
out = {}
for en, ef in ev.items():
    E = rd(ef); ek = [key(r['prompt']) for r in E]
    for tn in train:
        hits = [r['name'] for r, k in zip(E, ek) if k in TK[tn]]
        out[f'{en} vs {tn}'] = {'n_eval': len(E), 'class_overlap': len(hits), 'exact_prompt': sum(r['prompt'] in TP[tn] for r in E), 'examples': hits[:5]}
        print(en, 'vs', tn, out[f'{en} vs {tn}'])
EK = {en: {key(r['prompt']) for r in rd(ef)} for en, ef in ev.items()}
# mix files: every prompt that was trained on r9-r16
for s in (0, 1, 2):
    f = f'{D}/s{s}/mix_16.jsonl'
    if not os.path.exists(f): continue
    mp = set()
    for l in open(f):
        x = json.loads(l); p = x.get('prompt') or x.get('text', '').split('PRF')[0] + 'PRF'
        if 'THM' in p: mp.add(p.split('PRF')[0] + 'PRF')
    mk = {key(p) for p in mp}
    out[f'mix16_s{s}'] = {'n_prompts': len(mp), **{f'{en}_class_hits': len(mk & EK[en]) for en in EK}}
    print(f'mix_16 s{s}', out[f'mix16_s{s}'])
json.dump(out, open(f'{R}/review_rc/rv/splits.json', 'w'), indent=1)
