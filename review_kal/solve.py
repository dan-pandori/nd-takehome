#!/usr/bin/env python3
"""E4 recount: solve rates from the stored per-theorem rows (artifacts/kalmar/eval/*.rows.jsonl.gz, and the control's stored
best-state k 256 reads in artifacts/kalmar/ctl_stored/).  Own pass@k (unbiased), own atom counts and algorithm lengths
(kc.kalmar), own L_true join for rr600 (data/ladder/transfer_long_rr600.jsonl n_lines), cut-offs per stratum.
No textbook72 theorem is printed (aggregates only).

  python3 review_kal/solve.py -> out/solve.json, out/solve_table.txt
"""
import collections, json, os, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kc

E = os.path.join(kc.ROOT, 'artifacts', 'kalmar', 'eval')
CS = os.path.join(kc.ROOT, 'artifacts', 'kalmar', 'ctl_stored')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
LT = {r['name']: r['n_lines'] for r in kc.rows(os.path.join(kc.ROOT, 'data', 'ladder', 'transfer_long_rr600.jsonl'))}
INFO = {}


def info(prompt):
    if prompt not in INFO:
        m = kc.kalmar(prompt)
        INFO[prompt] = (m['n_atoms'], len(m['acts']), len(kc.split_prompt(prompt)[0])) if m else (None, None, None)
    return INFO[prompt]


def lbin(n):
    return '<100' if n < 100 else '100-199' if n < 200 else '200-299' if n < 300 else '>=300'


def strata(file, name, prompt):
    na, nact, npr = info(prompt)
    ks = [file, f'{file}|atoms={na}', f'{file}|alen={lbin(nact)}', f'ALL|atoms={na}', f'ALL|alen={lbin(nact)}']
    if file == 'transfer_long_rr600':
        L = LT[name]
        ks.append('rr600_Q' if 13 <= L <= 16 else 'rr600_11-12' if L in (11, 12) else f'rr600_L{L}')
    if file in ('transfer_long_ge17', 'transfer_long2'):
        ks.append('ge17_91')
    if file in ('candidate_v0', 'candidate_v1', 'batch3', 'hand_proved_14'):
        ks.append('release_all')
        if npr < 4:
            ks.append('release_ex4prem')
    return ks


res = {}
for fn in sorted(glob.glob(os.path.join(E, '*.rows.jsonl.gz'))):
    tag = os.path.basename(fn).replace('.rows.jsonl.gz', '')
    summ = json.load(open(fn.replace('.rows.jsonl.gz', '.json')))
    k = summ['k']
    agg = collections.defaultdict(collections.Counter)
    solved_names = collections.defaultdict(list)
    chk = collections.Counter()
    maxsteps = 0
    for r in kc.rows(fn):
        ok = r['ok']
        chk['rows'] += 1
        chk['nok_consistent'] += (r['n_ok'] == sum(ok) == sum(r['accepted'].values()) and len(ok) == k)
        chk['ok_only_done'] += all(s == 'done' for s, o in zip(r['status'], ok) if o)
        maxsteps = max(maxsteps, max(r['steps']))
        c = sum(ok)
        for s in strata(r['file'], r['name'], r['prompt']):
            a = agg[s]
            a['n'] += 1; a['solved'] += c > 0; a['attempts'] += k; a['ok'] += c
            for kk in (1, 8, 16, 32):
                if kk <= k:
                    a[f'p@{kk}'] += kc.unbiased_pass(k, c, kk)
            for st in r['status']:
                a['trunc'] += st == 'fail:truncated'
                a['stepcap'] += st == 'fail:step_cap'
        if c > 0 and r['file'] != 'textbook72':
            solved_names[r['file']].append(r['name'])
    res[tag] = {'arm': summ['arm'], 'k': k, 'seed': summ['seed'], 'batch': summ['batch'], 'max_steps': summ['max_steps'],
                'ckpt': summ['ckpt'], 'gpu': summ['gpu'], 'stored_solved': summ['solved'], 'checks': dict(chk), 'max_steps_reached': maxsteps,
                'agg': {s: dict(v) for s, v in agg.items()}, 'solved_names': solved_names}
    mism = {f: (agg[f]['solved'], v) for f, v in summ['solved'].items() if agg[f]['solved'] != v}
    print(f"{tag:28s} k {k:3d} b {summ['batch']} rows {chk['rows']} consistent {chk['nok_consistent']} okdone {chk['ok_only_done']} "
          f"maxsteps {maxsteps} stored-solved-mismatch {mism}", flush=True)

# the control's stored best-state reads (k 256, max_steps 96): rows {name, prompt, n_ok, n_tried, reasons}
FILEOF = {'h250': 'holdout250', 'long2': 'transfer_long2', 'rr600': 'transfer_long_rr600', 'tb72': 'textbook72'}
for fn in sorted(glob.glob(os.path.join(CS, '*.jsonl'))):
    tag = os.path.basename(fn).replace('.jsonl', '')
    mdl, st = tag.split('__')
    agg = collections.defaultdict(collections.Counter)
    reasons = collections.Counter()
    for r in kc.rows(fn):
        k, c = r['n_tried'], r['n_ok']
        rs = r['reasons']
        if isinstance(rs, str):
            import ast
            try:
                rs = ast.literal_eval(rs)
            except Exception:
                rs = [rs]
        if isinstance(rs, dict):
            for x, n in rs.items():
                reasons[x] += n
        else:
            for x in rs:
                reasons[x] += 1
        for s in strata(FILEOF[st], r['name'], r['prompt']):
            a = agg[s]
            a['n'] += 1; a['solved'] += c > 0; a['attempts'] += k; a['ok'] += c
            for kk in (1, 8, 16, 32, 256):
                a[f'p@{kk}'] += kc.unbiased_pass(k, c, kk)
    res['stored:' + tag] = {'k': 256, 'agg': {s: dict(v) for s, v in agg.items()},
                            'reasons_step': {x: n for x, n in reasons.items() if 'step' in x or 'cap' in x},
                            'reasons_trunc': {x: n for x, n in reasons.items() if 'trunc' in x or 'max_new' in x}}
    print(f"stored:{tag:22s} {FILEOF[st]} n {agg[FILEOF[st]]['n']} solved {agg[FILEOF[st]]['solved']} "
          f"step/cap reasons {res['stored:' + tag]['reasons_step']} trunc {res['stored:' + tag]['reasons_trunc']}", flush=True)
json.dump(res, open(os.path.join(OUT, 'solve.json'), 'w'))
