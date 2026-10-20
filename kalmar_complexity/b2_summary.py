#!/usr/bin/env python3
"""B2 summary table (run kalmar-complexity): per run, prequential code and EDL over [0, max_thm) and over [0, 8192)
(the common prefix for comparing sizes; EDL_8192 uses the per-token code of block [8192, 16384) -- or of the asymptote
block when max_thm = 8192 -- as L_inf).  -> artifacts/kc/b2_summary.json"""
import glob, json, math, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = {}
print(f"{'run':16} {'thm':>6} {'preq bits':>11} {'EDL bits':>11} {'Linf b/tok':>10} | {'preq@8192':>11} {'EDL@8192':>11} {'tokens@8192':>12} {'train steps':>11} {'GPU-s':>7}")
for f in sorted(glob.glob(os.path.join(ROOT, 'artifacts/kc/b2/*.json'))):
    R = json.load(open(f)); name = os.path.basename(f)[:-5]
    if 'summary' not in R:
        print(f'{name:16} (running: {len(R["blocks"]) - 1} model blocks done)'); continue
    S = R['summary']; B = R['blocks']
    pre8 = [b for b in B if b['block'][1] <= 8192]
    nxt = next(b for b in B if b['block'][0] == 8192)
    L8 = sum(b['bits'] for b in pre8); N8 = sum(b['loss_tokens'] for b in pre8)
    linf8 = nxt['bits'] / nxt['loss_tokens']
    steps = sum(b.get('steps', 0) for b in B); secs = sum(b.get('secs', 0) for b in B)
    out[name] = {'args': R['args'], 'summary': S, 'preq_8192': L8, 'tokens_8192': N8, 'Linf_8192_bits_per_tok': linf8,
                 'EDL_8192': L8 - N8 * linf8, 'train_steps': steps, 'train_tokens': sum(b.get('train_tokens', 0) for b in B),
                 'train_secs': secs, 'gpu': R.get('gpu')}
    print(f"{name:16} {S['theorems']:6} {S['prequential_bits']:11.4g} {S['EDL_bits']:11.4g} {S['L_inf_bits_per_token']:10.4f} | "
          f"{L8:11.4g} {L8 - N8 * linf8:11.4g} {N8:12,} {steps:11,} {secs:7.0f}")
json.dump(out, open(os.path.join(ROOT, 'artifacts/kc/b2_summary.json'), 'w'), indent=1)
