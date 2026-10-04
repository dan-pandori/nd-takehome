#!/usr/bin/env python3
"""Reviewer (rl-continue): group C per seed from trajectory's seed-0 reads (x0: unsolved at pend AND at r8; tb72 + h250),
pass@256 on sample seed 1 at r8 (trajectory) / r12 / r16 (this run); tb72 / h250 solved; per-stratum cut-off from `reasons`;
base reachability of C on pend's x1 draw; falsifier 2.  Own code (rl-continue-cap6 reviewer kit, adapted)."""
import json, os, math
R = os.path.expanduser('~/review/rl-continue'); A = f'{R}/artifacts/rc'
def load(f): return {json.loads(l)['name']: json.loads(l) for l in open(f) if l.strip()}
CUT = ('truncat', 'step cap', 'max_steps', 'eof', 'no-eos')
def cut(r): return sum(v for z, v in r['reasons'].items() if any(c in z for c in CUT)) if isinstance(r['reasons'], dict) else sum(1 for z in r['reasons'] if any(c in z for c in CUT))
def passk(n, c, k): return 1.0 if n - c < k else 1.0 - math.prod((n - c - i) / (n - i) for i in range(k))
def solved(r): return bool(r['proofs'])
out = {}; reasons_seen = set()
for s in (0, 1, 2):
    o = {}; C = {}
    for pool in ('tb72', 'h250'):
        p0 = load(f'{A}/tj_eval/s{s}_pend__{pool}_x0.jsonl'); p8 = load(f'{A}/tj_eval/s{s}_r8__{pool}_x0.jsonl')
        C[pool] = sorted(n for n in p0 if not solved(p0[n]) and not solved(p8[n]))
    o['C'] = C; o['C_total'] = sum(len(v) for v in C.values())
    for ck, files in (('pend', {p: f'{A}/tj_eval/s{s}_pend__{p}_x1.jsonl' for p in C}),
                      ('r8', {p: f'{A}/tj_eval/s{s}_r8__{p}_x1.jsonl' for p in C}),
                      ('r12', {p: f'{A}/eval/s{s}_r12__{p}_x1.jsonl' for p in C}),
                      ('r16', {p: f'{A}/eval/s{s}_r16__{p}_x1.jsonl' for p in C})):
        d = {p: load(f) for p, f in files.items()}
        for p in d:
            for r in d[p].values():
                reasons_seen |= set(r['reasons'])
        nfail = lambda r: sum(r['reasons'].values()) if isinstance(r['reasons'], dict) else len(r['reasons'])
        bad = [(p, n) for p in d for n, r in d[p].items() if r['n_tried'] != 256 or r['n_ok'] != r['n_tried'] - nfail(r) or r['solved'] != solved(r)]
        crow = [d[p][n] for p in C for n in C[p]]
        x = dict(incons=len(bad), C_solved=[f'{p}:{n}' for p in C for n in C[p] if solved(d[p][n])],
                 C_pass1=sum(r['n_ok'] / r['n_tried'] for r in crow) / len(crow), C_pass8=sum(passk(256, r['n_ok'], 8) for r in crow) / len(crow),
                 C_cut=sum(cut(r) for r in crow) / (256 * len(crow)))
        x['C_pass256'] = len(x['C_solved']) / len(crow)
        for p in d:
            x[f'{p}_solved'] = sum(solved(r) for r in d[p].values()); x[f'{p}_n'] = len(d[p])
            x[f'{p}_cut'] = sum(cut(r) for r in d[p].values()) / sum(r['n_tried'] for r in d[p].values())
            x[f'{p}_C_cut'] = sum(cut(d[p][n]) for n in C[p]) / (256 * max(1, len(C[p])))
            x[f'{p}_maxrow_cut'] = max(cut(r) / r['n_tried'] for r in d[p].values())
            x[f'{p}_sampleacc'] = sum(r['n_ok'] for r in d[p].values()) / sum(r['n_tried'] for r in d[p].values())
        o[ck] = x
    o['C_gained_r16'] = sorted(set(o['r16']['C_solved']) - set(o['r8']['C_solved'])); o['C_lost_r16'] = sorted(set(o['r8']['C_solved']) - set(o['r16']['C_solved']))
    o['delta_C_pass256'] = o['r16']['C_pass256'] - o['r8']['C_pass256']
    out[s] = o
    print(f"s{s}: C tb72 {len(C['tb72'])} h250 {len(C['h250'])} total {o['C_total']}")
    for ck in ('pend', 'r8', 'r12', 'r16'):
        x = o[ck]
        print(f"   {ck:4s}: C pass@256 {x['C_pass256']:.4f} ({len(x['C_solved'])}/{o['C_total']}) pass@8 {x['C_pass8']:.4f} pass@1 {x['C_pass1']:.5f}; "
              f"tb72 {x['tb72_solved']}/{x['tb72_n']} h250 {x['h250_solved']}/{x['h250_n']}; acc tb72 {x['tb72_sampleacc']:.3f} h250 {x['h250_sampleacc']:.3f}; "
              f"cut C {100*x['C_cut']:.3f}% tb72 {100*x['tb72_cut']:.3f}% (C {100*x['tb72_C_cut']:.3f}%, max row {100*x['tb72_maxrow_cut']:.1f}%) h250 {100*x['h250_cut']:.3f}% (C {100*x['h250_C_cut']:.3f}%, max row {100*x['h250_maxrow_cut']:.1f}%); incons {x['incons']}")
    print(f"   C solved r16 {o['r16']['C_solved']}; gained vs r8 {o['C_gained_r16']} lost {o['C_lost_r16']}")
d = [out[s]['delta_C_pass256'] for s in (0, 1, 2)]; r8 = [out[s]['r8']['C_pass256'] for s in (0, 1, 2)]
print('r8 C pass@256 per seed', [round(v, 4) for v in r8], 'r16', [round(out[s]['r16']['C_pass256'], 4) for s in (0, 1, 2)])
print('delta C pass@256 per seed', [round(x, 4) for x in d], 'mean', round(sum(d) / 3, 4), '; r8 spread', round(max(r8) - min(r8), 4),
      '; seeds rising', sum(x > 0 for x in d), '-> falsifier 2 fires:', sum(d) / 3 > max(r8) - min(r8) and sum(x > 0 for x in d) >= 2)
pooled = lambda ck: sum(len(out[s][ck]['C_solved']) for s in (0, 1, 2)) / sum(out[s]['C_total'] for s in (0, 1, 2))
print('pooled C pass@256: pend', round(pooled('pend'), 4), 'r8', round(pooled('r8'), 4), 'r12', round(pooled('r12'), 4), 'r16', round(pooled('r16'), 4))
# cross-seed: C theorems solved at r16 -- did another seed's r8 or pend (x1 and x0) solve it?
for s in (0, 1, 2):
    for t in out[s]['r16']['C_solved']:
        p, n = t.split(':'); seen = []
        for s2 in (0, 1, 2):
            for ck in ('pend', 'r8'):
                for x in (0, 1):
                    r = load(f'{A}/tj_eval/s{s2}_{ck}__{p}_x{x}.jsonl')[n]
                    if solved(r): seen.append(f's{s2}{ck}x{x}:{r["n_ok"]}')
        print(f'   s{s} r16 C-solved {t}: solved elsewhere {seen}')
print('reason strings seen:', sorted(reasons_seen))
json.dump(out, open(f'{R}/review_rc/rv/groupc.json', 'w'), indent=0)
