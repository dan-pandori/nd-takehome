#!/usr/bin/env python3
"""mcts_analysis.py -- every number of run `mcts-a` from the pulled files in artifacts/mcts (stdout: markdown tables).

  python3 mcts_analysis.py [--record] [--fig figures/mcts_a.png]

Inputs (all pulled from the pods; nothing else is read):
  artifacts/mcts/eval/s<S>_<ck>__<pool>__sample.json[l]   plain sampling (state_eval.py, k 256, T 0.8, seed 2)
  artifacts/mcts/eval/s<S>_<ck>__<pool>__{prior,value}.json[l]   PUCT read-outs (mcts_eval.py) at the matched budget
  artifacts/mcts/value/value_s<S>_<ck>.json               value-head calibration on held-out rl_targets / K12 states
  artifacts/mcts/vdata/vdata_s<S>_<ck>.json               rollout statistics behind each value head
Outputs: artifacts/mcts/summary.json; with --record, results-registry rows (record.py) for solved counts and compute.

Models: `trajectory`'s cap-12 seeds, ALiBiGPT 6 x 384, 9,560,832 parameters, lean_staten, from scratch on K12;
pend = stage1_best12_s<S>_b1200.pt (end of pretraining), r8 = la_T1_best12_s<S>_r8.pt (T1 ladder round 8).
"""
import argparse, collections, glob, json, math, os, random, sys

E = 'artifacts/mcts/eval'
POOLS = ['C', 'tb72', 'h250', 'rrQ100', 'long2']
ARMS = ['sample', 'prior', 'value']
TRAJ_X1_C_R8 = {0: 3, 1: 1, 2: 1}       # trajectory's group-C solved at r8, sample seed 1 (summary.json pass@256 x n)


def jl(fn):
    return [json.loads(l) for l in open(fn)] if os.path.exists(fn) else None


def js(fn):
    return json.load(open(fn)) if os.path.exists(fn) else None


def comb_ratio(n, c, k):
    """P(no success in k of n draws without replacement, c successes) -- the unbiased pass@k complement."""
    if n - c < k:
        return 0.0
    r = 1.0
    for i in range(k):
        r *= (n - c - i) / (n - i)
    return r


def load():
    R = {}
    for S in (0, 1, 2):
        for ck in ('r8', 'pend'):
            for P in POOLS:
                for A in ARMS:
                    b = f'{E}/s{S}_{ck}__{P}__{A}'
                    s, rows = js(b + '.json'), jl(b + '.jsonl')
                    if s is not None and rows is not None:
                        R[(S, ck, P, A)] = (s, rows)
    return R


def solved_names(rows):
    return {r['name'] for r in rows if r['solved']}


def compute_row(arm, s, rows):
    if arm == 'sample':
        env = s['env']
        steps = sum(int(k) * v for k, v in env['env_steps'].items())
        return dict(gpu_s=s['wall_s'], attempts=sum(r['n_tried'] for r in rows), actions=steps,
                    gen_tokens=round(env.get('action_declen_mean', 0) * steps),
                    lean_checks=env['env_end'].get('done', 0), util=s.get('gpu_util'))
    st = s['stats']
    return dict(gpu_s=st['wall_s'], attempts=None, actions=s['sampled'], expansions=s['expansions'],
                gen_tokens=st['gen_tokens'], lean_checks=s['lean_checks'], util=s.get('gpu_util_mean'),
                sampler_gpu_s=st['gpu_s'], peak_gb=s.get('peak_alloc_gb'), budget_s=s['budget_s'])


def sample_util(S, ck, P):
    fn = f'{E}/s{S}_{ck}__{P}__sample.util'
    if not os.path.exists(fn):
        return None
    x = [float(l) for l in open(fn) if l.strip().replace('.', '').isdigit()]
    return sum(x) / len(x) if x else None


def anytime(R, S, ck, P, fracs=(0.05, 0.1, 0.25, 0.5, 0.75, 1.0)):
    out = {}
    if (S, ck, P, 'sample') in R:
        s, rows = R[(S, ck, P, 'sample')]
        out['sample'] = [round(sum(1 - comb_ratio(r['n_tried'], r['n_ok'], max(1, int(round(f * r['n_tried']))))
                                   for r in rows), 2) for f in fracs]
    for A in ('prior', 'value'):
        if (S, ck, P, A) in R:
            s, rows = R[(S, ck, P, A)]
            B = s['budget_s']
            out[A] = [sum(1 for r in rows if r['solved'] and r['t_found'] <= f * B) for f in fracs]
    return fracs, out


def boot_delta(R, ck, P, a, b, n=10000, seed=0):
    """mean over seeds of (solved_a - solved_b) on pool P, with a stratified bootstrap (theorems within seed) 95 % CI."""
    per = {}
    for S in (0, 1, 2):
        if (S, ck, P, a) in R and (S, ck, P, b) in R:
            sa, sb = solved_names(R[(S, ck, P, a)][1]), solved_names(R[(S, ck, P, b)][1])
            names = [r['name'] for r in R[(S, ck, P, b)][1]]
            per[S] = [(x in sa) - (x in sb) for x in names]
    if not per:
        return None
    rng = random.Random(seed)
    pt = sum(sum(v) for v in per.values()) / len(per)
    bs = []
    for _ in range(n):
        tot = 0
        for v in per.values():
            tot += sum(v[rng.randrange(len(v))] for _ in range(len(v)))
        bs.append(tot / len(per))
    bs.sort()
    return dict(seeds={S: sum(v) for S, v in per.items()}, mean=round(pt, 3), ci=[bs[int(0.025 * n)], bs[int(0.975 * n)]])


def path_stats(rows):
    """found proofs: depth, the hardest step (lowest log pi) -- its depth, prior rank, log pi -- and steps with
    log pi < -4."""
    d = []
    for r in rows:
        if r['solved'] and r.get('path'):
            p = r['path']
            h = min(range(len(p)), key=lambda i: p[i]['logpi'])
            d.append(dict(name=r['name'], depth=len(p), hard_depth=h, hard_rank=p[h]['rank'], hard_logpi=p[h]['logpi'],
                          n_below4=sum(1 for x in p if x['logpi'] < -4), nodes=r['nodes'], sampled=r['sampled'],
                          t_found=r['t_found']))
    return d


def n_lines(nd):
    return nd.count(';') if nd else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--record', action='store_true')
    ap.add_argument('--fig', default=None)
    a = ap.parse_args()
    R = load()
    out = {'tables': {}, 'gate': {}, 'compute': [], 'anytime': {}, 'paths': {}, 'value': {}}
    # 1. solved per arm, pool, checkpoint, seed
    print('## Solved (matched GPU-seconds per pool; sample = k 256 T 0.8 seed 2)\n')
    for ck in ('r8', 'pend'):
        print(f'### {ck}\n\n| pool | n | ' + ' | '.join(f'{A} s{S}' for A in ARMS for S in (0, 1, 2)) + ' |')
        print('|---|---|' + '---|' * 9)
        for P in POOLS:
            cells, n = [], None
            for A in ARMS:
                for S in (0, 1, 2):
                    x = R.get((S, ck, P, A))
                    cells.append(str(x[0]['solved']) if x else '—')
                    if x and n is None:
                        n = len(x[1])
            nn = '36/35/28' if P == 'C' else str(n)
            print(f'| {P} | {nn} | ' + ' | '.join(cells) + ' |')
            out['tables'][f'{ck}/{P}'] = {f'{A}/s{S}': (R[(S, ck, P, A)][0]['solved'] if (S, ck, P, A) in R else None)
                                         for A in ARMS for S in (0, 1, 2)}
        print()
    # 2. gate
    print('## Gate (group C, r8, value − sample)\n')
    g = {}
    passes = 0
    for S in (0, 1, 2):
        if (S, 'r8', 'C', 'value') in R and (S, 'r8', 'C', 'sample') in R:
            v = R[(S, 'r8', 'C', 'value')][0]['solved']; s = R[(S, 'r8', 'C', 'sample')][0]['solved']
            spread = abs(s - TRAJ_X1_C_R8[S])
            ok = (v - s) >= 3 and (v - s) > spread
            passes += ok
            g[S] = dict(value=v, sample=s, delta=v - s, sample_spread=spread, seed_pass=ok)
            print(f'- s{S}: value {v}, sample {s} (trajectory x1 {TRAJ_X1_C_R8[S]}, spread {spread}), Δ {v - s:+d} → '
                  f'{"pass" if ok else "fail"}')
    if len(g) == 3:
        out['gate'] = dict(per_seed=g, verdict='PASS' if passes >= 2 else 'FAIL')
        print(f'\n**MCTS-A GATE: {out["gate"]["verdict"]}** ({passes} of 3 seeds)\n')
    # 3. paired differences with bootstrap
    print('## Paired differences (mean over seeds, stratified bootstrap 95 % CI over theorems)\n')
    print('| ck | pool | value − sample | prior − sample | value − prior |\n|---|---|---|---|---|')
    out['deltas'] = {}
    for ck in ('r8', 'pend'):
        for P in POOLS:
            row = []
            for x, y in (('value', 'sample'), ('prior', 'sample'), ('value', 'prior')):
                d = boot_delta(R, ck, P, x, y)
                out['deltas'][f'{ck}/{P}/{x}-{y}'] = d
                row.append('—' if d is None else f"{d['mean']:+.2f} [{d['ci'][0]:+.2f}, {d['ci'][1]:+.2f}] "
                           f"({', '.join(f'{v:+d}' for v in d['seeds'].values())})")
            print(f'| {ck} | {P} | ' + ' | '.join(row) + ' |')
    print()
    # 4. group C union / which theorems
    print('## Group C theorems solved (names), r8 and pend\n')
    out['C_sets'] = {}
    for ck in ('r8', 'pend'):
        for S in (0, 1, 2):
            sets = {A: sorted(solved_names(R[(S, ck, 'C', A)][1])) for A in ARMS if (S, ck, 'C', A) in R}
            out['C_sets'][f'{ck}/s{S}'] = sets
            if sets:
                allx = set().union(*map(set, sets.values()))
                print(f'- {ck} s{S}: ' + '; '.join(f'{A} {len(v)}' for A, v in sets.items()) +
                      f'; union {len(allx)}; value-only {len(set(sets.get("value", [])) - set(sets.get("sample", [])) - set(sets.get("prior", [])))}')
    print()
    # 5. anytime
    print('## Anytime (solved at a fraction of the matched budget; sample = unbiased pass@(f·256))\n')
    for ck in ('r8', 'pend'):
        for P in ('C', 'tb72', 'rrQ100'):
            for S in (0, 1, 2):
                f, an = anytime(R, S, ck, P)
                if an:
                    out['anytime'][f'{ck}/{P}/s{S}'] = dict(fracs=f, **an)
    for k, v in out['anytime'].items():
        if k.startswith('r8/C') or k.startswith('pend/C'):
            print(f'- {k}: ' + '; '.join(f'{A} {v[A]}' for A in ARMS if A in v))
    print()
    # 6. search statistics
    print('## Search statistics on found proofs (value / prior arms)\n')
    print('| ck | pool | arm | proofs | depth (mean) | hardest step depth (median) | its prior rank (median) | '
          'its log π (median) | steps < −4 nats (mean) | nodes per proof (median) |\n|---|---|---|---|---|---|---|---|---|---|')
    def med(x):
        x = sorted(x); return x[len(x) // 2] if x else None
    for ck in ('r8', 'pend'):
        for P in POOLS:
            for A in ('prior', 'value'):
                d = []
                for S in (0, 1, 2):
                    if (S, ck, P, A) in R:
                        d += path_stats(R[(S, ck, P, A)][1])
                if d:
                    out['paths'][f'{ck}/{P}/{A}'] = d
                    print(f'| {ck} | {P} | {A} | {len(d)} | {sum(x["depth"] for x in d) / len(d):.1f} | '
                          f'{med([x["hard_depth"] for x in d])} | {med([x["hard_rank"] for x in d])} | '
                          f'{med([x["hard_logpi"] for x in d])} | {sum(x["n_below4"] for x in d) / len(d):.2f} | '
                          f'{med([x["nodes"] for x in d])} |')
    print()
    # 6b. proof length: lines and Lean term size (mcts_termsize.py), on the theorems every arm solved
    ts = js('artifacts/mcts/termsize.json')
    if ts:
        print('## Proof length on theorems all three arms solved (ND lines / Lean term size, mean; '
              'sample = shortest of its accepted proofs, search = the one proof found)\n')
        print('| ck | pool | common | sample | prior | value |\n|---|---|---|---|---|---|')
        out['length'] = {}
        for ck in ('r8', 'pend'):
            for P in POOLS:
                acc = {A: [] for A in ARMS}
                n = 0
                for S in (0, 1, 2):
                    per = {A: ts['per'].get(f's{S}_{ck}__{P}__{A}', {}) for A in ARMS}
                    common = set(per['sample']) & set(per['prior']) & set(per['value'])
                    n += len(common)
                    for A in ARMS:
                        acc[A] += [per[A][x] for x in common if per[A][x][1] is not None]
                if n:
                    cell = {A: (sum(x[0] for x in v) / len(v), sum(x[1] for x in v) / len(v)) for A, v in acc.items() if v}
                    out['length'][f'{ck}/{P}'] = dict(common=n, **cell)
                    print(f'| {ck} | {P} | {n} | ' + ' | '.join(f'{cell[A][0]:.1f} / {cell[A][1]:.1f}' for A in ARMS) + ' |')
        print(f"\n(lean_check rejected {ts['rejected_by_lean_check']} of {ts['n']} found proofs)\n")
    # 7. value calibration
    print('## Value calibration (held-out rl_targets / K12 states)\n')
    print('| seed | ck | states | AUC solvable | Brier (const) | steps-to-go MAE | Spearman | rollouts accepted |\n'
          '|---|---|---|---|---|---|---|---|')
    for S in (0, 1, 2):
        for ck in ('r8', 'pend'):
            v = js(f'artifacts/mcts/value/value_s{S}_{ck}.json')
            vd = js(f'artifacts/mcts/vdata/vdata_s{S}_{ck}.json')
            if v:
                h = v['heldout']
                out['value'][f's{S}/{ck}'] = dict(heldout=h, rollouts=vd)
                acc = f"{vd['accepted']}/{vd['attempts']}" if vd else '—'
                print(f"| s{S} | {ck} | {h['states']} | {h['auc_solvable']} | {h['brier']} ({h['brier_const']}) | "
                      f"{h['stg_mae']} | {h['stg_spearman']} | {acc} |")
    print()
    # 7b. exploratory 10x read-out (addendum 2)
    X = 'artifacts/mcts/eval_x10'
    if os.path.isdir(X):
        print('## Exploratory (addendum 2): group C, r8, sampling k 2,560 (seed 3) vs PUCT-value at its wall clock\n')
        print('| seed | budget s | sample k 2,560 | value | value-only | sample-only | k 256 sample (seed 2) |\n|---|---|---|---|---|---|---|')
        out['x10'] = {}
        for S in (0, 1, 2):
            xa, xb = js(f'{X}/s{S}_r8__C__sample.json'), js(f'{X}/s{S}_r8__C__value.json')
            if xa and xb:
                sa, sv = solved_names(jl(f'{X}/s{S}_r8__C__sample.jsonl')), solved_names(jl(f'{X}/s{S}_r8__C__value.jsonl'))
                k256 = R[(S, 'r8', 'C', 'sample')][0]['solved'] if (S, 'r8', 'C', 'sample') in R else None
                out['x10'][S] = dict(budget_s=xa['wall_s'], sample=xa['solved'], value=xb['solved'], value_only=len(sv - sa),
                                     sample_only=len(sa - sv), sample_k256=k256, value_util=xb.get('gpu_util_mean'))
                print(f"| s{S} | {xa['wall_s']:.0f} | {xa['solved']} | {xb['solved']} | {len(sv - sa)} | {len(sa - sv)} | {k256} |")
        print()
    # 8. compute
    print('## Compute per arm (GPU-seconds = job wall clock on one A40; sampler = time inside the policy forward)\n')
    print('| seed | ck | pool | arm | GPU-s | sampler GPU-s | GPU util % | actions | gen tokens | Lean checks |\n'
          '|---|---|---|---|---|---|---|---|---|---|')
    for (S, ck, P, A), (s, rows) in sorted(R.items()):
        c = compute_row(A, s, rows)
        if A == 'sample':
            c['util'] = sample_util(S, ck, P)
        c.update(seed=S, ck=ck, pool=P, arm=A)
        out['compute'].append(c)
        u = f"{c['util']:.0f}" if c.get('util') is not None else '—'
        print(f"| s{S} | {ck} | {P} | {A} | {c['gpu_s']:.0f} | {c.get('sampler_gpu_s', 0) or 0:.0f} | {u} | "
              f"{c['actions']} | {c['gen_tokens']} | {c['lean_checks']} |")
    over = [c for c in out['compute'] if c['arm'] != 'sample' and c['gpu_s'] > 1.25 * c.get('budget_s', 1e9)]
    print(f'\nArms above 1.25× their budget: {len(over)}')
    os.makedirs('artifacts/mcts', exist_ok=True)
    json.dump(out, open('artifacts/mcts/summary.json', 'w'), indent=1, default=str)
    if a.record:
        os.environ.setdefault('ND_RUN_ID', 'mcts-a')
        import record
        for c in out['compute']:
            S, ck, P, A = c['seed'], c['ck'], c['pool'], c['arm']
            src = f'{E}/s{S}_{ck}__{P}__{A}.json'
            ckpt = f'ckpts/mcts/{"stage1_best12_s%d_b1200" % S if ck == "pend" else "la_T1_best12_s%d_r8" % S}.pt'
            lab = dict(arm=A, seed=S, ckpt=ckpt, data=f'data/mcts/{"groupC_s%d" % S if P == "C" else P}.jsonl',
                       source=src, gpu='NVIDIA A40', pool=P, round=None)
            record.record('solved', R[(S, ck, P, A)][0]['solved'], n=len(R[(S, ck, P, A)][1]), **lab)
            record.record('gpu_seconds', round(c['gpu_s'], 1), **lab)
            record.record('gen_tokens', c['gen_tokens'], **lab)
            record.record('actions', c['actions'], **lab)
            record.record('lean_checks', c['lean_checks'], **lab)
            record.record('train_steps', 0, **lab)
        for S, x in out.get('x10', {}).items():  # addendum 2 (exploratory, group C at r8, 10x budget)
            for A in ('sample', 'value'):
                b = f'artifacts/mcts/eval_x10/s{S}_r8__C__{A}'
                c = compute_row(A, js(b + '.json'), jl(b + '.jsonl'))
                lab = dict(arm=f'{A}_x10', seed=S, ckpt=f'ckpts/mcts/la_T1_best12_s{S}_r8.pt', data=f'data/mcts/groupC_s{S}.jsonl',
                           source=b + '.json', gpu='NVIDIA A40', pool='C', exploratory=True)
                record.record('solved', x[A], n=len(jl(b + '.jsonl')), **lab)
                for m in ('gpu_s', 'gen_tokens', 'actions', 'lean_checks'):
                    record.record({'gpu_s': 'gpu_seconds'}.get(m, m), round(c[m], 1) if m == 'gpu_s' else c[m], **lab)
        for S in (0, 1, 2):                     # value heads: rollout data and training (the policy is frozen)
            for ck in ('r8', 'pend'):
                vd = js(f'artifacts/mcts/vdata/vdata_s{S}_{ck}.json'); vr = js(f'artifacts/mcts/value/value_s{S}_{ck}.json')
                if not vd or not vr:
                    continue
                ckpt = f'ckpts/mcts/{"stage1_best12_s%d_b1200" % S if ck == "pend" else "la_T1_best12_s%d_r8" % S}.pt'
                lab = dict(arm='value_data', seed=S, ckpt=ckpt, data='data/ladder/rl_targets.jsonl+K12 1500',
                           source=f'artifacts/mcts/vdata/vdata_s{S}_{ck}.json', gpu='NVIDIA A40')
                record.record('gpu_seconds', round(vd['wall_s'], 1), **lab)
                record.record('gen_tokens', vd['gen_tokens'], **lab)
                record.record('attempts', vd['attempts'], **lab)
                record.record('lean_checks', vd['lean_checks'], **lab)
                steps = vr['args']['epochs'] * math.ceil(vr['train_states'] / vr['args']['batch'])
                lab.update(arm='value_train', source=f'artifacts/mcts/value/value_s{S}_{ck}.json')
                record.record('train_steps', steps, **lab)
                record.record('auc_solvable_heldout', vr['heldout']['auc_solvable'], n=vr['heldout']['states'], **lab)
        record.sync(raise_on_fail=False)
    if a.fig:
        fig(out, a.fig)


def fig(out, path):
    """anytime curves summed over the three seeds: group C at r8 (the gate) and rrQ100 at pend (the clearest gain)."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    col = {'sample': '#888888', 'prior': '#4C78A8', 'value': '#E45756'}
    lab = {'sample': 'sampling (k 256, T 0.8)', 'prior': 'PUCT, prior only', 'value': 'PUCT + value'}
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
    for a, (k, title) in zip(ax, (('r8/C', 'group C (99 theorems), r8'), ('pend/rrQ100', 'rr600 L 13-16 (300), end of pretraining'))):
        fr = None
        for A in ARMS:
            tot = None
            for S in (0, 1, 2):
                v = out['anytime'].get(f'{k}/s{S}')
                if not v or A not in v:
                    tot = None; break
                fr = v['fracs']
                tot = list(v[A]) if tot is None else [x + y for x, y in zip(tot, v[A])]
            if tot:
                a.plot([f * 100 for f in fr], tot, marker='o', color=col[A], label=lab[A])
        a.set_title(title, fontsize=10)
        a.set_xlabel('% of the matched GPU-seconds')
        a.set_ylabel('theorems solved (3 seeds)')
        a.spines[['top', 'right']].set_visible(False)
    ax[0].legend(frameon=False, fontsize=8)
    fig.suptitle('mcts-a: trajectory cap-12 ALiBiGPT 9.56M (lean_staten), 3 seeds, one A40 per job', fontsize=9)
    fig.tight_layout()
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    fig.savefig(path, dpi=130)


if __name__ == '__main__':
    main()
