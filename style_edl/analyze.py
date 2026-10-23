#!/usr/bin/env python3
"""Run `style-edl` numbers from the stored per-block losses (every EDL is recomputed here from edl_run.py's outputs).

  python3 style_edl/analyze.py [--edl artifacts/style_edl/edl] [--cap artifacts/style_edl/cap] [--out style_edl/results.csv]

Definitions (preregistration/style-edl.md):
  preq      = sum of block bits (blocks [0,8) ... [64,128); the first coded by the learner) + log2(#lrs) for the lr choice
  L_test    = theta*'s mean bits per proof on the 128 test proofs of the stream
  EDL       = preq - 128 * L_test                                         (the brief's)
  EDL_c     = 128 * (L0_test - L_test) - sum_blocks (learner bits - block bits) + log2(#lrs)  (= EDL - M; M = sum of the
              learner's bits on the stream - 128 * its mean bits on the test proofs: the split's mismatch, no training)
  the lr is chosen per (seed, stream, algo[, E]) by the mean over orders of preq; values are means over orders.
"""
import argparse, collections, csv, glob, gzip, json, math, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STREAMS = ('S_own', 'S_own2', 'S_seed', 'S_short', 'S_RL', 'S_Kal')


def run_stats(res, run, key='bits', nlr=3):
    """one (lr, E, order) run -> dict of the defined quantities (key 'bits' = names not coded, 'bits_all' = all)."""
    pen = math.log2(nlr) if nlr > 1 else 0.0
    n = res['n_stream']
    base_s = res['base']['stream'][key]
    base_t = res['base']['test'][key]
    perm = run['perm']
    blocks = run['blocks']
    preq = sum(sum(b['block'][key]) for b in blocks) + pen
    L_test = sum(run['theta']['test'][key]) / len(run['theta']['test'][key])
    L0_test = sum(base_t) / len(base_t)
    saved = sum(sum(base_s[perm[i]] for i in range(b['lo'], b['hi'])) - sum(b['block'][key]) for b in blocks)
    acts = sum(res['stream_acts'])
    edl = preq - n * L_test
    edl_c = n * (L0_test - L_test) - saved + pen
    first = blocks[0]
    return {'preq': preq, 'L_test': L_test, 'L0_test': L0_test, 'L0_stream': sum(base_s) / n,
            'EDL': edl, 'EDL_pp': edl / n, 'EDL_pa': edl / acts, 'EDL_c': edl_c, 'EDL_c_pp': edl_c / n,
            'EDL_c_pa': edl_c / acts, 'M': edl - edl_c,
            'start_pp': sum(first['block'][key]) / (first['hi'] - first['lo']),
            'block_pp': [sum(b['block'][key]) / (b['hi'] - b['lo']) for b in blocks],
            'curve_test': [b['test_mean_bits' if key == 'bits' else 'test_mean_bits_all'] for b in blocks] + [L_test],
            'pstar': [b['fit'].get('passes') for b in blocks] + [run['theta']['fit'].get('passes')]}


def lv_stats(res, run, nlr=3):
    """the same quantities with l_V in place of the single-string code (runs from --vset)."""
    pen = math.log2(nlr) if nlr > 1 else 0.0
    n = res['n_stream']
    lv0s, lv0t = res['base']['lv_stream'], res['base']['lv_test']
    perm = run['perm']; names = res['stream_names']
    preq = sum(sum(b['lv_block'].values()) for b in run['blocks']) + pen
    L_test = sum(run['theta']['lv_test'].values()) / len(run['theta']['lv_test'])
    L0_test = sum(lv0t.values()) / len(lv0t)
    saved = sum(sum(lv0s[names[perm[i]]] for i in range(b['lo'], b['hi'])) - sum(b['lv_block'].values())
                for b in run['blocks'])
    return {'lv_preq': preq, 'lv_L_test': L_test, 'lv_L0_test': L0_test, 'lv_EDL_pp': (preq - n * L_test) / n,
            'lv_EDL_c_pp': (n * (L0_test - L_test) - saved + pen) / n,
            'lv_start_pp': sum(run['blocks'][0]['lv_block'].values()) / (run['blocks'][0]['hi'] - run['blocks'][0]['lo'])}


def attribution(res, run, same_stream, same_test, key='bits'):
    """Addendum 1, A1: EDL_c split by whether a proof is identical to the learner's greedy proof ('same') or not.
    same_stream / same_test: bools in file order.  -> {class: {n_stream, n_test, L0_stream, L0_test, Lth_test,
    saved, EDL_c, EDL_c_per_proof}}"""
    base_s, base_t = res['base']['stream'][key], res['base']['test'][key]
    th_t = run['theta']['test'][key]
    perm = run['perm']
    blk = {}
    for b in run['blocks']:
        for j, i in enumerate(range(b['lo'], b['hi'])):
            blk[perm[i]] = b['block'][key][j]
    out = {}
    for cls, want in (('same', True), ('differ', False)):
        si = [i for i in range(len(base_s)) if same_stream[i] == want]
        ti = [i for i in range(len(base_t)) if same_test[i] == want]
        if not si or not ti:
            out[cls] = {'n_stream': len(si), 'n_test': len(ti)}
            continue
        L0t = sum(base_t[i] for i in ti) / len(ti)
        Lt = sum(th_t[i] for i in ti) / len(ti)
        saved = sum(base_s[i] - blk[i] for i in si)
        e = len(si) * (L0t - Lt) - saved
        out[cls] = {'n_stream': len(si), 'n_test': len(ti), 'L0_stream': sum(base_s[i] for i in si) / len(si),
                    'L0_test': L0t, 'Lth_test': Lt, 'saved': saved, 'EDL_c': e, 'EDL_c_per_proof': e / len(si)}
    return out


def select(res, algo, E=None, key='bits'):
    """-> (chosen lr, per-order stats at that lr, {lr: mean preq})"""
    runs = [r for r in res['runs'] if r.get('algo', 'fixed') == algo and (E is None or r['E'] == E)]
    lrs = sorted({r['lr'] for r in runs})
    by = collections.defaultdict(list)
    for r in runs:
        by[r['lr']].append(r)
    mean_preq = {lr: sum(run_stats(res, r, key, len(lrs))['preq'] for r in by[lr]) / len(by[lr]) for lr in lrs}
    lr = min(lrs, key=lambda x: (mean_preq[x], x))
    return lr, [run_stats(res, r, key, len(lrs)) for r in sorted(by[lr], key=lambda r: r['order'])], mean_preq, by[lr]


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def summarize(fn, algo='es', E=None):
    res = json.load(open(fn))
    lr, sts, mp, runs = select(res, algo, E)
    _, sts_all, _, _ = select(res, algo, E, key='bits_all')
    out = {'lr': lr, 'mean_preq_by_lr': mp, 'orders': [r['order'] for r in runs]}
    for k in ('preq', 'L_test', 'L0_test', 'L0_stream', 'EDL_pp', 'EDL_pa', 'EDL_c_pp', 'EDL_c_pa', 'M', 'start_pp'):
        out[k] = mean([s[k] for s in sts])
        out[k + '_by_order'] = [s[k] for s in sts]
    for k in ('EDL_pp', 'EDL_c_pp', 'L_test', 'start_pp', 'L0_test'):
        out['all_' + k] = mean([s[k] for s in sts_all])
    out['block_pp'] = [mean(v) for v in zip(*[s['block_pp'] for s in sts])]
    out['curve_test'] = [mean(v) for v in zip(*[s['curve_test'] for s in sts])]
    out['pstar'] = [s['pstar'] for s in sts]
    acts_s, acts_t = res['stream_acts'], res['test_acts']
    out['acts_pp'] = (sum(acts_s) + sum(acts_t)) / (len(acts_s) + len(acts_t))
    out['tok_pp'] = (sum(res['stream_tok']) + sum(res['test_tok'])) / (len(acts_s) + len(acts_t))
    out['tok_all_pp'] = mean(res['stream_tok_all'])
    ag = sum(res['base']['stream_agree']) + sum(res['base']['test_agree'])
    out['tf_agree'] = ag / (sum(acts_s) + sum(acts_t))
    if all('lv_block' in b for r in runs for b in r['blocks']):
        lvs = [lv_stats(res, r, len(mp)) for r in sorted(runs, key=lambda r: r['order'])]
        for k in lvs[0]:
            out[k] = mean([s[k] for s in lvs])
    out['secs'] = res.get('secs')
    return out


def cap_stats(fn, names):
    """plain / guided read rows -> (pass@32, pass@1) on the given theorem names."""
    ok = {}
    for l in gzip.open(fn, 'rt'):
        r = json.loads(l)
        if r['name'] in names:
            ok[r['name']] = r['ok']
    assert len(ok) == len(names), (fn, len(ok), len(names))
    p32 = sum(any(v) for v in ok.values()) / len(ok)
    p1 = sum(sum(v) / len(v) for v in ok.values()) / len(ok)
    return p32, p1


def same_masks(s, S):
    """per stream / test proof (file order): identical (canonical action sequence) to learner s's greedy proof."""
    sys.path.insert(0, os.path.join(ROOT, 'style_edl'))
    import common as C
    out = []
    for part in ('stream', 'test'):
        a = [json.loads(l) for l in open(f'{ROOT}/data/style_edl/streams/s{s}/{S}.{part}.jsonl')]
        b = [json.loads(l) for l in open(f'{ROOT}/data/style_edl/streams/s{s}/S_own.{part}.jsonl')]
        assert [r['name'] for r in a] == [r['name'] for r in b]
        out.append([C.canon_key(x['prompt'], x['nd']) == C.canon_key(y['prompt'], y['nd']) for x, y in zip(a, b)])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--edl', default='artifacts/style_edl/edl')
    ap.add_argument('--cap', default='artifacts/style_edl/cap')
    ap.add_argument('--fixed_E', type=float, default=None, help="A_fixed's E (chosen on the S_own pilot)")
    ap.add_argument('--out', default='style_edl/results.csv')
    a = ap.parse_args()
    man = json.load(open(f'{ROOT}/style_edl/streams_manifest.json'))
    test = set(man['theorems']['test'])
    rows = []
    for s in (0, 1, 2):
        for S in STREAMS:
            fn = f'{ROOT}/{a.edl}/s{s}/{S}.json'
            if not os.path.exists(fn):
                continue
            o = summarize(fn)
            row = {'seed': s, 'stream': S, **{k: v for k, v in o.items() if not isinstance(v, (list, dict))}}
            row['EDL_c_pp_o0'], row['EDL_c_pp_o1'] = (o['EDL_c_pp_by_order'] + [None, None])[:2]
            row['blocks_pp'] = ' '.join(f'{x:.4g}' for x in o['block_pp'])
            row['curve_test'] = ' '.join(f'{x:.4g}' for x in o['curve_test'])
            fx = f'{ROOT}/{a.edl}_x/s{s}/{S}.json'
            if os.path.exists(fx) and os.path.exists(f'{ROOT}/artifacts/style_edl/logs/xfit_s{s}_{S}.done'):
                ox = summarize(fx)
                row.update({'x_lr': ox['lr'], 'x_EDL_pp': ox['EDL_pp'], 'x_EDL_c_pp': ox['EDL_c_pp'],
                            'xfit_EDL_pp': (o['EDL_pp'] + ox['EDL_pp']) / 2, 'xfit_EDL_c_pp': (o['EDL_c_pp'] + ox['EDL_c_pp']) / 2})
            fl = f'{ROOT}/artifacts/style_edl/lv/s{s}/{S}.json'
            if os.path.exists(fl) and os.path.exists(f'{ROOT}/artifacts/style_edl/logs/lv_s{s}_{S}.done'):
                rl = json.load(open(fl))
                lruns = sorted(rl['runs'], key=lambda r: r['order'])
                lvs = [lv_stats(rl, r, 3) for r in lruns]
                sss = [run_stats(rl, r, 'bits', 3) for r in lruns]
                for k in lvs[0]:
                    row[k] = mean([x[k] for x in lvs])
                row['lv_ss_EDL_c_pp'] = mean([x['EDL_c_pp'] for x in sss])
                row['lv_ss_EDL_pp'] = mean([x['EDL_pp'] for x in sss])
                ph4 = {(r['order']): r for r in json.load(open(fn))['runs'] if r.get('algo') == 'es' and r['lr'] == rl['runs'][0]['lr']}
                row['lv_refit_max_abs_dbits'] = max(abs(a - b) for r in lruns for b4, bl in zip(ph4[r['order']]['blocks'], r['blocks'])
                                                    for a, b in zip(b4['block']['bits'], bl['block']['bits']))
            # A1 attribution at the chosen lr, mean over orders
            res = json.load(open(fn))
            ss, stt = same_masks(s, S)
            row['n_differ_stream'], row['n_differ_test'] = ss.count(False), stt.count(False)
            runs = [r for r in res['runs'] if r.get('algo') == 'es' and r['lr'] == o['lr']]
            at = [attribution(res, r, ss, stt) for r in runs]
            for cls in ('same', 'differ'):
                for k in ('L0_stream', 'L0_test', 'Lth_test', 'EDL_c', 'EDL_c_per_proof'):
                    v = [x[cls].get(k) for x in at]
                    row[f'{cls}_{k}'] = mean(v) if all(x is not None for x in v) else None
            if os.path.exists(fx) and os.path.exists(f'{ROOT}/artifacts/style_edl/logs/xfit_s{s}_{S}.done'):
                rx = json.load(open(fx))                      # cross-fit: stream and test halves swapped
                runs_x = [r for r in rx['runs'] if r.get('algo') == 'es' and r['lr'] == ox['lr']]
                atx = [attribution(rx, r, stt, ss) for r in runs_x]
                for cls in ('same', 'differ'):
                    ea = [x[cls].get('EDL_c') for x in at]; eb = [x[cls].get('EDL_c') for x in atx]
                    na, nb = at[0][cls]['n_stream'], atx[0][cls]['n_stream']
                    if na + nb and all(v is not None for v in ea + eb):
                        row[f'xfit_{cls}_EDL_c_per_proof'] = (mean(ea) + mean(eb)) / (na + nb)
            if row.get('same_EDL_c') is not None and row.get('differ_EDL_c') is not None:
                row['strat_EDL_c_pp'] = (row['same_EDL_c'] + row['differ_EDL_c'] + math.log2(3)) / res['n_stream']
            ff = f'{ROOT}/{a.edl}/s{s}/{S}.fixed.json'
            if os.path.exists(ff) and a.fixed_E is not None:
                of = summarize(ff, 'fixed', a.fixed_E)
                row.update({'fixed_lr': of['lr'], 'fixed_EDL_pp': of['EDL_pp'], 'fixed_EDL_c_pp': of['EDL_c_pp'],
                            'fixed_L_test': of['L_test']})
            for arm in ('plain', 'logical'):
                b = f'{ROOT}/{a.cap}/base_s{s}__{arm}_k32_seed2.rows.jsonl.gz'
                t = f'{ROOT}/{a.cap}/s{s}_{S}__{arm}_k32_seed2.rows.jsonl.gz'
                if os.path.exists(b):
                    row[f'{arm}_pass32_before'], row[f'{arm}_pass1_before'] = cap_stats(b, test)
                if os.path.exists(t):
                    row[f'{arm}_pass32_after'], row[f'{arm}_pass1_after'] = cap_stats(t, test)
            rows.append(row)
    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with open(a.out if os.path.isabs(a.out) else f'{ROOT}/{a.out}', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 5) if isinstance(v, float) else v) for k, v in r.items()})
    print(f'{len(rows)} rows -> {a.out}')


if __name__ == '__main__':
    main()
