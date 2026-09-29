#!/usr/bin/env python3
"""Held-out greedy evaluation of one or more Stage-1 `lean_seq` checkpoints, judged by LEAN ALONE
(AGENT_POLICY.md, Dan 2026-09-27): a sample counts iff the literal sampled text parses in the strict
`lean_seq` grammar AND Lean 4 core accepts that literal text as a proof of the theorem.  `nd_verify`
is never called.

  python3 sd_eval.py --ckpts 'ckpts/sd/w_s0*.pt' --in data/p2/heldout.jsonl --outdir artifacts/sd/ev \
      [--batch 512] [--texts] [--tag-from-name]

Per checkpoint it writes
  <outdir>/<ckpt stem>.jsonl   one record per theorem: name, n_lines, depth3, parsed, lean_ok,
                               n_tok (term size: tokens of the literal Lean term), n_have
                               (+ text, when --texts)
  <outdir>/<ckpt stem>.json    per-bin and per-slice solve rates with Wilson intervals, the sampler
                               and Lean timings, and the checkpoint's own label (params, mode, args).
Slices: len2..len6, the depth-3 slice (pat.depth3, 500 records, all 6-line), the 6-line non-depth-3
complement, and overall.  Every count in the .json is recomputable from the .jsonl.
"""
import argparse, glob, json, math, os, sys, time, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import torch
from model import load_ckpt
from sample import generate
from lean_gate import lean_check          # Lean 4 core on the literal text; imported, not modified


def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def slices(recs):
    idx = {'all': list(range(len(recs)))}
    for L in sorted({r['n_lines'] for r in recs}):
        idx[f'len{L}'] = [i for i, r in enumerate(recs) if r['n_lines'] == L]
    d3 = [i for i, r in enumerate(recs) if (r.get('pat') or {}).get('depth3')]
    if d3:
        idx['depth3'] = d3
        L6 = {r['n_lines'] for i, r in enumerate(recs) if i in set(d3)}
        for L in sorted(L6):
            idx[f'nodepth3_len{L}'] = [i for i, r in enumerate(recs)
                                       if r['n_lines'] == L and not (r.get('pat') or {}).get('depth3')]
    return idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpts', nargs='+', required=True, help='paths or globs')
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--outdir', required=True)
    ap.add_argument('--batch', type=int, default=512)
    ap.add_argument('--max_new', type=int, default=400)
    ap.add_argument('--texts', action='store_true', help='also store the literal Lean text of every sample')
    ap.add_argument('--skip_done', action='store_true')
    a = ap.parse_args()
    import record    # results registry (REGISTRY.md): per-slice accuracy and term size of every checkpoint
    record.save_config(vars(a), a.outdir + '/')
    os.makedirs(a.outdir, exist_ok=True)
    recs = [json.loads(l) for l in open(a.inp) if l.strip()]
    idx = slices(recs)
    prompts = [r['prompt'] for r in recs]
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    cks = [c for pat in a.ckpts for c in sorted(glob.glob(pat))]
    print(f'{len(cks)} checkpoints, {len(recs)} theorems, slices ' +
          str({k: len(v) for k, v in idx.items()}), flush=True)
    for ck in cks:
        stem = os.path.basename(ck)[:-3] if ck.endswith('.pt') else os.path.basename(ck)
        fj, fs = os.path.join(a.outdir, stem + '.jsonl'), os.path.join(a.outdir, stem + '.json')
        if a.skip_done and os.path.exists(fs):
            print('skip', stem, flush=True)
            continue
        t0 = time.time()
        model, tok, extra = load_ckpt(ck, dev)
        assert hasattr(tok, 'statement'), f'{ck} is not a Lean-format checkpoint (mode {tok.mode})'
        # sample.generate() assigns python lists into `raw`, so it must be a numpy array, not a tensor
        raw = np.full((len(prompts), a.max_new), tok.pad, dtype=np.int64)
        stats = {}
        # gate=False returns the literal Lean text of each sample (None if it never emitted <eos>);
        # `raw` receives the sampled token ids, so the strict-grammar verdict is read off the same ids.
        texts = generate(model, tok, prompts, greedy=True, temperature=0.0, max_new=a.max_new,
                         batch=a.batch, seed=0, stats=stats, gate=False, raw=raw)
        t_samp = time.time() - t0
        nd = [tok.decode(row.tolist()) for row in raw]
        parsed = [bool(tx) and not d.startswith('LEANPARSE') for tx, d in zip(texts, nd)]
        parse_reasons = collections.Counter(d[10:].strip() for d, tx in zip(nd, texts) if d.startswith('LEANPARSE'))
        del raw
        items, where = [], []
        for i, (p, tx) in enumerate(zip(prompts, texts)):
            if parsed[i]:
                items.append((tok.statement(p), tx)); where.append(i)
        ok, wall, proc = lean_check(items)
        lean_ok = [False] * len(prompts)
        for i, o in zip(where, ok):
            lean_ok[i] = bool(o)
        rows = []
        for i, r in enumerate(recs):
            tx = texts[i] or ''
            row = {'name': r.get('name'), 'n_lines': r['n_lines'],
                   'depth3': bool((r.get('pat') or {}).get('depth3')),
                   'parsed': parsed[i], 'lean_ok': lean_ok[i],
                   'n_tok': len(tx.split()), 'n_have': tx.count('have')}
            if a.texts:
                row['text'] = tx
            rows.append(row)
        with open(fj, 'w') as f:
            for row in rows:
                f.write(json.dumps(row) + '\n')
        out = {'ckpt': ck, 'heldout': a.inp, 'n': len(recs), 'judge': 'lean_alone',
               'judge_detail': 'strict lean_seq grammar parse AND lean 4 core accepts the literal text',
               'sampler': {'greedy': True, 'temperature': 0.0, 'batch': a.batch, 'max_new': a.max_new,
                           'path': os.environ.get('ND_SAMPLE_PATH', 'fast'),
                           'early': os.environ.get('ND_SAMPLE_EARLY', 'eos'),
                           'compact': os.environ.get('ND_SAMPLE_COMPACT', '1')},
               'model': {'n_params': extra.get('n_params'), 'mode': tok.mode,
                         'step': extra.get('step'), 'train_args': extra.get('args')},
               'timing': {'sample_s': t_samp, 'lean_wall_s': wall, 'lean_proc_s': proc,
                          'total_s': time.time() - t0},
               'parse_fail': sum(1 for x in parsed if not x),
               'parse_reasons': dict(parse_reasons.most_common(10)),
               'lean_rej_of_parsed': sum(1 for i in where if not lean_ok[i]),
               'slices': {}}
        for name, ii in idx.items():
            k = sum(1 for i in ii if lean_ok[i])
            lo, hi = wilson(k, len(ii))
            tk = [rows[i]['n_tok'] for i in ii if lean_ok[i]]
            hv = [rows[i]['n_have'] for i in ii if lean_ok[i]]
            out['slices'][name] = {'solved': k, 'n': len(ii), 'rate': k / max(len(ii), 1),
                                   'ci': [lo, hi],
                                   'mean_term_size': (sum(tk) / len(tk)) if tk else None,
                                   'mean_written_lines': ((sum(hv) / len(hv)) + 1) if hv else None}
        json.dump(out, open(fs, 'w'), indent=1)
        record.sdeval_rows(out, fs)
        s = out['slices']
        print(f"{stem}: all {s['all']['rate']:.4f} len6 {s.get('len6',{}).get('rate',0):.4f} "
              f"depth3 {s.get('depth3',{}).get('rate',0):.4f} | parse-fail {out['parse_fail']} "
              f"lean-rej {out['lean_rej_of_parsed']} | {t_samp:.0f}s sample {wall:.0f}s lean", flush=True)
        del model


if __name__ == '__main__':
    main()
