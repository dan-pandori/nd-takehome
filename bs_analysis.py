#!/usr/bin/env python3
"""best-state numbers from pulled files (run `best-state`).  Lean alone decides: a problem is solved by a checkpoint iff
>= 1 of its samples was accepted by the judge inside `state_eval.py` / `lpool_reread.py` (lean_judge, state env).

Sources:
  new checkpoints        artifacts/bs/eval/{Fz,T1}_best{6,12}_s{0,1,2}__{tb72,dev,h250,rr600,long2,held}.{json,jsonl}
  inherited, read here   artifacts/bs/eval/{Fz,T1}_SN{6,12}_s*__{dev,h250,long2}.json
  inherited, on file     textbook72: `git show origin/dan_textbook72:artifacts/textbook72/summary.json` (per_ckpt);
                         rr600 Q / long2 / held-out greedy: the state-cap12, long-pool-2 and state-env summaries
                         (constants below, each with its source).

  python3 bs_analysis.py [--lean_workers 2] --out artifacts/bs/summary.json > artifacts/bs/analysis_stdout.txt
"""
import argparse, json, math, os, random, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

E = 'artifacts/bs/eval'
NEW = {'best-cap6': [f'best6_s{s}' for s in range(3)], 'best-cap12': [f'best12_s{s}' for s in range(3)]}
INH = {'ours-cap6': [f'SN6_s{s}' for s in range(2)], 'ours-cap12': [f'SN12_s{s}' for s in range(4)]}
CELLS = ['ours-cap6', 'best-cap6', 'ours-cap12', 'best-cap12']
MEMBERS = {**NEW, **INH}
BINS = [('1-5', 1, 5), ('6-10', 6, 10), ('11-15', 11, 15), ('16+', 16, 999)]
# Inherited numbers not re-read here (source in the comment).  Q = rr600 generator theorems at L_true 13-16 (/380).
INH_Q = {  # state-cap12 summary (reviewed), max_steps 48; SN-v2 cap-6 from long-pool (via state-cap12's table)
    'T1_SN12': [233, 295, 320, 317], 'Fz_SN12': [134, 212, 228, 216], 'T1_SN6': [102, 28], 'Fz_SN6': [3, 0]}
INH_LONG2 = {  # long-pool-2 summary, "new 21 only", max_steps 96
    'T1_SN12': [8, 15, 17, 14], 'Fz_SN12': [3, 1, 3, 5], 'T1_SN6': [0, 0]}
INH_HELD = {  # held-out greedy (p2, 5,000): state-cap12 (Stage-1 SN12), state-env (SN-v2 Stage-1)
    'Fz_SN12': [0.969, 0.977, 0.978, 0.974]}


def iqm(xs):
    xs = sorted(xs); n = len(xs); k = n // 4
    mid = xs[k:n - k] if n - 2 * k > 0 else xs
    return sum(mid) / len(mid)


def boot_ci(xs, B=10000, seed=0):
    rng = random.Random(seed); v = sorted(iqm([rng.choice(xs) for _ in xs]) for _ in range(B))
    return [v[int(0.025 * B)], v[int(0.975 * B) - 1]]


def load(label, read):
    fn = f'{E}/{label}__{read}.json'
    return json.load(open(fn)) if os.path.exists(fn) else None


def rows(label, read):
    fn = f'{E}/{label}__{read}.jsonl'
    return [json.loads(l) for l in open(fn)] if os.path.exists(fn) else None


def passk(n, c, k):
    return 1.0 if n - c < k else 1.0 - math.prod((n - c - i) / (n - i) for i in range(k))


def binof(ref):
    return 'train14' if ref is None else next(b for b, lo, hi in BINS if lo <= ref <= hi)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='artifacts/bs/summary.json')
    ap.add_argument('--lean_workers', type=int, default=2)
    ap.add_argument('--no_term', action='store_true')
    a = ap.parse_args()
    tb = json.loads(subprocess.run(['git', 'show', 'origin/dan_textbook72:artifacts/textbook72/summary.json'],
                                   capture_output=True, text=True, check=True).stdout)['per_ckpt']
    dev_names = {json.loads(l)['name'] for l in open('data/eval_only/textbook72/textbook_dev.jsonl')}
    tbrefs = {json.loads(l)['name']: json.loads(l).get('reference_lines') for l in open('data/bs/textbook72.jsonl')}
    out = {'per_ckpt': {}, 'cells': {}}
    for cell in CELLS:
        for stage in ('Fz', 'T1'):
            for m in MEMBERS[cell]:
                L = f'{stage}_{m}'; fam = L.rsplit('_s', 1)[0]; s = int(L.rsplit('_s', 1)[1]); d = {}
                # textbook72
                if cell.startswith('ours'):
                    t = tb.get(L)
                    if t:
                        d['tb72'] = t['all72']; d['tb72_dev58'] = t['dev58']; d['tb72_train14'] = t['train14']
                        d['tb72_bins'] = t['by_bin']; d['tb72_solved'] = sorted(t['solved']); d['tb72_src'] = 'textbook72 run'
                else:
                    r = rows(L, 'tb72')
                    if r:
                        sol = [x['name'] for x in r if x['solved']]
                        d['tb72'] = len(sol); d['tb72_dev58'] = sum(n in dev_names for n in sol)
                        d['tb72_train14'] = d['tb72'] - d['tb72_dev58']
                        bins = {}
                        for n in sol:
                            b = 'train14' if n not in dev_names else binof(tbrefs[n])
                            bins[b] = bins.get(b, 0) + 1
                        d['tb72_bins'] = bins; d['tb72_solved'] = sorted(sol); d['tb72_src'] = f'{E}/{L}__tb72.jsonl'
                        d['tb72_proofs'] = {x['name']: x['proofs'] for x in r if x['solved']}
                        sm = load(L, 'tb72'); d['tb72_env_end'] = sm['env'].get('env_end') if sm else None
                # dev metric (Robbie's): dev half of transfer, 64 samples, solved at L_true >= 7 (all are >= 7)
                sm = load(L, 'dev')
                if sm:
                    d['dev'] = sm['solved']; d['dev_n'] = sm['n']
                    d['dev_by_len'] = {k: v['solved'] for k, v in sm['by_len'].items()}
                    d['dev_env_end'] = sm['env'].get('env_end')
                # holdout250 pass@k (unbiased, from n_ok of 256)
                r = rows(L, 'h250')
                if r:
                    d['h250'] = sum(x['solved'] for x in r)
                    d['h250_passk'] = {k: round(sum(passk(x['n_tried'], x['n_ok'], k) for x in r) / len(r), 4)
                                       for k in (1, 4, 16, 64, 256)}
                # long pools
                r = rows(L, 'rr600')
                if r:
                    pool = {x['name']: x for x in map(json.loads, open('data/ladder/transfer_long_rr600.jsonl'))}
                    d['Q'] = sum(1 for x in r if x['solved'] and pool[x['name']]['source'] == 'gen'
                                 and 13 <= pool[x['name']]['L_true'] <= 16)
                    d['rr600'] = sum(x['solved'] for x in r); d['Q_src'] = f'{E}/{L}__rr600.jsonl'
                elif fam in INH_Q:
                    d['Q'] = INH_Q[fam][s]; d['Q_src'] = 'state-cap12 / long-pool (max_steps 48)'
                sm = load(L, 'long2')
                if sm:
                    d['long2'] = sm['solved']; d['long2_src'] = f'{E}/{L}__long2.json'
                elif fam in INH_LONG2:
                    d['long2'] = INH_LONG2[fam][s]; d['long2_src'] = 'long-pool-2'
                sm = load(L, 'held')
                hj = f'{E}/heldout_{m}_b1200.json'
                if sm:
                    d['held'] = sm['rate']
                elif stage == 'Fz' and os.path.exists(hj):
                    d['held'] = json.load(open(hj))['rate']
                elif fam in INH_HELD:
                    d['held'] = INH_HELD[fam][s]
                out['per_ckpt'][L] = d
    # cell summaries
    print('## best-state read-outs (Lean alone; per seed, IQM [stratified-bootstrap 95 %])\n')
    for q, name in (('tb72', 'textbook72 all 72'), ('tb72_dev58', 'textbook72 dev58'), ('tb72_train14', 'textbook72 train14'),
                    ('dev', 'dev metric (1,108, k 64, >= 7)'), ('h250', 'holdout250 pass@256'), ('Q', 'rr600 Q (13-16, /380)'),
                    ('long2', 'transfer_long2 (/21)'), ('held', 'held-out greedy')):
        print(f'\n### {name}\n\n| cell | frozen per seed | frozen IQM | T1 per seed | T1 IQM |\n|---|---|---|---|---|')
        for cell in CELLS:
            line = f'| {cell} |'
            for stage in ('Fz', 'T1'):
                v = [out['per_ckpt'][f'{stage}_{m}'].get(q) for m in MEMBERS[cell]]
                have = [x for x in v if x is not None]
                if have:
                    ci = boot_ci(have) if len(have) >= 2 else None
                    fmt = (lambda x: f'{x:.3f}') if q == 'held' else (lambda x: f'{x:g}')
                    line += ' ' + ' / '.join('–' if x is None else fmt(x) for x in v) + f' | {fmt(iqm(have))}' + \
                            (f' [{fmt(ci[0])}, {fmt(ci[1])}]' if ci else '') + ' |'
                    out['cells'].setdefault(cell, {}).setdefault(stage, {})[q] = {'per_seed': v, 'iqm': iqm(have), 'ci': ci}
                else:
                    line += ' – | – |'
            print(line)
    # best - ours
    print('\n### best − ours (IQM difference; MDD from the pre-registration)\n\n| quantity | cap | frozen | T1 | MDD |\n|---|---|---|---|---|')
    MDD = {('tb72', 6): 9.3, ('tb72', 12): 6.5, ('dev', 6): 88, ('dev', 12): 61}
    for q in ('tb72', 'dev', 'h250', 'Q', 'long2'):
        for cap in (6, 12):
            c = out['cells']; row = f'| {q} | {cap} |'
            for stage in ('Fz', 'T1'):
                try:
                    dlt = c[f'best-cap{cap}'][stage][q]['iqm'] - c[f'ours-cap{cap}'][stage][q]['iqm']
                    row += f' {dlt:+.1f} |'; out.setdefault('diff', {})[f'{q}_cap{cap}_{stage}'] = dlt
                except KeyError:
                    row += ' – |'
            print(row + f" {MDD.get((q, cap), '–')} |")
    # textbook72 by reference_lines bin
    print('\n### textbook72 by reference_lines (per seed)\n\n| checkpoint | 1-5 | 6-10 | 11-15 | 16+ | train14 |\n|---|---|---|---|---|---|')
    for cell in CELLS:
        for stage in ('Fz', 'T1'):
            for m in MEMBERS[cell]:
                d = out['per_ckpt'][f'{stage}_{m}']
                if 'tb72_bins' in d:
                    b = d['tb72_bins']; print(f'| {stage}_{m} | ' + ' | '.join(str(b.get(k, 0)) for k in ('1-5', '6-10', '11-15', '16+', 'train14')) + ' |')
    # shortest accepted textbook72 proof per (new checkpoint, problem): lines and Lean term size
    if not a.no_term:
        import nd2lean
        from lean_check import check
        from lean_judge import n_lines
        prompts = {json.loads(l)['name']: json.loads(l)['prompt'] for l in open('data/bs/textbook72.jsonl')}
        items = []
        for L, d in out['per_ckpt'].items():
            for n, ps in d.get('tb72_proofs', {}).items():
                p = min(ps, key=n_lines); items.append((L, n, n_lines(p), nd2lean.translate(prompts[n], p, require_all_pr=False)))
        res, wall, _ = check([x[3] for x in items], workers=a.lean_workers) if items else ([], 0, None)
        per = {}
        for (L, n, nl, src), r in zip(items, res):
            per.setdefault(L, []).append((nl, r.get('size'), r['ok']))
        print('\n### textbook72, shortest accepted proof per solved problem (new checkpoints)\n\n'
              '| checkpoint | solved | median lines | median term size | lean_check ok |\n|---|---|---|---|---|')
        for L, v in sorted(per.items()):
            ls = sorted(x[0] for x in v); ts = sorted(x[1] for x in v if x[1] is not None)
            out['per_ckpt'][L]['tb72_min_lines_median'] = ls[len(ls) // 2]
            out['per_ckpt'][L]['tb72_min_term_median'] = ts[len(ts) // 2] if ts else None
            print(f'| {L} | {len(v)} | {ls[len(ls) // 2]} | {ts[len(ts) // 2] if ts else "–"} | {sum(x[2] for x in v)}/{len(v)} |')
    for d in out['per_ckpt'].values():
        d.pop('tb72_proofs', None)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
