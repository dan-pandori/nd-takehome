#!/usr/bin/env python3
"""textbook72 numbers from the pulled read-outs (`artifacts/textbook72/eval/<ckpt>.{jsonl,json}`).

Lean alone decides: a problem is solved by a checkpoint iff >= 1 of its 256 attempts was accepted by the judge inside
`state_eval.py` (lean_judge).  `nd_verify` is used for one labelled secondary count only (Robbie's reward is
Lean AND nd_verify); it decides nothing.  Term size = `lean_check`'s elaborated-term size of the nd2lean translation.

  python3 tb72_analysis.py [--lean_workers 7] --out artifacts/textbook72/summary.json > artifacts/textbook72/analysis_stdout.txt
"""
import argparse, collections, json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

E = 'artifacts/textbook72/eval'
CK = [f'{a}_{m}_s{s}' for m, ss in (('SN12', range(4)), ('SN6', range(2))) for s in ss for a in ('T1', 'Fz')]
ARMS = {'SN-cap12 T1': [f'T1_SN12_s{s}' for s in range(4)], 'SN-cap12 frozen': [f'Fz_SN12_s{s}' for s in range(4)],
        'SN-v2 cap-6 T1': [f'T1_SN6_s{s}' for s in range(2)], 'SN-v2 cap-6 frozen': [f'Fz_SN6_s{s}' for s in range(2)]}
BINS = [('1-5', 1, 5), ('6-10', 6, 10), ('11-15', 11, 15), ('16+', 16, 999)]


def binof(ref):
    if ref is None:
        return 'train14 (no ref)'
    return next(b for b, lo, hi in BINS if lo <= ref <= hi)


def iqm(xs):
    xs = sorted(xs); n = len(xs); k = n // 4
    mid = xs[k:n - k] if n - 2 * k > 0 else xs
    return sum(mid) / len(mid)


def boot_ci(xs, B=10000, seed=0):
    rng = random.Random(seed); v = []
    for _ in range(B):
        v.append(iqm([rng.choice(xs) for _ in xs]))
    v.sort()
    return [v[int(0.025 * B)], v[int(0.975 * B) - 1]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--lean_workers', type=int, default=4)
    ap.add_argument('--robbie', default='artifacts/textbook72/robbie_per_problem.json')
    a = ap.parse_args()
    from nd_verify import verify_text
    probs = [json.loads(l) for fn in ('textbook_dev', 'textbook_train') for l in open(f'data/eval_only/textbook72/{fn}.jsonl')]
    role = {p['name']: p['role'] for p in probs}; ref = {p['name']: p.get('reference_lines') for p in probs}
    prompt = {p['name']: p['prompt'] for p in probs}
    names = [p['name'] for p in probs]
    rows, summ = {}, {}
    for c in CK:
        if not os.path.exists(f'{E}/{c}.json'):
            print('MISSING', c); continue
        rows[c] = {r['name']: r for r in map(json.loads, open(f'{E}/{c}.jsonl'))}
        summ[c] = json.load(open(f'{E}/{c}.json'))
    out = {'per_ckpt': {}, 'arms': {}, 'per_problem': {}}
    # ---- per checkpoint
    print('| checkpoint | dev58 | train14 | all 72 | 1-5 /5 | 6-10 /24 | 11-15 /16 | 16+ /13 | Lean∧nd_verify (72) | '
          'accepted samples | distinct accepted | distinct failing nd_verify | step-cap % | action-cap % | peak GB | wall s |')
    print('|' + '---|' * 16)
    ndv_cache = {}
    for c, rr in rows.items():
        sol = {n for n in names if rr[n]['solved']}
        ndok = set(); nfail = 0; ndist = 0
        for n in names:
            for p in rr[n]['proofs']:
                ndist += 1
                key = (n, p)
                if key not in ndv_cache:
                    ndv_cache[key] = bool(verify_text(prompt[n].strip() + ' ' + p.strip())[0])
                if ndv_cache[key]:
                    ndok.add(n)
                else:
                    nfail += 1
        by = collections.Counter(binof(ref[n]) for n in sol)
        env = summ[c]['env']; att = sum(rr[n]['n_tried'] for n in names)
        ends = env.get('env_end', {})
        d = {'dev58': sum(role[n] == 'textbook_dev' for n in sol), 'train14': sum(role[n] != 'textbook_dev' for n in sol),
             'all72': len(sol), 'by_bin': {b: by.get(b, 0) for b, _, _ in BINS} | {'train14': by.get('train14 (no ref)', 0)},
             'lean_and_ndverify_all72': len(ndok), 'lean_and_ndverify_dev58': sum(role[n] == 'textbook_dev' for n in ndok),
             'accepted_samples': sum(rr[n]['n_ok'] for n in names), 'distinct_accepted': ndist,
             'distinct_failing_ndverify': nfail, 'attempts': att,
             'step_cap': ends.get('step_cap', 0), 'action_cap': ends.get('truncated', 0), 'env_end': ends,
             'step_cap_rate': ends.get('step_cap', 0) / att, 'action_cap_rate': ends.get('truncated', 0) / att,
             'peak_alloc_gb': env.get('peak_alloc_gb'), 'wall_s': summ[c]['wall_s'], 'solved': sorted(sol),
             'ndverify_solved': sorted(ndok), 'ckpt': summ[c]['ckpt'], 'batch': summ[c]['batch']}
        out['per_ckpt'][c] = d
        print(f"| {c} | {d['dev58']} | {d['train14']} | **{d['all72']}** | " + ' | '.join(str(d['by_bin'][b]) for b, _, _ in BINS) +
              f" | {d['lean_and_ndverify_all72']} | {d['accepted_samples']} | {ndist} | {nfail} | {100 * d['step_cap_rate']:.3f} | "
              f"{100 * d['action_cap_rate']:.3f} | {d['peak_alloc_gb']:.1f} | {d['wall_s']:.0f} |")
    # ---- arms: per-seed, IQM + bootstrap CI, union
    print('\n| arm | per seed (all 72) | IQM [95 % CI] | union | dev58 per seed | train14 per seed |')
    print('|---|---|---|---|---|---|')
    for arm, cs in ARMS.items():
        cs = [c for c in cs if c in out['per_ckpt']]
        if not cs:
            continue
        v = [out['per_ckpt'][c]['all72'] for c in cs]
        un = sorted(set().union(*(out['per_ckpt'][c]['solved'] for c in cs)))
        out['arms'][arm] = {'per_seed': v, 'iqm': iqm(v), 'ci': boot_ci(v), 'union': len(un), 'union_names': un,
                            'union_dev58': sum(role[n] == 'textbook_dev' for n in un)}
        print(f"| {arm} | {' / '.join(map(str, v))} | {iqm(v):.1f} [{boot_ci(v)[0]:.1f}, {boot_ci(v)[1]:.1f}] | {len(un)} | "
              f"{' / '.join(str(out['per_ckpt'][c]['dev58']) for c in cs)} | {' / '.join(str(out['per_ckpt'][c]['train14']) for c in cs)} |")
    pd = [out['per_ckpt'][f'T1_SN12_s{s}']['all72'] - out['per_ckpt'][f'Fz_SN12_s{s}']['all72'] for s in range(4)
          if f'T1_SN12_s{s}' in out['per_ckpt'] and f'Fz_SN12_s{s}' in out['per_ckpt']]
    out['sn12_T1_minus_frozen_paired'] = pd
    print('\nSN-cap12 T1 - frozen, paired by seed:', pd)
    # ---- per problem
    rob = json.load(open(a.robbie)) if os.path.exists(a.robbie) else None
    rc = set(rob['combined_solved']) if rob else set()
    ours = set().union(*(d['solved'] for d in out['per_ckpt'].values()))
    t1 = set(out['arms'].get('SN-cap12 T1', {}).get('union_names', []))
    none = [n for n in names if n not in ours]
    for n in names:
        out['per_problem'][n] = {'role': role[n], 'ref': ref[n], 'robbie_combined_union': n in rc,
                                 'solved_by': [c for c in out['per_ckpt'] if n in out['per_ckpt'][c]['solved']]}
    out['solved_by_none'] = none
    print(f'\nsolved by any checkpoint: {len(ours)} / 72; by none: {len(none)}')
    for n in none:
        print(f'  none: {n} ({role[n]}, ref {ref[n]}) Robbie-combined {n in rc}: {prompt[n]}')
    if rob:
        out['robbie'] = {'combined_union': len(rc), 'ours_any': len(ours), 'both': len(rc & ours),
                         'robbie_only': sorted(rc - ours), 'ours_only': sorted(ours - rc),
                         'sn12T1_union_vs_robbie': [len(t1 & rc), len(t1 - rc), len(rc - t1)]}
        print(f"\nRobbie combined (union of his 3 seeds) {len(rc)}; ours (any ckpt) {len(ours)}; both {len(rc & ours)}; "
              f"Robbie only {len(rc - ours)}; ours only {len(ours - rc)}")
        print(f"SN-cap12 T1 union {len(t1)}: both {len(t1 & rc)}, T1 only {len(t1 - rc)}, Robbie only {len(rc - t1)}")
        for n in sorted(rc - ours):
            print(f'  robbie-only: {n} ref {ref[n]}: {prompt[n]}')
    # ---- shortest accepted proof per problem (lines, term size) and the longest of those, in Lean
    import nd2lean
    from lean_check import check
    from lean_judge import n_lines
    best = {}
    for c, rr in rows.items():
        for n in names:
            for p in rr[n]['proofs']:
                L = n_lines(p)
                if n not in best or L < best[n][0]:
                    best[n] = (L, p, c)
    items = sorted(best.items())
    srcs = [nd2lean.translate(prompt[n], p, require_all_pr=False) for n, (L, p, c) in items]
    res, wall, _ = check(srcs, workers=a.lean_workers)
    print('\n| problem | role | ref lines | shortest accepted: lines | term size | lean_check ok | found by |')
    print('|---|---|---|---|---|---|---|')
    for (n, (L, p, c)), r, s in zip(items, res, srcs):
        out['per_problem'][n].update({'min_lines': L, 'min_term_size': r.get('size'), 'lean_check_ok': r['ok'],
                                      'min_proof_nd': p, 'min_proof_lean': s, 'min_from': c})
    for n, (L, p, c) in sorted(items, key=lambda x: (-(ref[x[0]] or 0), x[0])):
        pp = out['per_problem'][n]
        print(f"| {n} | {role[n]} | {ref[n]} | {L} | {pp['min_term_size']} | {pp['lean_check_ok']} | {c} |")
    top = sorted(items, key=lambda x: -x[1][0])[:3]
    out['longest_shortest'] = [n for n, _ in top]
    for n, (L, p, c) in top:
        print(f"\n### {n} ({role[n]}, reference_lines {ref[n]}): shortest accepted proof {L} lines, term size "
              f"{out['per_problem'][n]['min_term_size']}, from {c}\n```lean\n{out['per_problem'][n]['min_proof_lean']}\n```")
    json.dump(out, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
