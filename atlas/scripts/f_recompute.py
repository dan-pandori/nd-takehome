#!/usr/bin/env python3
"""Part F: harmonized textbook72 / dev1108 / holdout250 table across model families.

Recomputes solved counts and unbiased pass@k (expected solved = sum_theorems 1 - C(n-c,k)/C(n,k)) from
per-theorem files wherever they exist; copies everything else from read-out summaries (fork) or from
atlas/raw/D_metrics.csv (Robbie, no per-theorem files in git).

Inputs (read-only):
  fork   /home/dan/nd-takehome   via `git show origin/dan_<run>:<path>` (read-out summary .json + args)
  nd-rl  /home/dan/nd-rl         origin/robbie-experiments: combined-model/charts/passk.csv (per-problem n_ok/256)
  cache  /tmp/atlas/cache/<run>/eval/*.jsonl  per-theorem rows {name, n_ok, n_tried, ...} pulled from
         hf://buckets/dan-pandori/nd-rl/{textbook72/artifacts/textbook72,best-state/artifacts/bs,compute-match/
         artifacts/cm,trajectory/artifacts/tj,trajectory-cap6/artifacts/tj6,rl-from-ckpt/artifacts/rfc}/eval
  atlas/raw/C_metrics.csv, D_metrics.csv (metadata, copied Robbie rows, cross-check of copied fork numbers)

Outputs: atlas/data/textbook72_harmonized.csv, atlas/data/dev_holdout_harmonized.csv; prints cross-checks.
Usage: python3 atlas/scripts/f_recompute.py
"""
import csv, io, json, os, re, subprocess, sys
from collections import defaultdict

ATLAS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FORK, NDRL, CACHE = '/home/dan/nd-takehome', '/home/dan/nd-rl', '/tmp/atlas/cache'
COLS = ['family', 'model_label', 'params', 'format', 'init', 'train_set', 'cap', 'stage', 'seed', 'pool', 'n_pool',
        'metric', 'k', 'temperature', 'value', 'checker', 'judge', 'date', 'provenance', 'source_file', 'apples_group']
POOLS = {'tb72': ('textbook72', 72), 'dev': ('dev1108', 1108), 'h250': ('holdout250', 250)}
KS = (1, 4, 16, 64, 256)
FORK_JUDGE = 'fork lean_judge (Lean 4.34 alone); state_eval in-env sampling, max_action 512 max_steps 96'
ROBBIE_JUDGE = 'robbie harness judge (fork sample Lean gate 51604b3 then nd_verify); max_new 512'


def sh(*a):
    return subprocess.run(a, capture_output=True, text=True, check=True).stdout


def gshow(repo, ref, path):
    try:
        return sh('git', '-C', repo, 'show', f'{ref}:{path}')
    except subprocess.CalledProcessError:
        return None


def gls(repo, ref, path):
    return sh('git', '-C', repo, 'ls-tree', '-r', '--name-only', ref, path).split()


def passk(n, c, k):
    """unbiased pass@k = 1 - C(n-c,k)/C(n,k), numerically stable product form."""
    if k > n:
        return None
    if n - c < k:
        return 1.0
    p = 1.0
    for i in range(n - c + 1, n + 1):
        p *= 1.0 - k / i
    return 1.0 - p


# ----------------------------------------------------------------------------------------- fork families
FAM = {  # family: (params, format, init, train_set, cap)
    'ours-3.2M-SN-cap12': ('3.2M', 'lean_staten', 'scratch', 'K12 155k', '12'),
    'ours-3.2M-SN-v2-cap6': ('3.2M', 'lean_staten', 'scratch', 'cap-6 control 155k', '6'),
    'ours-3.2M-SN-cap12-k64ladder': ('3.2M', 'lean_staten', 'scratch', 'K12 155k', '12'),
    'best-9.56M-cap6': ('9.56M', 'lean_staten', 'scratch', 'cap-6 control 155k', '6'),
    'best-9.56M-cap12': ('9.56M', 'lean_staten', 'scratch', 'K12 155k', '12'),
    'best-9.56M-cap6-trajectory': ('9.56M', 'lean_staten', 'scratch', 'cap-6 control 155k', '6'),
    'best-9.56M-cap12-trajectory': ('9.56M', 'lean_staten', 'scratch', 'K12 155k', '12'),
}
ARM = {'SN12': ('ours-3.2M-SN-cap12', 'la_T1_SN12_s{S}_r8', 'stage1_SN12_s{S}'),
       'SN6': ('ours-3.2M-SN-v2-cap6', 'la_T1_SN_s{S}_r8', 'stage1_SN_s{S}'),
       'best6': ('best-9.56M-cap6', 'la_T1_best6_s{S}_r8', 'stage1_best6_s{S}_b1200'),
       'best12': ('best-9.56M-cap12', 'la_T1_best12_s{S}_r8', 'stage1_best12_s{S}_b1200'),
       'cm12k64': ('ours-3.2M-SN-cap12-k64ladder', 'la_T1_cm12k64_s{S}_r8', None)}


def readouts():
    """yield (run, branch, summary_path, cache_jsonl, family, label, stage, seed, poolkey, extra_judge)"""
    # textbook72 run (2026-09-30): eval/{Fz,T1}_{SN12,SN6}_s{S}.json, all on all72 = textbook72
    for p in gls(FORK, 'origin/dan_textbook72', 'artifacts/textbook72/eval'):
        m = re.match(r'.*/(Fz|T1)_(SN12|SN6)_s(\d)\.json$', p)
        if m:
            fam, lt, lf = ARM[m[2]]
            yield ('textbook72', 'dan_textbook72', p, f'{CACHE}/textbook72/eval/{m[1]}_{m[2]}_s{m[3]}.jsonl', fam,
                   (lt if m[1] == 'T1' else lf).format(S=m[3]), 'T1' if m[1] == 'T1' else 'frozen', m[3], 'tb72',
                   'textbook72 run, batch 4096')
    # best-state (2026-10-01): artifacts/bs/eval/{Fz,T1}_{arm}_s{S}__{tb72,dev,h250}.json
    for p in gls(FORK, 'origin/dan_best-state', 'artifacts/bs/eval'):
        m = re.match(r'.*/(Fz|T1)_(SN12|SN6|best6|best12)_s(\d)__(tb72|dev|h250)\.json$', p)
        if m:
            fam, lt, lf = ARM[m[2]]
            yield ('best-state', 'dan_best-state', p, f'{CACHE}/best-state/eval/{os.path.basename(p)}l', fam,
                   (lt if m[1] == 'T1' else lf).format(S=m[3]), 'T1' if m[1] == 'T1' else 'frozen', m[3], m[4],
                   'best-state read, batch 2048')
    # compute-match (2026-10-02): artifacts/cm/eval/T1_{SN12,cm12k64}_s{S}__{pool}.json
    for p in gls(FORK, 'origin/dan_compute-match', 'artifacts/cm/eval'):
        m = re.match(r'.*/T1_(SN12|cm12k64)_s(\d)__(tb72|dev|h250)\.json$', p)
        if m:
            fam, lt, _ = ARM[m[1]]
            yield ('compute-match', 'dan_compute-match', p, f'{CACHE}/compute-match/eval/{os.path.basename(p)}l', fam,
                   lt.format(S=m[2]), 'T1-k64' if m[1] == 'cm12k64' else 'T1', m[2], m[3],
                   'compute-match read, batch 2048' + (' (re-read of textbook72-run ckpt)' if m[1] == 'SN12' else ''))
    # trajectory / trajectory-cap6: s{S}_p{step}|pend|r{N}__{tb72,h250}_x{X}.json
    for run, br, d, arm in (('trajectory', 'dan_trajectory', 'tj', 'best12'),
                            ('trajectory-cap6', 'dan_trajectory-cap6', 'tj6', 'best6')):
        fam = f'best-9.56M-cap{arm[4:]}-trajectory'
        for p in gls(FORK, f'origin/{br}', f'artifacts/{d}/eval'):
            m = re.match(r'.*/s(\d)_(p\d+|pend|r\d)__(tb72|h250)_x(\d)\.json$', p)
            if not m:
                continue
            s, t = m[1], m[2]
            if t.startswith('r'):
                stage = 'T1' if t == 'r8' else f'rl{t[1:]}'
                label = f'la_T1_{arm}_s{s}_{t}'
            else:
                stage, label = f'frozen@{t}', f'stage1_{arm}_s{s}_{t}'
            yield (run, br, p, f'{CACHE}/{run}/eval/{os.path.basename(p)}l', fam, label, stage, s, m[3],
                   f'sample seed x{m[4]}')
    # rl-from-ckpt: s{S}_p{step}_r{N} (EI ladder from an early Stage-1 ckpt), c{S}_... (replay-only control), _rr (re-read)
    for p in gls(FORK, 'origin/dan_rl-from-ckpt', 'artifacts/rfc/eval'):
        m = re.match(r'.*/([sc])(\d)_(p\d+|pend)_(r\d|rr)__(tb72|h250)_x(\d)\.json$', p)
        if not m:
            continue
        kind, s, st, r = m[1], m[2], m[3], m[4]
        if r == 'rr':
            stage, label = f'frozen@{st}', f'stage1_best12_s{s}_{st} (rfc re-read)'
        elif kind == 's':
            stage, label = ('T1' if r == 'r8' else f'rl{r[1:]}') + f'-from-{st}', f'la_T1_best12_s{s}_{st} {r}'
        else:
            stage, label = ('replay-only' if r == 'r8' else f'replay-only-rl{r[1:]}') + f'-from-{st}', \
                f'rc_best12_s{s}_{st} {r}'
        yield ('rl-from-ckpt', 'dan_rl-from-ckpt', p, f'{CACHE}/rl-from-ckpt/eval/{os.path.basename(p)}l',
               'best-9.56M-cap12-trajectory', label, stage, s, m[5], f'sample seed x{m[6]}')


def group(pool, k, T, checker):
    return f'{pool}|k{k}|T{T}|{checker}'


def fork_rows(checks):
    out = []
    for run, br, sp, cj, fam, label, stage, seed, pk, extra in readouts():
        summ = json.loads(gshow(FORK, f'origin/{br}', sp))
        args_txt = gshow(FORK, f'origin/{br}', sp[:-5] + '.jsonl.tmp.args.json')
        args = json.loads(args_txt) if args_txt else {}
        k = summ.get('k', args.get('k'))
        T = summ.get('temperature', args.get('temperature'))
        if k is None:  # textbook72-run summaries carry no k/T: take them from the args file
            k, T = args['k'], args['temperature']
        ms = summ.get('max_steps', args.get('max_steps'))
        date = (args.get('_meta') or {}).get('utc', '')[:10]
        pool, npool = POOLS[pk]
        params, fmt, init, ts, cap = FAM[fam]
        judge = f'{FORK_JUDGE.replace("96", str(ms))}; seed {summ.get("seed", args.get("seed"))}; {extra}'
        base = dict(family=fam, model_label=label, params=params, format=fmt, init=init, train_set=ts, cap=cap,
                    stage=stage, seed=seed, pool=pool, n_pool=npool, temperature=T, checker='lean_only',
                    judge=judge, date=date)
        metric = 'dev_metric' if pk == 'dev' else 'solved'
        src_sum = f'fork:{br}:{sp}'
        if os.path.exists(cj):
            rows = [json.loads(l) for l in open(cj) if l.strip()]
            assert len(rows) == npool, (cj, len(rows))
            solved = sum(1 for r in rows if r['n_ok'] > 0)
            assert solved == sum(1 for r in rows if r['solved']), cj
            if pk == 'dev':  # Robbie's dev metric = solved with n_lines >= 7; check the filter is vacuous
                ge7 = sum(1 for r in rows if r['n_ok'] > 0 and (r.get('n_lines') or 0) >= 7)
                assert ge7 == solved, (cj, ge7, solved)
            n = rows[0]['n_tried']
            assert all(r['n_tried'] == n for r in rows) and n == k, (cj, n, k)
            src = f'hf://buckets/dan-pandori/nd-rl/{run}/{_evdir(run)}{os.path.basename(cj)}'
            out.append({**base, 'metric': metric, 'k': k, 'value': solved, 'provenance': 'recomputed',
                        'source_file': src, 'apples_group': group(pool, k, T, 'lean_only')})
            for kk in KS:
                if kk <= n:
                    v = sum(passk(n, r['n_ok'], kk) for r in rows)
                    out.append({**base, 'metric': 'pass_at_k_expected_solved', 'k': kk, 'value': round(v, 3),
                                'provenance': 'recomputed', 'source_file': src,
                                'apples_group': group(pool, kk, T, 'lean_only')})
            checks.append(('fork-summary', f'{run}:{os.path.basename(sp)}', solved, summ.get('solved')))
        else:
            out.append({**base, 'metric': metric, 'k': k, 'value': summ['solved'], 'provenance': 'copied',
                        'source_file': src_sum, 'apples_group': group(pool, k, T, 'lean_only')})
    return out


def _evdir(run):
    return {'textbook72': 'artifacts/textbook72/eval/', 'best-state': 'artifacts/bs/eval/',
            'compute-match': 'artifacts/cm/eval/', 'trajectory': 'artifacts/tj/eval/',
            'trajectory-cap6': 'artifacts/tj6/eval/', 'rl-from-ckpt': 'artifacts/rfc/eval/'}[run]


# ----------------------------------------------------------------------------------------- Robbie
def robbie_rows(D):
    meta = {}
    for r in D:
        if r['family'].startswith('robbie-factorial:'):
            meta.setdefault(r['family'], r)
    path = 'experiment-summaries/2026-09-28-combined-model/charts/passk.csv'
    per = defaultdict(list)
    for r in csv.DictReader(io.StringIO(gshow(NDRL, 'origin/robbie-experiments', path))):
        per[(r['run'], r['pool'])].append((int(r['n']), int(r['n_ok'])))
    out = []
    for (run, pool), xs in sorted(per.items()):
        m = re.match(r'fact-(abs|lean)-(naive|best)-(ei|leon)_s(\d)$', run)
        fam = f'robbie-factorial:{m[1]}-{m[2]}-{m[3]}'
        md = meta[fam]
        chk = 'lean_and_ndverify' if m[1] == 'lean' else 'nd_verify'
        base = {c: md[c] for c in ('model_label', 'params', 'format', 'init', 'train_set', 'cap', 'stage', 'date')}
        base.update(family=fam, seed=m[4], pool=pool, n_pool=len(xs), temperature='0.8', checker=chk,
                    judge=ROBBIE_JUDGE + ('' if m[1] == 'lean' else ' (abs/token: nd_verify alone)'),
                    provenance='recomputed', source_file=f'nd-rl:robbie-experiments:{path}')
        n = xs[0][0]
        assert all(a == n for a, _ in xs)
        out.append({**base, 'metric': 'solved', 'k': n, 'value': sum(1 for _, c in xs if c > 0),
                    'apples_group': group(pool, n, '0.8', chk)})
        for kk in KS:
            out.append({**base, 'metric': 'pass_at_k_expected_solved', 'k': kk,
                        'value': round(sum(passk(n, c, kk) for _, c in xs), 3),
                        'apples_group': group(pool, kk, '0.8', chk)})
    return out


def copied_D(D):
    """Robbie numbers with no per-theorem file in git: copy D rows on our three pools (skip what we recompute)."""
    out = []
    for r in D:
        if r['pool'] not in ('textbook72', 'dev1108', 'holdout250') or r['provenance'] == 'recomputed':
            continue
        if r['family'].startswith('robbie-factorial:') and r['pool'] != 'dev1108':
            continue
        r = dict(r)
        if r['metric'] == 'dev_solved_cumulative' or r['temperature'] not in ('0.8', ''):
            g = f'{r["pool"]}|{r["metric"]}|T{r["temperature"]}|test-time-training-on-dev (not comparable)'
        else:
            g = group(r['pool'], r['k'], r['temperature'], r['checker'])
            if r['family'].startswith('robbie-autoresearch') and r['seed'] in ('', 'mean'):
                g += '|3-seed-mean'
        r['apples_group'] = g
        out.append(r)
    return out


# ----------------------------------------------------------------------------------------- cross-check vs C
def norm_stage(fam, stage, judge):
    x = re.search(r'sample seed x(\d)', judge or '')
    x = x[1] if x else ''
    if fam == 'best-9.56M-cap12-trajectory' or fam == 'best-9.56M-cap6-trajectory':
        if stage in ('frozen', 'frozen@pend'):
            return 'frozen@pend', x
        if stage in ('T1', 'T1-from-pend'):
            return 'T1', x
    return stage, x


def cross_check_C(rows, C):
    mine = defaultdict(set)
    for r in rows:
        if r['metric'] in ('solved', 'dev_metric') and r['provenance'] == 'recomputed':
            mine[(r['family'], *norm_stage(r['family'], r['stage'], r['judge']), str(r['seed']), r['pool'])].add(
                (str(r['value']), r['source_file'].split('/')[-1]))
    res = []
    for c in C:
        if c['pool'] not in ('textbook72', 'dev1108', 'holdout250') or c['metric'] != 'solved':
            continue
        st, x = norm_stage(c['family'], c['stage'], c['judge'])
        if c['family'].endswith('trajectory') and not x:
            continue
        key = (c['family'], st, x, c['seed'], c['pool'])
        if key in mine:
            vals = {v for v, _ in mine[key]}
            res.append((key, c['value'], sorted(mine[key]), c['value'] in vals))
    return res


def main():
    D = list(csv.DictReader(open(f'{ATLAS}/raw/D_metrics.csv')))
    C = list(csv.DictReader(open(f'{ATLAS}/raw/C_metrics.csv')))
    checks = []
    rows = fork_rows(checks) + robbie_rows(D) + copied_D(D)
    for r in rows:
        r['k'], r['n_pool'] = str(r['k']), str(r['n_pool'])
    os.makedirs(f'{ATLAS}/data', exist_ok=True)
    for fn, pools in (('textbook72_harmonized.csv', {'textbook72'}),
                      ('dev_holdout_harmonized.csv', {'dev1108', 'holdout250'})):
        sel = [r for r in rows if r['pool'] in pools]
        sel.sort(key=lambda r: (r['apples_group'], r['family'], r['stage'], r['seed'], r['judge']))
        with open(f'{ATLAS}/data/{fn}', 'w', newline='') as f:
            w = csv.DictWriter(f, COLS, quoting=csv.QUOTE_ALL, extrasaction='ignore')
            w.writeheader()
            w.writerows(sel)
        prov = defaultdict(int)
        for r in sel:
            prov[r['provenance']] += 1
        print(f'{fn}: {len(sel)} rows {dict(prov)}')
    bad = [c for c in checks if c[2] != c[3]]
    print(f'recomputed solved vs read-out summary .json: {len(checks)} checked, {len(bad)} disagree')
    for b in bad:
        print('  DISAGREE', b)
    cc = cross_check_C(rows, C)
    print(f'recomputed vs C_metrics copied (summary text): {len(cc)} matched keys, '
          f'{sum(1 for x in cc if not x[3])} disagree')
    for key, cv, mv, ok in cc:
        if not ok:
            print('  DISAGREE', key, 'C=', cv, 'recomputed=', mv)
    # D factorial recomputation sanity: our solved@256 must equal D's recomputed solved
    dsol = {(r['family'], r['seed'], r['pool']): r['value'] for r in D
            if r['family'].startswith('robbie-factorial:') and r['metric'] == 'solved'}
    ours = {(r['family'], r['seed'], r['pool']): str(r['value']) for r in rows
            if r['family'].startswith('robbie-factorial:') and r['metric'] == 'solved'}
    dd = [(k, dsol[k], v) for k, v in ours.items() if k in dsol and dsol[k] != v]
    print(f'factorial solved vs D_metrics: {len(ours)} rows, {len(dd)} disagree', dd[:5])


if __name__ == '__main__':
    main()
