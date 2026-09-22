#!/usr/bin/env python3
"""ds-composition: every number of the run re-derived from pulled files -> artifacts/dsc/summary.json (one row per arm x seed) + printed tables.

  python3 dsc_analysis.py

Sources (all under artifacts/dsc/ unless stated)
  held-out greedy      heldout_<arm>_s<k>.jsonl (eval_set.py rows; Lean-gated); by length and by pattern / no-pattern of the generator proof (data/p2/heldout.jsonl `pat`)
  base rates           cov_<arm>_s<k>_<pool>.s0.jsonl (coverage_lean.py; pools depth3 = data/p2/targets_depth3.jsonl, d3req = data/r3_1/depth3_req.jsonl, redreq = data/p2/targets_reductio_req.jsonl)
  dial                 {ei,frozen}_<arm>_s<k>/round_4.json + found_4.jsonl (control: artifacts/lf/{ei,frozen}_d3_seq_s<k>/ same files); acquisition = targets with a depth-3 proof (patterns.classify on the pruned proof), min round per normalised proof
  ladder               la_{T1,frozen}_<arm>_s<k>/found_transfer_8.jsonl, found_8.jsonl vs data/ladder pools; L* = max L with >= 5 theorems solved at L_true >= L; textbook solves per schema
  checker of record    record_<arm>.json (nd2lean.py --check on every counted proof)
  gate                 gate_*.jsonl (2 x 2 agreement of Lean and nd_verify on distinct sampled texts), cov_*.gate.json
  set shape            data/dsc/shape_<arm>.json
"""
import json, os, sys, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from normalize import norm
from patterns import classify

D = 'artifacts/dsc'
ARMS = ['c0', 'a1', 'a2', 'a3', 'a4']
SEEDS = (0, 1)


def rd(fn):
    return [json.loads(l) for l in open(fn) if l.strip()]


def jl(fn):
    return json.load(open(fn)) if os.path.exists(fn) else None


def heldout(arm, s):
    fn = f'{D}/heldout_{arm}_s{s}.jsonl'
    if not os.path.exists(fn):
        return None
    pat = {r['name']: any(r['pat'].values()) for r in rd('data/p2/heldout.jsonl')}
    rows = rd(fn)
    by = collections.defaultdict(lambda: [0, 0]); byp = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        by[r['n_lines']][0] += r['solved']; by[r['n_lines']][1] += 1
        byp[(r['n_lines'], pat[r['name']])][0] += r['solved']; byp[(r['n_lines'], pat[r['name']])][1] += 1
    tot = sum(v[0] for v in by.values()); n = sum(v[1] for v in by.values())
    return {'n': n, 'rate': tot / n, 'by_len': {L: by[L][0] / by[L][1] for L in sorted(by)},
            'by_len_pattern': {f'{L}_{"pat" if p else "nopat"}': {'solved': k, 'n': m, 'rate': k / m} for (L, p), (k, m) in sorted(byp.items())},
            'nopat_rate': sum(k for (L, p), (k, m) in byp.items() if not p) / sum(m for (L, p), (k, m) in byp.items() if not p),
            'pat_rate': sum(k for (L, p), (k, m) in byp.items() if p) / max(1, sum(m for (L, p), (k, m) in byp.items() if p))}


def coverage(arm, s, pool):
    fn = f'{D}/cov_{arm}_s{s}_{pool}.s0.jsonl'
    if not os.path.exists(fn):
        return None
    rows0 = rd(fn)
    # 2026-09-22: orphaned duplicate coverage processes (log.md 09:25) appended a second record for some targets; keep the FIRST record per
    # target (both copies ran the same checkpoint and sampling seed) and report how many duplicates differed.
    seen = {}; rows = []; n_dup = 0; n_dup_diff = 0
    for r in rows0:
        if r['name'] in seen:
            n_dup += 1; n_dup_diff += [p['proof'] for p in r['proofs']] != [p['proof'] for p in seen[r['name']]['proofs']]
            continue
        seen[r['name']] = r; rows.append(r)
    key = 'depth3' if pool in ('d3sub', 'depth3', 'd3req') else 'derived_dn'
    key2 = 'reductio' if pool == 'redreq' else None
    solved = sum(1 for r in rows if r['n_ok'] > 0)
    patt = sum(1 for r in rows if any(p['pat'][key] for p in r['proofs']))
    strict = sum(1 for r in rows if any(p['pat'][key2] for p in r['proofs'])) if key2 else None
    tried = sum(r['n_tried'] for r in rows); ok = sum(r['n_ok'] for r in rows); ok_nd = sum(r['n_ok_nd'] for r in rows); pf = sum(r['n_parse_fail'] for r in rows)
    strata = collections.defaultdict(lambda: [0, 0, 0])
    for r in rows:
        st = str(r.get('min_lines_ub') if r.get('min_lines_ub') is not None else r.get('gen_lines'))
        strata[st][2] += 1; strata[st][0] += r['n_ok'] > 0; strata[st][1] += any(p['pat'][key] for p in r['proofs'])
    long_pat = sum(1 for r in rows for p in r['proofs'] if p['written'] >= 8 and p['pat'][key])
    wh = collections.Counter(p['written'] for r in rows for p in r['proofs'])
    g = collections.Counter()
    for r in rows:
        for k, v in r['gate'].items():
            g[k] += v
    return {'n': len(rows), 'duplicate_records_dropped': n_dup, 'duplicates_differing': n_dup_diff, 'solved': solved, 'solved_with_pattern': patt, 'pattern_key': key, 'solved_with_reductio_strict': strict, 'rate': patt / len(rows),
            'samples': tried, 'accepted_samples': ok, 'nd_only_samples': ok_nd - ok, 'parse_fail_samples': pf, 'per_sample_rate': ok / tried,
            'by_stratum': {k: {'n': v[2], 'solved': v[0], 'pattern': v[1]} for k, v in sorted(strata.items())},
            'distinct_pattern_proofs_ge8': long_pat, 'written_hist': dict(sorted(wh.items())), 'distinct_proofs': sum(len(r['proofs']) for r in rows),
            'gate': dict(g), 'pass_at': {B: sum(1 for r in rows if r['solved_within'][B]) for B in ('32', '128', '512', '1000', '2000')}}


def dial(d, R=4):
    """acquisition at round R: targets with a depth-3 (pruned) proof whose earliest round <= R."""
    if not os.path.exists(f'{d}/round_{R}.json'):
        return None
    fn = f'{d}/found_{R}.jsonl' if os.path.exists(f'{d}/found_{R}.jsonl') else sorted(glob.glob(f'{d}/found_*.jsonl'), key=lambda f: int(f.split('_')[-1][:-6]))[-1]
    recs = rd(fn); minround = {}
    for x in recs:
        k = (x['name'], norm(x['proof'])); minround[k] = min(minround.get(k, 99), x['round'])
    acq = set(); solved = set(); nproof = 0; seen = set(); texts = 0
    for x in recs:
        k = (x['name'], norm(x['proof']))
        if minround[k] > R or k in seen:
            continue
        seen.add(k); solved.add(x['name']); nproof += 1; texts += 'text' in x and bool(x['text'])
        cl = classify(x['proof'])
        if cl and cl['depth3']:
            acq.add(x['name'])
    st = json.load(open(f'{d}/round_{R}.json'))
    return {'dir': d, 'round': R, 'attempts': R * st['k'], 'targets_solved': len(solved), 'acq_targets': len(acq) / 1000, 'acq_n': len(acq), 'distinct_proofs': nproof,
            'proofs_with_text': texts, 'heldout_greedy': st['heldout_greedy']['rate'], 'transfer_solved': st['transfer_cum']['solved'], 'secs': st['secs']}


def ladder(d, R=8):
    if not os.path.exists(f'{d}/found_transfer_{R}.jsonl'):
        return None
    transfer, targets = rd('data/ladder/transfer.jsonl'), rd('data/ladder/rl_targets.jsonl')
    out = {'dir': d, 'round': R}
    for pool, fn, recs in (('transfer', f'{d}/found_transfer_{R}.jsonl', transfer), ('targets', f'{d}/found_{R}.jsonl', targets)):
        by = collections.defaultdict(set)
        for x in rd(fn):
            by[x['name']].add(norm(x['proof']))
        solved = set(by)
        Lt = {r['name']: r['n_lines'] for r in recs}
        ge = {L: sum(1 for n in solved if Lt[n] >= L) for L in range(7, 15)}
        bins = {L: [sum(1 for r in recs if r['n_lines'] == L and r['name'] in solved), sum(1 for r in recs if r['n_lines'] == L)] for L in range(7, 15)}
        sch = collections.defaultdict(lambda: [0, 0])
        for r in recs:
            if r.get('schema'):
                sch[r['schema']][0] += r['name'] in solved; sch[r['schema']][1] += 1
        out[pool] = {'n': len(recs), 'solved': len(solved), 'lstar': max([L for L, c in ge.items() if c >= 5], default=0), 'ge': ge, 'by_bin': bins,
                     'distinct_proofs': sum(len(v) for v in by.values()), 'by_schema': {k: v[0] for k, v in sorted(sch.items())},
                     'schemas_ge5': sorted(k for k, v in sch.items() if v[0] >= 5),
                     'textbook_solved': sum(1 for r in recs if r.get('source') == 'textbook' and r['name'] in solved),
                     'gen_solved': sum(1 for r in recs if r.get('source') == 'gen' and r['name'] in solved)}
    st = json.load(open(f'{d}/round_{R}.json'))
    out['heldout_greedy_r8'] = st['heldout_greedy']['rate']; out['secs_by_round'] = [json.load(open(f'{d}/round_{r}.json'))['secs'] for r in range(1, R + 1) if os.path.exists(f'{d}/round_{r}.json')]
    return out


def main():
    S = {'rows': {}, 'shape': {}, 'record': {}, 'gate': {}}
    for arm in ARMS:
        S['shape'][arm] = jl(f'data/dsc/shape_{arm}.json')
        S['record'][arm] = jl(f'{D}/record_{arm}.json')
        for s in SEEDS:
            row = {'arm': arm, 'seed': s, 'cap': 8 if arm == 'a3' else 6, 'label': 'cap 8' if arm == 'a3' else 'cap 6'}
            row['heldout'] = heldout(arm, s)
            row['coverage'] = {pool: coverage(arm, s, pool) for pool in ('d3sub', 'd3req', 'redreq')}
            if arm == 'c0':
                row['dial_ei'] = dial(f'artifacts/lf/ei_d3_seq_s{s}'); row['dial_frozen'] = dial(f'artifacts/lf/frozen_d3_seq_s{s}')
                row['dial_ei_rerun'] = dial(f'{D}/ei_c0_s{s}'); row['dial_frozen_rerun'] = dial(f'{D}/frozen_c0_s{s}')
            else:
                row['dial_ei'] = dial(f'{D}/ei_{arm}_s{s}'); row['dial_frozen'] = dial(f'{D}/frozen_{arm}_s{s}')
            if row['dial_ei'] and row['dial_frozen']:
                row['dial_ei_minus_frozen'] = row['dial_ei']['acq_targets'] - row['dial_frozen']['acq_targets']
            row['ladder_T1'] = ladder(f'{D}/la_T1_{arm}_s{s}'); row['ladder_frozen'] = ladder(f'{D}/la_frozen_{arm}_s{s}')
            S['rows'][f'{arm}_s{s}'] = row
    # gate totals per arm
    for arm in ARMS:
        g = collections.Counter()
        for fn in glob.glob(f'{D}/gate_*_{arm}_s*.jsonl') + glob.glob(f'{D}/gate_*_{arm}.jsonl'):
            if fn.endswith('.disagree.jsonl'):
                continue
            for x in rd(fn):
                for k in ('samples', 'parse_fail', 'distinct_checked', 'both_ok', 'nd_ok_lean_rej', 'nd_rej_lean_ok', 'both_rej'):
                    g[k] += x[k]
        for fn in glob.glob(f'{D}/cov_{arm}_s*.gate.json'):
            x = json.load(open(fn)); g['cov_samples'] += x.get('samples', 0); g['cov_nd_ok_lean_rej_texts'] += x.get('nd_ok_lean_rej_texts', 0); g['cov_nd_ok_lean_ok_texts'] += x.get('nd_ok_lean_ok_texts', 0)
        S['gate'][arm] = dict(g)
    json.dump(S, open(f'{D}/summary.json', 'w'), indent=1)
    # ---- print
    print('held-out greedy (overall; by length 2..6; no-pattern / pattern):')
    for k, r in S['rows'].items():
        h = r['heldout']
        if h:
            print(f"  {k:6s} [{r['label']}] {h['rate']:.4f}  " + ' '.join(f"{h['by_len'][L]:.3f}" for L in sorted(h['by_len'])) + f"  nopat {h['nopat_rate']:.3f} pat {h['pat_rate']:.3f}")
    print('base rates pass@2,000 (targets solved with the pattern / solved; per-sample rate; >=8-line pattern proofs):')
    for k, r in S['rows'].items():
        c = r['coverage']
        print(f"  {k:6s} " + '  '.join(f"{p}: {c[p]['solved_with_pattern']}/{c[p]['solved']} of {c[p]['n']} ({c[p]['per_sample_rate']:.4f}; ge8 {c[p]['distinct_pattern_proofs_ge8']})" for p in c if c[p]))
    print('dial round 4 (acq EI / frozen / diff; held-out at r4):')
    for k, r in S['rows'].items():
        e, f = r.get('dial_ei'), r.get('dial_frozen')
        if e and f:
            print(f"  {k:6s} {e['acq_targets']:.3f} / {f['acq_targets']:.3f} / {e['acq_targets'] - f['acq_targets']:+.3f}  heldout {e['heldout_greedy']:.3f}  solved {e['targets_solved']} / {f['targets_solved']}")
    print('ladder (transfer solved, L*; frozen; textbook schemata >= 5 (T1); L_true=7 bin):')
    for k, r in S['rows'].items():
        t, f = r.get('ladder_T1'), r.get('ladder_frozen')
        if t and f:
            print(f"  {k:6s} T1 {t['transfer']['solved']} L*{t['transfer']['lstar']} | frozen {f['transfer']['solved']} L*{f['transfer']['lstar']} | bin7 {t['transfer']['by_bin'][7][0]} | ge11 {t['transfer']['ge'][11]} | schemata {t['transfer']['schemas_ge5']}")
    print('record:', json.dumps({a: {k: (v['n'], v['both_accept']) for k, v in r.items()} for a, r in S['record'].items() if r}))
    print('gate:', json.dumps(S['gate']))


if __name__ == '__main__':
    main()
