#!/usr/bin/env python3
"""Reviewer (trajectory-cap6; adapted from review_tj/eventual.py): (a) candidate set == distinct accepted proofs of
r8 x0 per theorem; (b) eventual == argmax total T1.0 log p over scored candidates (and margin to runner-up);
(c) replay failures; (d) eventual proofs are r8-x0 accepted; (e) targets_s == eventual + refs; data/tj6/eventual == artifacts."""
import json, os, collections, statistics as st
R = os.path.expanduser('~/review/trajectory-cap6'); A = f'{R}/artifacts/tj6'
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
out = {}
for s in (0, 1, 2):
    ev0 = {}
    for pool in ('tb72', 'h250'):
        for r in rd(f'{A}/eval/s{s}_r8__{pool}_x0.jsonl'):
            if r['proofs']: ev0[(pool, r['name'])] = set(r['proofs'])
    cand = collections.defaultdict(set); ctid = {}
    for r in rd(f'{A}/targets/cand_s{s}.jsonl'): cand[(r['pool'], r['name'])].add(r['proof']); ctid[r['tid']] = r
    sc = {r['tid']: sum(r['T1.0']['step_lp']) for r in rd(f'{A}/score/cand_s{s}/s{s}_r8.jsonl')}
    meta = {r['tid']: r for r in rd(f'{A}/score/cand_s{s}/targets.jsonl')}
    nfail = [t for t, m in meta.items() if not m['replay_ok']]
    diff = [k for k in set(ev0) | set(cand) if ev0.get(k, set()) != cand.get(k, set())]
    allc = collections.defaultdict(list)
    for t, v in sc.items(): allc[(ctid[t]['pool'], ctid[t]['name'])].append((v, ctid[t]['proof']))
    best = {k: max(v) for k, v in allc.items()}
    margins = [sorted(v)[-1][0] - sorted(v)[-2][0] for v in allc.values() if len(v) > 1]
    evt = {(r['pool'], r['name']): r['proof'] for r in rd(f'{A}/targets/eventual_s{s}.jsonl')}
    evd = {(r['pool'], r['name']): r['proof'] for r in rd(f'{R}/data/tj6/eventual_s{s}.jsonl')}
    tgt = rd(f'{A}/targets/targets_s{s}.jsonl')
    tev = {(r['pool'], r['name']): r['proof'] for r in tgt if r['kind'] == 'ev'}
    ref = {(r['pool'], r['name']): r['proof'] for r in rd(f'{R}/data/tj6/ref_targets.jsonl')}
    tref = {(r['pool'], r['name']): r['proof'] for r in tgt if r['kind'] == 'ref'}
    mism = [k for k in evt if best.get(k, (0, None))[1] != evt[k]]
    notacc = [k for k in evt if evt[k] not in ev0.get(k, set())]
    o = out[s] = dict(r8x0_solved=len(ev0), cand_thms=len(cand), cand_proofs=sum(map(len, cand.values())),
                      distinct_acc=sum(map(len, ev0.values())), set_mism=len(diff), replay_fail=len(nfail), eventual=len(evt),
                      not_argmax=len(mism), not_r8x0=len(notacc), missing_eventual=len(set(ev0) - set(evt)),
                      data_eq_art=evd == evt, targets_ev_eq=tev == evt, targets_ref_eq=tref == ref, n_ref=len(ref),
                      margin_lt_1e3=sum(m < 1e-3 for m in margins), n_multi=len(margins),
                      margin_med=st.median(margins) if margins else None)
    print(f'seed {s}:', o)
# data/tj6/ref_targets.jsonl == trajectory's data/tj/ref_targets.jsonl?
a = open(f'{R}/data/tj6/ref_targets.jsonl').read(); b = open(f'{R}/data/tj/ref_targets.jsonl').read()
print('ref_targets identical to trajectory:', a == b, len(a.splitlines()))
json.dump(out, open(f'{R}/rv6/eventual.json', 'w'), indent=0)
