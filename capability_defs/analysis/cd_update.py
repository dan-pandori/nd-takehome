#!/usr/bin/env python3
"""capability-defs Part 3, card kl-update-size (parameter view): how big is RL's update, against reference updates?

  ~/venv-cpu/bin/python capability_defs/analysis/cd_update.py > capability_defs/analysis/out/update_size.txt

Seed 0, cap 12 (best-cap12, 9,560,832 params).  Updates (theta_b - theta_a, every 2-D weight matrix):
  RL r8        pend -> r8            (8 EI rounds: 4,800 fine-tune steps on RL proofs + replay)
  RL r16       pend -> r16
  replay-only  pend -> rc_pend_r8    (rl-from-ckpt control: the same 8 rounds of fine-tuning, replay only, no RL proofs)
  late PT      step 20,000 -> pend   (the last ≈ 4,000 pretraining steps)
  seed gap     pend s0 vs pend s1    (two independent pretraining runs; a scale for "different model")
Reported per update: relative Frobenius norm sum||dW|| / sum||W_pend||, and the median over matrices of the effective
rank (number of singular values carrying 90 % of ||dW||^2) as a share of full rank; plus the cosine between the RL and
replay-only updates (are they the same direction?).
"""
import os, sys
import numpy as np
import torch

H = os.path.expanduser('~')
CK = {'pend': f'{H}/review/trajectory/rv/ck/stage1_best12_s0_b1200.pt', 'pend1': f'{H}/review/trajectory/rv/ck/stage1_best12_s1_b1200.pt',
      'r8': f'{H}/review/trajectory/rv/ck/la_T1_best12_s0_r8.pt',
      'r16': os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../artifacts/cd/ck/la_T1_best12_s0_r16.pt'),
      'ctrl': os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../artifacts/cd/ck/rc_best12_s0_pend_r8.pt'),
      'p20000': os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../artifacts/cd/ck/stage1_best12_s0_b1200_step20000.pt')}


def sd(path):
    d = torch.load(path, map_location='cpu', weights_only=False)
    m = d.get('state', d.get('model', d.get('state_dict', d)))
    return {k: v.float().numpy() for k, v in m.items() if hasattr(v, 'dim') and v.dim() == 2}


def effrank(M, q=0.9):
    s = np.linalg.svd(M, compute_uv=False) ** 2
    c = np.cumsum(s) / s.sum()
    return int(np.searchsorted(c, q) + 1), min(M.shape)


def main():
    W = {k: sd(v) for k, v in CK.items()}
    keys = sorted(set(W['pend']) & set(W['r8']) & set(W['ctrl']) & set(W['p20000']) & set(W['pend1']))
    base = sum(np.linalg.norm(W['pend'][k]) for k in keys)
    upd = {'RL r8': ('pend', 'r8'), 'RL r16': ('pend', 'r16'), 'replay-only r8': ('pend', 'ctrl'),
           'late PT (20k->end)': ('p20000', 'pend'), 'seed gap (pend s0 vs s1)': ('pend1', 'pend')}
    D = {}
    print(f'{len(keys)} weight matrices; sum ||W_pend|| = {base:.1f}')
    for lab, (a, b) in upd.items():
        d = {k: W[b][k] - W[a][k] for k in keys}
        D[lab] = d
        rel = sum(np.linalg.norm(v) for v in d.values()) / base
        er = [effrank(v) for v in d.values()]
        share = np.median([r / f for r, f in er])
        print(f'  {lab:26s} relative norm {rel:.4f}; effective rank (90 % energy) median share of full rank {share:.3f}')
    # direction: cosine between RL and replay-only updates, concatenated
    def vec(d):
        return np.concatenate([d[k].ravel() for k in keys])
    a, b = vec(D['RL r8']), vec(D['replay-only r8'])
    print(f'  cosine(RL r8 update, replay-only update) = {a @ b / np.linalg.norm(a) / np.linalg.norm(b):.3f}')
    c = vec(D['late PT (20k->end)'])
    print(f'  cosine(RL r8 update, late-PT update) = {a @ c / np.linalg.norm(a) / np.linalg.norm(c):.3f}; '
          f'cosine(replay-only, late-PT) = {b @ c / np.linalg.norm(b) / np.linalg.norm(c):.3f}')
    r = vec(D['RL r8']) - vec(D['replay-only r8'])
    print(f'  RL-specific part (r8 update minus replay-only update): relative norm {np.linalg.norm(r) / np.linalg.norm(vec({k: W["pend"][k] for k in keys})):.4f} '
          f'(vs r8 update {np.linalg.norm(a) / np.linalg.norm(vec({k: W["pend"][k] for k in keys})):.4f})')


if __name__ == '__main__':
    main()
