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
    with open(f'{ROOT}/{a.out}', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 5) if isinstance(v, float) else v) for k, v in r.items()})
    print(f'{len(rows)} rows -> {a.out}')


if __name__ == '__main__':
    main()
