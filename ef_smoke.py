#!/usr/bin/env python3
"""Run efficiency: correctness smoke test of the fast decode path, before any measurement.

  1. base(rowrng) vs fast(early=eos, compact=0)   -> token streams must be IDENTICAL (the fast loop is faithful)
  2. fast(early=eos, compact=0) vs compact=1      -> IDENTICAL (dropping finished rows changes nothing)
  3. fast(early=exact) and fast(early=goal)       -> each row's stream is a PREFIX of the eos stream up to its stop,
                                                     plus the terminator the sampler appended; shows examples.
"""
import os, sys, json, numpy as np, torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model import load_ckpt
import sample as S

CK = sys.argv[1] if len(sys.argv) > 1 else 'ckpts/ef/stage1_full_seq_s0.pt'
NT, K, MAXNEW, BATCH = 8, 32, 256, 128
dev = 'cuda' if torch.cuda.is_available() else 'cpu'
model, tok, _ = load_ckpt(CK, dev)
tg = [json.loads(l) for l in open('artifacts/ef/targets200.jsonl')][:NT]
prompts = [t['prompt'] for t in tg for _ in range(K)]
print('smoke:', len(prompts), 'samples, mode', tok.mode)


def run(**kw):
    raw = np.zeros((len(prompts), MAXNEW), dtype=np.int16)
    st = {}
    tx = S.generate(model, tok, prompts, greedy=False, temperature=0.8, max_new=MAXNEW, batch=BATCH,
                    seed=0, stats=st, gate=False, raw=raw, **kw)
    return raw, np.array(st['declen_by_prompt']), tx, st


rb, db, tb, sb = run(path='base', rowrng=True)
rf, df, tf, sf = run(path='fast', early='eos', compact=False, rowrng=True)
print('1. base(rowrng) vs fast(eos,nocompact): tokens equal =', bool((rb == rf).all()), '; declen equal =', bool((db == df).all()))
rc, dc, tc, sc = run(path='fast', early='eos', compact=True, rowrng=True)
print('2. fast(eos) vs fast(eos,compact): tokens equal =', bool((rc == rf).all()), '; declen equal =', bool((dc == df).all()))
print('   rowsteps  nocompact', sf['rowsteps'], ' compact', sc['rowsteps'])

for early in ('exact', 'goal'):
    re_, de_, te_, se_ = run(path='fast', early=early, compact=True, rowrng=True)
    pref = ok = 0
    for i in range(len(prompts)):
        n = int(de_[i])
        if n < MAXNEW:
            if (re_[i, :n] == rf[i, :n]).all():
                pref += 1
        else:
            if (re_[i] == rf[i]).all():
                pref += 1
    print(f'3. early={early}: rows whose decoded prefix matches the eos run: {pref}/{len(prompts)}; '
          f'stops eos/exact/goal = {se_.get("stop_eos")}/{se_.get("stop_exact")}/{se_.get("stop_goal")}; '
          f'mean declen {de_.mean():.1f} (eos run {df.mean():.1f}); texts {sum(1 for x in te_ if x is not None)}/{len(prompts)} '
          f'(eos run {sum(1 for x in tf if x is not None)})')
    ex = [x for x in te_ if x is not None][:2]
    for e in ex:
        print('   example:', e[:240])

# 4. the appended terminator must be checked, not trusted: send both runs' texts to Lean
from lean_check import check
for nm, tx in (('eos', tf), ('goal', te_)):
    items = [(p, t) for p, t in zip(prompts, tx) if t is not None]
    if not items:
        print(f'4. {nm}: no texts'); continue
    srcs = [tok.statement(p) + ' ' + t for p, t in items]
    res, wall, cpu = check(srcs)
    print(f'4. {nm}: {len(srcs)} texts to Lean -> {sum(1 for r in res if r["ok"])} accepted, {wall:.1f}s wall {cpu:.1f}s proc')
