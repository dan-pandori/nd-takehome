#!/usr/bin/env python3
"""Reviewer: size of the weight update (s0, cap 12): relative Frobenius norm sum||dW|| / sum||W_pend|| over 2-D
weight matrices, and the cosine between the RL (pend -> r8) and replay-only (pend -> rc_pend_r8) updates."""
import os, torch, numpy as np
H = os.path.expanduser('~')
CK = {'pend': f'{H}/review/trajectory/rv/ck/stage1_best12_s0_b1200.pt', 'pend1': f'{H}/review/trajectory/rv/ck/stage1_best12_s1_b1200.pt',
      'r8': f'{H}/review/trajectory/rv/ck/la_T1_best12_s0_r8.pt', 'r16': f'{H}/review/capability-defs/artifacts/cd/ck/la_T1_best12_s0_r16.pt',
      'ctrl': f'{H}/review/capability-defs/artifacts/cd/ck/rc_best12_s0_pend_r8.pt', 'p20000': f'{H}/review/capability-defs/artifacts/cd/ck/stage1_best12_s0_b1200_step20000.pt'}
def mats(p):
    d = torch.load(p, map_location='cpu', weights_only=False)
    for k in ('model', 'state', 'state_dict'):
        if isinstance(d, dict) and k in d and isinstance(d[k], dict): d = d[k]; break
    return {k: v.float().numpy() for k, v in d.items() if hasattr(v, 'dim') and v.dim() == 2}
W = {k: mats(p) for k, p in CK.items()}
keys = sorted(W['pend'])
assert all(sorted(W[k]) == keys for k in W), 'key mismatch'
base = sum(np.linalg.norm(W['pend'][k]) for k in keys)
def rel(a, b): return sum(np.linalg.norm(W[b][k] - W[a][k]) for k in keys) / base
print('2-D matrices', len(keys))
for lab, (a, b) in {'RL r8': ('pend', 'r8'), 'RL r16': ('pend', 'r16'), 'replay-only r8': ('pend', 'ctrl'), 'late PT (p20000 -> pend)': ('p20000', 'pend'), 'seed gap (pend s0 vs s1)': ('pend', 'pend1')}.items():
    print(f'{lab:28s} relative Frobenius {rel(a, b):.3f}')
u = np.concatenate([(W['r8'][k] - W['pend'][k]).ravel() for k in keys]); v = np.concatenate([(W['ctrl'][k] - W['pend'][k]).ravel() for k in keys])
print('cosine(RL r8 update, replay-only update) %.3f' % (u @ v / np.linalg.norm(u) / np.linalg.norm(v)))
