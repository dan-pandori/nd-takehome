#!/usr/bin/env python3
"""round3-run4b analysis: depth-3 on the required@8 pool at 25M / 85M, with run 1's 3.2M row counted by the same code.

  python3 r3_4b_analysis.py [--verify_all]   # -> artifacts/r3_4b/summary.json, artifacts/r3_4b/summary_table.md

Per draw: parameters (Stage-1 log), held-out greedy (eval_set summary), pre-RL pattern hits / rate (coverage_stats on the
k = 2,000 sample), req / frozen / mix arms (r3_1_analysis.arm_summary: start-index normalised, min-round rule, patterns.depth3
on the pruned proof, nd_verify re-run), base-reachable at 10^4 (k = 10,000 sample, when run) and the EI-only fraction
= acquired required targets with no pattern proof in the base's 10^4 samples / acquired.
"""
import argparse, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r3_1_analysis import arm_summary, THR
from ignition_analysis import coverage_stats
from phase2_metrics import arm_metrics

A = 'artifacts/r3_4b'
PAT = 'depth3'
REQ = {json.loads(l)['name']: json.loads(l) for l in open('data/r3_1/depth3_req.jsonl')}


def cov(fn):
    if not os.path.exists(fn):
        return None
    c = coverage_stats(fn, PAT)
    return {'file': fn, 'n_targets': c['n_targets'], 'n_tried': c['n_tried'], 'hits': c['hits_pattern'], 'rate': c['rate_pattern'],
            'targets_with_pattern': c['targets_with_pattern'], 'pattern_targets': sorted(t['name'] for t in c['per_target']),
            'distinct_pattern_proofs': c['distinct_pattern_proofs'], 'frozen256_pattern_theorems': c['frozen256_pattern_theorems'],
            'solved_any': c['solved_any'], 'zero_rate': c['hits_pattern'] == 0, 'top_targets': c['per_target'][:5]}


def arm(d, verify_all):
    if not os.path.isdir(d) or not os.path.exists(f'{d}/round_1.json'):
        return None
    r = arm_summary(d, PAT, verify_all)
    if r is None:
        return None
    last = arm_metrics(d, PAT)[-1]
    r['pattern_required_names'] = sorted(n for n in last['pattern_names_targets'] if n.startswith('d3req_'))
    r['ignition_round_2pct'] = next((p['round'] for p in r['per_round'] if p['pattern_required'] >= 6), None)
    r['alt_route'] = [{'name': n, 'r10_min_lines_ub': REQ[n].get('r10_min_lines_ub')} for n in r['required_solved_without_pattern']]
    r['trained_rounds'] = sum(1 for p in r['per_round'] if p['mix_rl_records'] > 0)
    r['args'] = {k: v for k, v in json.load(open(f'{d}/args.json')).items() if k in ('ft_lr', 'ft_steps', 'batch', 'k', 'rounds', 'no_train', 'seed', 'targets', 'init')}
    return r


def draw(tag, covfn, armdir, s1log=None, gatefn=None, cov10k=None, verify_all=False):
    D = {'tag': tag}
    if s1log and os.path.exists(s1log):
        t = open(s1log).read()
        m = re.search(r'params (\d+)', t); D['params'] = int(m.group(1)) if m else None
        v = re.findall(r'step (\d+) loss ([\d.]+) .* val ([\d.]+)', t); D['stage1_last'] = {'step': int(v[-1][0]), 'loss': float(v[-1][1]), 'val': float(v[-1][2])} if v else None
    if gatefn and os.path.exists(gatefn):
        g = json.load(open(gatefn)); D['heldout_greedy'] = g.get('rate', g.get('overall', g)); D['heldout_greedy_file'] = gatefn
    D['pre_rl'] = cov(covfn)
    for a in ('req', 'frozen', 'mix'):
        D[a] = arm(armdir.format(arm=a), verify_all)
    if cov10k:
        D['base_1e4'] = cov(cov10k)
    D['optional_pool_pre_rl'] = cov(covfn.replace('/cov_depth3_', '/optcov_depth3_')) if '/cov_depth3_' in covfn and 'r3_4b' in covfn else None
    D['frozen_skipped'] = os.path.exists(f"{A}/q/frozen_{tag}.skipped")
    if D.get('req') and D.get('base_1e4'):
        acq = set(D['req']['pattern_required_names']); base = set(D['base_1e4']['pattern_targets'])
        base_u = base | set(D['pre_rl']['pattern_targets']) if D['pre_rl'] else base
        D['ei_only'] = {'acquired': len(acq), 'base_reachable_1e4': len(base), 'acquired_and_base': len(acq & base), 'ei_only': len(acq - base),
                        'fraction': len(acq - base) / len(acq) if acq else None, 'base_only': len(base - acq),
                        'ei_only_vs_union_with_600k': len(acq - base_u)}
    elif D.get('req') and D.get('pre_rl'):   # no 10^4 sample: the 600k (k = 2,000) sample stands in, labelled as such
        acq = set(D['req']['pattern_required_names']); base = set(D['pre_rl']['pattern_targets'])
        D['ei_only_at_2000'] = {'acquired': len(acq), 'base_reachable_2000': len(base), 'ei_only': len(acq - base),
                                'fraction': len(acq - base) / len(acq) if acq else None}
    return D


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--verify_all', action='store_true'); a = ap.parse_args()
    S = {'sizes': {}}
    for size in ('25M', '25Mr', '85M', '85Mr'):
        S['sizes'][size] = {}
        for s in (0, 1, 2):
            T = f'{size}_s{s}'
            if not os.path.exists(f'{A}/q/s1_{T}.log'):
                continue
            S['sizes'][size][f's{s}'] = draw(T, f'{A}/cov_depth3_{T}.s0.jsonl', f'{A}/ei_depth3_{T}_{{arm}}', f'{A}/q/s1_{T}.log',
                                             f'{A}/heldout_greedy_{T}.json', f'{A}/cov1e4_depth3_{T}.s0.jsonl', a.verify_all)
    S['sizes']['3.2M'] = {f's{s}': draw(f'3.2M_s{s}', f'artifacts/r3_1/cov_depth3_s{s}.s0.jsonl', f'artifacts/r3_1/ei_depth3_s{s}_{{arm}}', verify_all=a.verify_all)
                          for s in range(20, 28)}
    for size, dr in S['sizes'].items():
        pre = [d['pre_rl'] for d in dr.values() if d.get('pre_rl')]
        rates = sorted(p['rate'] for p in pre)
        S.setdefault('by_size', {})[size] = {'draws_sampled': len(pre), 'non_zero': sum(not p['zero_rate'] for p in pre),
                                             'median_rate': rates[len(rates) // 2] if len(rates) % 2 else (sum(rates[len(rates) // 2 - 1:len(rates) // 2 + 1]) / 2 if rates else None)}
    json.dump(S, open(f'{A}/summary.json', 'w'), indent=1)
    L = ['| size | draw | params | held-out greedy | optional-pool hits / tried (targets) | pre-RL hits / tried | rate | targets w/ pattern | frozen@256 | req: ignition (>= 20) | req pattern targets r1-8 | req solved w/o pattern | trained rounds | frozen arm r8 | mix r1-8 | base@1e4 targets | EI-only / acquired | verify fail |',
         '|' + '---|' * 18]
    for size in ('3.2M', '25M', '25Mr', '85M', '85Mr'):
        for k, d in S['sizes'][size].items():
            p, r, f, m, e = d.get('pre_rl'), d.get('req'), d.get('frozen'), d.get('mix'), d.get('ei_only')
            hg = d.get('heldout_greedy'); hg = f'{hg:.3f}' if isinstance(hg, float) else (hg or '-')
            o = d.get('optional_pool_pre_rl'); o = f"{o['hits']} / {o['n_tried']} ({o['targets_with_pattern']})" if o else '-'
            L.append(f"| {size} | {k} | {d.get('params', '-')} | {hg} | {o} | " + (f"{p['hits']} / {p['n_tried']} | {p['rate']:.1e} | {p['targets_with_pattern']} | {p['frozen256_pattern_theorems']}" if p else '- | - | - | -') + ' | ' +
                     (f"{r['ignition_round']} | {[x['pattern_required'] for x in r['per_round']]} | {len(r['required_solved_without_pattern'])} | {r['trained_rounds']}" if r else '- | - | - | -') + ' | ' +
                     (f"{f['final_pattern_required']}" if f else ('= req (skipped)' if d.get('frozen_skipped') else '-')) + ' | ' + (f"{[x['pattern_required'] for x in m['per_round']]}" if m else '-') + ' | ' +
                     (f"{e['base_reachable_1e4']} | {e['ei_only']} / {e['acquired']}" if e else '- | -') + ' | ' +
                     (f"{r['verify_failures']} / {r['verify_sample']}" if r else '-') + ' |')
    L.append('\n' + json.dumps(S['by_size']))
    open(f'{A}/summary_table.md', 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
