#!/usr/bin/env python3
"""gt_analysis.py -- every number in run `guided-tts`'s write-up, from the pulled read files (no torch; VPS-safe).

  python3 gt_analysis.py [--eval artifacts/gt/eval] [--json artifacts/gt/analysis.json] > artifacts/gt/analysis_stdout.txt

Inputs: <eval>/<model>_s<S>_<arm>.rows.jsonl.gz (one row per theorem: per-attempt ok / tokens / ...) and .json (job
summary: timings, rejection causes).  Models: best12 = trajectory's la_T1_best12_s<S>_r8.pt, best6 =
trajectory-cap6's la_T1_best6_s<S>_r8.pt (both 9,560,832-param ALiBiGPT, lean_staten, T1 ladder r8).

Curves (pre-registered):
  matched tokens  at plain-equivalent k, theorem t: budget b = k * c_plain(t) sampled tokens; arm A gets
                  k' = b / c_A(t) attempts; solve prob = unbiased pass@k' (Chen et al. 2021) interpolated linearly
                  between floor(k') and ceil(k'); k' capped at n = 256.
  matched wall    same with one ratio per job: (job seconds per attempt of A) / (of plain), job seconds = sampling loop
                  (GPU + checker + environment) + final Lean.
  per attempt     plain pass@k of each arm (not compute-matched).
  wall_by_draws   (not pre-registered) matched wall with the job's seconds shared out to theorems by draws, since one
                  ratio per job under-charges theorems where guided redraws are frequent.
Groups: file, min_lines bin (release files; tb72 dev by reference_lines), long (release, min_lines > 10), Roy,
Pelletier, batch3.  Differences vs plain per seed; IQM over seeds with a stratified bootstrap (theorems resampled
within group) 95 % interval; MDD from a bootstrap over attempts within theorem (2.8 x sd of the difference).
"""
import argparse, collections, glob, gzip, json, math, os, random
import numpy as np

KS = [1, 2, 4, 8, 16, 32, 64, 128, 256]
ARMS = ['plain', 'structural', 'logical']
MODELS = ['best12', 'best6']
REL = ('candidate_v0', 'candidate_v1', 'batch3', 'hand_proved_14')


def passk_table(n, c, kmax):
    """unbiased pass@k for k = 0..kmax (k = 0 -> 0): 1 - prod_{i<k} (n-c-i)/(n-i)."""
    i = np.arange(kmax)
    f = np.clip((n - c - i) / (n - i), 0.0, None)
    return np.concatenate([[0.0], 1.0 - np.cumprod(f)])


def interp(tab, k):
    k = min(max(k, 0.0), len(tab) - 1)
    lo = int(math.floor(k)); hi = min(lo + 1, len(tab) - 1)
    return tab[lo] + (k - lo) * (tab[hi] - tab[lo])


def groups_of(r):
    g = ['all', 'file:' + r['file']]
    f, ml, book = r['file'], r.get('min_lines'), r.get('book') or ''
    if f in REL:
        g.append('bin:' + ('<=10' if ml <= 10 else '11-20' if ml <= 20 else '>20'))
        g.append('release')
        if ml > 10:
            g.append('long')
        if 'Roy' in book:
            g.append('Roy')
        if 'Pelletier' in book:
            g.append('Pelletier')
        if f == 'batch3':
            g.append('batch3')
    elif f == 'tb72_textbook_dev' and ml is not None:
        g.append('tb72dev_ref:' + ('<=10' if ml <= 10 else '>10'))
    if f.startswith('tb72'):
        g.append('tb72')
    return g


def load(ev):
    data = {}
    for fn in sorted(glob.glob(os.path.join(ev, '*.rows.jsonl.gz'))):
        key = os.path.basename(fn).replace('.rows.jsonl.gz', '')
        m, s, a = key.split('_')
        rows = [json.loads(l) for l in gzip.open(fn, 'rt')]
        summ = json.load(open(fn.replace('.rows.jsonl.gz', '.json')))
        data[(m, int(s[1:]), a)] = (rows, summ)
    return data


def job_secs(summ):
    st = summ['stats']
    return st['loop_wall_s'] + st.get('lean_s', 0.0)


def curves(rows_a, rows_p, summ_a, summ_p, boot_att=None):
    """per theorem: arrays over KS of (matched-token, matched-wall, per-attempt) solve probability."""
    wr = (job_secs(summ_a) / summ_a['attempts']) / (job_secs(summ_p) / summ_p['attempts'])
    # not pre-registered robustness variant: job seconds shared out to theorems by their share of draws (waves x rows)
    da = sum(sum(r['draws']) for r in rows_a); dp = sum(sum(r['draws']) for r in rows_p)
    out = []
    for ra, rp in zip(rows_a, rows_p):
        assert ra['prompt'] == rp['prompt']
        n = ra['k']
        oka, tka = ra['ok'], ra['tokens']
        tkp = rp['tokens']
        if boot_att is not None:
            ia = [boot_att.randrange(n) for _ in range(n)]
            oka = [oka[i] for i in ia]; tka = [tka[i] for i in ia]
        tab = passk_table(n, sum(oka), n)
        ca, cp = sum(tka) / n, sum(tkp) / n
        tok = [interp(tab, k * cp / ca) for k in KS]
        wal = [interp(tab, k / wr) for k in KS]
        att = [interp(tab, k) for k in KS]
        wa = job_secs(summ_a) * sum(ra['draws']) / da / n; wp = job_secs(summ_p) * sum(rp['draws']) / dp / n
        wt = [interp(tab, k * wp / wa) for k in KS]
        out.append((tok, wal, att, wt))
    return np.array(out)            # (theorems, 4, len(KS))


def iqm(x):
    x = np.sort(np.asarray(x, float)); n = len(x)
    if n < 4:                       # rliable's IQM on n values: trimmed mean of the middle 50 % (fractional weights)
        w = np.zeros(n); lo, hi = 0.25 * n, 0.75 * n
        for i in range(n):
            w[i] = max(0.0, min(i + 1, hi) - max(i, lo))
        return float((w * x).sum() / w.sum())
    lo, hi = int(round(0.25 * n)), int(round(0.75 * n))
    return float(x[lo:hi].mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--eval', default='artifacts/gt/eval')
    ap.add_argument('--json', default='artifacts/gt/analysis.json')
    ap.add_argument('--boot', type=int, default=1000)
    a = ap.parse_args()
    D = load(a.eval)
    out = {'ks': KS, 'cells': {}, 'jobs': {}, 'diff': {}}
    rng = random.Random(0)

    # ---- jobs: compute and rejection diagnostics
    print('## Jobs (per model, seed, arm): attempts, sampled / prefill tokens, seconds, peak memory, ends')
    print('model s arm | solved/259 | acc attempts | samp tok M | prefill tok M | gpu_s check_s env_s lean_s loop_s | '
          'peak GB | trunc draws % | step_cap % | max_rej % | redraws | P(repeat) mean | Lean-rejected finished')
    for (m, s, arm), (rows, summ) in sorted(D.items()):
        st = summ['stats']
        rc = collections.Counter(st['rej_cause'])
        draws = sum(sum(r['draws']) for r in rows)
        end = collections.Counter(st['end'])
        att = summ['attempts']
        fin_rej = summ['finished'] - summ['accepted']
        out['jobs'][f'{m}_s{s}_{arm}'] = dict(
            solved=summ['solved_total'], accepted=summ['accepted'], batch=summ['batch'], attempts=att, finished=summ['finished'],
            sampled_tokens=st['sampled_tokens'], prefill_tokens=st['prefill_tokens'], draws=draws,
            gpu_s=st['gpu_s'], check_s=st['check_s'], env_s=st['env_s'], lean_s=st.get('lean_s'),
            loop_s=st['loop_wall_s'], wall_s=summ['wall_s'], peak_gb=st.get('peak_alloc_gb'), gpu=summ['gpu'],
            truncated_draws=rc.get('truncated', 0), step_cap=end.get('fail:step_cap', 0),
            max_rej=end.get('fail:max_rej', 0), redraws=summ['n_redraws'], repeat_mean=summ['repeat_mean'],
            reject_p_mean=summ['reject_p_mean'], lean_rejected_finished=fin_rej,
            rej_cause=dict(rc), end=dict(end), flag_cause=st.get('flag_cause'),
            proof_level_check=summ.get('proof_level_check'), cache_hits=st.get('cache_hits'),
            cache_miss=st.get('cache_miss'), noncanon_attempts=st.get('noncanon_attempts', 0))
        j = out['jobs'][f'{m}_s{s}_{arm}']
        print(f"{m} {s} {arm} | {summ['solved_total']} | {summ['accepted']}/{att} | {st['sampled_tokens'] / 1e6:.2f} | "
              f"{st['prefill_tokens'] / 1e6:.1f} | {st['gpu_s']:.0f} {st['check_s']:.1f} {st['env_s']:.1f} "
              f"{st.get('lean_s', 0):.1f} {st['loop_wall_s']:.0f} | {j['peak_gb']:.1f} | "
              f"{100 * j['truncated_draws'] / draws:.3f} | {100 * j['step_cap'] / att:.3f} | {100 * j['max_rej'] / att:.1f} | "
              f"{j['redraws']} | {j['repeat_mean'] if j['repeat_mean'] is None else round(j['repeat_mean'], 3)} | {fin_rej}")

    for (m, s, arm), (rows, summ) in sorted(D.items()):
        if summ['batch'] != 2048:
            print(f'NOTE: {m} s{s} {arm} ran at batch {summ["batch"]} (OOM at 2,048): its tokens-matched and per-attempt '
                  f'values are comparable (a re-draw); its wall-matched values are not (smaller batch = more seconds).')
    # ---- step-level rejection rates (per draw), by kind and top causes
    print('\n## Rejections per draw (S = environment / structural, L = logical check, truncated) and logical failures '
          'let through (plain / structural: flagged accepted steps)')
    for (m, s, arm), (rows, summ) in sorted(D.items()):
        st = summ['stats']; rc = collections.Counter(st['rej_cause'])
        draws = sum(sum(r['draws']) for r in rows)
        S = sum(v for k, v in rc.items() if k.startswith('S:')); L = sum(v for k, v in rc.items() if k.startswith('L:'))
        fl = sum((st.get('flag_cause') or {}).values())
        top = ', '.join(f'{k} {v}' for k, v in rc.most_common(6))
        print(f'{m} s{s} {arm}: draws {draws}; S {S} ({100 * S / draws:.2f} %), L {L} ({100 * L / draws:.2f} %), '
              f'trunc {rc.get("truncated", 0)}; flagged-through {fl}; top: {top}')

    # ---- curves
    gnames = collections.OrderedDict()
    any_rows = next(iter(D.values()))[0]
    for r in any_rows:
        for g in groups_of(r):
            gnames.setdefault(g, 0); gnames[g] += 1
    print('\n## Groups (n theorems): ' + ', '.join(f'{g} {n}' for g, n in gnames.items()))
    per = {}
    for (m, s, arm), (rows, summ) in D.items():
        if (m, s, 'plain') not in D:
            continue
        rp, sp = D[(m, s, 'plain')]
        per[(m, s, arm)] = curves(rows, rp, summ, sp)
    gidx = {g: [i for i, r in enumerate(any_rows) if g in groups_of(r)] for g in gnames}
    kinds = ['tokens', 'wall', 'attempt', 'wall_by_draws']
    for (m, s, arm), C in sorted(per.items()):
        for g, ix in gidx.items():
            out['cells'][f'{m}|{s}|{arm}|{g}'] = {kd: C[ix, q, :].mean(0).tolist() for q, kd in enumerate(kinds)}

    # MDD: bootstrap over attempts within theorem, both arms resampled (seed 0 of each cap, long + all)
    print('\n## MDD (2.8 x bootstrap sd of the arm - plain difference; attempts resampled within theorem; 200 draws)')
    mdd = {}
    for m in MODELS:
        for arm in ('structural', 'logical'):
            if (m, 0, arm) not in D:
                continue
            ra, sa = D[(m, 0, arm)]; rp, sp = D[(m, 0, 'plain')]
            diffs = {g: [] for g in ('long', 'all', 'tb72') if g in gidx}
            for b in range(200):
                Ca = curves(ra, rp, sa, sp, boot_att=rng)
                Cp = curves(rp, rp, sp, sp, boot_att=rng)
                for g in diffs:
                    diffs[g].append(Ca[gidx[g], 0, :].mean(0) - Cp[gidx[g], 2, :].mean(0))
            for g, v in diffs.items():
                sd = np.std(np.array(v), 0)
                mdd[f'{m}|{arm}|{g}'] = (2.8 * sd).tolist()
                print(f'{m} {arm} {g}: MDD (pp) at k ' + ' '.join(f'{k}:{100 * 2.8 * x:.1f}' for k, x in zip(KS, sd)))
    out['mdd'] = mdd

    # differences vs plain, per seed and IQM [stratified bootstrap]
    show = ['long', 'Roy', 'Pelletier', 'batch3', 'bin:<=10', 'bin:11-20', 'bin:>20', 'tb72', 'release', 'all']
    for kd_i, kd in enumerate(kinds):
        print(f'\n## Solve rate, {kd}-matched (plain-equivalent k), and arm - plain in pp: per seed s0/s1/s2, '
              f'IQM [95 % stratified bootstrap]')
        for m in MODELS:
            for g in show:
                if g not in gidx:
                    continue
                ix = gidx[g]
                for k_show in (1, 4, 16, 64, 256):
                    q = KS.index(k_show)
                    seeds = sorted({s for (mm, s, aa) in per if mm == m and aa == 'plain'})
                    line = [f'{m} {g} (n {len(ix)}) k={k_show}:']
                    for arm in ARMS:
                        vals = [per[(m, s, arm)][ix, kd_i, q].mean() for s in seeds if (m, s, arm) in per]
                        line.append(f"{arm} {'/'.join(f'{100 * v:.1f}' for v in vals)}")
                    for arm in ('structural', 'logical'):
                        ss = [s for s in seeds if (m, s, arm) in per]
                        if not ss:
                            continue
                        dd = [100 * (per[(m, s, arm)][ix, kd_i, q].mean() - per[(m, s, 'plain')][ix, kd_i, q].mean()) for s in ss]
                        bs = []
                        for b in range(a.boot):
                            jx = [ix[rng.randrange(len(ix))] for _ in ix]
                            sb = [ss[rng.randrange(len(ss))] for _ in ss]
                            bs.append(iqm([100 * (per[(m, s, arm)][jx, kd_i, q].mean() - per[(m, s, 'plain')][jx, kd_i, q].mean()) for s in sb]))
                        lo, hi = np.percentile(bs, [2.5, 97.5])
                        out['diff'][f'{kd}|{m}|{g}|{k_show}|{arm}'] = dict(per_seed=dd, iqm=iqm(dd), ci=[lo, hi])
                        line.append(f"Δ{arm[0].upper()} {'/'.join(f'{d:+.1f}' for d in dd)} IQM {iqm(dd):+.1f} [{lo:+.1f}, {hi:+.1f}]")
                    print(' | '.join(line))

    # falsifier: guided-logical <= plain at every budget, on long, in >= 2/3 seeds at both caps (tokens-matched)
    print('\n## Falsifier check (tokens-matched, long): seeds where logical <= plain at every k')
    fals = {}
    for m in (MODELS if 'long' in gidx else []):
        ss = sorted({s for (mm, s, aa) in per if mm == m and aa == 'logical'})
        le = [s for s in ss if all(per[(m, s, 'logical')][gidx['long'], 0, q].mean() <= per[(m, s, 'plain')][gidx['long'], 0, q].mean() + 1e-12 for q in range(len(KS)))]
        fals[m] = dict(seeds=ss, le_every_k=le)
        print(f'{m}: seeds {ss}; logical <= plain at every k in {le}')
    out['falsifier'] = fals
    out['falsified'] = all(len(fals[m]['le_every_k']) >= 2 for m in fals) if fals else None
    print('falsified:', out['falsified'])
    os.makedirs(os.path.dirname(a.json) or '.', exist_ok=True)
    json.dump(out, open(a.json, 'w'), indent=0)


if __name__ == '__main__':
    main()
