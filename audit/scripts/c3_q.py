#!/usr/bin/env python3
"""C3: long-pool read-outs re-derived from per-theorem re-read rows (state-cap12, long-pool pass 1/2, long-pool-2).

solved := n_ok > 0 and >= 1 stored proof (checked against the row's 'solved' flag).
Q = rr600 generator theorems at L_true 13-16 (/380).  ge17 = transfer_long_ge17 (/70).
long2: new21 + calib70 = 91; exact-17 (L_true == 17, n 61) vs >= 18 (L_lb == 18, n 30).

Outputs (stdout tables + audit/out/c3_reads.tsv, c3_pairs.tsv):
  1. every read: ckpt, pool, k, T, seed, batch, max_steps/max_action/max_new, Q / rr600 / textbook-in-rr600 / ge17 / long2 strata
  2. the 2x2 (state vs whole-proof x cap6 vs cap12) at T1 per seed, main effects and interaction (raw and logit), Welch
  3. same-checkpoint double reads (long-pool pass1 vs pass2, ms48 vs ms96, sc12 ge17 vs lp2 calib) vs binomial redraw sd
  4. Q re-binned by the pool's Lean label_term_size instead of L_true
  5. long-pool-2 exact-17 vs >=18 per seed and power
"""
import glob, hashlib, json, math, os, re, random, collections
import numpy as np
from scipy import stats

H = os.path.expanduser('~')
AUD = f'{H}/work/claim-audit/audit'
R = f'{AUD}/raw'
D = f'{H}/work/best-state/data/ladder'
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()[:10]

rr = {r['name']: r for r in map(json.loads, open(f'{D}/transfer_long_rr600.jsonl'))}
QSET = {n for n, r in rr.items() if r['source'] == 'gen' and 13 <= r['L_true'] <= 16}
TBSET = {n for n, r in rr.items() if r['source'] == 'textbook'}
ge17 = {r['name'] for r in map(json.loads, open(f'{D}/transfer_long_ge17.jsonl'))}
l2 = {}
for f in ('transfer_long2.jsonl', 'transfer_long2_calib.jsonl'):
    for r in map(json.loads, open(f'{D}/{f}')):
        l2[r['name']] = r
EX17 = {n for n, r in l2.items() if r.get('L_true') == 17}
GE18 = {n for n, r in l2.items() if r.get('L_lb') == 18}
assert len(QSET) == 380 and len(EX17) == 61 and len(GE18) == 30, (len(QSET), len(EX17), len(GE18))


def load(p):
    s, nok, mm = {}, {}, 0
    for l in open(p):
        r = json.loads(l)
        v = r.get('n_ok', 0) > 0 and len(r.get('proofs') or []) > 0
        mm += bool(r.get('solved')) != v
        s[r['name']] = v
        nok[r['name']] = (r.get('n_ok', 0), r.get('n_tried', 0))
    return s, nok, mm


def label(p):
    b = os.path.basename(p)[:-6]
    run = 'sc12' if '/state-cap12/' in p else ('lp2' if '/long-pool-2/' in p else ('lp_rr2' if '/rr2/' in p else 'lp_rr1'))
    return run, b


def main():
    files = sorted(glob.glob(f'{R}/state-cap12/artifacts/sc12/rr/*.jsonl') + glob.glob(f'{R}/long-pool/artifacts/lpool/rr*/*.jsonl')
                   + glob.glob(f'{R}/long-pool-2/artifacts/lpool2/rr/*.jsonl'))
    reads = {}
    out = []
    for p in files:
        js = p[:-6] + '.json'
        meta = json.load(open(js)) if os.path.exists(js) else {}
        s, nok, mm = load(p)
        names = set(s)
        run, b = label(p)
        pool = 'rr600' if QSET <= names else ('ge17' if names == ge17 else ('long2' if names <= set(l2) else '?'))
        sol = {n for n, v in s.items() if v}
        row = dict(run=run, read=b, pool=pool, n=len(s), solved=len(sol), Q=len(sol & QSET) if pool == 'rr600' else '',
                   tb_in_rr600=len(sol & TBSET) if pool == 'rr600' else '', ex17=len(sol & EX17) if pool == 'long2' else '',
                   ge18=len(sol & GE18) if pool == 'long2' else '', k=meta.get('k'), T=meta.get('temperature'), seed=meta.get('seed'),
                   batch=meta.get('batch'), max_steps=meta.get('max_steps'), max_action=meta.get('max_action'),
                   max_new=meta.get('max_new', ''), mode=meta.get('state_mode') or meta.get('tok_mode'), flag_mm=mm,
                   ckpt=meta.get('ckpt', ''), md5=md5(p))
        out.append(row)
        reads[(run, b)] = (s, nok)
    cols = list(out[0])
    with open(f'{AUD}/out/c3_reads.tsv', 'w') as f:
        f.write('\t'.join(cols) + '\n')
        for r in out:
            f.write('\t'.join(str(r[c]) for c in cols) + '\n')
    print('run\tread\tpool\tn\tsolved\tQ\ttb\tex17\tge18\tk\tT\tbatch\tms\tma\tmax_new\tmm')
    for r in out:
        print('\t'.join(str(r[c]) for c in ('run', 'read', 'pool', 'n', 'solved', 'Q', 'tb_in_rr600', 'ex17', 'ge18', 'k', 'T',
                                             'batch', 'max_steps', 'max_action', 'max_new', 'flag_mm')))
    print('flag mismatches total', sum(r['flag_mm'] for r in out))

    # ---- 2x2 at T1 (the reads state-cap12 used: sc12 for new arms, long-pool pass 2 for inherited)
    def q(run, b):
        s, _ = reads[(run, b)]
        return sum(s[n] for n in QSET)
    cells = {
        'state_cap12 (SN-cap12 T1)': [q('sc12', f'T1_SN12_s{i}__rr600') for i in range(4)],
        'wp_cap12 (K12 T1)': [q('sc12', f'T1_K12_s{i}__rr600') for i in range(2)],
        'state_cap6 (SN-v2 T1)': [q('lp_rr2', f'state-env__la_T1_SN_s{i}_r8') for i in range(2)],
        'wp_cap6 (C0 T1)': [q('lp_rr2', f'ds-generator__la_T1_c0_s{i}_r8') for i in range(2)],
    }
    print('\n2x2 at T1, Q per seed:', cells)
    m = {k: np.mean(v) for k, v in cells.items()}
    v = {k: np.var(v, ddof=1) / len(v) for k, v in cells.items()}
    ks = list(cells)
    I = (m[ks[0]] - m[ks[1]]) - (m[ks[2]] - m[ks[3]])
    se = math.sqrt(sum(v.values()))
    dfw = sum(v.values()) ** 2 / sum(v[k] ** 2 / (len(cells[k]) - 1) for k in ks)
    print(f'means {m}')
    print(f'state effect at cap12 {m[ks[0]] - m[ks[1]]:.1f}, at cap6 {m[ks[2]] - m[ks[3]]:.1f}; cap effect for state '
          f'{m[ks[0]] - m[ks[2]]:.1f}, for wp {m[ks[1]] - m[ks[3]]:.1f}')
    print(f'interaction (raw Q) = {I:.1f}, se {se:.1f}, Welch df {dfw:.1f}, t {I / se:.2f}, p {2 * stats.t.sf(abs(I / se), dfw):.3f}')
    lg = lambda x: math.log((x + 0.5) / (380 - x + 0.5))
    lc = {k: [lg(x) for x in vv] for k, vv in cells.items()}
    lm = {k: np.mean(x) for k, x in lc.items()}
    lv = {k: np.var(x, ddof=1) / len(x) for k, x in lc.items()}
    Il = (lm[ks[0]] - lm[ks[1]]) - (lm[ks[2]] - lm[ks[3]])
    sel = math.sqrt(sum(lv.values()))
    dfl = sum(lv.values()) ** 2 / sum(lv[k] ** 2 / (len(lc[k]) - 1) for k in ks)
    print(f'interaction (logit Q/380) = {Il:.2f}, se {sel:.2f}, df {dfl:.1f}, t {Il / sel:.2f}, p {2 * stats.t.sf(abs(Il / sel), dfl):.3f}')
    print('logit cell means', {k: round(x, 2) for k, x in lm.items()})

    # ---- same-checkpoint double reads
    def pair(a, b, keys=None):
        sa, na = reads[a]
        sb, nb = reads[b]
        ks_ = sorted((keys or set(sa)) & set(sa) & set(sb))
        ca, cb = sum(sa[k] for k in ks_), sum(sb[k] for k in ks_)
        var = 0
        for k in ks_:
            ok = na[k][0] + nb[k][0]
            n = na[k][1] + nb[k][1]
            qq = ok / n if n else 0
            pp = 1 - (1 - qq) ** max(na[k][1], 1)
            var += pp * (1 - pp)
        sd = math.sqrt(2 * var)
        fl = sum(sa[k] != sb[k] for k in ks_)
        return (a[0] + ':' + a[1], b[0] + ':' + b[1], len(ks_), ca, cb, ca - cb, fl, round(sd, 2), round((ca - cb) / sd, 2) if sd else 0)
    pairs = []
    for b in [k[1] for k in reads if k[0] == 'lp_rr1']:
        if ('lp_rr2', b) in reads:
            pairs.append(pair(('lp_rr1', b), ('lp_rr2', b)))
    for i in range(2):
        for pl in ('rr600', 'ge17'):
            for arm in ('T1_SN12', 'stage1_SN12'):
                a, b = ('sc12', f'{arm}_s{i}__{pl}'), ('sc12', f'{arm}_s{i}__{pl}_ms96')
                if a in reads and b in reads:
                    pairs.append(pair(a, b))
    for i in (2, 3):
        for pl in ('rr600', 'ge17'):
            a, b = ('sc12', f'T1_SN12_s{i}__{pl}'), ('lp2', f'T1_SN12_s{i}_ms96__{pl}')
            if a in reads and b in reads:
                pairs.append(pair(a, b))
    for arm, n in (('T1_SN12', 4), ('stage1_SN12', 4), ('T1_K12', 2)):
        for i in range(n):
            a, b = ('sc12', f'{arm}_s{i}__ge17'), ('lp2', f'{arm}_s{i}__cal')
            if a in reads and b in reads:
                pairs.append(pair(a, b))
    print('\nsame-checkpoint double reads: a, b, n, solved_a, solved_b, diff, flips, redraw_sd, z')
    for p_ in pairs:
        print('\t'.join(map(str, p_)))
    with open(f'{AUD}/out/c3_pairs.tsv', 'w') as f:
        f.write('a\tb\tn\tsolved_a\tsolved_b\tdiff\tflips\tredraw_sd\tz\n')
        for p_ in pairs:
            f.write('\t'.join(map(str, p_)) + '\n')
    # Q-only for rr600 pairs
    print('Q-subset diffs for rr600 pairs:')
    for p_ in pairs:
        if 'rr600' in p_[0] or ('lp_rr' in p_[0] and '__ge17' not in p_[0]):
            a = tuple(p_[0].split(':', 1)); b = tuple(p_[1].split(':', 1))
            print('  ', pair(a, b, QSET))

    # ---- Q by Lean label_term_size instead of L_true
    ts = {n: rr[n].get('label_term_size') for n in QSET}
    vals = np.array([ts[n] for n in QSET if ts[n] is not None])
    print(f'\nlabel_term_size over Q: n {len(vals)}, quartiles {np.percentile(vals, [25, 50, 75])}')
    lt = [rr[n]['L_true'] for n in QSET if ts[n] is not None]
    print(f'Spearman(L_true, label_term_size) on Q = {stats.spearmanr(lt, vals).correlation:.3f}')
    allrr = [n for n in rr if rr[n]['source'] == 'gen' and rr[n].get('label_term_size') is not None]
    print(f'Spearman on all rr600 gen (L 11-16) = {stats.spearmanr([rr[n]["L_true"] for n in allrr], [rr[n]["label_term_size"] for n in allrr]).correlation:.3f}')
    qs = np.percentile(vals, [25, 50, 75])
    qbin = lambda x: int(np.searchsorted(qs, x, side='right'))
    bins = collections.defaultdict(list)
    for n in QSET:
        if ts[n] is not None:
            bins[qbin(ts[n])].append(n)
    print('term-size quartile bins (n):', {k: len(v) for k, v in sorted(bins.items())})
    print('arm\t' + '\t'.join(f'TSq{k}' for k in sorted(bins)) + '\t| by L_true 13/14/15/16')
    arms = [('SN-cap12 T1', [('sc12', f'T1_SN12_s{i}__rr600') for i in range(4)]),
            ('SN-cap12 Fz', [('sc12', f'stage1_SN12_s{i}__rr600') for i in range(4)]),
            ('K12 T1', [('sc12', f'T1_K12_s{i}__rr600') for i in range(2)]),
            ('SN-v2 c6 T1', [('lp_rr2', f'state-env__la_T1_SN_s{i}_r8') for i in range(2)]),
            ('C0 T1', [('lp_rr2', f'ds-generator__la_T1_c0_s{i}_r8') for i in range(2)])]
    for nm, rs in arms:
        cells_ = []
        for k in sorted(bins):
            cells_.append(np.mean([np.mean([reads[r][0][n] for n in bins[k]]) for r in rs]))
        byl = [np.mean([np.mean([reads[r][0][n] for n in QSET if rr[n]['L_true'] == L]) for r in rs]) for L in (13, 14, 15, 16)]
        print(nm + '\t' + '\t'.join(f'{c:.2f}' for c in cells_) + '\t| ' + ' '.join(f'{c:.2f}' for c in byl))

    # ---- long-pool-2 strata
    print('\nlong-pool-2: exact17 (61) / ge18 (30) per seed (new + cal reads)')
    for arm, n in (('T1_SN12', 4), ('stage1_SN12', 4), ('T1_K12', 2), ('T1_SNv2', 2)):
        res = []
        for i in range(n):
            s = {}
            for part in ('new', 'cal'):
                if ('lp2', f'{arm}_s{i}__{part}') in reads:
                    s.update(reads[('lp2', f'{arm}_s{i}__{part}')][0])
            res.append((sum(s.get(x, False) for x in EX17), sum(s.get(x, False) for x in GE18), sum(s.values())))
        print(arm, res)
        if arm == 'T1_SN12':
            d = [a / 61 - b / 30 for a, b, _ in res]
            print(f'  exact17 - ge18 per seed (pp): {[round(100 * x, 1) for x in d]}, mean {100 * np.mean(d):.1f}')
            # theorem-level: per-theorem solve fraction over 4 seeds; bootstrap theorems within strata
            frac = {}
            for x in EX17 | GE18:
                frac[x] = np.mean([any(reads[('lp2', f'{arm}_s{i}__{pt}')][0].get(x, False) for pt in ('new', 'cal')
                                       if ('lp2', f'{arm}_s{i}__{pt}') in reads) for i in range(n)])
            a = np.array([frac[x] for x in EX17]); b = np.array([frac[x] for x in GE18])
            rng = np.random.default_rng(0)
            bs = [rng.choice(a, len(a)).mean() - rng.choice(b, len(b)).mean() for _ in range(20000)]
            print(f'  theorem-level diff {100 * (a.mean() - b.mean()):.1f} pp, bootstrap 95% [{100 * np.percentile(bs, 2.5):.1f}, {100 * np.percentile(bs, 97.5):.1f}]')
            sd_t = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
            print(f'  se {100 * sd_t:.1f} pp -> MDD (80% power, a .05 2-sided, normal) {100 * 2.80 * sd_t:.1f} pp')
            # power to detect a drop of 20 / 30 pp at these n with theorem-level sd
            for drop in (0.1, 0.2, 0.3):
                pw = stats.norm.sf(1.96 - drop / sd_t)
                print(f'  power to detect a {int(drop * 100)} pp drop: {pw:.2f}')


if __name__ == '__main__':
    main()
