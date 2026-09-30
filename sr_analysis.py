#!/usr/bin/env python3
"""state-readouts analysis (reads only pulled files; stdout is tables; writes artifacts/state-readouts/summary.json).

Part A: H records artifacts/state-readouts/H_<arm>_<T08|T10>_s<seed>.s0.jsonl (ss_support.py) for arms S / SH, and
support-state's SN records (git show origin/dan_support-state:artifacts/ss/H_base_<T>_s<seed>.s0.jsonl) as the
inherited comparator. A survivor is reached if any row (either temperature) has n_ok >= 1 (Lean-accepted literal text).
Part B: re-reads artifacts/state-readouts/rr/<label>__<tb|tbl>.jsonl (lpool_reread.py): solved = n_ok >= 1 of k 256.
"""
import json, os, glob, subprocess, statistics, collections, sys

D = 'artifacts/state-readouts'
SURV = [l.strip() for l in open('data/sc/falsifier_survivors.txt') if l.strip()]
THM = {json.loads(l)['name']: json.loads(l) for l in open('data/sc/theorems.jsonl') if l.strip()}


def rows_local(path):
    return [json.loads(l) for l in open(path) if l.strip()] if os.path.exists(path) else []


def rows_git(path, ref='origin/dan_support-state'):
    p = subprocess.run(['git', 'show', f'{ref}:{path}'], capture_output=True, text=True)
    return [json.loads(l) for l in p.stdout.splitlines() if l.strip()] if p.returncode == 0 else []


def part_a():
    arms = {}
    for m in ('S', 'SH'):
        for s in range(4):
            t08 = rows_local(f'{D}/H_{m}_T08_s{s}.s0.jsonl')
            if t08:
                arms[(m, s)] = (t08, rows_local(f'{D}/H_{m}_T10_s{s}.s0.jsonl'))
    for s in (0, 1):
        arms[('SN (inherited)', s)] = (rows_git(f'artifacts/ss/H_base_T08_s{s}.s0.jsonl'),
                                       rows_git(f'artifacts/ss/H_base_T10_s{s}.s0.jsonl'))
    out, per_thm = {}, collections.defaultdict(dict)
    print('Part A: survivors reached per arm and seed (29 theorems; Lean alone)')
    print(f"{'arm':16s}{'seed':>5s}{'T08 rows':>9s}{'T10 rows':>9s}{'reached':>8s}{'@T0.8':>6s}{'@10k':>6s}"
          f"{'med p08':>9s}{'attempts':>11s}{'stepcap%':>9s}{'actcap%':>8s}{'syntax%':>8s}")
    for (m, s), (t08, t10) in arms.items():
        a08 = {r['name']: r for r in t08}; a10 = {r['name']: r for r in t10}
        reached = [n for n in SURV if (a08.get(n, {}).get('n_ok', 0) + a10.get(n, {}).get('n_ok', 0)) > 0]
        r08 = [n for n in SURV if a08.get(n, {}).get('n_ok', 0) > 0]
        r10k = [n for n in SURV if a08.get(n, {}).get('first_hit') and a08[n]['first_hit'] <= 10000]
        p08 = [a08[n]['n_ok'] / a08[n]['n_tried'] if n in a08 else 0.0 for n in SURV]
        rows = t08 + t10
        att = sum(r['n_tried'] for r in rows)
        cap = sum(r.get('n_step_cap', 0) for r in rows); act = sum(r.get('n_trunc_action', 0) for r in rows)
        syn = sum(r.get('n_parse_fail', 0) for r in rows)
        caprow = max((r.get('n_step_cap', 0) + r.get('n_trunc_action', 0)) / r['n_tried'] for r in rows)
        complete = len(a08) == 29
        print(f"{m:16s}{s:>5d}{len(a08):>9d}{len(a10):>9d}{len(reached):>8d}{len(r08):>6d}{len(r10k):>6d}"
              f"{statistics.median(p08):>9.4f}{att:>11,d}{100*cap/att:>9.3f}{100*act/att:>8.3f}{100*syn/att:>8.2f}"
              + ('' if complete else '  (incomplete)'))
        lines = [p['n_lines'] for r in rows for p in r['proofs']]
        size = [p['term_size'] for r in rows for p in r['proofs'] if p.get('term_size') is not None]
        out[f'{m}|{s}'] = {'arm': m, 'seed': s, 'complete': complete, 'reached': len(reached), 'reached_T08': len(r08),
                           'reached_T08_10k': len(r10k), 'median_p_T08': statistics.median(p08), 'attempts': att,
                           'step_cap': cap, 'action_cap': act, 'parse_fail': syn, 'max_row_cap_frac': caprow,
                           'missed': [n for n in SURV if n not in reached],
                           'median_lines': statistics.median(lines) if lines else None,
                           'median_term_size': statistics.median(size) if size else None,
                           'distinct_proofs': len(lines)}
        for n in SURV:
            per_thm[n][f'{m}|{s}'] = {'p08': (a08[n]['n_ok'] / a08[n]['n_tried']) if n in a08 else None,
                                     'n08': a08.get(n, {}).get('n_tried'), 'ok08': a08.get(n, {}).get('n_ok'),
                                     'p10': (a10[n]['n_ok'] / a10[n]['n_tried']) if n in a10 else None,
                                     'n10': a10.get(n, {}).get('n_tried'), 'ok10': a10.get(n, {}).get('n_ok')}
    keys = list(out)
    print('\nPer theorem p-hat at T 0.8 (ok/attempts; "0/N" = unreached at T 0.8; T 1.0 in brackets when run)')
    print(f"{'theorem':18s}{'L':>3s} " + ''.join(f'{k.replace(" (inherited)", ""):>16s}' for k in keys))
    for n in SURV:
        cells = []
        for k in keys:
            c = per_thm[n].get(k, {})
            if c.get('n08') is None:
                cells.append('-'); continue
            t = f"{c['p08']:.2g}" if c['ok08'] else f"0/{c['n08']//1000}k"
            if c.get('n10') is not None:
                t += f"[{c['ok10']}/{c['n10']//1000}k]"
            cells.append(t)
        print(f"{n:18s}{THM[n]['L_true']:>3d} " + ''.join(f'{x:>16s}' for x in cells))
    return out, per_thm


def part_b():
    pool = {json.loads(l)['name']: json.loads(l) for f in ('data/sr/textbook_transfer.jsonl', 'data/sr/textbook_long.jsonl')
            for l in open(f) if l.strip()}
    dead = ['demorgan_and_to_nor', 'demorgan_nor_to_and', 'demorgan_or_to_nand', 'dist_and_over_or',
            'dist_and_over_or_conv', 'dist_or_over_and', 'excluded_middle', 'import', 'negated_conditional',
            'negated_conditional_conv', 'peirce', 'peirce_sequent']
    res = {}
    for f in sorted(glob.glob(f'{D}/rr/*__tb*.jsonl')):
        lab, t = os.path.basename(f)[:-6].split('__')
        rows = [json.loads(l) for l in open(f) if l.strip()]
        sm = json.load(open(f[:-6] + '.json')) if os.path.exists(f[:-6] + '.json') else {}
        c = collections.Counter(pool[r['name']]['schema'] for r in rows if r['n_ok'] > 0)
        n = collections.Counter(pool[r['name']]['schema'] for r in rows)
        res.setdefault(lab, {})[t] = {'by_schema': dict(c), 'n_by_schema': dict(n), 'solved': sum(c.values()),
                                      'n': len(rows), 'env': sm.get('env'), 'peak_mem_gb': sm.get('peak_mem_gb')}
    if not res:
        return {}
    labs = sorted(res, key=lambda x: (not x.startswith('T1'), x))
    for t, title in (('tb', 'transfer.jsonl textbook (40 per schema)'), ('tbl', 'transfer_long.jsonl textbook')):
        sch = sorted({s for l in labs if t in res[l] for s in res[l][t]['n_by_schema']})
        if not sch:
            continue
        print(f'\nPart B: solves per schema, k 256, T 0.8, max_steps 96 — {title}')
        print(f"{'schema':26s}{'n':>4s}" + ''.join(f'{l:>11s}' for l in labs))
        for s in sch:
            nn = max(res[l][t]['n_by_schema'].get(s, 0) for l in labs if t in res[l])
            print(f"{s + (' *' if s in dead else ''):26s}{nn:>4d}" +
                  ''.join(f"{res[l][t]['by_schema'].get(s, 0) if t in res[l] else '-':>11}" for l in labs))
        print(f"{'total':26s}{'':>4s}" + ''.join(f"{res[l][t]['solved'] if t in res[l] else '-':>11}" for l in labs))
        if t == 'tb':
            print(f"{'dead schemata >= 5 (/12)':30s}" + ''.join(
                f"{sum(res[l][t]['by_schema'].get(s, 0) >= 5 for s in dead) if t in res[l] else '-':>11}" for l in labs))
        print(f"{'step-cap hits %':30s}" + ''.join(
            f"{(100 * res[l][t]['env']['end'].get('step_cap', 0) / max(1, sum(res[l][t]['env']['end'].values()))) if t in res[l] and res[l][t].get('env') and 'end' in res[l][t]['env'] else float('nan'):>11.3f}"
            for l in labs))
    return res


if __name__ == '__main__':
    a, pt = part_a()
    b = part_b()
    json.dump({'part_a': a, 'part_a_per_theorem': pt, 'part_b': b}, open(f'{D}/summary.json', 'w'), indent=1)
