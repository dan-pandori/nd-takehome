#!/usr/bin/env python3
"""Run ckpt-avg: per-slice validation loss on HALF A only (data/ca/heldout_A.jsonl), with train.py's
own code (load_val / val_bins: fixed name-shift presentation VAL_SHIFT_SEED, token-weighted mean
proof-token cross-entropy per slice).  This is the only quantity used to select a checkpoint (LS6,
LSd3); half B is never read here.

  python3 ca_valloss.py --ckpts 'ckpts/sd/*.pt' 'ckpts/ca/*.pt' --out artifacts/ca/valloss_A.jsonl
"""
import argparse, glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from model import load_ckpt
from train import load_val, val_bins


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpts', nargs='+', required=True)
    ap.add_argument('--val', default='data/ca/heldout_A.jsonl')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    assert 'heldout_B' not in a.val
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    done = set()
    if os.path.exists(a.out):
        done = {json.loads(l)['ckpt'] for l in open(a.out)}
    cks = [c for p in a.ckpts for c in sorted(glob.glob(p)) if '.state' not in c]
    vdata = vidx = None
    with open(a.out, 'a') as f:
        for ck in cks:
            if ck in done:
                continue
            model, tok, extra = load_ckpt(ck, dev)
            if vdata is None:
                vdata, vidx = load_val(a.val, tok)
            loss = val_bins(model, vdata, vidx, tok, dev)
            f.write(json.dumps({'ckpt': ck, 'val': a.val, 'step': extra.get('step'),
                                'n_params': extra.get('n_params'), 'loss': loss}) + '\n')
            f.flush()
    print('valloss done', len(cks))


if __name__ == '__main__':
    main()
