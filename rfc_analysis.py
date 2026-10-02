#!/usr/bin/env python3
"""rl-from-ckpt: the threshold test, r8 by start, ladder vs replay-only control, trajectories, reproducibility.
VPS-runnable (numpy + matplotlib, no torch).  Pre-registration: preregistration/rl-from-ckpt.md.

  bash pod/rfc/fetch_inherit.sh ; python3 rfc_analysis.py      stdout = the tables; writes artifacts/rfc/summary.json,
                                                                figures/rfc_*.png

Models: `trajectory`'s best-cap12 seeds 0-2 (ALiBiGPT 6 x 384, 9,560,832 params, `lean_staten`, from scratch on K12).
Starts p0 / p1600 / p5000 / p12000 / p16000 (kept Stage-1 checkpoints) and pend (end of Stage-1; its T1 ladder and
reads are trajectory's, inherited).  Ladders la_T1_best12_s<S>_<start> (r1..r8); controls rc_best12_s<S>_<start>
(replay-only, rfc_replay.py).  Lean alone decides (state-env gate in state_eval.py).
Inputs:
  inherit/tj/eval/s<S>_<ck>__<pool>_x<x>.jsonl     trajectory's reads (ck = p<step>, pend, r<k>)
  inherit/tj/score/{s,new8_s}<S>/s<S>_<ck>.jsonl   trajectory's teacher-forced scores (ref: and ev: targets)
  artifacts/rfc/eval/<label>__<pool>_x<x>.jsonl    this run's reads: s<S>_<start>_r<k>, c<S>_<start>_r8, s0_<start>_rr
  artifacts/rfc/score/s<S>_<start>/s<S>_<start>_{r0,r2,r4,r8,c8}.jsonl   this run's scores (refs + own eventual proofs)
  artifacts/rfc/score/cpend_s<S>/s<S>_pend_c8.jsonl                      refs under the pend controls' r8
"""
import json, math, os, random, statistics as stt, sys
import numpy as np

I, R = 'inherit/tj', 'artifacts/rfc'
STARTS = ['p1600', 'p5000', 'p12000', 'p16000', 'pend']
EARLY = STARTS[:4]
POOLS = ('tb72', 'h250')
SEEDS = (0, 1, 2)
LO = -12.0          # the pre-registered "far below" cut, nats
XCLIP = -40.0
KS = (1, 8, 64, 256)


def rj(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def passk(n, c, k):
    return 1.0 if n - c < k else 1.0 - math.comb(n - c, k) / math.comb(n, k)


_rc = {}
def reads(label, x):
    """{name: row} for a checkpoint label and sample seed, or None.  Labels: s<S>_<start>_r<k> / c<S>_<start>_r8 /
    s0_<start>_rr (this run); s<S>_<start>_r0 and s<S>_pend_r<k> map to trajectory's files."""
    key = (label, x)
    if key in _rc:
        return _rc[key]
    parts = label.split('_')
    if label[0] == 's' and parts[-1] == 'r0':
        src = f'{I}/eval/{parts[0]}_{parts[1]}'
    elif label[0] == 's' and parts[1] == 'pend' and parts[-1] != 'rr':
        src = f'{I}/eval/{parts[0]}_{parts[2]}'
    else:
        src = f'{R}/eval/{label}'
    out = {}
    for pool in POOLS:
        p = f'{src}__{pool}_x{x}.jsonl'
        if not os.path.exists(p):
            _rc[key] = None
            return None
        for r in rj(p):
            r['pool'] = pool
            out[r['name']] = r
    _rc[key] = out
    return out


def solved(label, x):
    d = reads(label, x)
    return None if d is None else {n: r['n_ok'] > 0 for n, r in d.items()}


_sc = {}
def tscore(path):
    if path not in _sc:
        _sc[path] = {o['tid']: o['T1.0'] for o in rj(path)} if os.path.exists(path) else None
    return _sc[path]


def w1_start(s, start, kind='ref'):
    """{name: worst-step log p} of trajectory's reference (kind ref) or eventual (kind ev) proofs under the start."""
    out = {}
    for sub in (f's{s}', f'new8_s{s}'):
        d = tscore(f'{I}/score/{sub}/s{s}_{start}.jsonl') or {}
        for tid, o in d.items():
            k, n = tid.split(':', 1)
            if k == kind:
                out[n] = o['w1']
    return out


def w1_own(s, start, ck, kind='ref'):
    """this run's scores: ck in r0 r2 r4 r8 c8 (refs and the ladder's own eventual proofs)."""
    if start == 'pend' and ck == 'c8':
        d = tscore(f'{R}/score/cpend_s{s}/s{s}_pend_c8.jsonl')
    else:
        d = tscore(f'{R}/score/s{s}_{start}/s{s}_{start}_{ck}.jsonl')
    if d is None:
        return None
    return {tid.split(':', 1)[1]: o['w1'] for tid, o in d.items() if tid.split(':', 1)[0] == kind}


def logit_fit(x, y, lam=1e-2, iters=100):
    X = np.c_[np.ones(len(x)), x]; b = np.zeros(2)
    for _ in range(iters):
        p = 1 / (1 + np.exp(-X @ b)); W = p * (1 - p) + 1e-9
        b = b + np.linalg.solve(X.T @ (W[:, None] * X) + lam * np.eye(2), X.T @ (y - p) - lam * b)
    return b


def x50(b):
    return float(np.clip(-b[0] / b[1], XCLIP, 5)) if b[1] > 1e-6 else float('nan')


def P(b, x):
    return 1 / (1 + math.exp(-(b[0] + b[1] * max(x, XCLIP))))


def iqm_ci(per_seed_vals, B=2000, seed=0):
    """per_seed_vals: list (per seed) of lists of per-theorem values -> IQM over seeds of the per-seed mean, with a
    bootstrap 95 % interval resampling theorems within each seed (stratified by seed)."""
    def iqm(v):
        v = sorted(v); n = len(v); k = n // 4
        return float(np.mean(v[k:n - k])) if n - 2 * k > 0 else float(np.mean(v))
    vals = [list(v) for v in per_seed_vals if v]
    if not vals:
        return None
    pt = iqm([np.mean(v) for v in vals]); rng = random.Random(seed); bs = []
    for _ in range(B):
        bs.append(iqm([np.mean([v[rng.randrange(len(v))] for _ in v]) for v in vals]))
    bs.sort()
    return {'iqm': pt, 'lo': bs[int(0.025 * B)], 'hi': bs[int(0.975 * B)], 'per_seed': [float(np.mean(v)) for v in vals]}


def groups(s):
    """trajectory's groups for seed s (sample seed 0 at pend and r8 of the end arm)."""
    a, b = solved(f's{s}_pend_r0', 0), solved(f's{s}_pend_r8', 0)
    return {n: 'A' if a[n] else 'B' if b[n] else 'C' for n in a}


def lean_of(prompt, proof):
    try:
        import nd2lean
        return nd2lean.translate(prompt, proof, require_all_pr=False)
    except Exception as e:      # noqa: BLE001  (display only)
        return f'-- translate failed: {e}\n{proof}'


def main():
    out = {}
    G = {s: groups(s) for s in SEEDS}
    print('# rl-from-ckpt analysis.  Models: trajectory best-cap12 s0-s2 (ALiBiGPT 9,560,832 params, lean_staten, K12, '
          'from scratch).  Lean alone.  k 256, T 0.8; solved = >= 1 Lean-accepted of 256.\n')

    # ---- p0 ladders: stop rule
    print('## p0 (initialisation) ladders: target accepts in rounds 1 / 2 (of 4,495; 143,840 attempts per round)')
    for s in SEEDS:
        p = f'{R}/la_T1_best12_s{s}_p0'
        if os.path.exists(f'{p}/round_1.json'):
            acc = [json.load(open(f'{p}/round_{r}.json'))['targets_round']['solved'] for r in (1, 2) if os.path.exists(f'{p}/round_{r}.json')]
            print(f'  s{s}: {acc}  stopped={os.path.exists(p + "/STOPPED")}')
    out['p0_accepts'] = {s: [json.load(open(f'{R}/la_T1_best12_s{s}_p0/round_{r}.json'))['targets_round']['solved'] for r in (1, 2)]
                         for s in SEEDS if os.path.exists(f'{R}/la_T1_best12_s{s}_p0/round_2.json')}

    # ---- solved counts by start and checkpoint
    print('\n## solved (of 72 / 250) by start, checkpoint, sample seed: s0 / s1 / s2   [r0 = the start, inherited; pend ladders inherited]')
    tab = {}
    for start in ['p0'] + STARTS:
        for ck in ('r0', 'r2', 'r4', 'r8', 'c8'):
            for x in (1, 0):
                row = []
                for s in SEEDS:
                    lab = f'c{s}_{start}_r8' if ck == 'c8' else f's{s}_{start}_{ck}'
                    if start == 'p0' and ck != 'r0':
                        row.append(None); continue
                    d = solved(lab, x)
                    row.append(None if d is None else {pool: sum(v for n, v in d.items() if reads(lab, x)[n]['pool'] == pool) for pool in POOLS})
                tab[(start, ck, x)] = row
                if all(r is None for r in row):
                    continue
                f = lambda pool: ' / '.join('-' if r is None else str(r[pool]) for r in row)
                print(f'  {start:7s} {ck:3s} x{x}: tb72 {f("tb72"):14s} h250 {f("h250")}')
    out['solved'] = {f'{a}|{b}|x{c}': v for (a, b, c), v in tab.items()}

    # ---- r8 vs control, IQM (sample seed 1)
    print('\n## r8 vs replay-only control r8 (sample seed 1); IQM over seeds of the per-seed count, 95 % stratified bootstrap')
    out['r8_vs_ctrl'] = {}
    for start in STARTS:
        for pool in POOLS:
            ys = []
            for which in ('r8', 'c8'):
                per = []
                for s in SEEDS:
                    lab = f'c{s}_{start}_r8' if which == 'c8' else f's{s}_{start}_r8'
                    d = reads(lab, 1)
                    per.append([] if d is None else [float(r['n_ok'] > 0) for r in d.values() if r['pool'] == pool])
                ys.append(per)
            n = 72 if pool == 'tb72' else 250
            a, c = iqm_ci(ys[0]), iqm_ci(ys[1])
            diff = None
            if all(ys[0]) and all(ys[1]):
                names = [sorted(n_ for n_, r in reads(f's{s}_{start}_r8', 1).items() if r['pool'] == pool) for s in SEEDS]
                diff = iqm_ci([[float(reads(f's{s}_{start}_r8', 1)[m]['n_ok'] > 0) - float(reads(f'c{s}_{start}_r8', 1)[m]['n_ok'] > 0)
                                for m in names[i]] for i, s in enumerate(SEEDS)])
            fmt = lambda q: '-' if q is None else f"{q['iqm'] * n:6.1f} [{q['lo'] * n:.1f}, {q['hi'] * n:.1f}]"
            print(f'  {start:7s} {pool}: ladder {fmt(a)}   control {fmt(c)}   ladder - control {fmt(diff)}')
            out['r8_vs_ctrl'][f'{start}|{pool}'] = {'ladder': a, 'control': c, 'diff': diff, 'n': n}

    # ---- threshold test
    print('\n## threshold test: y = ladder r8 solves (x1); logistic P(y | x), x clipped at -40; null = end arm curve')
    endrows = []
    for s in SEEDS:
        X, Y = w1_start(s, 'pend'), solved(f's{s}_pend_r8', 1)
        endrows += [(X[n], float(Y[n])) for n in X if n in Y]
    bnull = logit_fit(np.array([max(x, XCLIP) for x, _ in endrows]), np.array([y for _, y in endrows]))
    print(f'  null (end arm, pooled): b0 {bnull[0]:.2f} b1 {bnull[1]:.3f} x50 {x50(bnull):.1f}')
    out['null'] = {'b': bnull.tolist(), 'x50': x50(bnull)}
    out['threshold'] = {}
    for xs_name in ('x_start', 'x_ctrl', 'x_ev'):
        print(f'\n  ### x = {xs_name}' + {'x_start': ' (reference worst step under the start checkpoint; brief\'s form)',
                                         'x_ctrl': ' (reference worst step under the same start\'s replay-only control r8)',
                                         'x_ev': ' (worst step of trajectory\'s eventual proof, end-arm r8\'s own, under the start; '
                                                 'exists only where the end arm solved)'}[xs_name])
        print('  start   seed  pairs  x50     #x<-12  solved(x<-12)  null E   excess')
        tot = {'obs': 0, 'exp': 0.0, 'per_seed_excess': {}}
        bn = bnull
        if xs_name == 'x_ev':    # its own null: the end arm's curve on the same measure (not pre-registered; secondary)
            ev = [(max(w1_start(s, 'pend', 'ev')[n], XCLIP), float(solved(f's{s}_pend_r8', 1)[n])) for s in SEEDS
                  for n in w1_start(s, 'pend', 'ev')]
            bn = logit_fit(np.array([a for a, _ in ev]), np.array([y for _, y in ev]))
            print(f'  null for x_ev (end arm, pooled): b0 {bn[0]:.2f} b1 {bn[1]:.3f} x50 {x50(bn):.1f}')
        for start in STARTS:
            for s in SEEDS:
                Y = solved(f's{s}_{start}_r8', 1)
                if xs_name == 'x_start':
                    X = w1_start(s, start)
                elif xs_name == 'x_ctrl':
                    X = w1_own(s, start, 'c8')
                else:
                    X = w1_start(s, start, 'ev')
                if Y is None or not X:
                    print(f'  {start:7s} s{s}   (missing)'); continue
                pr = [(max(X[n], XCLIP), float(Y[n])) for n in X if n in Y]
                b = logit_fit(np.array([a for a, _ in pr]), np.array([y for _, y in pr]))
                low = [(x, y) for x, y in pr if x < LO]
                obs, exp = int(sum(y for _, y in low)), sum(P(bn, x) for x, _ in low)
                print(f'  {start:7s} s{s}  {len(pr):5d}  {x50(b):6.1f}  {len(low):6d}  {obs:9d}  {exp:9.1f}  {obs - exp:+7.1f}')
                out['threshold'][f'{xs_name}|{start}|s{s}'] = {'b': b.tolist(), 'x50': x50(b), 'n': len(pr), 'n_low': len(low),
                                                                'obs_low': obs, 'exp_low': exp}
                if start in EARLY:
                    tot['obs'] += obs; tot['exp'] += exp
                    tot['per_seed_excess'][s] = tot['per_seed_excess'].get(s, 0) + obs - exp
        E = tot['obs'] - tot['exp']
        fires = E >= 15 and sum(v >= 3 for v in tot['per_seed_excess'].values()) >= 2
        print(f'  starts p1600-p16000, 3 seeds: solved from x<-12 = {tot["obs"]}, null expects {tot["exp"]:.1f}, excess {E:+.1f}; '
              f'per-seed excess {", ".join(f"s{k} {v:+.1f}" for k, v in sorted(tot["per_seed_excess"].items()))}; '
              f'pre-registered falsifier (E >= 15, >= 2 seeds >= 3) {"FIRES" if fires else "does not fire"}')
        out['threshold'][f'{xs_name}|total'] = dict(tot, excess=E, fires=fires)

    # ---- RL-only solves from far below: ladder r8 solves, the start and the control never do (both sample seeds)
    print('\n## RL-only solves with x_start < -12: ladder r8 (x1) solves; start (x0, x1) and control r8 (x0, x1) do not')
    rlonly = []
    for start in EARLY + ['pend']:
        for s in SEEDS:
            Y = solved(f's{s}_{start}_r8', 1); X = w1_start(s, start); Xc = w1_own(s, start, 'c8') or {}
            S0 = [solved(f's{s}_{start}_r0', x) for x in (0, 1)]; C = [solved(f'c{s}_{start}_r8', x) for x in (0, 1)]
            if Y is None or any(c is None for c in C):
                continue
            for n, x in X.items():
                if x < LO and Y.get(n) and not any(d.get(n) for d in S0 if d) and not any(c.get(n) for c in C):
                    rlonly.append((start, s, n, x, Xc.get(n), G[s].get(n)))
    for start in EARLY + ['pend']:
        sub = [r for r in rlonly if r[0] == start]
        print(f'  {start:7s}: {len(sub)} pairs (s0 / s1 / s2 = {" / ".join(str(sum(r[1] == s for r in sub)) for s in SEEDS)}); '
              f'trajectory group {dict(sorted({g: sum(r[5] == g for r in sub) for g in "ABC"}.items()))}')
    out['rl_only_low'] = [list(r) for r in rlonly]

    # ---- group C and per-group pass@k at r8 by start (sample seed 1)
    print('\n## r8 pass@k by trajectory group (sample seed 1; mean over theorem-seed pairs)')
    out['passk'] = {}
    for start in ['pend_r0'] + STARTS:
        st, ck = ('pend', 'r0') if start == 'pend_r0' else (start, 'r8')
        line = []
        for g in 'ABC':
            v = {k: [] for k in KS}; cs = 0
            for s in SEEDS:
                d = reads(f's{s}_{st}_{ck}', 1)
                if d is None:
                    continue
                for n, r in d.items():
                    if G[s].get(n) == g:
                        for k in KS:
                            v[k].append(passk(r['n_tried'], r['n_ok'], k))
                        cs += r['n_ok'] > 0
            if v[1]:
                line.append(f"{g}: " + ' '.join(f'{np.mean(v[k]):.2f}' for k in KS) + f' ({cs} solved / {len(v[1])})')
                out['passk'][f'{start}|{g}'] = {k: float(np.mean(v[k])) for k in KS} | {'solved': cs, 'n': len(v[1])}
        print(f'  {start:8s} ' + '   '.join(line))

    # ---- trajectories: reference worst step (median) by group at r0, r2, r4, r8 per start (this run's scores)
    print('\n## reference worst step (median over theorem-seed pairs) by group, per start: r0 / r2 / r4 / r8 / control r8')
    out['traj_ref'] = {}
    for start in EARLY:
        for g in 'ABC':
            meds = []
            for ck in ('r0', 'r2', 'r4', 'r8', 'c8'):
                v = []
                for s in SEEDS:
                    W = w1_own(s, start, ck)
                    if W:
                        v += [w for n, w in W.items() if G[s].get(n) == g]
                meds.append(stt.median(v) if v else None)
            out['traj_ref'][f'{start}|{g}'] = meds
            print(f'  {start:7s} {g}: ' + ' / '.join('-' if m is None else f'{m:.2f}' for m in meds))

    # ---- reproducibility
    print('\n## reproducibility (seed 0): re-read of the starts (sample seed 1) vs trajectory; re-scored refs vs trajectory')
    out['repro'] = {}
    for start in EARLY:
        a, b = solved(f's0_{start}_rr', 1), solved(f's0_{start}_r0', 1)
        if a and b:
            dif = sum(a[n] != b[n] for n in a)
            cnt = {pool: (sum(a[n] for n in a if reads(f's0_{start}_rr', 1)[n]['pool'] == pool),
                          sum(b[n] for n in b if reads(f's0_{start}_r0', 1)[n]['pool'] == pool)) for pool in POOLS}
            print(f'  {start}: solved (re-read, trajectory) {cnt}; theorems whose verdict differs {dif}')
            out['repro'][f'read|{start}'] = {'counts': cnt, 'differ': dif}
    for start in EARLY:
        for s in SEEDS:
            mine, theirs = w1_own(s, start, 'r0'), w1_start(s, start)
            if mine:
                d = max(abs(mine[n] - theirs[n]) for n in mine if n in theirs)
                print(f'  rescore s{s} {start}: max |delta w1| over {len(mine)} refs = {d:.2e}')
                out['repro'][f'score|s{s}|{start}'] = d

    # ---- truncation per stratum (pool x group), this run's reads
    print('\n## truncation (action truncated + step cap, share of samples) per stratum; worst strata of this run\'s reads')
    tr = []
    for fn in sorted(os.listdir(f'{R}/eval')) if os.path.isdir(f'{R}/eval') else []:
        if not fn.endswith('.jsonl'):
            continue
        lab, rest = fn.split('__'); pool, x = rest[:-6].split('_x')
        s = int(lab[1])
        agg = {}
        for r in rj(f'{R}/eval/{fn}'):
            g = G[s].get(r['name'], '?')
            t = sum(('truncated' in q) or ('step cap' in q) for q in r.get('reasons', []))
            a = agg.setdefault(g, [0, 0]); a[0] += t; a[1] += r['n_tried']
        for g, (t, n) in agg.items():
            tr.append((t / n, lab, pool, x, g, n))
    tr.sort(reverse=True)
    for v, lab, pool, x, g, n in tr[:8]:
        print(f'  {v * 100:5.2f} %  {lab} {pool} x{x} group {g} ({n} samples)')
    print(f'  strata over 0.1 %: {sum(v > 0.001 for v, *_ in tr)} of {len(tr)}')
    out['truncation_top'] = tr[:40]

    # ---- examples in Lean: RL-only solves from the lowest x_start
    print('\n## examples (RL-only, lowest x_start): the ladder r8 proof in Lean (its eventual proof where scored)')
    for start, s, n, x, xc, g in sorted(rlonly, key=lambda r: r[3])[:3]:
        ev = {o['name']: o for o in rj(f'{R}/targets/eventual_s{s}_{start}.jsonl')} if os.path.exists(f'{R}/targets/eventual_s{s}_{start}.jsonl') else {}
        r = reads(f's{s}_{start}_r8', 1)[n]
        proof = ev[n]['proof'] if n in ev else r['proofs'][0]
        xcs = f'{xc:.2f}' if xc is not None else '-'
        print(f'\n  {start} s{s} {n} (group {g}): x_start {x:.2f}, x_ctrl {xcs}; r8 n_ok {r["n_ok"]}/256')
        print('  ' + lean_of(r['prompt'], proof).replace('\n', '\n  '))

    os.makedirs(R, exist_ok=True)
    json.dump(out, open(f'{R}/summary.json', 'w'), indent=1, default=str)
    if '--figs' in sys.argv:
        figures(out, endrows, bnull)


def figures(out, endrows, bnull):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    os.makedirs('figures', exist_ok=True)
    col = {'p1600': '#d62728', 'p5000': '#ff7f0e', 'p12000': '#2ca02c', 'p16000': '#1f77b4', 'pend': '#222222'}
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.3), sharey=True)
    xx = np.linspace(-40, 0, 200)
    for ax, xs_name in zip(axs, ('x_start', 'x_ctrl', 'x_ev')):
        for start in STARTS:
            bs = [out['threshold'].get(f'{xs_name}|{start}|s{s}', {}).get('b') for s in SEEDS]
            bs = [b for b in bs if b]
            for b in bs:
                ax.plot(xx, 1 / (1 + np.exp(-(b[0] + b[1] * xx))), color=col[start], alpha=0.35, lw=1)
            if bs:
                bm = np.mean(bs, axis=0)
                ax.plot(xx, 1 / (1 + np.exp(-(bm[0] + bm[1] * xx))), color=col[start], lw=2.2, label=start)
        ax.plot(xx, 1 / (1 + np.exp(-(bnull[0] + bnull[1] * xx))), 'k--', lw=1, label='null (end arm)')
        ax.axvline(LO, color='grey', lw=0.8, ls=':')
        ax.set_xlabel({'x_start': 'reference worst step under the start (nats)',
                       'x_ctrl': "reference worst step under the start's replay control r8",
                       'x_ev': "end-arm eventual proof's worst step under the start"}[xs_name], fontsize=9)
        ax.set_title(xs_name)
    axs[0].set_ylabel('P(ladder r8 solves at k 256)'); axs[0].legend(fontsize=8)
    fig.suptitle('Threshold test: logistic fits per start (thin: per seed; thick: mean coefficients). Lean alone; best-cap12 9.56M.', fontsize=10)
    fig.tight_layout(); fig.savefig('figures/rfc_threshold.png', dpi=130); plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(11, 4))
    for ax, pool in zip(axs, POOLS):
        n = 72 if pool == 'tb72' else 250
        for i, start in enumerate(STARTS):
            for j, which in enumerate(('ladder', 'control')):
                q = out['r8_vs_ctrl'].get(f'{start}|{pool}', {}).get(which)
                if q:
                    ax.errorbar(i + (0.15 if j else -0.15), q['iqm'] * n, yerr=[[q['iqm'] * n - q['lo'] * n], [q['hi'] * n - q['iqm'] * n]],
                                fmt='o' if j == 0 else 's', color='#1f77b4' if j == 0 else '#999999', label=which if i == 0 else None)
                    ax.scatter([i + (0.15 if j else -0.15)] * len(q['per_seed']), [v * n for v in q['per_seed']], s=8, color='k', zorder=3)
            r0 = [out['solved'].get(f'{start}|r0|x1')]
            r0 = [r[pool] for r in (r0[0] or []) if r]
            if r0:
                ax.scatter([i] * len(r0), r0, marker='x', color='#d62728', label='start (r0)' if i == 0 else None)
        ax.set_xticks(range(len(STARTS))); ax.set_xticklabels(STARTS); ax.set_title(f'{pool} solved at k 256 (of {n})')
    axs[0].legend(fontsize=8)
    fig.suptitle('r8 of the T1 ladder vs its replay-only control, by start (IQM, 95 % CI; dots per seed). Sample seed 1.', fontsize=10)
    fig.tight_layout(); fig.savefig('figures/rfc_r8_by_start.png', dpi=130); plt.close(fig)

    fig, axs = plt.subplots(1, 3, figsize=(14, 4), sharey=True)
    for ax, g in zip(axs, 'ABC'):
        for start in EARLY:
            m = out['traj_ref'].get(f'{start}|{g}')
            if m and any(v is not None for v in m[:4]):
                ax.plot([0, 2, 4, 8], [v if v is not None else np.nan for v in m[:4]], 'o-', color=col[start], label=start)
                if m[4] is not None:
                    ax.scatter([8.6], [m[4]], marker='s', color=col[start], alpha=0.6)
        ax.set_title(f'group {g}: reference worst step (median)'); ax.set_xlabel('RL round (square: control r8)')
    axs[0].set_ylabel('nats (T 1.0)'); axs[0].legend(fontsize=8)
    fig.tight_layout(); fig.savefig('figures/rfc_traj_ref.png', dpi=130); plt.close(fig)


if __name__ == '__main__':
    main()
