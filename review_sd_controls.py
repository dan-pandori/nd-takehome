#!/usr/bin/env python3
# (reviewer of run stage1-dynamics; independent of the executor.  Phase 1 was run in ~/review/stage1-dynamics.)
"""Negative controls for my Lean re-check harness: it must REJECT
 (a) samples the run itself recorded as parsed-but-Lean-rejected,
 (b) counted proofs I corrupt by hand (swap Or.inl->Or.inr, drop a have, wrong premise),
 (c) a proof of a DIFFERENT theorem (statement/proof mismatch),
 (d) an explicit `sorry` (which the strict grammar cannot emit, but my axiom check must catch).
It must ACCEPT the untouched counted proofs it is paired against."""
import json, random, collections
rng = random.Random(7)
held = {r['name']: r for r in (json.loads(l) for l in open('data/p2/heldout.jsonl'))}
spec = {}

# (a) run-rejected samples: parsed True, lean_ok False -- need text, so from a --texts file
rej, acc = [], []
for st in ['c_s0', 'c_s1', 'w_s0', 'w6_s0', 'w12_s0', 'f_s0']:
    for l in open(f'artifacts/sd/ev/{st}.jsonl'):
        r = json.loads(l)
        if r['parsed'] and not r['lean_ok'] and r['text']:
            rej.append({'name': r['name'], 'text': r['text'], 'ckpt': st})
        elif r['lean_ok']:
            acc.append({'name': r['name'], 'text': r['text'], 'ckpt': st})
spec['ctl_run_rejected'] = rng.sample(rej, 60)
base = rng.sample(acc, 60)
spec['ctl_untouched'] = list(base)

# (b) corruptions
corr = []
for it in base:
    t = it['text']
    v = None
    if 'Or.inl' in t: v = t.replace('Or.inl', 'Or.inr', 1)
    elif 'Or.inr' in t: v = t.replace('Or.inr', 'Or.inl', 1)
    elif '.1' in t: v = t.replace('.1', '.2', 1)
    elif '.2' in t: v = t.replace('.2', '.1', 1)
    if v and v != t:
        corr.append({'name': it['name'], 'text': v, 'ckpt': it['ckpt'] + ':corrupt'})
spec['ctl_corrupted'] = corr

# (c) proof of another theorem, same premise count so the statement still elaborates
byp = collections.defaultdict(list)
for it in base:
    byp[held[it['name']]['n_prem']].append(it)
mm = []
for k, v in byp.items():
    for i in range(len(v) - 1):
        if held[v[i]['name']]['thm'] != held[v[i+1]['name']]['thm']:
            mm.append({'name': v[i]['name'], 'text': v[i+1]['text'], 'ckpt': 'mismatch'})
spec['ctl_wrong_theorem'] = mm[:40]

# (d) sorry
spec['ctl_sorry'] = [{'name': it['name'], 'text': 'sorry', 'ckpt': 'sorry'} for it in base[:10]]

json.dump(spec, open('review_sd_controls.json', 'w'), indent=1)
for k, v in spec.items():
    print(k, len(v))
