#!/usr/bin/env python3
"""state-cap12: tables from the pulled raw files (no GPU, no torch).

  python3 sc12_analysis.py [--out artifacts/sc12/summary.json] [--md artifacts/sc12/tables.md]

Long-pool readout (final checkpoint, k 256, long-pool pass-2 settings): per `L_true` bin 11-16 of
`transfer_long_rr600.jsonl` (all / generator-only), the >= 17 file, `L*` (max L with >= 5 solved at `L_true` >= L,
the >= 17 file counting towards every L; ">=17" if it alone has >= 5), and the primary quantity
Q = generator theorems solved in bins 13-16 (380).  Comparators come from long-pool's own files
(artifacts/sc12/lp_rr2/, = hf://buckets/dan-pandori/nd-rl/long-pool/artifacts/lpool/rr2/).
Original pool: in-loop cumulative T1 (round_8.json of each ladder) and the k 256 Stage-1 re-read on transfer.jsonl.
Per arm: per-seed values, IQM and a 95 % bootstrap interval over seeds (Agarwal et al. 2021; n <= 4, so crude).
"""
import argparse, glob, json, os, random
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import record

RR = 'artifacts/sc12/rr'
LP = 'artifacts/sc12/lp_rr2'
POOL = {json.loads(l)['name']: json.loads(l) for l in open('data/ladder/transfer_long_rr600.jsonl')}
ORIG = {json.loads(l)['name']: json.loads(l) for l in open('data/ladder/transfer.jsonl')}

# arm -> list of (seed label, rr600 jsonl path); the >= 17 file is <path minus .jsonl>__ge17.jsonl (lp) or __ge17 (ours)
ARMS = {
    'SN-cap12 T1': [(s, f'{RR}/T1_SN12_s{s}__rr600.jsonl') for s in range(4)],
    'SN-cap12 frozen': [(s, f'{RR}/stage1_SN12_s{s}__rr600.jsonl') for s in range(4)],
    'K12 T1 (whole-proof)': [(s, f'{RR}/T1_K12_s{s}__rr600.jsonl') for s in range(2)],
    'SN-v2 cap-6 T1': [(s, f'{LP}/state-env__la_T1_SN_s{s}_r8.jsonl') for s in range(2)],
    'SN-v2 cap-6 frozen': [(s, f'{LP}/state-env__stage1_SN_s{s}.jsonl') for s in range(2)],
    'K12 frozen (whole-proof)': [(0, f'{LP}/cap-horizon__stage1_k12_s0.jsonl')],
    'K14 frozen (whole-proof)': [(0, f'{LP}/cap-horizon__stage1_k14_s0.jsonl')],
    'S cap-6 T1': [(s, f'{LP}/state-env__la_T1_S_s{s}_r8.jsonl') for s in range(2)],
    'C0 cap-6 T1 (whole-proof)': [(s, f'{LP}/ds-generator__la_T1_c0_s{s}_r8.jsonl') for s in range(2)],
}
LADDER = {'SN-cap12 T1': [f'artifacts/sc12/la_T1_SN12_s{s}' for s in range(4)],
          'K12 T1 (whole-proof)': [f'artifacts/sc12/la_T1_K12_s{s}' for s in range(2)]}


def ge17_path(p):
    return p.replace('__rr600.jsonl', '__ge17.jsonl') if '__rr600' in p else p.replace('.jsonl', '__ge17.jsonl')


def rows(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else None


def one(p):
    rr = rows(p)
    if rr is None:
        return None
    g17 = rows(ge17_path(p))
    allb = {L: 0 for L in range(11, 17)}; gen = dict(allb); ngen = dict(allb)
    for r in rr:
        t = POOL[r['name']]; L = int(t['L_true'])
        if t['source'] == 'gen':
            ngen[L] += 1
        if r['n_ok'] > 0:
            allb[L] += 1
            if t['source'] == 'gen':
                gen[L] += 1
    s17 = sum(1 for r in g17 if r['n_ok'] > 0) if g17 is not None else None
    lstar = '<11'
    for L in range(11, 17):
        if sum(allb[x] for x in range(L, 17)) + (s17 or 0) >= 5:
            lstar = L
    if (s17 or 0) >= 5:
        lstar = '>=17'
    summ = json.load(open(p[:-6] + '.json')) if os.path.exists(p[:-6] + '.json') else {}
    trunc = summ.get('trunc_frac')
    env = summ.get('env') or {}
    return {'by_bin': allb, 'gen_by_bin': gen, 'gen_n': ngen, 'Q': sum(gen[L] for L in range(13, 17)),
            'total': sum(allb.values()), 'ge17': s17, 'lstar': lstar, 'trunc_frac': trunc,
            'env_caps': {k: env.get(k) for k in ('frac_action_cap', 'frac_step_cap', 'action_cap_frac', 'step_cap_frac') if k in env},
            'peak_mem_gb': summ.get('peak_mem_gb'), 'ckpt': summ.get('ckpt')}


def iqm(xs):
    xs = sorted(xs); n = len(xs); k = n // 4
    mid = xs[k:n - k] if n >= 4 else xs
    return sum(mid) / len(mid)


def boot(xs, B=10000, seed=0):
    if len(xs) < 2:
        return None
    rng = random.Random(seed); v = sorted(iqm([rng.choice(xs) for _ in xs]) for _ in range(B))
    return [v[int(0.025 * B)], v[int(0.975 * B) - 1]]


def ladder(d):
    fs = sorted(glob.glob(f'{d}/round_*.json'), key=lambda f: int(f.split('_')[-1][:-5]))
    if not fs:
        return None
    last = json.load(open(fs[-1])); tc = last.get('transfer_cum', {})
    ge13 = None
    fp = f'{d}/found_transfer_{len(fs)}.jsonl'
    if os.path.exists(fp):
        ge13 = sum(1 for l in open(fp) if json.loads(l).get('proofs') and int(ORIG[json.loads(l)['name']]['n_lines']) >= 13)
    return {'rounds': len(fs), 'solved': tc.get('solved'), 'lstar': tc.get('lstar'), 'ge13': ge13}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='artifacts/sc12/summary.json'); ap.add_argument('--md', default='artifacts/sc12/tables.md')
    a = ap.parse_args()
    record.save_config(vars(a), a.out)
    res, md = {}, []
    md.append('| arm | seed | 11 | 12 | 13 | 14 | 15 | 16 | >=17 /70 | total /600 | `L*` | Q gen 13-16 /380 | gen 11-16 |')
    md.append('|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|')
    for arm, cells in ARMS.items():
        res[arm] = {}
        for s, p in cells:
            o = one(p)
            if o is None:
                continue
            res[arm][s] = o
            b = o['by_bin']; g = o['gen_by_bin']
            md.append(f"| {arm} | s{s} | " + ' | '.join(str(b[L]) for L in range(11, 17)) +
                      f" | {o['ge17']} | {o['total']} | {o['lstar']} | **{o['Q']}** | " + ' '.join(str(g[L]) for L in range(11, 17)) + ' |')
        qs = [o['Q'] for o in res[arm].values()]
        if qs:
            res[arm]['_Q'] = {'per_seed': qs, 'mean': sum(qs) / len(qs), 'iqm': iqm(qs), 'boot95': boot(qs)}
    md.append('')
    md.append('| arm | n | Q per seed | Q mean | Q IQM [95 % bootstrap] |')
    md.append('|---|---:|---|---:|---|')
    for arm in ARMS:
        q = res[arm].get('_Q')
        if q:
            md.append(f"| {arm} | {len(q['per_seed'])} | {q['per_seed']} | {q['mean']:.1f} | {q['iqm']:.1f} {q['boot95']} |")
    md.append('')
    md.append('Original pool (`transfer.jsonl`, 2,285): in-loop cumulative T1 at round 8.')
    md.append('')
    md.append('| arm | seed | rounds | solved | `L*` | solved at `L_true` >= 13 |')
    md.append('|---|---|---:|---:|---|---:|')
    res['_ladder'] = {}
    for arm, ds in LADDER.items():
        for d in ds:
            o = ladder(d)
            if o:
                res['_ladder'][os.path.basename(d)] = o
                md.append(f"| {arm} | {d[-2:]} | {o['rounds']} | {o['solved']} | {o['lstar']} | {o['ge13']} |")
    md.append('')
    md.append('Original pool, frozen = Stage-1 re-read at k 256 on `transfer.jsonl`.')
    md.append('')
    res['_orig_frozen'] = {}
    for s in range(4):
        p = f'{RR}/stage1_SN12_s{s}__orig.json'
        if os.path.exists(p):
            d = json.load(open(p))
            res['_orig_frozen'][s] = {'solved': d['solved'], 'lstar_by_len': d.get('by_len')}
            ge = {int(L): v['solved'] for L, v in d['by_len'].items()}
            lst = max([L for L in ge if sum(v for k, v in ge.items() if k >= L) >= 5] or [0])
            res['_orig_frozen'][s]['lstar'] = lst; res['_orig_frozen'][s]['ge13'] = sum(v for k, v in ge.items() if k >= 13)
            md.append(f"- SN-cap12 frozen s{s}: solved {d['solved']} / {d['n']}, `L*` {lst}, at >= 13: {res['_orig_frozen'][s]['ge13']}")
    md.append('')
    md.append('Held-out greedy (`data/p2/heldout.jsonl`, 5,000), Stage-1 SN-cap12:')
    for s in range(4):
        p = f'artifacts/sc12/heldout_SN12_s{s}.json'
        if os.path.exists(p):
            d = json.load(open(p)); res.setdefault('_heldout', {})[s] = d.get('rate', d.get('acc'))
            md.append(f"- s{s}: {d.get('rate', d.get('acc'))}  ({d.get('solved')} / {d.get('n')})")
    json.dump(res, open(a.out, 'w'), indent=1, default=str)
    open(a.md, 'w').write('\n'.join(md) + '\n')
    print('\n'.join(md))


if __name__ == '__main__':
    main()
