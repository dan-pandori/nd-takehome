#!/usr/bin/env python3
"""B1: prequential code length of the first training epoch, from kalmar-pretrain's logged curves (run kalmar-complexity).

  python3 kalmar_complexity/b1_preq.py            # -> artifacts/kc/b1_preq.json + a table on stdout

Source of the curves: each checkpoint's `extra['curve']` (`kalmar_complexity/ckpt_meta.py`; for KAL-D the same points
are printed in `artifacts/kalmar/logs/train_kalD_s*.log`).  A curve point's `train_loss` is the mean, over every 20th
step since the previous point, of the pre-update next-token loss on the batch (nats per loss token; loss tokens =
action tokens + <eos>), so in the first epoch -- every pair seen once, scored before the update that uses it -- the
points sample a prequential code:

  L_preq = sum_i loss_i * N * (e_i - e_{i-1}) / ln 2      over the intervals of epoch 1 (the last one cut at e = 1)

with N = loss tokens per epoch (`kalmar_complexity/count_tokens.py`, exact) and e_i the logged epoch fraction.
Absorbed bits (excess / model part of a two-part code, Donoway 2026; Whitney et al. 2020): EDL = L_preq - N * L_inf / ln 2
for three choices of L_inf: (a) the final train loss (end of training), (b) the final held-out loss (`final_val`),
(c) the train loss at the end of epoch 1.  Bias bound: steps 1-19 are never sampled; if they cost the uniform code
(log2 V per token) they would add at most `bias_bound_bits`.
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ckpt_meta import meta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LN2 = math.log(2)
MODELS = {f'KAL-D s{s}': (f'ckpts/kc_src/stage1_kalD_s{s}.pt', 'artifacts/kc/tokens_kal_sl.json') for s in range(3)}
MODELS.update({f'control s{s}': (f'ckpts/kc_src/stage1_best12_s{s}_b1200.pt', 'artifacts/kc/tokens_k12.json')
               for s in range(3)})


def preq(curve, N, bpe, V):
    pts = sorted(curve, key=lambda p: p['step'])
    L, e0, s0 = 0.0, 0.0, 0
    rows = []
    end_loss = None
    for p in pts:
        e1 = min(p['epochs'], 1.0)
        if e1 <= e0:
            break
        tok = N * (e1 - e0)
        L += p['train_loss'] * tok / LN2
        rows.append({'step': p['step'], 'epochs': round(p['epochs'], 4), 'loss_nats': p['train_loss'],
                     'tokens': tok, 'bits': p['train_loss'] * tok / LN2})
        end_loss = p['train_loss']
        e0, s0 = e1, p['step']
        if p['epochs'] >= 1.0:
            break
    tok_per_step = N / bpe
    first = pts[0]['train_loss']
    bias = 19 * tok_per_step * max(0.0, math.log2(V) - first / LN2)
    return L, end_loss, rows, bias


def main():
    out = {}
    print(f"{'model':12} {'N loss tok':>13} {'L_preq bits':>12} {'bits/tok':>8} {'L_inf a/b/c (nats)':>26} "
          f"{'EDL a':>11} {'EDL b':>11} {'EDL c':>11} {'bias<=':>9}")
    for name, (ck, tf) in MODELS.items():
        o = meta(os.path.join(ROOT, ck))
        ex = o['extra']
        tk = json.load(open(os.path.join(ROOT, tf)))
        N = tk['loss_tokens']
        V = o['cfg'].get('vocab') if isinstance(o.get('cfg'), dict) else None
        V = V or 128
        L, end_loss, rows, bias = preq(ex['curve'], N, ex['batches_per_epoch'], V)
        la, lb, lc = ex['last_train_loss'], ex['final_val'], end_loss
        edl = {k: L - N * x / LN2 for k, x in (('a_final_train', la), ('b_final_val', lb), ('c_epoch1_end', lc))}
        out[name] = {'ckpt': ck, 'tokens_file': tf, 'N_loss_tokens': N, 'pairs': tk['pairs'], 'vocab': V,
                     'L_preq_bits': L, 'bits_per_token': L / N, 'L_inf_nats': {'a_final_train': la, 'b_final_val': lb,
                     'c_epoch1_end': lc}, 'EDL_bits': edl, 'bias_bound_bits': bias, 'intervals': rows,
                     'steps_epoch1': ex['batches_per_epoch'], 'n_params': ex.get('n_params') or o['cfg']}
        print(f"{name:12} {N:13,} {L:12.4g} {L / N:8.4f} {la:8.4f}/{lb:7.4f}/{lc:7.4f}   "
              f"{edl['a_final_train']:11.4g} {edl['b_final_val']:11.4g} {edl['c_epoch1_end']:11.4g} {bias:9.3g}")
    json.dump(out, open(os.path.join(ROOT, 'artifacts/kc/b1_preq.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
