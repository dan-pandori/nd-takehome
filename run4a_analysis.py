#!/usr/bin/env python3
"""round3-run4a summary: reductio on the required pool vs model size (3.2M same-set control / 25M / 85M on the rebuilt
f = 0 set `train_reductio_f0_b1`; run 5's 3.2M draws on the original set alongside, from artifacts/r5).

Per draw: parameters, Stage-1 val loss, held-out greedy, pre-RL strict-reductio hits / rate (coverage k = 2000 x 300),
EI and frozen acquisition per round and per stratum (start-index-normalised, dependency-pruned strict predicate),
oracle violations (solved without the pattern), base reachability at 1e4 on the acquired targets, EI-only fraction.
  python3 run4a_analysis.py            -> artifacts/r3_4a/summary.json (+ figures with --figs figures)
Every number is derived from files under artifacts/r3_4a/ and artifacts/r5/ (pulled from the pods / committed).
"""
import argparse, json, os, sys, glob, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from normalize import norm
from patterns import classify

A = 'artifacts/r3_4a'
TARGETS = 'data/p2/targets_reductio_req.jsonl'
TRANSFER = 'data/p2/transfer_reductio_req.jsonl'
SIZES = [('m3', '3.2M same-set'), ('m25', '25M config A'), ('m25B', '25M config B'), ('m85', '85M config A'), ('m85B', '85M config B')]
IGNITE = 6            # >= 2 % of 300 targets acquired (cumulative)


def read(fn):
    return [json.loads(l) for l in open(fn) if l.strip()]


def strict(proof):
    c = classify(norm(proof))
    return bool(c and c['reductio'])


def arm(d, T, TR):
    """cumulative acquisition per round from found_<last>.jsonl (each proof carries its first round)."""
    fns = sorted(glob.glob(f'{d}/found_[0-9]*.jsonl'), key=lambda x: int(re.findall(r'found_(\d+)', x)[0]))
    if not fns:
        return None
    last = int(re.findall(r'found_(\d+)', fns[-1])[0])
    strat = {t['name']: t['min_lines_ub'] for t in T}; schema = {t['name']: t['schema'] for t in T}
    first_pat, first_any, proofs = {}, {}, set()
    for x in read(fns[-1]):
        first_any[x['name']] = min(first_any.get(x['name'], 99), x['round'])
        if strict(x['proof']):
            first_pat[x['name']] = min(first_pat.get(x['name'], 99), x['round'])
            proofs.add((x['name'], norm(x['proof'])))
    out = {'rounds': last, 'solved': len(first_any), 'acquired': len(first_pat), 'solved_without_pattern': len(set(first_any) - set(first_pat)),
           'distinct_pattern_proofs': len(proofs),
           'acq_by_round': [sum(r <= k for r in first_pat.values()) for k in range(1, last + 1)],
           'acq_by_stratum': {str(L): sum(1 for n in first_pat if strat[n] == L) for L in (7, 8, 9, 10)},
           'acq_by_schema': dict(sorted(collections.Counter(schema[n] for n in first_pat).items())),
           'acquired_names': sorted(first_pat)}
    ig = [k + 1 for k, v in enumerate(out['acq_by_round']) if v >= IGNITE]
    out['ignition_round'] = ig[0] if ig else None
    out['first_proof_round'] = min(first_pat.values()) if first_pat else None
    tf = f'{d}/found_transfer_{last}.jsonl'
    if os.path.exists(tf):
        ts = {t['name']: t['min_lines_ub'] for t in TR}; acq = {x['name'] for x in read(tf) if strict(x['proof'])}
        out['transfer_acquired'] = len(acq); out['transfer_by_stratum'] = {str(L): sum(1 for n in acq if ts[n] == L) for L in (7, 8, 9, 10)}
    rj = [json.load(open(f)) for f in sorted(glob.glob(f'{d}/round_*.json'), key=lambda x: int(re.findall(r'round_(\d+)', x)[0]))]
    out['heldout_greedy_by_round'] = [r['heldout_greedy']['rate'] for r in rj]
    out['trained_rounds'] = sum(1 for r in rj if r.get('mix_rl_records', 0) > 0)
    if os.path.exists(f'{d}/args.json'):
        a = json.load(open(f'{d}/args.json')); out['args'] = {k: a[k] for k in ('ft_lr', 'ft_steps', 'batch', 'k', 'rounds', 'seed', 'no_train', 'init', 'train')}
    return out


def cov(fn, T, within=None):
    if not os.path.exists(fn):
        return None
    strat = {t['name']: t['min_lines_ub'] for t in T}; schema = {t['name']: t['schema'] for t in T}
    rs = read(fn)
    assert len({r['name'] for r in rs}) == len(rs) and {r['name'] for r in rs} <= set(strat), fn
    hit = [r for r in rs if r['hits_by_pattern'].get('reductio', 0) > 0]
    out = {'file': fn, 'targets': len(rs), 'samples': sum(r['n_tried'] for r in rs), 'n_ok': sum(r['n_ok'] for r in rs),
           'strict_hits': sum(r['hits_by_pattern'].get('reductio', 0) for r in rs), 'targets_hit': len(hit),
           'targets_hit_names': sorted(r['name'] for r in hit),
           'solved_without_pattern': sum(1 for r in rs if r['n_ok'] > 0 and r['hits_by_pattern'].get('reductio', 0) == 0),
           'hits_by_stratum': {str(L): sum(r['hits_by_pattern']['reductio'] for r in hit if strat[r['name']] == L) for L in (7, 8, 9, 10)},
           'targets_hit_by_stratum': {str(L): sum(1 for r in hit if strat[r['name']] == L) for L in (7, 8, 9, 10)},
           'hits_by_schema': dict(sorted(collections.Counter({s: sum(r['hits_by_pattern']['reductio'] for r in hit if schema[r['name']] == s) for s in {schema[r['name']] for r in hit}}).items())),
           'pass_at_256_targets': sum(1 for r in rs if r['first_hit'] is not None and r['first_hit'] <= 256)}
    out['rate'] = out['strict_hits'] / max(1, out['samples'])
    out['complete'] = len(rs) == len(T)
    # comparable 'non-zero in the first 2000 samples per target' flag for files sampled at larger k (run 5's pass@1e4 files)
    out['targets_hit_within_2000'] = sum(1 for r in rs if any(p['pat'].get('reductio') and p['first'] <= 2000 for p in r['proofs']))
    return out


def stage1(tag):
    out = {}
    fn = f'{A}/train_{tag}.log'
    if os.path.exists(fn):
        txt = open(fn).read()
        m = re.search(r'params (\d+)', txt); out['params'] = int(m.group(1)) if m else None
        v = re.findall(r'step (\d+) loss [\d.]+ lr [\d.e+-]+ (\d+)s val ([\d.]+)', txt)
        if v:
            out['steps'] = int(v[-1][0]); out['train_secs'] = int(v[-1][1]); out['val_loss'] = float(v[-1][2]); out['val_loss_min'] = min(float(x[2]) for x in v)
    fn = f'{A}/heldout_greedy_{tag}.json'
    if os.path.exists(fn):
        s = json.load(open(fn)); out['heldout_greedy'] = s['rate']; out['heldout_solved'] = s['solved']; out['heldout_n'] = s['n']
    return out


def draw(tag, T, TR, adir=A, names=None):
    names = names or {'cov': f'{adir}/cov_{tag}_pre.s0.jsonl', 'ei': f'{adir}/ei_{tag}', 'frozen': f'{adir}/frozen_{tag}', 'b10k': f'{adir}/cov_{tag}_b10k.s0.jsonl'}
    D = {'tag': tag, 'pre_rl': cov(names['cov'], T), 'ei': arm(names['ei'], T, TR), 'frozen': arm(names['frozen'], T, TR)}
    b = cov(names['b10k'], T)
    if D['ei'] and D['ei']['acquired'] and b:
        reach = set(b['targets_hit_names']); acq = set(D['ei']['acquired_names'])
        covered = {r['name'] for r in read(names['b10k'])}
        D['base10k'] = {'file': names['b10k'], 'targets_sampled': b['targets'], 'samples': b['samples'], 'acquired_covered': len(acq & covered),
                        'acquired_base_reachable': len(acq & reach), 'ei_only': len((acq & covered) - reach),
                        'ei_only_fraction': len((acq & covered) - reach) / max(1, len(acq & covered)), 'rate': b['rate'],
                        'base_reachable_all_sampled': b['targets_hit'], 'solved_without_pattern': b['solved_without_pattern']}
    return D


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', default=f'{A}/summary.json'); ap.add_argument('--figs', default=None)
    a = ap.parse_args()
    T, TR = read(TARGETS), read(TRANSFER)
    res = {'targets': TARGETS, 'n_targets': len(T), 'strata': dict(sorted(collections.Counter(t['min_lines_ub'] for t in T).items())), 'sizes': {}}
    for sz, label in SIZES:
        tags = sorted({re.findall(r'stage1_(' + sz + r'_s\d+)\.done', f)[0] for f in glob.glob(f'{A}/stage1_{sz}_s*.done')})
        cell = {'label': label, 'draws': {}}
        extra = {'label': label + ' EXTRA draws (exploratory, coverage only)', 'draws': {}}
        for tag in [t for t in tags if int(t.split('_s')[1]) >= 3]:
            D = draw(tag, T, TR); D['stage1'] = stage1(tag); extra['draws'][tag] = D
        tags = [t for t in tags if int(t.split('_s')[1]) < 3]
        for tag in tags:
            D = draw(tag, T, TR); D['stage1'] = stage1(tag); cell['draws'][tag] = D
        ds = [d for d in cell['draws'].values() if d['pre_rl'] and d['pre_rl']['complete']]
        cell['n_draws_sampled'] = len(ds); cell['n_nonzero'] = sum(1 for d in ds if d['pre_rl']['targets_hit_within_2000'] > 0)
        res['sizes'][sz] = cell
        if extra['draws']:
            ds = [d for d in extra['draws'].values() if d['pre_rl'] and d['pre_rl']['complete']]
            extra['n_draws_sampled'] = len(ds); extra['n_nonzero'] = sum(1 for d in ds if d['pre_rl']['targets_hit_within_2000'] > 0)
            res['sizes'][sz + 'x'] = extra
    # run 5's 3.2M draws on the ORIGINAL set (reviewed files; pre-RL = the pass@1e4 coverage file, 3e6 samples)
    old = {'label': '3.2M original set (run 5)', 'draws': {}}
    for s in (0, 1, 2):
        nm = {'cov': f'artifacts/r5/cov_reductio_f0_s{s}_req.s0.jsonl', 'ei': f'artifacts/r5/ei_reductio_f0_s{s}_req', 'frozen': f'artifacts/r5/frozen_reductio_f0_s{s}_req',
              'b10k': f'artifacts/r5/cov_reductio_f0_s{s}_req.s0.jsonl'}
        if os.path.exists(nm['cov']):
            old['draws'][f'r5_s{s}'] = draw(f'r5_s{s}', T, TR, names=nm)
    res['sizes']['m3_run5'] = old
    # exploratory extras (not pre-registered): ft_lr 3e-5 on 85M-A s0; rounds 9-16 on 85M-A s2
    res['extras'] = {k: arm(f'{A}/{k}', T, TR) for k in ('x_ei_m85_s0_lr3e-5', 'x_ei_m85_s2_r9-16') if os.path.isdir(f'{A}/{k}')}
    json.dump(res, open(a.out, 'w'), indent=1)
    # console table
    print(f"{'draw':10s} {'params':>9s} {'val':>6s} {'held':>6s} | {'hits':>6s} {'rate':>8s} {'tg':>3s} | {'EI acq':>6s} {'7/8/9/10':>12s} {'ign':>3s} {'viol':>4s} | {'frz':>4s} | {'b10k reach/acq':>14s} {'EI-only':>7s}")
    for sz, cell in res['sizes'].items():
        for tag, D in cell['draws'].items():
            s1 = D.get('stage1', {}); p = D['pre_rl'] or {}; e = D['ei'] or {}; f = D['frozen'] or {}; b = D.get('base10k') or {}
            st = e.get('acq_by_stratum', {})
            print(f"{tag:10s} {str(s1.get('params', '')):>9s} {str(s1.get('val_loss', '')):>6s} {str(s1.get('heldout_greedy', '')):>6s} | {str(p.get('strict_hits', '')):>6s} {p.get('rate', float('nan')):8.1e} {str(p.get('targets_hit', '')):>3s} | "
                  f"{str(e.get('acquired', '')):>6s} {'/'.join(str(st.get(str(L), '')) for L in (7, 8, 9, 10)):>12s} {str(e.get('ignition_round', '')):>3s} {str(e.get('solved_without_pattern', '')):>4s} | {str(f.get('acquired', '')):>4s} | "
                  f"{(str(b.get('acquired_base_reachable', '')) + '/' + str(b.get('acquired_covered', ''))):>14s} {b.get('ei_only_fraction', float('nan')):7.2f}")
    if a.figs:
        figures(res, a.figs)


def figures(res, outdir):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    PAR = {'m3': 3.21e6, 'm3_run5': 3.21e6, 'm25': 25.3e6, 'm25B': 25.3e6 * 1.25, 'm85': 85.2e6, 'm85B': 85.2e6 * 1.25, 'm85x': 85.2e6 * 0.8}
    COL = {'m3': '#4477AA', 'm3_run5': '#BBBBBB', 'm25': '#EE6677', 'm25B': '#AA3377', 'm85': '#228833', 'm85B': '#117733', 'm85x': '#99CC99'}
    fig, ax = plt.subplots(1, 3, figsize=(13.5, 4.3))
    for sz, cell in res['sizes'].items():
        ds = [d for d in cell['draws'].values() if d['pre_rl']]
        if not ds:
            continue
        jit = 0.93 if sz == 'm3_run5' else 1.0
        for i, d in enumerate(ds):
            x = PAR[sz] * jit * (1 + 0.06 * (i - 1))
            r = d['pre_rl']['rate']
            ax[0].scatter([x], [max(r, 1e-7)], color=COL[sz], marker='o' if r > 0 else 'x', s=45, zorder=3)
            if d['ei']:
                ax[1].scatter([x], [d['ei']['acquired']], color=COL[sz], s=45, zorder=3)
                if d['frozen']:
                    ax[1].scatter([x], [d['frozen']['acquired']], facecolors='none', edgecolors=COL[sz], s=45, zorder=3)
            if d.get('base10k'):
                ax[2].scatter([x], [d['base10k']['ei_only_fraction']], color=COL[sz], s=45, zorder=3)
        ax[0].scatter([], [], color=COL[sz], label=f"{cell['label'].replace(' (exploratory, coverage only)', '')}: {sum(1 for d in ds if d['pre_rl']['targets_hit_within_2000'] > 0)}/{len(ds)} non-zero in 600k")
    ax[0].set_yscale('log'); ax[0].set_ylabel('pre-RL strict-reductio rate per sample\n(× = 0 hits, drawn at 1e-7)'); fig.legend(*ax[0].get_legend_handles_labels(), fontsize=7.5, frameon=False, ncol=4, loc='lower center')
    ax[1].set_ylabel('targets acquired / 300 after 8 rounds\n(filled EI, open frozen twin)')
    ax[2].set_ylabel('EI-only fraction\n(acquired, not base-reachable at 1e4)'); ax[2].set_ylim(-0.03, 1.03)
    for x in ax:
        x.set_xscale('log'); x.set_xlabel('parameters'); x.set_xlim(2e6, 1.5e8); x.grid(alpha=0.25, lw=0.5)
        for s in ('top', 'right'):
            x.spines[s].set_visible(False)
    fig.tight_layout(rect=(0, 0.1, 1, 1)); os.makedirs(outdir, exist_ok=True); fig.savefig(f'{outdir}/run4a_size.png', dpi=150); plt.close(fig)
    # per-round curves
    fig, ax = plt.subplots(1, 1, figsize=(5.5, 3.8))
    for sz, cell in res['sizes'].items():
        for tag, d in cell['draws'].items():
            if d['ei']:
                ax.plot(range(1, d['ei']['rounds'] + 1), d['ei']['acq_by_round'], color=COL[sz], lw=1.4, marker='o', ms=3, label=cell['label'])
    h, l = ax.get_legend_handles_labels(); seen = {}
    for hh, ll in zip(h, l):
        seen.setdefault(ll, hh)
    ax.legend(seen.values(), seen.keys(), fontsize=7, frameon=False); ax.set_xlabel('EI round (32 attempts per target each)'); ax.set_ylabel('targets acquired / 300 (cumulative)')
    ax.axhline(52, color='k', lw=0.5, ls=':'); ax.text(1, 54, '7-line stratum = 52', fontsize=7)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(f'{outdir}/run4a_curves.png', dpi=150); plt.close(fig)


if __name__ == '__main__':
    main()
