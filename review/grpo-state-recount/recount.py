#!/usr/bin/env python3
"""Reviewer (grpo-state) phase-1 recount, own code: start-index normaliser, line / term-size counters, per-arm step
aggregates, found-file recount vs round_*.json / alloc_*.json, registry compute rows.  Run from the phase-1 copy."""
import json, glob, os, re, collections, statistics as S
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'recount.json')
def rd(fn): return [json.loads(l) for l in open(fn) if l.strip()]
LINE = re.compile(r'N(\d+) ((?:\| )*)(.*) : (\w+)((?: N\d+)*)')
def lines(pf):
    out = []
    for s in pf.split(' ; '):
        s = s.strip()
        if not s or s == 'QED': continue
        m = LINE.fullmatch(s); assert m, s
        out.append((int(m.group(1)), len(m.group(2)) // 2, m.group(3).strip(), m.group(4), [int(x[1:]) for x in m.group(5).split()]))
    return out
def rnorm(pf):
    L = lines(pf); mp = {i: k + 1 for k, (i, *_ ) in enumerate(L)}
    return ' ; '.join(f"N{mp[i]} {'| ' * d}{f} : {r}" + ''.join(f' N{mp[x]}' for x in rf) for i, d, f, r, rf in L)
TS = {'PR': 0, 'AS': 0, 'R': 0, 'ORE': 3, 'DN': 3}
def used(L):
    by = {i: (r, rf) for i, d, f, r, rf in L}; need = set(); st = [L[-1][0]]
    while st:
        i = st.pop()
        if i in need: continue
        need.add(i); st += by[i][1]
    return need
def term_size(pf):
    L = lines(pf); u = used(L)
    return sum(TS.get(r, 1) for i, d, f, r, rf in L if i in u)
def pruned(pf):
    L = lines(pf); u = used(L); return sum(1 for x in L if x[0] in u)
res = {}
for d in sorted([x for x in glob.glob('artifacts/grpo_state/*/') if os.path.exists(x + 'args.json')]):
    arm = os.path.basename(d.rstrip('/')); o = res[arm] = {}
    args = json.load(open(f'{d}/args.json')); args = args.get('config', args)
    st = rd(f'{d}/steps.jsonl')
    o['updates'] = len(st)
    for k in ('mean_reward', 'frac_groups_with_variance', 'frac_groups_nonzero_adv', 'frac_groups_all_fail', 'sample_judge_s', 'update_s', 'update_tokens', 'update_pairs', 'actions'):
        o['mean_' + k] = S.mean(s[k] for s in st)
    o['mean_s_per_update'] = S.mean(s['sample_judge_s'] + s['update_s'] for s in st)
    o['wall_s_last'] = st[-1]['secs']
    o['peak_alloc_gb_max'] = max(s['peak_alloc_gb'] or 0 for s in st)
    o['mean_reward_by_step'] = [round(s['mean_reward'], 4) for s in st]
    o['sum_new_proofs_steps'] = sum(s['new_proofs'] for s in st)
    o['grad_norm'] = [round(s['grad_norm'], 4) for s in st]
    o['loss'] = [s['loss'] for s in st]
    o['kl'] = [s['kl_per_token'] for s in st]
    fs = sorted((f for f in glob.glob(f'{d}/found_*.jsonl') if re.fullmatch(r'found_\d+\.jsonl', os.path.basename(f))), key=lambda f: int(re.findall(r'(\d+)\.', f)[-1]))
    prev = None; o['found'] = {}
    for f in fs:
        r = int(re.findall(r'(\d+)\.', f)[-1]); F = rd(f)
        keys = collections.defaultdict(set); rounds = collections.Counter(); dup = 0; bad_norm = 0; wr_mis = 0; pr_mis = 0
        for x in F:
            k = rnorm(x['proof'])
            if k in keys[x['name']]: dup += 1
            keys[x['name']].add(k); rounds[x['round']] += 1
            if rnorm(x['norm']) != k: bad_norm += 1
            if len(lines(x['proof'])) != x['written']: wr_mis += 1
            if pruned(x['proof']) != x['pruned']: pr_mis += 1
        fo = {'records': len(F), 'distinct': sum(len(v) for v in keys.values()), 'solved': len(keys), 'dup_within_target': dup,
              'stored_norm_differs': bad_norm, 'written_mismatch': wr_mis, 'pruned_mismatch': pr_mis, 'by_round': dict(sorted(rounds.items())),
              'L_true_hist_solved': dict(sorted(collections.Counter(next(x['L_true'] for x in F if x['name'] == n) for n in keys).items())),
              'mean_written': S.mean(len(lines(x['proof'])) for x in F), 'mean_term_size': S.mean(term_size(x['proof']) for x in F),
              'max_written': max(len(lines(x['proof'])) for x in F)}
        if prev is not None:
            fo['superset_of_prev'] = all(prev[n] <= keys.get(n, set()) for n in prev)
        prev = keys
        rj = f'{d}/round_{r}.json'
        if os.path.exists(rj):
            R = json.load(open(rj)); tc = R.get('targets_cum', {})
            fo['round_json'] = {'solved': tc.get('solved'), 'distinct': tc.get('distinct_proofs'), 'n': tc.get('n'), 'new_this_round': R.get('new_proofs_this_round'),
                                'target_sample_acc': R.get('target_sample_acc'), 'n_steps_in_round': len(R.get('steps', []))}
        al = f'{d}/alloc_{r}.json'
        if os.path.exists(al):
            A = json.load(open(al)); fo['alloc_tried'] = sum(A['tried'].values()); fo['alloc_accepted'] = sum(A['accepted'].values())
            fo['alloc_rate'] = fo['alloc_accepted'] / fo['alloc_tried']
            fo['alloc_names_accepted_eq_solved'] = sum(1 for v in A['accepted'].values() if v) == len(keys)
        o['found'][r] = fo
    ft = sorted((f for f in glob.glob(f'{d}/found_transfer_*.jsonl')), key=lambda f: int(re.findall(r'(\d+)\.', f)[-1]))
    o['transfer'] = {}
    for f in ft:
        r = int(re.findall(r'(\d+)\.', f)[-1]); F = rd(f)
        keys = collections.defaultdict(set)
        for x in F: keys[x['name']].add(rnorm(x['proof']))
        tf = {'records': len(F), 'distinct': sum(len(v) for v in keys.values()), 'solved': len(keys)}
        rj = f'{d}/round_{r}.json'
        if os.path.exists(rj):
            R = json.load(open(rj)); tc = R.get('transfer_cum') or {}
            tf['round_json_cum'] = {'solved': tc.get('solved'), 'distinct': tc.get('distinct_proofs'), 'n': tc.get('n')}
            tr = R.get('transfer_round') or {}
            tf['round_json_transfer_round'] = {k: v for k, v in tr.items() if not isinstance(v, (list, dict))} if isinstance(tr, dict) else tr
            hg = R.get('heldout_greedy') or {}
            tf['heldout_greedy'] = {k: v for k, v in hg.items() if not isinstance(v, (list, dict))} if isinstance(hg, dict) else hg
        o['transfer'][r] = tf
# registry compute rows
reg = collections.defaultdict(lambda: collections.defaultdict(float)); regn = collections.Counter()
for f in glob.glob('artifacts/grpo-state/registry/*.jsonl'):
    for x in rd(f):
        if x['metric'] in ('gpu_seconds', 'gen_tokens', 'attempts', 'actions', 'train_steps', 'train_tokens', 'lean_checks'):
            reg[x['arm']][x['metric']] += x['value'] or 0; regn[(x['arm'], x['metric'])] += 1
        if x['metric'] == 'gpu_seconds':
            reg[x['arm']]['gpu_' + str((x.get('labels') or {}).get('phase'))] += x['value'] or 0
            reg[x['arm']]['gpu_type'] = (x.get('labels') or {}).get('gpu') or x.get('labels', {}).get('gpu_type') or 0
for arm in res:
    res[arm]['registry'] = dict(reg.get(arm, {}))
json.dump(res, open(OUT, 'w'), indent=1, default=str)
for arm, o in res.items():
    print('==', arm, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in o.items() if k.startswith('mean_') or k in ('updates', 'peak_alloc_gb_max', 'sum_new_proofs_steps')})
    for r, fo in o['found'].items(): print('  found', r, fo)
    for r, tf in o['transfer'].items(): print('  transfer', r, tf)
    print('  registry', o['registry'])
