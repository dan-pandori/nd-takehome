#!/usr/bin/env python3
"""compute-match numbers from pulled files (run `compute-match`).  Lean alone decides: a problem is solved by a checkpoint
iff >= 1 of its samples was accepted by the judge inside `state_eval.py` / `lpool_reread.py` (lean_judge, state env).

Models (all `lean_staten`, from scratch, trained on K12 `data/kh/train_k12.jsonl`, 155,000 records):
  cm12 T1      3,216,384-param GPT (4 x 256), SN-cap12 Stage-1 (state-cap12 `stage1_SN12_s{0,1,2}.pt`, 6,000 steps x 128)
               + T1 ladder at k 64 (this run): ckpts/cm/ladder/la_T1_cm12k64_s{0,1,2}_r8.pt
  SN12 T1      same Stage-1 + T1 ladder at k 32 (state-cap12): la_T1_SN12_s{0,1,2}_r8.pt
  best12 T1    9,560,832-param ALiBiGPT (Robbie's recipe, 1,200 s Stage-1) + T1 ladder at k 32 (best-state)

Sources:
  new reads          artifacts/cm/eval/T1_cm12k64_s*__{tb72,dev,h250,rr600,long2,held}.{json,jsonl}
  paired re-reads    artifacts/cm/eval/T1_SN12_s*__{tb72,long2,rr600}.{json,jsonl}  (best-state read settings)
  best-state         `git show HEAD:artifacts/bs/summary.json` per_ckpt (best12 Fz/T1, SN12 Fz/T1 as best-state reported them)
  ladders            artifacts/cm/la_T1_cm12k64_s*/found_<r>.jsonl (this run); inherited SN12 / best12 from the logs

  python3 cm_analysis.py [--lean_workers 2] --out artifacts/cm/summary.json > artifacts/cm/analysis_stdout.txt
"""
import argparse, json, os, random, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bs_analysis import iqm, boot_ci, passk, binof

E = 'artifacts/cm/eval'
SEEDS = (0, 1, 2)
MDD = {'tb72': 6.5, 'dev': 61}   # best-state's pre-registered cap-12 MDDs
QS = (('tb72', 'textbook72 /72'), ('tb72_dev58', 'textbook72 dev58'), ('dev', 'dev metric /1,108 (k 64)'),
      ('h250', 'holdout250 /250 (k 256)'), ('Q', 'rr600 Q (L_true 13-16, /380)'), ('long2', 'transfer_long2 /21'),
      ('held', 'held-out greedy /5,000 (rate)'))


def rows(label, read):
    fn = f'{E}/{label}__{read}.jsonl'
    return [json.loads(l) for l in open(fn)] if os.path.exists(fn) else None


def summ(label, read):
    fn = f'{E}/{label}__{read}.json'
    return json.load(open(fn)) if os.path.exists(fn) else None


def cut_frac(sm):
    """Fraction of attempts that ended neither done nor on a syntax / rule error: action-truncated or step-capped."""
    e = (sm or {}).get('env', {}).get('env_end') or {}
    n = sum(e.values())
    return (n - e.get('done', 0) - e.get('syntax', 0)) / n if n else None


def read_ckpt(L, dev_names, tbrefs, pool):
    d = {}
    r = rows(L, 'tb72')
    if r:
        sol = [x['name'] for x in r if x['solved']]
        d['tb72'] = len(sol); d['tb72_dev58'] = sum(n in dev_names for n in sol)
        bins = {}
        for n in sol:
            b = 'train14' if n not in dev_names else binof(tbrefs[n])
            bins[b] = bins.get(b, 0) + 1
        d['tb72_bins'] = bins; d['tb72_solved'] = sorted(sol)
        d['tb72_proofs'] = {x['name']: x['proofs'] for x in r if x['solved']}
    sm = summ(L, 'dev')
    if sm:
        d['dev'] = sm['solved']
    r = rows(L, 'h250')
    if r:
        d['h250'] = sum(x['solved'] for x in r)
        d['h250_passk'] = {k: round(sum(passk(x['n_tried'], x['n_ok'], k) for x in r) / len(r), 4) for k in (1, 16, 256)}
    r = rows(L, 'rr600')
    if r:
        d['Q'] = sum(1 for x in r if x['solved'] and pool[x['name']]['source'] == 'gen' and 13 <= pool[x['name']]['L_true'] <= 16)
        d['rr600'] = sum(x['solved'] for x in r)
    sm = summ(L, 'long2')
    if sm:
        d['long2'] = sm['solved']
    sm = summ(L, 'held')
    if sm:
        d['held'] = sm['rate']
    d['cut'] = {rd: cut_frac(summ(L, rd)) for rd in ('tb72', 'dev', 'h250', 'rr600', 'long2') if summ(L, rd)}
    return d


def boot_diff(a, b, B=10000, seed=0):
    rng = random.Random(seed)
    v = sorted(iqm([rng.choice(a) for _ in a]) - iqm([rng.choice(b) for _ in b]) for _ in range(B))
    return [v[int(0.025 * B)], v[int(0.975 * B) - 1]]


def ladder_curve(name):
    out = []
    for r in range(1, 9):
        fn = f'artifacts/cm/{name}/found_{r}.jsonl'
        if not os.path.exists(fn):
            break
        names = set()
        for l in open(fn):
            names.add(json.loads(l)['name'])
        out.append(len(names))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='artifacts/cm/summary.json')
    ap.add_argument('--lean_workers', type=int, default=2)
    ap.add_argument('--no_term', action='store_true')
    a = ap.parse_args()
    import record
    record.save_config(vars(a), a.out)
    bs = json.loads(subprocess.run(['git', 'show', 'HEAD:artifacts/bs/summary.json'], capture_output=True, text=True,
                                   check=True).stdout)['per_ckpt']
    dev_names = {json.loads(l)['name'] for l in open('data/eval_only/textbook72/textbook_dev.jsonl')}
    tbrefs = {json.loads(l)['name']: json.loads(l).get('reference_lines') for l in open('data/bs/textbook72.jsonl')}
    pool = {x['name']: x for x in map(json.loads, open('data/ladder/transfer_long_rr600.jsonl'))}
    per = {}
    for s in SEEDS:
        per[f'T1_cm12k64_s{s}'] = read_ckpt(f'T1_cm12k64_s{s}', dev_names, tbrefs, pool)
        rr = read_ckpt(f'T1_SN12_s{s}', dev_names, tbrefs, pool)            # paired re-read (tb72, long2, rr600 only)
        base = {k: bs[f'T1_SN12_s{s}'].get(k) for k in ('tb72', 'tb72_dev58', 'dev', 'h250', 'Q', 'long2', 'held')}
        per[f'T1_SN12_s{s} (best-state)'] = base
        per[f'T1_SN12_s{s} (re-read)'] = {**{k: v for k, v in base.items() if k in ('dev', 'h250', 'held')}, **rr}
        per[f'T1_best12_s{s}'] = {k: bs[f'T1_best12_s{s}'].get(k) for k in base}
        per[f'Fz_SN12_s{s}'] = {k: bs[f'Fz_SN12_s{s}'].get(k) for k in base}
    arms = [('best12 T1 (best-state)', 'T1_best12_s{}'), ('cm12 T1, k 64 (this run)', 'T1_cm12k64_s{}'),
            ('SN12 T1, k 32 (re-read here*)', 'T1_SN12_s{} (re-read)'), ('SN12 T1, k 32 (as best-state)', 'T1_SN12_s{} (best-state)'),
            ('SN12 frozen (best-state)', 'Fz_SN12_s{}')]
    out = {'per_ckpt': per, 'arms': {}, 'diff': {}}
    print('## compute-match read-outs (Lean alone; seeds 0 / 1 / 2, IQM = mean at n 3, [stratified-bootstrap 95 %])\n')
    print('*Re-read here at best-state settings (batch 2,048, max_steps 96): tb72, long2, rr600 Q; dev / h250 / held '
          'are best-state\'s reads of the same checkpoints.\n')
    for q, name in QS:
        print(f'\n### {name}\n\n| arm | per seed | IQM [95 %] | max cut-off % |\n|---|---|---|---|')
        for an, pat in arms:
            v = [per[pat.format(s)].get(q) for s in SEEDS]
            if any(x is None for x in v):
                print(f'| {an} | ' + ' / '.join('–' if x is None else f'{x:g}' for x in v) + ' | – | – |'); continue
            ci = boot_ci(v); f = (lambda x: f'{x:.3f}') if q == 'held' else (lambda x: f'{x:.1f}')
            rd = q.replace('_dev58', '').replace('Q', 'rr600')
            cuts = [per[pat.format(s)].get('cut', {}).get(rd) for s in SEEDS]
            cuts = [c for c in cuts if c is not None]
            print(f"| {an} | {' / '.join(f'{x:g}' for x in v)} | {f(iqm(v))} [{f(ci[0])}, {f(ci[1])}] | "
                  f"{(f'{100 * max(cuts):.2f}' if cuts else '–')} |")
            out['arms'].setdefault(an, {})[q] = {'per_seed': v, 'iqm': iqm(v), 'ci': ci}
    print('\n### Headline: best12 T1 − cm12 T1 (and the k 32 control)\n')
    print('| quantity | best12 − cm12 [95 % boot] | MDD | best12 − SN12 k 32 (same read) | cm12 − SN12, paired per seed | mean paired |')
    print('|---|---|---|---|---|---|')
    for q in ('tb72', 'dev', 'h250', 'Q', 'long2', 'held'):
        b = [per[f'T1_best12_s{s}'].get(q) for s in SEEDS]; c = [per[f'T1_cm12k64_s{s}'].get(q) for s in SEEDS]
        o = [per[f'T1_SN12_s{s} (re-read)'].get(q) for s in SEEDS]
        if any(x is None for x in b + c + o):
            continue
        dd = iqm(b) - iqm(c); ci = boot_diff(b, c); pr = [ci_ - oi for ci_, oi in zip(c, o)]
        fm = (lambda x: f'{x:+.3f}') if q == 'held' else (lambda x: f'{x:+.1f}')
        print(f"| {q} | {fm(dd)} [{fm(ci[0])}, {fm(ci[1])}] | {MDD.get(q, '–')} | {fm(iqm(b) - iqm(o))} | "
              f"{' / '.join(fm(x) for x in pr)} | {fm(sum(pr) / 3)} |")
        out['diff'][q] = {'best_minus_cm': dd, 'ci': ci, 'best_minus_sn32': iqm(b) - iqm(o), 'cm_minus_sn32_paired': pr}
    for q, m in MDD.items():
        if q in out['diff']:
            out['diff'][q]['closed'] = out['diff'][q]['best_minus_cm'] < m
    print('\nFalsifier ("the recipe, not the compute"): gap < MDD → ' +
          ', '.join(f"{q}: {'CLOSED' if out['diff'][q]['closed'] else 'open'}" for q in MDD if q in out['diff']))
    # textbook72 by bin
    print('\n### textbook72 by reference_lines (per seed)\n\n| checkpoint | 1-5 | 6-10 | 11-15 | 16+ | train14 |\n|---|---|---|---|---|---|')
    for L in [f'T1_cm12k64_s{s}' for s in SEEDS] + [f'T1_SN12_s{s} (re-read)' for s in SEEDS]:
        b = per[L].get('tb72_bins', {})
        print(f'| {L} | ' + ' | '.join(str(b.get(k, 0)) for k in ('1-5', '6-10', '11-15', '16+', 'train14')) + ' |')
    # ladders: distinct targets solved (cumulative, /4,495) per round
    print('\n### Ladder: cumulative rl_targets solved (/4,495) by round, cm12 k 64 (from found_<r>.jsonl)\n')
    print('| seed | ' + ' | '.join(f'r{r}' for r in range(1, 9)) + ' |\n|---|' + '---|' * 8)
    for s in SEEDS:
        cv = ladder_curve(f'la_T1_cm12k64_s{s}'); out.setdefault('ladder', {})[s] = cv
        print(f'| {s} | ' + ' | '.join(f'{x:,}' for x in cv) + ' |')
    if not a.no_term:
        import nd2lean
        from lean_check import check
        from lean_judge import n_lines
        prompts = {json.loads(l)['name']: json.loads(l)['prompt'] for l in open('data/bs/textbook72.jsonl')}
        items = []
        for L, d in per.items():
            for n, ps in d.get('tb72_proofs', {}).items():
                p = min(ps, key=n_lines); items.append((L, n, n_lines(p), nd2lean.translate(prompts[n], p, require_all_pr=False)))
        res, _, _ = check([x[3] for x in items], workers=a.lean_workers) if items else ([], 0, None)
        agg = {}
        for (L, n, nl, src), r in zip(items, res):
            agg.setdefault(L, []).append((nl, r.get('size'), r['ok']))
        print('\n### textbook72, shortest accepted proof per solved problem\n\n'
              '| checkpoint | solved | median lines | median term size | lean_check ok |\n|---|---|---|---|---|')
        for L, v in sorted(agg.items()):
            ls = sorted(x[0] for x in v); ts = sorted(x[1] for x in v if x[1] is not None)
            per[L]['tb72_min_lines_median'] = ls[len(ls) // 2]; per[L]['tb72_min_term_median'] = ts[len(ts) // 2] if ts else None
            print(f'| {L} | {len(v)} | {ls[len(ls) // 2]} | {ts[len(ts) // 2] if ts else "–"} | {sum(x[2] for x in v)}/{len(v)} |')
    for d in per.values():
        d.pop('tb72_proofs', None)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
