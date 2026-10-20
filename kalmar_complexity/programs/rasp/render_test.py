#!/usr/bin/env python3
"""Teacher-forced check of the RASP rendering program (run kalmar-complexity).

For each state the sequence `state + action` is fed to the rendering program, with the decision program's
content injected at `<act>` (the decision program is causal, so its values at `<act>` do not depend on the
action tokens).  The prediction at `<act>` + i must be action[i] for every i and `<end>` after the last token;
if every prediction is right, autoregressive decoding reproduces the action exactly."""
import collections, time
import numpy as np
import rasp as R
import kalmar_policy as KP

IDX_FIELDS = ('Fp', 'Bp')


def check(states, contents, outs, info, H, batch=256, show=3):
    nxt = KP.build_render(outs, info['start'])
    fields = list(outs)
    seqs, acts = [], []
    for (ti, st, act, tag) in states:
        seqs.append(KP.encode(st) + KP.encode(act))
        acts.append(KP.encode(act) + [KP.END_T])

    def extra_fn(chunk, arr, padn):
        B, N = arr.shape
        ex = {}
        for f in fields:
            v = np.array([contents[i][f] for i in chunk], dtype=np.int64)
            if f in IDX_FIELDS:
                v = np.where(v >= 0, v + padn, v)
            ex[outs[f]] = np.repeat(v[:, None], N, 1)
        return ex
    t0 = time.time()
    res = R.run_program([nxt], seqs, batch=batch, all_positions=True, extra_fn=extra_fn, bucket=32,
                        inputs=[outs[f] for f in fields])[nxt]
    dt = time.time() - t0
    ok = collections.Counter()
    shown = 0
    for i, (ti, st, act, tag) in enumerate(states):
        p0 = len(st) - 1                                   # position of <act>
        pred = list(res[i][p0:p0 + len(act) + 1])
        if pred == acts[i]:
            ok[tag] += 1
        elif shown < show:
            shown += 1
            print('RENDER MISMATCH', tag, '\n  want', ' '.join(act + ['<end>']),
                  '\n  got ', ' '.join(KP.ITOS.get(int(x), f'?{x}') for x in pred), '\n  content', contents[i])
    return ok, None, dt
