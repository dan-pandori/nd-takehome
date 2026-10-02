#!/usr/bin/env python3
"""value_head.py -- a value head on the frozen policy trunk (run `mcts-a`, proposal 22, Phase 0).

Input: the feature `mcts.Sampler` computes for a state in the same forward that samples its actions -- ln_f of the
last state token (`<act>`) concatenated with ln_f of the mean hidden state over the state's tokens (2 x d).  The trunk
is frozen: the head never back-propagates into the policy, so the policy is unchanged (Phase A attributes any gain to
search).

Outputs, per state:
  solvable logit  s   trained with soft BCE on the fraction of the policy's rollouts through the state that ended in
                      a Lean-accepted proof (states on failed attempts count as "unsolved" -- a state reached by both
                      kinds of attempt gets the empirical fraction: HTPS's soft critic, W/N);
  steps-to-go     d   Huber regression on the mean number of actions the successful rollouts through the state still
                      took (only states with at least one success).
Search value (AlphaProof's Q = gamma^(steps-to-go), times the chance the state is solvable at all):
  v = sigmoid(s) * gamma^max(d, 0)
"""
import torch
import torch.nn as nn


class ValueHead(nn.Module):
    def __init__(self, d_in, hidden=512, gamma=0.95):
        super().__init__()
        self.cfg = dict(d_in=d_in, hidden=hidden, gamma=gamma)
        self.net = nn.Sequential(nn.LayerNorm(d_in), nn.Linear(d_in, hidden), nn.GELU(), nn.Linear(hidden, hidden),
                                 nn.GELU(), nn.Linear(hidden, 2))
        self.gamma = gamma

    def forward(self, x):
        o = self.net(x)
        return o[:, 0], o[:, 1]

    @torch.no_grad()
    def value(self, feats):
        """feats: (B, d_in) -> list of B floats in [0, 1]."""
        dev = next(self.parameters()).device
        s, d = self(feats.to(dev).float())
        v = torch.sigmoid(s) * self.gamma ** d.clamp(min=0)
        return v.cpu().tolist()


def save(path, head, extra=None):
    torch.save({'cfg': head.cfg, 'state': head.state_dict(), 'extra': extra or {}}, path)


def load(path, device='cpu'):
    ck = torch.load(path, map_location=device)
    h = ValueHead(**ck['cfg'])
    h.load_state_dict(ck['state'])
    return h.to(device).eval()
