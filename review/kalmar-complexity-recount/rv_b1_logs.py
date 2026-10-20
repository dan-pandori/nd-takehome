#!/usr/bin/env python3
"""Do the checkpoint curves equal the printed training-log points?  (KAL-D: artifacts/kalmar/logs/train_kalD_s*.log)"""
import json, os, re, subprocess, sys
import torch
WT = os.path.expanduser('~/work/kalmar-complexity'); WS = os.path.expanduser('~/review/kalmar-complexity')
for s in range(3):
    log = subprocess.run(['git', '-C', WT, 'show', f'HEAD:artifacts/kalmar/logs/train_kalD_s{s}.log'], capture_output=True, text=True).stdout
    pts = [(int(m.group(1)), float(m.group(2)), float(m.group(3))) for m in re.finditer(r'step (\d+) loss ([\d.]+) mtp [\d.]+ lr \S+ epochs ([\d.]+)', log)]
    ck = torch.load(os.path.join(WS, f'ckpts/kc_src/stage1_kalD_s{s}.pt'), map_location='cpu', weights_only=False)['extra']['curve']
    m = {p['step']: p for p in ck}
    bad = [(st, l, m[st]['train_loss']) for st, l, e in pts if st not in m or abs(m[st]['train_loss'] - l) > 5e-5]
    print(f'KAL-D s{s}: log points {len(pts)}, ckpt points {len(ck)}, mismatches {len(bad)}', bad[:3])
