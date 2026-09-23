#!/usr/bin/env python3
"""Run efficiency: the fast path is now sample.py's default, so check it is a no-op for the OTHER tokenizers too.
For each checkpoint given, sample the same prompts with path='base' (rowrng) and the new default and require
identical token streams and identical decoded proofs."""
import sys, os, json
import numpy as np, torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model import load_ckpt
import sample as S

tg = [json.loads(l) for l in open('artifacts/ef/targets200.jsonl')][:16]
prompts = [t['prompt'] for t in tg for _ in range(8)]
MAXNEW, BATCH = 192, 64
dev = 'cuda' if torch.cuda.is_available() else 'cpu'
bad = 0
for ck in sys.argv[1:]:
    model, tok, _ = load_ckpt(ck, dev)
    outs = {}
    for name, kw in (('base', dict(path='base', rowrng=True)),
                     ('default', {}),                                    # whatever sample.py now defaults to
                     ('fast_nocompact', dict(path='fast', compact=False, rowrng=True))):
        raw = np.zeros((len(prompts), MAXNEW), dtype=np.int16)
        st = {}
        res = S.generate(model, tok, prompts, greedy=False, temperature=0.8, max_new=MAXNEW, batch=BATCH,
                         seed=0, stats=st, gate=False, raw=raw, **kw)
        outs[name] = (raw, res, st)
    ok_ids = bool((outs['base'][0] == outs['default'][0]).all()) and bool((outs['base'][0] == outs['fast_nocompact'][0]).all())
    ok_res = outs['base'][1] == outs['default'][1] == outs['fast_nocompact'][1]
    print(f'{os.path.basename(ck)}: mode {tok.mode}, {len(prompts)} samples — token streams identical {ok_ids}, '
          f'decoded strings identical {ok_res}, mean declen '
          f'{np.mean(outs["base"][2]["declen_by_prompt"]):.1f} / {np.mean(outs["default"][2]["declen_by_prompt"]):.1f}')
    bad += (not ok_ids) or (not ok_res)
print('REGRESSION', 'PASS' if bad == 0 else f'FAIL ({bad})')
