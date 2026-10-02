#!/usr/bin/env python3
"""grpo-best analysis (preregistration/grpo-best.md § 6).  Reads per-theorem read-outs only:
  EI (trajectory, inherited)   artifacts/gb/ei_eval/s<S>_<ck>__<pool>_x<x>.jsonl        ck in pend r2 r4 r8
  EI r8 end reads (here)       artifacts/gb/eval/ei_s<S>_r8__{dev,held}_x0.json
  GRPO arms (here)             artifacts/gb/eval/gb_<adv>_s<S>_<ck>__<pool>_x<x>.jsonl  ck in r2 r4 r8; r8 also dev, held
  groups                       artifacts/gb/groups.json (gb_groups.py)
  ladder files                 artifacts/gb/gb_<adv>_s<S>/round_<r>.json
-> tables on stdout, artifacts/gb/summary.json.  All counts: Lean alone (state-env gate)."""
import json, math, os, random, sys
from bs_analysis import iqm, boot_ci

E, G = 'artifacts/gb/ei_eval', 'artifacts/gb/eval'
ARMS = ['EI', 'default', 'unlikely', 'passk', 'distinct']
SEEDS = (0, 1, 2)
POOLS = ('tb72', 'h250')
MDD = {'C_r8_x1': 3.5, 'all_r8_x1': 9.3, 'tb72_r8_x0': 9.8, 'held': 0.063}
groups = {int(s): g for s, g in json.load(open('artifacts/gb/groups.json'))['groups'].items()}


def path(arm, s, ck, pool, x, ext='jsonl'):
    if arm == 'EI' and ck != 'r8' or arm == 'EI' and pool in POOLS:
        return f'{E}/s{s}_{ck}__{pool}_x{x}.{ext}'
    lab = f'ei_s{s}_{ck}' if arm == 'EI' else f'gb_{arm}_s{s}_{ck}'
    return f'{G}/{lab}__{pool}_x{x}.{ext}'


_cache = {}
def rows(arm, s, ck, x):
    """name -> (n_ok, n_tried) over textbook72 + holdout250, or None if a read is missing."""
    key = (arm, s, ck, x)
    if key not in _cache:
        out = {}
        for p in POOLS:
            fn = path(arm, s, ck, p, x)
            if not os.path.exists(fn):
                _cache[key] = None; return None
            for l in open(fn):
                r = json.loads(l)
                out[r['name']] = (r['n_ok'], r['n_tried'])
        _cache[key] = out
    return _cache[key]


def summ(arm, s, read):
    fn = path(arm, s, 'r8', read, 0, 'json')
    return json.load(open(fn)) if os.path.exists(fn) else None


def fmt(v, nd=0):
    return '—' if v is None else (f'{v:.{nd}f}' if isinstance(v, float) else str(v))


def line(label, vals, nd=0, mdd=None, ref=None):
    ok = [v for v in vals if v is not None]
    s = f'  {label:<34}' + ' / '.join(fmt(v, nd) for v in vals)
    if len(ok) == len(vals) and ok:
        lo, hi = boot_ci(ok)
        s += f'   IQM {iqm(ok):.{max(nd, 1)}f} [{lo:.{max(nd, 1)}f}, {hi:.{max(nd, 1)}f}]'
        if ref is not None and all(v is not None for v in ref):
            d = iqm(ok) - iqm(ref)
            s += f'   Δ vs EI {d:+.{max(nd, 1)}f}' + (f' (MDD {mdd}; {"outside" if abs(d) >= mdd else "inside"})' if mdd else '')
    return s


def sign_test(k, n):
    """exact two-sided binomial sign test p for k of n discordant pairs going one way."""
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(0, min(k, n - k) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


S = {'arms': {}}
print('# grpo-best — read-outs (Lean alone).  Models: best-cap12 s0/s1/s2 (ALiBiGPT 9,560,832 params, lean_staten, from scratch on K12,')
print('#   Stage-1 1,200 s); EI = trajectory T1 ladder r<k>; GRPO arms = grpo_state.py round-equivalent r<k> from the same base.')
print('# per seed s0 / s1 / s2; IQM (n = 3: the mean) with a stratified-bootstrap 95 % interval.\n')

# ---- 1. headline: group C
print('## 1. Group C (EI never solved on sample seed 0: end of pretraining nor r8) solved at k 256')
ref = {}
for q, desc in (('C_r8_x1', 'r8, sample seed 1 (headline)'), ('C_r8_either', 'r8, either sample seed'),
                ('C_r4_x1', 'r4, sample seed 1'), ('C_r2_x1', 'r2, sample seed 1')):
    print(f' {desc}  (C sizes {[sum(v == "C" for v in groups[s].values()) for s in SEEDS]})')
    for arm in ARMS:
        vals = []
        for s in SEEDS:
            ck = q.split('_')[1]
            C = [n for n, g in groups[s].items() if g == 'C']
            xs = (0, 1) if q.endswith('either') else (1,)
            rr = [rows(arm, s, ck, x) for x in xs]
            vals.append(None if any(r is None for r in rr) else sum(1 for n in C if any(r[n][0] for r in rr)))
        if arm == 'EI':
            ref[q] = vals
        S['arms'].setdefault(arm, {})[q] = vals
        print(line(arm, vals, mdd=MDD.get(q), ref=None if arm == 'EI' else ref[q]))
print()

# ---- 2. bias-free companion: discordant theorem-seed pairs vs EI at r8 over both sample seeds (all 322)
print('## 2. Discordant theorems vs EI r8 (solved on either sample seed; all 322 per seed, pooled over seeds)')
print(f'  {"arm":<10}{"arm-only":>9}{"EI-only":>9}{"both":>7}{"neither":>9}   sign-test p   (C only: arm-only / EI-only)')
for arm in ARMS[1:]:
    a_only = e_only = both = nei = ca = ce = 0; ok = True; per = []
    for s in SEEDS:
        ra = [rows(arm, s, 'r8', x) for x in (0, 1)]; re_ = [rows('EI', s, 'r8', x) for x in (0, 1)]
        if any(r is None for r in ra + re_):
            ok = False; break
        sa = sb = 0
        for n in re_[0]:
            a, e = any(r[n][0] for r in ra), any(r[n][0] for r in re_)
            a_only += a and not e; e_only += e and not a; both += a and e; nei += not a and not e
            sa += a and not e; sb += e and not a
            if groups[s][n] == 'C':
                ca += a and not e; ce += e and not a
        per.append((sa, sb))
    if ok:
        p = sign_test(a_only, a_only + e_only)
        S['arms'][arm]['discordant'] = {'arm_only': a_only, 'ei_only': e_only, 'both': both, 'neither': nei, 'p': p,
                                        'per_seed': per, 'C_arm_only': ca, 'C_ei_only': ce}
        print(f'  {arm:<10}{a_only:>9}{e_only:>9}{both:>7}{nei:>9}   {p:.3g}          {ca} / {ce}   per seed {per}')
    else:
        print(f'  {arm:<10} (reads missing)')
print()

# ---- 3. sharpening vs support: pass@1 and pass@256 by group (sample seed 1)
print('## 3. pass@1 / pass@256 by group (sample seed 1; mean over the group, then IQM over seeds)')
for grp in 'ABC':
    print(f' group {grp}')
    for arm in ARMS:
        cells = []
        for ck in (['pend'] if arm == 'EI' else []) + ['r2', 'r4', 'r8']:
            p1, p256 = [], []
            for s in SEEDS:
                r = rows(arm, s, ck, 1)
                if r is None:
                    break
                names = [n for n, g in groups[s].items() if g == grp]
                p1.append(sum(r[n][0] / r[n][1] for n in names) / len(names))
                p256.append(sum(1 for n in names if r[n][0]) / len(names))
            if len(p1) == 3:
                cells.append(f'{ck} {iqm(p1):.3f} / {iqm(p256):.3f}')
                S['arms'][arm][f'{grp}_{ck}_pass1_pass256_x1'] = [p1, p256]
            else:
                cells.append(f'{ck} —')
        print(f'  {arm:<10}' + '   '.join(cells))
print()

# ---- 4. totals and retention
print('## 4. Totals and retention')
for q, desc in (('all_r8_x1', 'all 322 solved, r8, sample seed 1'), ('tb72_r8_x0', 'textbook72 solved, r8, sample seed 0'),
                ('h250_r8_x0', 'holdout250 solved, r8, sample seed 0')):
    print(f' {desc}')
    for arm in ARMS:
        vals = []
        for s in SEEDS:
            x = int(q[-1]); r = rows(arm, s, 'r8', x)
            if r is None:
                vals.append(None); continue
            names = [n for n in r if q.startswith('all') or (q.startswith('tb72') == n.startswith('textbook'))]
            vals.append(sum(1 for n in names if r[n][0]))
        if arm == 'EI':
            ref[q] = vals
        S['arms'][arm][q] = vals
        print(line(arm, vals, mdd=MDD.get(q), ref=None if arm == 'EI' else ref[q]))
for read, desc, nd in (('held', 'held-out greedy (5,000), r8', 3), ('dev', 'dev metric (1,108, k 64), r8', 0)):
    print(f' {desc}')
    for arm in ARMS:
        vals = []
        for s in SEEDS:
            sm = summ(arm, s, read)
            vals.append(None if sm is None else (sm['rate'] if read == 'held' else sm['solved']))
        if arm == 'EI':
            ref[read] = vals
        S['arms'][arm][read] = vals
        print(line(arm, vals, nd, mdd=MDD.get(read), ref=None if arm == 'EI' else ref[read]))
print('  (Stage-1 held-out greedy, trajectory: 0.921 / 0.936 / 0.962)')
print()

# ---- 5. truncation (policy: report the fraction of samples that hit a cap), from each read's env_end counts
print('## 5. Samples hitting a cap (action truncated + step cap; the read summaries\' env_end), all reads of each arm')
for arm in ARMS:
    tot = tr = 0; worst = (0, None)
    for s in SEEDS:
        for ck in ('r2', 'r4', 'r8'):
            for x in (0, 1):
                for pool in POOLS:
                    fn = path(arm, s, ck, pool, x, 'json')
                    if not os.path.exists(fn):
                        continue
                    sm = json.load(open(fn))['env']['env_end']
                    a = sum(sm.values()); b = sm.get('truncated', 0) + sm.get('step_cap', 0)
                    tot += a; tr += b
                    if a and b / a > worst[0]:
                        worst = (b / a, f's{s}_{ck}_{pool}_x{x}')
    if tot:
        S['arms'][arm]['trunc'] = [tr, tot]
        print(f'  {arm:<10}{tr:>8} / {tot} = {100 * tr / tot:.3f} %   worst read {100 * worst[0]:.3f} % ({worst[1]})')
print()

# ---- 6. GRPO mechanics from the ladders' own files
print('## 6. GRPO mechanics per round-equivalent (IQM over seeds): mean reward / groups with variance / all-fail / targets cum. solved / held-out greedy (boundary)')
for arm in ARMS[1:]:
    cells = []
    for r_ in range(1, 9):
        v = []
        for s in SEEDS:
            fn = f'artifacts/gb/gb_{arm}_s{s}/round_{r_}.json'
            if os.path.exists(fn):
                j = json.load(open(fn))
                v.append((j['target_sample_acc'], j['frac_groups_with_variance_mean'], j['frac_groups_all_fail_mean'],
                          j['targets_cum']['solved'], (j.get('heldout_greedy') or {}).get('rate')))
        if len(v) == 3:
            m = [iqm([x[i] for x in v]) if all(x[i] is not None for x in v) else None for i in range(5)]
            cells.append(f'r{r_} {m[0]:.2f}/{m[1]:.2f}/{m[2]:.2f}/{m[3]:.0f}/{fmt(m[4], 3)}')
            S['arms'][arm][f'mech_r{r_}'] = v
    print(f'  {arm:<10}' + '  '.join(cells))

json.dump(S, open('artifacts/gb/summary.json', 'w'), indent=1)
