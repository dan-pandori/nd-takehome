#!/usr/bin/env python3
"""R3 (reviewer, phase 1): EDL recount from the stored per-proof, per-block bits (artifacts/style_edl/edl, edl_x).
Nothing is taken from the files' 'summary' fields; every quantity is recomputed from the per-proof lists.

Pre-registered definitions (preregistration/style-edl.md):
  preq(lr, o)  = sum over blocks of the block's coded bits;  L_test(lr, o) = mean of theta*'s test bits
  lr*          = argmin_lr mean_o preq(lr, o)   (A_ES grid 1e-5, 1e-4, 1e-3);  + log2(3) bits for the choice
  EDL          = mean_o [preq(lr*, o) - 128 L_test(lr*, o)] + log2 3
  M            = sum_stream learner bits - 128 * mean_test learner bits         (no training can change it)
  EDL_c        = EDL - M
  F            = max(0.1; |EDL_c(S_own) - EDL_c(S_own2)| over seeds; |EDL_c(o0) - EDL_c(o1)| over seeds, S_own, S_own2)
  python3 r3_edl.py -> out/r3_edl.json
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_core as C

A = f'{C.WS}/artifacts/style_edl'
SEEDS = (0, 1, 2)
STREAMS = ('S_own', 'S_own2', 'S_seed', 'S_short', 'S_RL', 'S_Kal')
LOG3 = math.log2(3)


def cell(fn, lr_fixed=None):
    d = json.load(open(fn))
    n = d['n_stream']
    nt = d['n_test']
    b0s = d['base']['stream']['bits']
    b0t = d['base']['test']['bits']
    acts = sum(d['stream_acts'])
    M = sum(b0s) - n * (sum(b0t) / nt)
    runs = {}
    checks = {'block0_equals_learner': 0, 'block0_checked': 0, 'perm_ok': 0}
    for r in d['runs']:
        perm = r['perm']
        assert sorted(perm) == list(range(n))
        checks['perm_ok'] += 1
        pre = 0.0
        per_proof = [None] * n            # block bits per proof, in file order
        curve = []
        for b in r['blocks']:
            lo, hi = b['lo'], b['hi']
            bits = b['block']['bits']
            assert len(bits) == hi - lo
            pre += sum(bits)
            for k, x in zip(range(lo, hi), bits):
                per_proof[perm[k]] = x
            curve.append({'lo': lo, 'hi': hi, 'bits_per_proof': sum(bits) / (hi - lo), 'p': b['fit'].get('passes'),
                          'test_mean_bits': b['test_mean_bits']})
            if lo == 0:
                for k, x in zip(range(lo, hi), bits):
                    checks['block0_checked'] += 1
                    checks['block0_equals_learner'] += abs(x - b0s[perm[k]]) < 1e-3
        Lt = sum(r['theta']['test']['bits']) / nt
        key = (r['lr'], r['E'])
        runs.setdefault(key, {})[r['order']] = {
            'preq': pre, 'L_test': Lt, 'EDL_raw': pre - n * Lt, 'EDL_c_raw': pre - n * Lt - M,
            'first_block_per_proof': curve[0]['bits_per_proof'], 'curve': curve, 'per_proof_block_bits': per_proof,
            'theta_test_bits': r['theta']['test']['bits'], 'p_theta': r['theta']['fit'].get('passes'),
            'p_blocks': [c['p'] for c in curve], 'theta_ckpt': r.get('theta_ckpt'),
            'theta_test_agree': sum(r['theta']['test_agree']), 'stream_after_mean': sum(r['theta']['stream_after']['bits']) / n}
    keys = sorted(runs)
    mean_pre = {k: sum(v['preq'] for v in runs[k].values()) / len(runs[k]) for k in keys}
    if lr_fixed is not None:
        kstar = [k for k in keys if abs(k[0] - lr_fixed) < 1e-12][0]
    else:
        kstar = min(keys, key=lambda k: mean_pre[k])
    R = runs[kstar]
    orders = sorted(R)
    edl = sum(R[o]['EDL_raw'] for o in orders) / len(orders) + LOG3
    out = {'n': n, 'n_test': nt, 'stream_actions': acts, 'stream_actions_per_proof': acts / n,
           'test_actions_per_proof': sum(d['test_acts']) / nt,
           'stream_tok_per_proof': sum(d['stream_tok']) / n, 'stream_tok_all_per_proof': sum(d['stream_tok_all']) / n,
           'learner_stream_mean': sum(b0s) / n, 'learner_test_mean': sum(b0t) / nt,
           'learner_all256_mean': (sum(b0s) + sum(b0t)) / (n + nt), 'M_per_proof': M / n,
           'learner_stream_all_tok_mean': sum(d['base']['stream']['bits_all']) / n,
           'lr_star': kstar[0], 'E': kstar[1], 'mean_preq_by_lr': {f'{k[0]:g}': v for k, v in mean_pre.items()},
           'EDL_per_proof': edl / n, 'EDL_per_action': edl / acts, 'EDL_c_per_proof': (edl - M) / n,
           'EDL_c_per_action': (edl - M) / acts,
           'EDL_c_per_proof_by_order': {o: (R[o]['EDL_c_raw'] + LOG3) / n for o in orders},
           'EDL_per_proof_by_order': {o: (R[o]['EDL_raw'] + LOG3) / n for o in orders},
           'L_test_per_proof': sum(R[o]['L_test'] for o in orders) / len(orders),
           'first_block_per_proof': sum(R[o]['first_block_per_proof'] for o in orders) / len(orders),
           'first_block_by_order': {o: R[o]['first_block_per_proof'] for o in orders},
           'preq_per_proof': sum(R[o]['preq'] for o in orders) / len(orders) / n,
           'curve': {o: R[o]['curve'] for o in orders},
           'p_theta': {o: R[o]['p_theta'] for o in orders}, 'p_blocks': {o: R[o]['p_blocks'] for o in orders},
           'theta_ckpt': {o: R[o]['theta_ckpt'] for o in orders},
           'theta_test_agree_frac': {o: R[o]['theta_test_agree'] / sum(d['test_acts']) for o in orders},
           'stream_after_mean': {o: R[o]['stream_after_mean'] for o in orders},
           'learner_tf_agree_stream': sum(d['base']['stream_agree']) / acts,
           'learner_tf_agree_all256': (sum(d['base']['stream_agree']) + sum(d['base']['test_agree'])) / (acts + sum(d['test_acts'])),
           'checks': checks, 'secs': d.get('secs'), 'peak_alloc_gb': d.get('peak_alloc_gb'), 'dev': d.get('dev'),
           'all_runs': {f'{k[0]:g}/E{k[1]}': {o: {x: v[x] for x in ('preq', 'L_test', 'EDL_raw', 'EDL_c_raw', 'p_theta', 'p_blocks')}
                                              for o, v in runs[k].items()} for k in keys}}
    out['_R'] = R
    out['_b0s'] = b0s
    out['_b0t'] = b0t
    out['_names'] = (d['stream_names'], d['test_names'])
    return out


def main():
    res = {}
    for s in SEEDS:
        for S in STREAMS:
            res[f's{s}/{S}'] = cell(f'{A}/edl/s{s}/{S}.json')
            res[f's{s}/{S}/fixed'] = cell(f'{A}/edl/s{s}/{S}.fixed.json')
            res[f's{s}/{S}/xfit'] = cell(f'{A}/edl_x/s{s}/{S}.json')
            res[f's{s}/{S}/xfit_at_lrstar'] = cell(f'{A}/edl_x/s{s}/{S}.json', lr_fixed=res[f's{s}/{S}']['lr_star'])
    # pilot E choice (seed 0 S_own, fixed, E in 1,2,4)
    d = json.load(open(f'{A}/edl/s0/S_own.fixed.json'))
    pe = {}
    for r in d['runs']:
        pre = sum(sum(b['block']['bits']) for b in r['blocks'])
        pe.setdefault((r['E'], r['lr']), []).append(pre)
    best_by_E = {}
    for (E, lr), v in pe.items():
        m = sum(v) / len(v)
        if E not in best_by_E or m < best_by_E[E][1]:
            best_by_E[E] = (lr, m)
    pilot = {'E_grid': sorted({E for E, _ in pe}), 'best_lr_and_mean_preq_by_E': {str(E): v for E, v in sorted(best_by_E.items())}}
    Es = sorted(best_by_E, key=lambda E: best_by_E[E][1])
    pilot['lowest'] = Es[0]
    pilot['rule_choice'] = 2 if (2 in best_by_E and best_by_E[2][1] - best_by_E[Es[0]][1] <= 1.0) else Es[0]
    # the fixed runs of the other cells use which E?
    pilot['E_used_elsewhere'] = sorted({res[k]['E'] for k in res if k.endswith('/fixed') and k != 's0/S_own/fixed'})
    # gate: S_own pilot (seed 0, A_ES, both orders) |EDL_c| <= 0.3 bits per proof
    gate = {'EDL_c_per_proof_s0_S_own': res['s0/S_own']['EDL_c_per_proof'],
            'by_order': res['s0/S_own']['EDL_c_per_proof_by_order']}
    gate['pass'] = abs(gate['EDL_c_per_proof_s0_S_own']) <= 0.3 and all(abs(v) <= 0.3 for v in gate['by_order'].values())
    # floor F
    c1 = [abs(res[f's{s}/S_own']['EDL_c_per_proof'] - res[f's{s}/S_own2']['EDL_c_per_proof']) for s in SEEDS]
    c2 = [abs(res[f's{s}/{S}']['EDL_c_per_proof_by_order'][0] - res[f's{s}/{S}']['EDL_c_per_proof_by_order'][1])
          for s in SEEDS for S in ('S_own', 'S_own2')]
    F = max([0.1] + c1 + c2)
    floor = {'own_vs_own2': c1, 'order_diffs': c2, 'F': F}
    # excess over S_own2
    exc = {}
    for S in STREAMS:
        exc[S] = {'EDL': [res[f's{s}/{S}']['EDL_per_proof'] - res[f's{s}/S_own2']['EDL_per_proof'] for s in SEEDS],
                  'EDL_c': [res[f's{s}/{S}']['EDL_c_per_proof'] - res[f's{s}/S_own2']['EDL_c_per_proof'] for s in SEEDS]}
        exc[S]['exceeds_F_3of3_EDL'] = all(x > F for x in exc[S]['EDL'])
        exc[S]['exceeds_F_3of3_EDL_c'] = all(x > F for x in exc[S]['EDL_c'])
    # cross-fit mean (exploratory): mean of the two directions, each at its own lr*
    xm = {}
    for S in STREAMS:
        xm[S] = {'EDL_xmean_per_proof': [(res[f's{s}/{S}']['EDL_per_proof'] + res[f's{s}/{S}/xfit']['EDL_per_proof']) / 2 for s in SEEDS],
                 'EDL_x_per_proof': [res[f's{s}/{S}/xfit']['EDL_per_proof'] for s in SEEDS],
                 'EDL_c_x_per_proof': [res[f's{s}/{S}/xfit']['EDL_c_per_proof'] for s in SEEDS],
                 'xfit_lr_star': [res[f's{s}/{S}/xfit']['lr_star'] for s in SEEDS]}
    for k in res:
        for x in ('_R', '_b0s', '_b0t', '_names'):
            res[k].pop(x, None)
    out = {'cells': res, 'pilot_E': pilot, 'gate': gate, 'floor': floor, 'excess_over_S_own2': exc, 'xfit_mean': xm}
    json.dump(out, open(os.path.join(C.HERE, 'out', 'r3_edl.json'), 'w'), indent=1)
    # table
    print('pilot', json.dumps(pilot)); print('gate', json.dumps(gate)); print('floor', json.dumps(floor))
    hdr = f"{'cell':16s} {'lr*':>7s} {'start':>8s} {'L0all':>8s} {'Ltest':>8s} {'EDL/pf':>8s} {'EDLc/pf':>8s} {'EDL/act':>8s} {'M/pf':>7s} {'acts':>6s} {'tok':>6s} {'TFag':>6s} {'p*theta':>8s}"
    print(hdr)
    for s in SEEDS:
        for S in STREAMS:
            c = res[f's{s}/{S}']
            print(f"{'s%d/%s' % (s, S):16s} {c['lr_star']:7.0e} {c['first_block_per_proof']:8.3f} {c['learner_all256_mean']:8.3f} {c['L_test_per_proof']:8.3f} "
                  f"{c['EDL_per_proof']:8.3f} {c['EDL_c_per_proof']:8.3f} {c['EDL_per_action']:8.4f} {c['M_per_proof']:7.3f} {c['stream_actions_per_proof']:6.2f} {c['stream_tok_per_proof']:6.1f} {c['learner_tf_agree_all256']:6.3f} {str(list(c['p_theta'].values())):>8s}")
    for S in STREAMS:
        print(S, 'excess EDL', [round(x, 3) for x in exc[S]['EDL']], 'EDL_c', [round(x, 3) for x in exc[S]['EDL_c']],
              exc[S]['exceeds_F_3of3_EDL'], exc[S]['exceeds_F_3of3_EDL_c'])
    for S in STREAMS:
        print(S, 'xfit', {k: [round(x, 3) if isinstance(x, float) else x for x in v] for k, v in xm[S].items()})
    for s in SEEDS:
        for S in STREAMS:
            c = res[f's{s}/{S}/fixed']
            print('fixed', f's{s}/{S}', c['E'], c['lr_star'], round(c['EDL_per_proof'], 3), round(c['EDL_c_per_proof'], 3))


if __name__ == '__main__':
    main()
