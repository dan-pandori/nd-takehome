#!/usr/bin/env python3
"""Assemble kalmar_complexity/measures.csv: one row per algorithm x measure (run kalmar-complexity).

  .venv-tok/bin/python kalmar_complexity/build_measures.py

Columns: algorithm, measure, value, units, language, method, source.  Sources (all in the repository):
  artifacts/kc/python_sizes.json                Python programs (programs/python/measure.py)
  kalmar_complexity/programs/blc/results.json   BLC / binary CL programs (programs/blc), if present
  kalmar_complexity/programs/rasp/results.json  RASP-L programs (programs/rasp), if present
  artifacts/kc/dtree/tree_u_b3.json             decision procedure
  artifacts/kc/b1_preq.json                     B1 prequential code / EDL from kalmar-pretrain's logs
  artifacts/kc/b2/*.json                        B2 block-wise prequential code / EDL, if present
  artifacts/kc/q4/states_tf1200.json.gz         per-step operations of policy.py (Kt per step)
"""
import csv, glob, gzip, json, math, os, statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, p)
ROWS = []


def add(alg, meas, val, units, lang, method, src):
    if val is None:
        return
    ROWS.append({'algorithm': alg, 'measure': meas, 'value': round(val, 6) if isinstance(val, float) else val,
                 'units': units, 'language': lang, 'method': method, 'source': src})


PY_ALG = {
    'K-sl algorithm': ('Kalmar sl (K12-Kalmar)', 'algorithm'),
    'K-sl render ND': ('Kalmar sl (K12-Kalmar)', 'rendering: ND text'),
    'K-sl render lean_seq': ('Kalmar sl (K12-Kalmar)', 'rendering: lean_seq (canonical names)'),
    'parse (prompt -> sequent)': ('parse (prompt -> sequent)', 'parse'),
    'K-sl algorithm + ND render': ('Kalmar sl (K12-Kalmar)', 'algorithm + ND rendering'),
    'K-sl algorithm + lean_seq render': ('Kalmar sl (K12-Kalmar)', 'algorithm + lean_seq rendering'),
    'K-sl end to end (parse + algorithm + ND)': ('Kalmar sl (K12-Kalmar)', 'parse + algorithm + ND rendering'),
    'K-sl end to end (parse + algorithm + lean_seq)': ('Kalmar sl (K12-Kalmar)', 'parse + algorithm + lean_seq rendering'),
    'K-tt algorithm': ('Kalmar tt (tt_prover per-atom split)', 'algorithm'),
    'K-tt render Lean': ('Kalmar tt (tt_prover per-atom split)', 'rendering: Lean term text'),
    'K-tt algorithm + Lean render': ('Kalmar tt (tt_prover per-atom split)', 'algorithm + Lean rendering'),
    'K-tt end to end (parse + algorithm + Lean)': ('Kalmar tt (tt_prover per-atom split)', 'parse + algorithm + Lean rendering'),
    'K-sl per-step policy (state -> lean_seq action)': ('Kalmar sl per-step policy', 'state -> action (incl. state parsing and action rendering)'),
    'mech: kalmar/kalmar.py (builder + render)': ('Kalmar sl (K12-Kalmar)', 'mechanical minification of the builder file'),
    'mech: tt_prover.py (whole file)': ('Kalmar tt (tt_prover per-atom split)', 'mechanical minification of the whole file'),
    'mech: gen.py (K12 generator, all knobs)': ('K12 generator', 'mechanical minification of gen.py (all knobs; upper bound)'),
    'mech: policy.py (per-step policy)': ('Kalmar sl per-step policy', 'mechanical minification of policy.py'),
}
CAL = {'copy': 'copy', 'reverse': 'reverse', 'parity': 'parity', 'parity_nb': 'parity', 'sort': 'sort',
       'sort_nb': 'sort', 'add': 'addition', 'add_nb': 'addition', 'eval': 'eval (formula truth value)',
       'taut': 'taut (truth-table validity)'}


def python():
    P = json.load(open(A('artifacts/kc/python_sizes.json')))
    src = 'artifacts/kc/python_sizes.json'
    for k, v in P.items():
        if k.startswith('calib '):
            c = k[6:]
            alg, part = CAL[c], ('algorithm, no builtins' if c.endswith('_nb') else 'algorithm, with builtins')
        else:
            alg, part = PY_ALG[k]
        meth = (v.get('method') or 'hand-golfed') + f'; part: {part}; files {",".join(v["files"])}'
        add(alg, 'program length (raw)', v['raw_bytes'] * 8, 'bits', 'Python 3 (minified source)', meth, src)
        add(alg, 'program length (DEFLATE)', v['deflate_bytes'] * 8, 'bits', 'Python 3, raw DEFLATE level 9', meth, src)
        add(alg, 'program length (xz)', v['xz_bytes'] * 8, 'bits', 'Python 3, raw LZMA2 preset 9e', meth, src)
        add(alg, 'program length (tokens)', v['qwen3_tokens'], 'Qwen3 tokens', 'Python 3, Qwen3 tokenizer', meth, src)
        add(alg, 'program length (tokens)', v['gpt2_tokens'], 'GPT-2 tokens', 'Python 3, GPT-2 BPE', meth, src)


def blc():
    f = A('kalmar_complexity/programs/blc/results.json')
    if not os.path.exists(f):
        return
    R = json.load(open(f))
    src = 'kalmar_complexity/programs/blc/results.json'
    names = {'parse': ('parse (prompt -> sequent)', 'parse'), 'K-sl algorithm': ('Kalmar sl (K12-Kalmar)', 'algorithm'),
             'K-sl rendering': ('Kalmar sl (K12-Kalmar)', 'rendering: ND tokens'),
             'K-tt algorithm': ('Kalmar tt (tt_prover per-atom split)', 'algorithm'),
             'K-tt rendering': ('Kalmar tt (tt_prover per-atom split)', 'rendering: Lean text'),
             'K-sl algorithm + rendering': ('Kalmar sl (K12-Kalmar)', 'algorithm + rendering'),
             'K-sl parse + algorithm + rendering': ('Kalmar sl (K12-Kalmar)', 'parse + algorithm + rendering'),
             'K-tt algorithm + rendering': ('Kalmar tt (tt_prover per-atom split)', 'algorithm + rendering'),
             'K-tt parse + algorithm + rendering': ('Kalmar tt (tt_prover per-atom split)', 'parse + algorithm + rendering')}
    for name, v in R['programs'].items():
        if name.startswith('calib '):
            alg, part = CAL[name[6:]], 'algorithm'
        else:
            alg, part = names[name]
        ok = f"; {v['pass']}/{v['cases']} test cases exact" if 'pass' in v else ''
        m = f"part: {part}; file {v.get('file', 'sum of parts')}{ok}"
        add(alg, 'program length', v['blc_bits'], 'bits', 'binary lambda calculus (Tromp)', m, src)
        add(alg, 'program length', v['cl_bits'], 'bits', 'binary combinatory logic (S, K; bracket abstraction)', m, src)
        if 'beta' in v:
            add(alg, "Levin's Kt (program bits + log2 median beta-steps)", v['Kt_bits_median'], 'bits',
                'binary lambda calculus (Tromp)', m + f"; beta-steps median {v['beta']['median']}, mean {v['beta']['mean']:.0f}", src)


def rasp():
    f = A('kalmar_complexity/programs/rasp/results.json')
    if not os.path.exists(f):
        return
    R = json.load(open(f))
    src = 'kalmar_complexity/programs/rasp/results.json'
    lang = 'RASP-L (Zhou et al. 2023; flagged non-RASP-L ops counted in method)'
    for part, lab in (('decision', 'per-step decision'), ('rendering', 'action rendering'), ('total', 'decision + rendering')):
        v = R[part]
        m = f"part: {lab}; H = {R['H']} formula levels; flagged non-RASP-L ops {v['flagged_ops']}"
        add('Kalmar sl per-step policy', 'program length', v['ops'], 'RASP-L primitive ops', lang, m, src)
        add('Kalmar sl per-step policy', 'program length (source)', v['source_tokens'], 'source tokens', lang, m, src)
        d = v.get('attn_depth', v.get('attn_depth_added'))
        add('Kalmar sl per-step policy', 'attention depth' + (' (added)' if part == 'rendering' else ''), d,
            'select-aggregate layers', lang, m, src)
    names = {'copy': 'copy', 'reverse': 'reverse', 'sort': 'sort', 'parity': 'parity', 'addition': 'addition',
             'eval': 'eval (formula truth value)', 'taut': 'taut (truth-table validity)'}
    for r in R['calibration']['rows']:
        t = r['task']
        alg = next((v for k, v in names.items() if t.startswith(k)), t)
        m = f"variant {t}; {r['cases']} random cases, {r['exact']} exact; flagged {r['flagged_ops']}; published: {r.get('published')}"
        add(alg, 'program length', r['ops'], 'RASP-L primitive ops', lang, m, src)
        add(alg, 'program length (source)', r['source_tokens'], 'source tokens', lang, m, src)
        add(alg, 'attention depth', r['attn_depth'], 'select-aggregate layers', lang, m, src)


def dtree():
    T = json.load(open(A('artifacts/kc/dtree/tree_u_b3.json')))
    m = (f"smallest tree found (beam {T['beam']}) over {T['features']} generic state features, exact on "
         f"{T['distinct_rows']} distinct rows (4,000 theorems) and a fresh 2,000; given the feature extractor")
    add('Kalmar sl per-step policy', 'decision procedure size', T['bits'], 'bits', 'decision tree (prefix code)', m,
        'artifacts/kc/dtree/tree_u_b3.json')
    add('Kalmar sl per-step policy', 'decision procedure leaves', T['leaves'], 'leaves', 'decision tree', m,
        'artifacts/kc/dtree/tree_u_b3.json')


def preq():
    B = json.load(open(A('artifacts/kc/b1_preq.json')))
    for name, v in B.items():
        alg = 'Kalmar sl (K12-Kalmar)' if name.startswith('KAL') else 'K12 proof style (K12 control data)'
        lr = 'kalmar-pretrain KAL-D' if name.startswith('KAL') else 'best-state control (stage1_best12)'
        meth = f'{lr} {name.split()[-1]}, 9.56 M ALiBiGPT, first epoch from logged curve'
        add(alg, 'prequential code, first epoch (B1)', v['L_preq_bits'], 'bits', 'learner: ' + lr, meth,
            'artifacts/kc/b1_preq.json')
        for k, lab in (('b_final_val', 'residual = final held-out loss'), ('a_final_train', 'residual = final train loss'),
                       ('c_epoch1_end', 'residual = loss at end of epoch 1')):
            add(alg, f'absorbed bits EDL (B1, {lab})', v['EDL_bits'][k], 'bits', 'learner: ' + lr, meth,
                'artifacts/kc/b1_preq.json')
    for f in sorted(glob.glob(A('artifacts/kc/b2/*.json'))):
        R = json.load(open(f))
        if 'summary' not in R:
            continue
        a = R['args']
        alg = {'kal': 'Kalmar sl (K12-Kalmar)', 'k12': 'K12 proof style (K12 control data)',
               'eval': 'eval (formula truth value)'}[a['task']]
        v2 = 'v2 ' if a.get('patience_steps') else ''
        meth = (f"B2 {v2}block-wise, size {a['size']}, seed {a['seed']}, {R['summary']['theorems']} theorems, AdamW "
                f"+ early stopping")
        rel = os.path.relpath(f, ROOT)
        add(alg, f'prequential code (B2 {v2}{a["size"]})', R['summary']['prequential_bits'], 'bits',
            f'learner: ALiBiGPT {a["size"]}', meth, rel)
        add(alg, f'absorbed bits EDL (B2 {v2}{a["size"]})', R['summary']['EDL_bits'], 'bits',
            f'learner: ALiBiGPT {a["size"]}', meth, rel)


def kt_steps():
    S = json.load(gzip.open(A('artifacts/kc/q4/states_tf1200.json.gz'), 'rt'))
    ops = [s['ops'] for s in S]
    add('Kalmar sl per-step policy', 'per-step operations (mean)', statistics.mean(ops), 'operations',
        'policy.py (evaluations + lookups + recursion calls)', 'all 137,984 tf1200 states',
        'artifacts/kc/q4/states_tf1200.json.gz')


def main():
    for f in (python, blc, rasp, dtree, preq, kt_steps):
        f()
    out = A('kalmar_complexity/measures.csv')
    with open(out, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=['algorithm', 'measure', 'value', 'units', 'language', 'method', 'source'])
        w.writeheader()
        w.writerows(ROWS)
    print(f'{len(ROWS)} rows -> {out}')


if __name__ == '__main__':
    main()
