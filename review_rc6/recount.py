#!/usr/bin/env python3
"""Reviewer (rl-continue-cap6) phase-1 ladder recount, independent of rc6_*.py.  Reads found_{8,16}.jsonl /
found_transfer_{8,16}.jsonl (bucket), alloc_*.json and round_*.json (git).  Own normaliser: relabel N-indices in order
of first appearance (start-index normalisation) and compare distinct-proof counts with the run's `norm` field."""
import json, os, re, collections, sys
R = os.path.expanduser('~/review/rl-continue-cap6'); A = f'{R}/artifacts/rc6'; D = os.path.expanduser('~/review/rc6_data')
def rd(f): return [json.loads(l) for l in open(f) if l.strip()]
def mynorm(p):
    m = {}
    return re.sub(r'\bN(\d+)\b', lambda x: 'N%d' % m.setdefault(x.group(1), len(m) + 1), p)
TG = rd(f'{R}/data/ladder/rl_targets.jsonl'); TR = rd(f'{R}/data/ladder/transfer.jsonl')
TGN = {t['name'] for t in TG}; TRN = {t['name'] for t in TR}
out = {}
for s in (0, 1, 2):
    o = {}; N = f'la_T1_best6_s{s}'
    for pool, pre, names in (('targets', 'found', TGN), ('transfer', 'found_transfer', TRN)):
        f8 = rd(f'{D}/s{s}/{pre}_8.jsonl'); f16 = rd(f'{D}/s{s}/{pre}_16.jsonl')
        assert {x['name'] for x in f16} <= names
        s8 = {x['name'] for x in f8}; s16 = {x['name'] for x in f16}
        k8 = {(x['name'], x['proof']) for x in f8}; k16 = {(x['name'], x['proof']) for x in f16}
        first = {}
        for x in f16: first[x['name']] = min(first.get(x['name'], 99), x['round'])
        percum = {r: sum(1 for v in first.values() if v <= r) for r in range(1, 17)}
        dn_run = len({(x['name'], x['norm']) for x in f16}); dn_me = len({(x['name'], mynorm(x['proof'])) for x in f16})
        o[pool] = dict(n_pool=len(names), solved8=len(s8), solved16=len(s16), new=len(s16) - len(s8), lost=len(s8 - s16),
                       proofs8_kept=len(k8 & k16), proofs8=len(k8), proofs16=len(f16), distinct16_runnorm=dn_run, distinct16_mynorm=dn_me,
                       percum=percum, new_by_round={r: percum[r] - percum[r - 1] for r in range(9, 17)},
                       round_field_ge9_in_r8solved=sum(1 for n in s8 if first[n] >= 9))
        # cross-check against the round JSONs
        o[pool]['roundjson_cum'] = {r: json.load(open(f'{A}/{N}/round_{r}.json'))[f'{pool}_cum']['solved'] for r in range(8, 17)}
        o[pool]['roundjson_mismatch'] = {r: (o[pool]['roundjson_cum'][r], percum[r]) for r in range(8, 17) if o[pool]['roundjson_cum'][r] != percum[r]}
        if pool == 'targets':
            # L_true bins at r16 for the new targets
            Lt = {t['name']: t['n_lines'] for t in TG}
            o[pool]['new_Ltrue_hist'] = dict(sorted(collections.Counter(Lt[n] for n in s16 - s8).items()))
            o[pool]['unsolved16_Ltrue_hist'] = dict(sorted(collections.Counter(Lt[n] for n in names - s16).items()))
    # sample accuracy from alloc tried/accepted (cumulative counters)
    acc = {}
    for r in range(9, 17):
        a0 = json.load(open(f'{A}/{N}/alloc_{r-1}.json')); a1 = json.load(open(f'{A}/{N}/alloc_{r}.json'))
        t = sum(a1['tried'].values()) - sum(a0['tried'].values()); c = sum(a1['accepted'].values()) - sum(a0['accepted'].values())
        rj = json.load(open(f'{A}/{N}/round_{r}.json'))
        acc[r] = (round(c / t, 4), round(rj['target_sample_acc'], 4), rj['target_samples'], round(rj['secs']), rj['ckpt'], rj['seed'])
    o['acc'] = acc
    o['r8_acc'] = round(json.load(open(f'{A}/{N}/round_8.json'))['target_sample_acc'], 4)
    out[s] = o
    t, tr = o['targets'], o['transfer']
    print(f"s{s}: targets {t['solved8']} -> {t['solved16']} (+{t['new']}, lost {t['lost']}); transfer {tr['solved8']} -> {tr['solved16']} (+{tr['new']}, lost {tr['lost']})")
    print(f"    r8 proofs kept {t['proofs8_kept']}/{t['proofs8']} (transfer {tr['proofs8_kept']}/{tr['proofs8']}); distinct16 run-norm {t['distinct16_runnorm']} my-norm {t['distinct16_mynorm']} rows {t['proofs16']}")
    print(f"    new targets per round {t['new_by_round']}; transfer {tr['new_by_round']}")
    print(f"    round-json mismatches targets {t['roundjson_mismatch']} transfer {tr['roundjson_mismatch']}; r8-solved with first round>=9: {t['round_field_ge9_in_r8solved']}")
    print(f"    new L_true {t['new_Ltrue_hist']}; unsolved at r16 L_true {t['unsolved16_Ltrue_hist']}")
    print(f"    acc r8 {o['r8_acc']}; r9-16 (mine, json, samples, secs, ckpt, seed): " + '; '.join(f'r{r} {v[0]}/{v[1]} n{v[2]} {v[3]}s {os.path.basename(v[4])} seed{v[5]}' for r, v in acc.items()))
json.dump(out, open(f'{R}/review_rc6/rv/recount.json', 'w'), indent=0)
