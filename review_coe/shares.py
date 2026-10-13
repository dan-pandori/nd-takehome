#!/usr/bin/env python3
"""Reviewer recount of per-round family training shares from the ladders' alloc_<r>.json (cumulative tried / accepted).

Successes on target t in round r = accepted_r[t] - accepted_{r-1}[t] (round 1 = the base's own k 32 sample).
Training share of a family in round r = share of its trained members (key-step 136 / strict 123) with >= 1 success in
round r.  Round of first acquisition = first round with share >= 0.5.  Also: strict trained targets solved per round,
attempts per target per round (should be k 32 for every target), and the cumulative-count consistency of the files.
Ladders: new (ko s0-s5, full s3-s5, dose1 s0-s2, ko s1 to r24) and old full s0-s2 (trajectory r1-r8 + rl-continue r9-r16)."""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

RV = C.RV
FAM = json.load(open(f'{RV}/review_coe/out_families.json'))
TR = {r['name']: r for r in C.rows(f'{RV}/data/ladder/rl_targets.jsonl')}
FAMS = FAM['classical_families']
KEY = set(FAM['keystep_trained']); STRICT = set(FAM['strict_trained'])
fam = {n: TR[n]['schema'] for n in TR}


def ladder_files(arm, s):
    if arm == 'full' and s < 3:
        d = f'{C.BIG}/old/la_T1_best12_s{s}'
        files = {}
        for r in range(1, 9):
            files[r] = f'{d}/tj/alloc_{r}.json'
        for r in range(9, 17):
            files[r] = f'{d}/rc/alloc_{r}.json'
        return files
    d = f'{RV}/artifacts/coe/ladder/la_{arm}_s{s}'
    if not os.path.isdir(d):
        d = f'{C.BIG}/la_{arm}_s{s}'
    return {int(f[6:-5]): f'{d}/{f}' for f in os.listdir(d) if f.startswith('alloc_')}


out = {}
for arm, seeds in (('full', range(6)), ('ko', range(6)), ('dose1', range(3))):
    for s in seeds:
        files = ladder_files(arm, s)
        R = sorted(files)
        prev_acc = collections.Counter(); prev_tr = collections.Counter()
        rows = []
        bad = []
        for r in R:
            a = json.load(open(files[r]))
            acc = collections.Counter(a['accepted']); tr = collections.Counter(a['tried'])
            d_acc = {t: acc[t] - prev_acc[t] for t in TR}
            d_tr = {t: tr[t] - prev_tr[t] for t in TR}
            if any(v < 0 for v in d_acc.values()) or any(v < 0 for v in d_tr.values()):
                bad.append(r)
            ks = collections.Counter(d_tr.values())
            row = {'round': r, 'tried_per_target': dict(ks)}
            for nm, S in (('key', KEY), ('strict', STRICT)):
                for f in FAMS:
                    mem = [t for t in S if fam[t] == f]
                    row[f'{nm}:{f}'] = sum(1 for t in mem if d_acc[t] > 0) / len(mem)
                row[f'{nm}:solved'] = sum(1 for t in S if d_acc[t] > 0)
            row['all_targets_solved'] = sum(1 for t in TR if d_acc[t] > 0)
            rows.append(row)
            prev_acc, prev_tr = acc, tr
        first = {}
        for nm in ('key', 'strict'):
            for f in FAMS:
                first[f'{nm}:{f}'] = next((x['round'] for x in rows if x[f'{nm}:{f}'] >= 0.5), None)
        out[f'{arm}_s{s}'] = {'rounds': rows, 'first_acq': first, 'negative_diffs_rounds': bad}
        print(f'{arm}_s{s}: rounds {R[0]}-{R[-1]}; negative diffs in rounds {bad}; tried/target per round '
              f'{sorted({k for x in rows for k in x["tried_per_target"]})}')
print()
for nm in ('key', 'strict'):
    print(f'== first round with training share >= 0.5 ({nm} trained members)')
    print(f'{"ladder":10s} ' + ' '.join(f'{f[:12]:>12s}' for f in FAMS) + '   r1 share contraposition_conv / strict solved r1, r16')
    for k, v in out.items():
        r1 = v['rounds'][0]; r16 = next(x for x in v['rounds'] if x['round'] == 16)
        print(f'{k:10s} ' + ' '.join(f'{str(v["first_acq"][f"{nm}:{f}"]):>12s}' for f in FAMS) +
              f'   {r1[f"{nm}:contraposition_conv"]:.2f} / {r1[f"{nm}:solved"]}, {r16[f"{nm}:solved"]}')
print()
print('== strict trained members solved per round (of 123)')
for k, v in out.items():
    print(f'{k:10s} ' + ' '.join(f'{x["strict:solved"]:3d}' for x in v['rounds']))
print('== contraposition_conv strict training share per round')
for k, v in out.items():
    print(f'{k:10s} ' + ' '.join(f'{x["strict:contraposition_conv"]:.2f}' for x in v['rounds']))
json.dump(out, open(f'{RV}/review_coe/out_shares.json', 'w'), indent=1)
