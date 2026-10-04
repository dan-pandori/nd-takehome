#!/usr/bin/env python3
"""Reviewer (rl-continue) phase-1 ladder recount, independent of rc_*.py.  Streams found_{8,16}.jsonl /
found_transfer_{8,16}.jsonl (bucket) and reads alloc_*.json / round_*.json (git).  Own start-index normaliser (relabel
N-indices in order of first appearance) vs the run's `norm` field.  Checks: found_8 subset of found_16, per-round first
solves, round-JSON cum counts, sample accuracy from alloc counters, sampling seeds / ckpt chain."""
import json, os, re, collections, hashlib
R = os.path.expanduser('~/review/rl-continue'); A = f'{R}/artifacts/rc'; D = os.path.expanduser('~/review/rc_data')
def rd(f):
    for l in open(f):
        if l.strip(): yield json.loads(l)
def mynorm(p):
    m = {}
    return re.sub(r'\bN(\d+)\b', lambda x: 'N%d' % m.setdefault(x.group(1), len(m) + 1), p)
h = lambda s: hashlib.md5(s.encode()).hexdigest()[:16]
TG = list(rd(f'{R}/data/ladder/rl_targets.jsonl')); TR = list(rd(f'{R}/data/ladder/transfer.jsonl'))
TGN = {t['name'] for t in TG}; TRN = {t['name'] for t in TR}
LT = {t['name']: t.get('n_lines', t.get('L_true')) for t in TG + TR}
def cum(js, key):
    v = js[key]; v = eval(v) if isinstance(v, str) else v
    return v['solved']
out = {}
for s in (0, 1, 2):
    o = {}; N = f'la_T1_best12_s{s}'
    rj = lambda r: json.load(open(f'{A}/{N}/round_{r}.json') if r >= 8 else open(f'{A}/tj_rounds/s{s}_round_{r}.json'))
    for pool, pre, names in (('targets', 'found', TGN), ('transfer', 'found_transfer', TRN)):
        k8 = set(); s8 = set(); n8 = 0
        for x in rd(f'{D}/s{s}/{pre}_8.jsonl'): k8.add((x['name'], h(x['proof']))); s8.add(x['name']); n8 += 1
        k16 = set(); first = {}; n16 = 0; dn_run = set(); dn_me = set(); badnorm = 0; rounds = collections.Counter(); outside = 0
        firstrow = {}
        for x in rd(f'{D}/s{s}/{pre}_16.jsonl'):
            n16 += 1; k16.add((x['name'], h(x['proof']))); rounds[x['round']] += 1
            if x['name'] not in names: outside += 1
            if x['round'] < first.get(x['name'], 99): first[x['name']] = x['round']
            dn_run.add((x['name'], h(x['norm']))); m = mynorm(x['proof']); dn_me.add((x['name'], h(m))); badnorm += (m != x['norm'])
        s16 = set(first)
        percum = {r: sum(1 for v in first.values() if v <= r) for r in range(1, 17)}
        o[pool] = dict(n_pool=len(names), rows8=n8, rows16=n16, solved8=len(s8), solved16=len(s16), new=len(s16 - s8), lost=len(s8 - s16),
                       proofs8_kept=len(k8 & k16), proofs8_distinct=len(k8), distinct16_runnorm=len(dn_run), distinct16_mynorm=len(dn_me), norm_differs=badnorm,
                       outside_pool=outside, rows_by_round=dict(sorted(rounds.items())), percum=percum,
                       new_by_round={r: percum[r] - percum[r - 1] for r in range(2, 17)},
                       r8solved_first_ge9=sum(1 for n in s8 if first.get(n, 0) >= 9), first_le8_not_in_8=sum(1 for n, r in first.items() if r <= 8 and n not in s8),
                       roundjson_cum={r: cum(rj(r), f'{pool}_cum') for r in range(1, 17)})
        o[pool]['roundjson_mismatch'] = {r: (o[pool]['roundjson_cum'][r], percum[r]) for r in range(1, 17) if o[pool]['roundjson_cum'][r] != percum[r]}
        o[pool]['new_Ltrue_hist'] = dict(sorted(collections.Counter(LT[n] for n in s16 - s8).items()))
        o[pool]['unsolved16_Ltrue_hist'] = dict(sorted(collections.Counter(LT[n] for n in names - s16).items()))
        o[pool]['new_names'] = sorted(s16 - s8)
    acc = {}
    for r in range(9, 17):
        a0 = json.load(open(f'{A}/{N}/alloc_{r-1}.json')); a1 = json.load(open(f'{A}/{N}/alloc_{r}.json'))
        t = sum(a1['tried'].values()) - sum(a0['tried'].values()); c = sum(a1['accepted'].values()) - sum(a0['accepted'].values())
        j = rj(r)
        acc[r] = dict(mine=round(c / t, 4), json=round(j['target_sample_acc'], 4), samples=j['target_samples'], secs=round(j['secs']), ckpt=os.path.basename(j['ckpt']), seed=j['seed'],
                      tr_acc=round(j['transfer_sample_acc'], 4))
    o['acc'] = acc; o['r8_acc'] = round(rj(8)['target_sample_acc'], 4)
    o['r6_8_new'] = {r: o['targets']['roundjson_cum'][r] - o['targets']['roundjson_cum'][r - 1] for r in (6, 7, 8)}
    out[s] = o
    t, tr = o['targets'], o['transfer']
    print(f"s{s}: targets {t['solved8']} -> {t['solved16']} (+{t['new']}, lost {t['lost']}) of {t['n_pool']}; transfer {tr['solved8']} -> {tr['solved16']} (+{tr['new']}, lost {tr['lost']}) of {tr['n_pool']}")
    print(f"    rows r8 {t['rows8']} r16 {t['rows16']}; r8 distinct proofs kept {t['proofs8_kept']}/{t['proofs8_distinct']} (transfer {tr['proofs8_kept']}/{tr['proofs8_distinct']}); distinct16 run-norm {t['distinct16_runnorm']} my-norm {t['distinct16_mynorm']} (norm field != mine on {t['norm_differs']} rows); outside pool {t['outside_pool']}/{tr['outside_pool']}")
    print(f"    new targets per round r2-16 {t['new_by_round']}")
    print(f"    new transfer per round r2-16 {tr['new_by_round']}")
    print(f"    round-json mismatches targets {t['roundjson_mismatch']} transfer {tr['roundjson_mismatch']}; r8-solved first>=9 {t['r8solved_first_ge9']}; first<=8 but not in found_8 {t['first_le8_not_in_8']}")
    print(f"    new L_true {t['new_Ltrue_hist']}; unsolved at r16 L_true {t['unsolved16_Ltrue_hist']}; transfer new L {tr['new_Ltrue_hist']}")
    print(f"    acc r8 {o['r8_acc']}; r9-16: " + '; '.join(f"r{r} {v['mine']}/{v['json']} n{v['samples']} {v['secs']}s {v['ckpt']} seed{v['seed']} tr{v['tr_acc']}" for r, v in acc.items()))
    print(f"    r6-r8 new (round json) {o['r6_8_new']}")
    json.dump(out, open(f'{R}/review_rc/rv/recount.json', 'w'), indent=0)
nw = [out[s]['targets']['new'] for s in out]
print('new targets r9-16 per seed', nw, '-> falsifier 1 (>=60 on >=2 seeds):', sum(v >= 60 for v in nw) >= 2)
if len(out) == 3:
    I = set.intersection(*[set(out[s]['targets']['new_names']) for s in out]); U = set.union(*[set(out[s]['targets']['new_names']) for s in out])
    print('new targets: union', len(U), 'in all three', len(I))
