#!/usr/bin/env python3
"""Run ckpt-avg: build every uniform weight average listed by ca_plan.averages().

Each average is the element-wise mean (in float32) of its members' state dicts; the members must share
cfg and tok_mode, and every non-floating tensor must be identical across members (asserted).  Saved as
ckpts/ca/<run>.<variant>.pt in train.py's format, with extra = {n_params, step: None, avg_of: [...]}.

  python3 ca_average.py [--src ckpts/sd] [--out ckpts/ca]
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from ca_plan import averages


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default='ckpts/sd')
    ap.add_argument('--out', default='ckpts/ca')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for name, members in averages().items():
        fo = os.path.join(a.out, name + '.pt')
        if os.path.exists(fo):
            continue
        cks = [torch.load(os.path.join(a.src, m + '.pt'), map_location='cpu') for m in members]
        c0 = cks[0]
        assert all(c['cfg'] == c0['cfg'] and c['tok_mode'] == c0['tok_mode'] for c in cks), name
        st = {}
        for key, v in c0['state'].items():
            if torch.is_floating_point(v):
                st[key] = (sum(c['state'][key].float() for c in cks) / len(cks)).to(v.dtype)
            else:
                assert all(torch.equal(c['state'][key], v) for c in cks), (name, key)
                st[key] = v
        extra = {'n_params': c0['extra'].get('n_params'), 'step': None, 'avg_of': members,
                 'member_steps': [c['extra'].get('step') for c in cks], 'args': c0['extra'].get('args')}
        torch.save({'cfg': c0['cfg'], 'state': st, 'tok_mode': c0['tok_mode'], 'extra': extra}, fo)
        print(name, len(members), flush=True)


if __name__ == '__main__':
    main()
