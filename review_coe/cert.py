#!/usr/bin/env python3
"""Reviewer recount of K_train(16) per new seed and of the knockout bases' certificates on the strict held-out members.

K_train(R) = sum over rounds <= R of the ladder's sample + fine-tune phase GPU-seconds (registry rows, script
state_ladder_ei.py) / (322 x c_base), c_base = wall_s / attempts of the seed's pend timing read on the 322 (k 256, batch
1,024, alone on the A40).  Certificate: pooled over the strict family members (105; la_transfer_916 separately), attempts
and successes of the knockout pend in the large-k files (sig178_* + sig105_topup_* chunks), one-sided 95 % Clopper-Pearson
upper bound UB95 of the pooled mean p; certified at K iff UB95 < 0.05 / K.  Per family the same and the largest K
certified (0.05 / UB95).  Also K_att = ladder target attempts / 322 per round."""
import collections, glob, json, math, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
from scipy.stats import beta

RV = C.RV
FAM = json.load(open(f'{RV}/review_coe/out_families.json'))
HO = {r['name']: r for r in C.rows(f'{RV}/data/ladder/transfer.jsonl')}
STRICT_F = FAM['strict_heldout_family']; FAMS = FAM['classical_families']
famof = {n: HO[n]['schema'] for n in HO}

reg = []
for f in sorted(glob.glob(f'{RV}/artifacts/create-or-elicit/registry/*.jsonl')):
    reg += list(C.rows(f))


def ub95(c, n):
    return 1.0 if n == 0 else (1 - 0.05 ** (1 / n) if c == 0 else float(beta.ppf(0.95, c + 1, n - c)))


K = {}
print('== K_train(16), uniform allocation (registry phase rows / timing read)')
for arm, seeds in (('ko', range(6)), ('full', range(3, 6)), ('dose1', range(3))):
    for s in seeds:
        nm = f'la_{arm}_s{s}'
        ph = collections.defaultdict(float); seen = collections.Counter()
        for r in reg:
            lab = r.get('labels') or {}
            if r['metric'] == 'gpu_seconds' and r.get('script') == 'state_ladder_ei.py' and r.get('arm') == nm and lab.get('round') and lab['round'] <= 16:
                ph[lab['phase']] += r['value']; seen[(lab['phase'], lab['round'])] += 1
        miss = [(p, rr) for p in ('sample', 'eval', 'finetune') for rr in range(1, 17) if seen[(p, rr)] != 1]
        child = collections.Counter(); cseen = collections.Counter()
        for r in reg:
            lab = r.get('labels') or {}
            out = (r.get('config') or {}).get('out') or ''
            m = re.match(rf'ckpts/coe/ladder/{nm}_r(\d+)\.pt$', out)
            if r['metric'] == 'gpu_seconds' and r.get('script') == 'state_train.py' and lab.get('phase') == 'finetune' and m and int(m.group(1)) <= 16:
                child[int(m.group(1))] += r['value']; cseen[int(m.group(1))] += 1
        ft_child = sum(child.values())
        cmiss = [rr for rr in range(1, 17) if cseen[rr] != 1]
        t = json.load(open(f'{RV}/artifacts/coe/timing/A40_pend_{arm}_s{s}_b1024.json'))
        att = int(t['n']) * int(t['k'])
        c_base = float(t['wall_s']) / att
        ktr = (ph['sample'] + ph['finetune']) / (322 * c_base)
        ktr_child = (ph['sample'] + ph['finetune'] + ft_child) / (322 * c_base)
        # round files: secs
        d = f'{RV}/artifacts/coe/ladder/{nm}'
        if not os.path.isdir(d):
            d = f'{C.BIG}/{nm}'
        secs = sum(json.load(open(f'{d}/round_{rr}.json'))['secs'] for rr in range(1, 17))
        tgt_att = sum(json.load(open(f'{d}/round_{rr}.json'))['target_samples'] for rr in range(1, 17))
        K[(arm, s)] = ktr_child
        K[(arm, s, 'ladder_rows_only')] = ktr
        print(f'{nm:12s} sample {ph["sample"]:8.0f}s finetune {ph["finetune"]:7.0f}s eval {ph["eval"]:7.0f}s (rows missing/dup {len(miss)}); '
              f'round-file secs {secs:8.0f}; c_base {1000*c_base:.3f} ms ({att} att, {float(t["wall_s"]):.0f}s); K_train(16) = {ktr:,.0f}; '
              f'K_att(16) = {tgt_att/322:,.1f}')
        print(f'{"":12s} + fine-tune child rows {ft_child:7.0f}s (rounds missing/dup {cmiss}) -> K_train(16) incl. fine-tune = {ktr_child:,.0f}  (sample+ft+eval+child = {ph["sample"]+ph["finetune"]+ph["eval"]+ft_child:,.0f}s vs round-file secs {secs:,.0f}s)')

print('\n== knockout certificates (strict family members, pooled)')
CERT = {}
for s in range(6):
    per = collections.defaultdict(lambda: [0, 0])
    for fn in (f'{RV}/artifacts/coe/large/sig178_ko_s{s}.chunks.jsonl', f'{RV}/artifacts/coe/large/sig105_topup_ko_s{s}.chunks.jsonl'):
        for x in C.rows(fn):
            if 'name' not in x:
                continue
            per[x['name']][0] += x['ok']; per[x['name']][1] += x['tried']
    n_tot = sum(per[m][1] for m in STRICT_F); c_tot = sum(per[m][0] for m in STRICT_F)
    k = K[('ko', s)]; k0 = K[('ko', s, 'ladder_rows_only')]
    u = ub95(c_tot, n_tot)
    fam = {}
    for f in FAMS:
        mem = [m for m in STRICT_F if famof[m] == f]
        nf = sum(per[m][1] for m in mem); cf = sum(per[m][0] for m in mem)
        uf = ub95(cf, nf)
        fam[f] = {'members': len(mem), 'n': nf, 'c': cf, 'ub95': uf, 'K_max': 0.05 / uf, 'certified_at_K': uf < 0.05 / k}
    succ = {m: per[m] for m in per if per[m][0] > 0}
    t916 = per.get('la_transfer_916')
    minn = min(per[m][1] for m in STRICT_F)
    CERT[s] = {'K_train16': k, 'n': n_tot, 'c': c_tot, 'ub95': u, 'threshold': 0.05 / k, 'certified': u < 0.05 / k,
               'n_needed': math.log(0.05) / math.log(1 - 0.05 / k), 'min_n_member': minn, 'families': fam,
               'members_with_success_any_of_178': {m: v for m, v in succ.items()}, 't916': t916}
    print(f'ko s{s}: [with ladder-rows-only K {k0:,.0f}: {"CERTIFIED" if u < 0.05/k0 else "not certified"}]')
    print(f'ko s{s}: K_train(16) {k:,.0f}; pooled n {n_tot:,} (min per member {minn:,}) c {c_tot}; UB95 {u:.3e} vs 0.05/K {0.05/k:.3e} -> '
          f'{"CERTIFIED" if u < 0.05/k else "not certified"} (needs n >= {CERT[s]["n_needed"]:,.0f}); t916 {t916}')
    print('     per family K_max: ' + ', '.join(f'{f[:12]} {fam[f]["K_max"]:,.0f} ({"ok" if fam[f]["certified_at_K"] else "NO"})' for f in FAMS))
    strict_succ = {m: v for m, v in succ.items() if m in STRICT_F}
    print(f'     strict members with a success: {strict_succ}; non-strict (of the 178) with successes: {len(succ) - len(strict_succ) - (1 if t916 and t916[0] else 0)}')
json.dump({'K': {'_'.join(map(str, k)): v for k, v in K.items()}, 'cert': CERT}, open(f'{RV}/review_coe/out_cert.json', 'w'), indent=1, default=str)
