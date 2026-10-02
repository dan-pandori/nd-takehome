"""Turn this run's re-score read-outs (artifacts/atlas/eval/*.jsonl, from atlas/scripts/rescore_job.sh) into harmonized
rows: atlas/data/rescore_wholeproof.csv (same columns as textbook72_harmonized.csv). Prints a per-read table with the
max_new truncation share. Reads in artifacts/atlas/b4096_partial/eval (the first attempt's reads that completed at batch
4,096) are kept as re-draw rows (judge says 're-read', so figures skip them).

All eight checkpoints: 3.2M (4 x 256), lean_seq whole proof, from scratch, Lean alone (eval_set -> lean_judge)."""
import csv, glob, json, math, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
OUT = os.path.join(ROOT, 'atlas', 'data', 'rescore_wholeproof.csv')
MODELS = {
    'c0fz': ('ours-3.2M-C0-wp-cap6', 'frozen', 'lean-format/ckpts/lf/stage1_a1_seq_s{s}.pt', '6',
             'cap-6 control (depth3 f0 a1) 155k'),
    'c0t1': ('ours-3.2M-C0-wp-cap6', 'T1', 'ds-generator/ckpts/ladder/la_T1_c0_s{s}_r8.pt', '6',
             'cap-6 control (depth3 f0 a1) 155k + T1 ladder r8'),
    'k12fz': ('ours-3.2M-K12-wp-cap12', 'frozen', 'cap-horizon/ckpts/kh/stage1_k12_s{s}.pt', '12', 'K12 155k'),
    'k12t1': ('ours-3.2M-K12-wp-cap12', 'T1', 'state-cap12/ckpts/ladder/la_T1_K12_s{s}_r8.pt', '12', 'K12 155k + T1 ladder r8'),
}
POOLS = {'tb72': ('textbook72', 72, 256), 'dev': ('dev1108', 1108, 64), 'h250': ('holdout250', 250, 256)}
KS = [1, 4, 16, 64, 256]
COLS = ['family', 'model_label', 'params', 'format', 'init', 'train_set', 'cap', 'stage', 'seed', 'pool', 'n_pool', 'metric',
        'k', 'temperature', 'value', 'checker', 'judge', 'date', 'provenance', 'source_file', 'apples_group']


def pass_at_k(n, c, k):
    if n - c < k:
        return 1.0
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)


rows, table = [], []
for sub, batch, tag in (('eval', 2048, ''), ('b4096_partial/eval', 4096, 're-read (first attempt, batch 4096); ')):
    for f in sorted(glob.glob(os.path.join(ROOT, 'artifacts', 'atlas', sub, '*__*.jsonl'))):
        m = re.match(r'(c0fz|c0t1|k12fz|k12t1)_s(\d)__(tb72|dev|h250)\.jsonl$', os.path.basename(f))
        if not m or not os.path.exists(f[:-1 * len('.jsonl')] + '.json'):
            continue
        key, seed, pool = m.groups()
        fam, stage, ck, cap, data = MODELS[key]
        pname, npool, kk = POOLS[pool]
        recs = [json.loads(l) for l in open(f)]
        assert len(recs) == npool, (f, len(recs))
        assert all(r['n_tried'] == kk for r in recs), f
        solved = sum(r['solved'] for r in recs)
        gs_f = f + '.genstats.json'
        gs = json.load(open(gs_f)) if os.path.exists(gs_f) else {}
        trunc = gs.get('truncated', float('nan')) / max(gs.get('rows', 0), 1) if gs else float('nan')
        rel = os.path.relpath(f, ROOT)
        base = dict(family=fam, model_label=f'{ck.format(s=seed)} (3.2M lean_seq whole proof)', params='3.2M',
                    format='lean_seq', init='scratch', train_set=data, cap=cap, stage=stage, seed=seed, pool=pname,
                    n_pool=npool, temperature='0.8', checker='lean_only',
                    judge=f'{tag}fork lean_judge (Lean 4.34 alone); eval_set whole-proof sampling, max_new 512, batch {batch}; sample seed 0',
                    date='2026-10-02', provenance='recomputed', source_file=f'fork:dan_evidence-atlas:{rel}',
                    apples_group=f'{pname}|k{kk}|T0.8|lean_only')
        rows.append(dict(base, metric='solved', k=kk, value=solved))
        for k in KS:
            if k <= kk:
                rows.append(dict(base, metric='pass_at_k_expected_solved', k=k,
                                 value=round(sum(pass_at_k(kk, r['n_ok'], k) for r in recs), 3)))
        table.append((key, seed, pool, batch, solved, npool, gs.get('rows'), gs.get('truncated'), trunc,
                      gs.get('peak_alloc_gb')))

with open(OUT, 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=COLS); w.writeheader(); w.writerows(rows)
print(f'{"model":6s} {"seed":4s} {"pool":5s} {"batch":5s} {"solved":>7s} {"samples":>8s} {"hit max_new":>11s} {"share":>7s} {"peak GB":>7s}')
for key, seed, pool, b, s, n, nr, nt, tr, pk in table:
    print(f'{key:6s} {seed:4s} {pool:5s} {b:5d} {s:4d}/{n:<4d} {nr or 0:8d} {nt or 0:11d} {tr:7.4%} {pk or float("nan"):7.2f}')
print('rows', len(rows), '->', os.path.relpath(OUT, ROOT))
