#!/usr/bin/env python3
"""Reviewer (rl-continue-cap6): group C from trajectory-cap6's eval rows (seed-0 samples x0: unsolved at pend AND at r8,
tb72 + h250), r8 vs r16 pass@256 on sample seed 1, tb72 solved counts, per-stratum cut-off fractions.  Own code."""
import json, os, collections, math
R = os.path.expanduser('~/review/rl-continue-cap6'); A = f'{R}/artifacts/rc6'
def load(f): return {json.loads(l)['name']: json.loads(l) for l in open(f) if l.strip()}
CUT = ('truncat', 'step cap', 'max_steps', 'eof', 'no-eos')
def cut(r): return sum(1 for z in r['reasons'] if any(c in z for c in CUT))
def passk(n, c, k): return 1.0 if n - c < k else 1.0 - math.prod((n - c - i) / (n - i) for i in range(k))
out = {}
for s in (0, 1, 2):
    o = {}; C = {}
    for pool in ('tb72', 'h250'):
        p0 = load(f'{A}/tj6_eval/s{s}_pend__{pool}_x0.jsonl'); p8 = load(f'{A}/tj6_eval/s{s}_r8__{pool}_x0.jsonl')
        C[pool] = sorted(n for n in p0 if not p0[n]['proofs'] and not p8[n]['proofs'])
    hc = {json.loads(l)['name'] for l in open(f'{R}/data/rc6/h250_C_s{s}.jsonl')}
    o['C_sizes'] = {p: len(v) for p, v in C.items()}; o['C_total'] = sum(o['C_sizes'].values())
    o['h250C_file_matches'] = (hc == set(C['h250']), len(hc), len(hc ^ set(C['h250'])))
    rows = {}
    for ck, files in (('r8', {'tb72': f'{A}/tj6_eval/s{s}_r8__tb72_x1.jsonl', 'h250': f'{A}/tj6_eval/s{s}_r8__h250_x1.jsonl'}),
                      ('r16', {'tb72': f'{A}/eval/s{s}_r16__tb72_x1.jsonl', 'h250': f'{A}/eval/s{s}_r16__h250C_x1.jsonl'})):
        d = {p: load(f) for p, f in files.items()}
        bad = [(p, n) for p in d for n, r in d[p].items() if r['n_tried'] != 256 or r['n_ok'] != r['n_tried'] - len(r['reasons']) or r['solved'] != bool(r['proofs'])]
        crow = [d[p][n] for p in C for n in C[p]]
        solvedC = [f'{p}:{n}' for p in C for n in C[p] if d[p][n]['proofs']]
        cutC = sum(cut(r) for r in crow) / sum(r['n_tried'] for r in crow)
        tb = d['tb72']; 
        o[ck] = dict(incons=len(bad), C_pass256=len(solvedC) / len(crow), C_solved=solvedC, C_pass1=sum(r['n_ok'] / r['n_tried'] for r in crow) / len(crow),
                     C_pass8=sum(passk(256, r['n_ok'], 8) for r in crow) / len(crow),
                     C_cut=cutC, tb72_solved=sum(bool(r['proofs']) for r in tb.values()), tb72_n=len(tb),
                     tb72_cut=sum(cut(r) for r in tb.values()) / sum(r['n_tried'] for r in tb.values()),
                     tb72_C_cut=sum(cut(tb[n]) for n in C['tb72']) / (256 * max(1, len(C['tb72']))),
                     h250_C_cut=sum(cut(d['h250'][n]) for n in C['h250']) / (256 * max(1, len(C['h250']))),
                     tb72_nonC_cut=sum(cut(r) for n, r in tb.items() if n not in C['tb72']) / (256 * (len(tb) - len(C['tb72']))))
        if ck == 'r8':
            h = d['h250']; o['r8']['h250_solved'] = sum(bool(r['proofs']) for r in h.values())
            o['r8']['h250_cut'] = sum(cut(r) for r in h.values()) / sum(r['n_tried'] for r in h.values())
        rows[ck] = d
    # theorems solved at r16 in C: also solved at r8?
    o['C_gained'] = sorted(set(o['r16']['C_solved']) - set(o['r8']['C_solved'])); o['C_lost'] = sorted(set(o['r8']['C_solved']) - set(o['r16']['C_solved']))
    o['delta_C_pass256'] = o['r16']['C_pass256'] - o['r8']['C_pass256']
    out[s] = o
    print(f"s{s}: C {o['C_sizes']} total {o['C_total']}; h250C file == my h250 C: {o['h250C_file_matches']}")
    for ck in ('r8', 'r16'):
        x = o[ck]
        print(f"   {ck}: C pass@256 {x['C_pass256']:.3f} ({len(x['C_solved'])}/{o['C_total']}) pass@8 {x['C_pass8']:.4f} pass@1 {x['C_pass1']:.4f}; tb72 solved {x['tb72_solved']}/{x['tb72_n']}"
              + (f"; h250 solved {x['h250_solved']}/250 cut {100*x['h250_cut']:.2f}%" if ck == 'r8' else '')
              + f"; cut-off: C {100*x['C_cut']:.2f}%  tb72 {100*x['tb72_cut']:.2f}%  tb72-C {100*x['tb72_C_cut']:.2f}% tb72-nonC {100*x['tb72_nonC_cut']:.2f}% h250-C {100*x['h250_C_cut']:.2f}%; incons {x['incons']}")
    print(f"   gained {o['C_gained']} lost {o['C_lost']}")
d = [out[s]['delta_C_pass256'] for s in (0, 1, 2)]
r8 = [out[s]['r8']['C_pass256'] for s in (0, 1, 2)]
print('delta C pass@256 per seed', [round(x, 4) for x in d], 'mean', round(sum(d) / 3, 4), '; r8 spread (max-min)', round(max(r8) - min(r8), 4),
      '; seeds rising', sum(x > 0 for x in d), '-> falsifier 2', sum(d) / 3 > max(r8) - min(r8) and sum(x > 0 for x in d) >= 2)
json.dump(out, open(f'{R}/review_rc6/rv/groupc.json', 'w'), indent=0)
