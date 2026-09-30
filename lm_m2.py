#!/usr/bin/env python3
"""lit-measures M2: initialisation seed vs data-order seed (preregistration/lit-measures.md §M2).

  python3 lm_m2.py            # reads artifacts/lit-measures/m2/{heldout,metrics}_i<I>_d<D>.*; writes summary.json, report.txt

Cells: init seed I (torch.manual_seed -> model init only; no dropout), data seed D (data order + name shifts) of the
noise-floor control recipe (train.py --impl fast, lean_seq, cap 6, 6,000 x 128, data/nf/train_p1.jsonl).
Read-outs per cell: held-out greedy overall (5,000), depth-3 slice (500, heldout `pat.depth3`, as nf_analysis.heldout),
final validation loss (`val2k` of the last metrics line).  Variance components: two-way crossed random-effects ANOVA
(I x D, one replicate: interaction is in the residual), shares clipped at 0; 95 % interval from a two-way bootstrap
(resample init levels and data levels independently, 2,000 draws, seed 0).  Stdlib only (runs on the VPS).
"""
import collections, json, math, os, random, statistics
D = 'artifacts/lit-measures/m2'
INITS = list(range(8)); DATAS = list(range(100, 108))
rd = lambda fn: [json.loads(l) for l in open(fn)]


def cell(i, d, rep=None):
    c = f'i{i}_d{d}' + (f'_{rep}' if rep else '')
    fh, fm = f'{D}/heldout_{c}.jsonl', f'{D}/metrics_{c}.jsonl'
    if not (os.path.exists(fh) and os.path.exists(f'{D}/heldout_{c}.json')):
        return None
    pat = LAB
    rows = rd(fh); d3 = [r['solved'] for r in rows if pat[r['name']].get('depth3')]
    m = [x for x in rd(fm) if x.get('kind', 'step') == 'step' and 'val2k' in x]
    return {'overall': sum(r['solved'] for r in rows) / len(rows), 'n': len(rows), 'depth3': sum(d3) / len(d3),
            'n_depth3': len(d3), 'val_loss': m[-1]['val2k'], 'val_step': m[-1]['step']}


def comps(Y):
    I, J = len(Y), len(Y[0]); g = sum(map(sum, Y)) / (I * J)
    r = [sum(row) / J - g for row in Y]; c = [sum(Y[i][j] for i in range(I)) / I - g for j in range(J)]
    msr = J * sum(x * x for x in r) / (I - 1); msc = I * sum(x * x for x in c) / (J - 1)
    mse = sum((Y[i][j] - g - r[i] - c[j]) ** 2 for i in range(I) for j in range(J)) / ((I - 1) * (J - 1))
    vi, vd = max((msr - mse) / J, 0.0), max((msc - mse) / I, 0.0); t = vi + vd + mse
    return {'init': vi / t, 'data': vd / t, 'resid': mse / t, 'var_init': vi, 'var_data': vd, 'var_resid': mse,
            'ms_init': msr, 'ms_data': msc, 'ms_resid': mse}


def boot(Y, B=2000, seed=0):
    R = random.Random(seed); I, J = len(Y), len(Y[0]); out = collections.defaultdict(list)
    for _ in range(B):
        a = [R.randrange(I) for _ in range(I)]; b = [R.randrange(J) for _ in range(J)]
        Z = [[Y[x][y] for y in b] for x in a]
        try:
            s = comps(Z)
        except ZeroDivisionError:
            continue
        for k in ('init', 'data', 'resid'):
            out[k].append(s[k])
    q = lambda v, p: sorted(v)[min(len(v) - 1, int(p * len(v)))]
    return {k: [q(v, 0.025), q(v, 0.975)] for k, v in out.items()}


def perm_mode(H, n=100000, seed=0):
    """Is the high-mode indicator concentrated by rows (init) or by columns (data)?  Statistic: sum over rows of
    (row count - mean)^2 (resp. columns); null: all 64 labels shuffled."""
    R = random.Random(seed); flat = [x for row in H for x in row]; I, J = len(H), len(H[0])
    def st(M):
        rs = [sum(r) for r in M]; cs = [sum(M[i][j] for i in range(I)) for j in range(J)]
        mr, mc = sum(rs) / I, sum(cs) / J
        return sum((x - mr) ** 2 for x in rs), sum((x - mc) ** 2 for x in cs)
    o = st(H); ge = [0, 0]
    for _ in range(n):
        R.shuffle(flat); M = [flat[i * J:(i + 1) * J] for i in range(I)]; s = st(M)
        ge[0] += s[0] >= o[0] - 1e-12; ge[1] += s[1] >= o[1] - 1e-12
    return {'stat_rows': o[0], 'stat_cols': o[1], 'p_rows': (ge[0] + 1) / (n + 1), 'p_cols': (ge[1] + 1) / (n + 1)}


LAB = {r['name']: r['pat'] for r in rd('data/p2/heldout.jsonl')}
if __name__ == '__main__':
    cells = {(i, d): cell(i, d) for i in INITS for d in DATAS}
    have = {k: v for k, v in cells.items() if v}
    res = {'model': 'Stage-1 3.2 M-param (checked per cell) lean_seq GPT, from scratch, cap 6, train.py --impl fast 6,000 x 128 '
                    'on data/nf/train_p1.jsonl (noise-floor control recipe); init seeds 0-7 x data seeds 100-107',
           'n_cells': len(have), 'cells': {f'i{i}_d{d}': v for (i, d), v in sorted(have.items())}, 'quantities': {}}
    lines = [res['model'], f'cells {len(have)} / 64', '']
    if len(have) == 64:
        for q in ('depth3', 'overall', 'val_loss'):
            Y = [[cells[(i, d)][q] for d in DATAS] for i in INITS]
            c = comps(Y); ci = boot(Y); flat = [x for r in Y for x in r]
            res['quantities'][q] = {'components': c, 'ci95': ci, 'mean': statistics.mean(flat), 'sd': statistics.stdev(flat),
                                    'min': min(flat), 'max': max(flat)}
            lines.append(f"{q:9s} mean {statistics.mean(flat):.4f} sd {statistics.stdev(flat):.4f} range [{min(flat):.4f}, {max(flat):.4f}] | "
                         + ' '.join(f"{k} {c[k]:.2f} [{ci[k][0]:.2f}, {ci[k][1]:.2f}]" for k in ('init', 'data', 'resid')))
        H = [[int(cells[(i, d)]['depth3'] >= 0.5) for d in DATAS] for i in INITS]
        pm = perm_mode(H); res['high_mode'] = {'H': H, 'row_counts': [sum(r) for r in H],
                                              'col_counts': [sum(H[i][j] for i in range(8)) for j in range(8)], **pm}
        lines += ['', f"high mode (depth-3 >= 0.5): {sum(map(sum, H))} / 64; per init row {res['high_mode']['row_counts']}; "
                      f"per data column {res['high_mode']['col_counts']}; perm p rows {pm['p_rows']:.4f} cols {pm['p_cols']:.4f}"]
    lines += ['', 'depth-3 slice per cell (rows init 0-7, columns data 100-107):']
    for i in INITS:
        lines.append(f'  i{i} ' + ' '.join(f"{cells[(i, d)]['depth3']:.3f}" if cells[(i, d)] else '  -  ' for d in DATAS))
    json.dump(res, open(f'{D}/summary.json', 'w'), indent=1)
    open(f'{D}/report.txt', 'w').write('\n'.join(lines) + '\n'); print('\n'.join(lines))
