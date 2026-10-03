#!/usr/bin/env python3
"""gt_repeat.py -- how often a with-replacement redraw would have repeated an already-rejected action (run guided-tts).

For every redraw in a guided read (`<eval>/*_{structural,logical}.repeat.json.gz`, `repeat_p`): P = the summed
tempered probability (T 0.8, unshifted model distribution) of the actions already rejected at that state in that
attempt = the chance a with-replacement draw repeats one of them.  Expected wasted draws per redraw with replacement:
P / (1 - P).  `reject_p`: each rejected complete action's own probability.  Exact token sequences: two actions that
differ only in an environment-assigned name count as different (so this understates repeats).

  python3 gt_repeat.py > artifacts/gt/repeat_stdout.txt
"""
import glob, gzip, json, os
import numpy as np
print('read | redraws | mean P(repeat) | median | P > 0.5 | P > 0.9 | expected wasted draws per redraw (with replacement) | mean P(rejected action)')
for fn in sorted(glob.glob('artifacts/gt/eval/*.repeat.json.gz')):
    d = json.load(gzip.open(fn, 'rt'))
    r = np.array(d['repeat_p']); q = np.array(d['reject_p'])
    if not len(r):
        continue
    rc = np.clip(r, 0, 0.999)
    print(f"{os.path.basename(fn).replace('.repeat.json.gz', '')} | {len(r)} | {r.mean():.3f} | {np.median(r):.3f} | "
          f"{(r > 0.5).mean():.3f} | {(r > 0.9).mean():.3f} | {(rc / (1 - rc)).mean():.2f} | {q.mean():.3f}")
