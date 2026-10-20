#!/usr/bin/env python3
"""Independent re-derivation of teacher-forced verdicts on a sample of tf1200 states: the checkpoint is re-run on CPU
(fp32) at the algorithm's states (project env `state_env.decompose`, names shifted by the stored per-record base), greedy
to <eos>; the reviewer's own name masking decides agreement.  Compared state by state with the stored '1'/'0' string.

  ~/venv-cpu/bin/python review_kal/tf_cpu.py <model> <ckpt.pt> [--per_atoms 4]
"""
import argparse, json, os, random, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kc
sys.path.insert(0, kc.ROOT)
import torch
torch.set_num_threads(1)
from model import load_ckpt
from sample import generate_ids_fast
from state_env import decompose

ap = argparse.ArgumentParser()
ap.add_argument('model'); ap.add_argument('ckpt')
ap.add_argument('--per_atoms', type=int, default=4)
ap.add_argument('--batch', type=int, default=48)
a = ap.parse_args()
NAME = re.compile(r'^n(\d+)$')


def shift(toks, b):
    return [f'n{int(m.group(1)) + b}' if (m := NAME.match(t)) else t for t in toks]


def env_names_masked(act):
    """mask the names the environment assigns: the `have` name, and the binder of a box opened right after `:=`
    (`:= ( fun ( NAME :` or `:= Or.elim X ( fun ( NAME :`)."""
    x = list(act)
    if len(x) >= 2 and x[0] == 'have':
        x[1] = '*'
        if ':=' in x:
            i = x.index(':=') + 1
            if x[i:i + 3] == ['(', 'fun', '(']:
                x[i + 3] = '*'
            elif x[i:i + 1] == ['Or.elim'] and x[i + 2:i + 5] == ['(', 'fun', '(']:
                x[i + 5] = '*'
    return x


recs = list(kc.rows(os.path.join(kc.ROOT, 'data', 'kalmar', 'tf1200_kal_sl.jsonl')))
stored = json.load(open(os.path.join(kc.ROOT, 'artifacts', 'kalmar', 'tf', f'{a.model}__tf1200.json')))['rows']
rng = random.Random(7)
pick = []
for na in (1, 2, 3, 4):
    idx = [i for i, r in enumerate(recs) if r['n_atoms'] == na]
    pick += sorted(rng.sample(idx, a.per_atoms))
model, tok, extra = load_ckpt(a.ckpt, 'cpu')
model.eval()
items = []
for i in pick:
    r = recs[i]
    b = stored[i]['base']
    steps, toks, env = decompose(r['prompt'], r['proof'], canon=True)
    assert len(steps) == len(stored[i]['agree']), (i, len(steps), len(stored[i]['agree']))
    for j, (s, act, hs) in enumerate(steps):
        items.append((i, j, tok.encode_toks(shift(s, b)), shift(act, b), stored[i]['agree'][j] == '1'))
t0 = time.time()
order = sorted(range(len(items)), key=lambda k: len(items[k][2]))
mine = [None] * len(items)
with torch.no_grad():
    for s0 in range(0, len(order), a.batch):
        idx = order[s0:s0 + a.batch]
        outs = generate_ids_fast(model, tok, [items[k][2] for k in idx], goals=None, greedy=True, max_new=512, seed=0,
                                 early='eos', compact=True)
        for k, o in zip(idx, outs):
            atoks, ended = tok.decode_action(o)
            mine[k] = bool(ended) and env_names_masked(atoks) == env_names_masked(items[k][3])
n = len(items)
same = sum(m == it[4] for m, it in zip(mine, items))
res = {'model': a.model, 'ckpt': a.ckpt, 'records': pick, 'n_states': n, 'cpu_agree': sum(mine), 'stored_agree': sum(it[4] for it in items),
       'verdicts_identical': same, 'cpu1_stored0': sum(m and not it[4] for m, it in zip(mine, items)),
       'cpu0_stored1': sum((not m) and it[4] for m, it in zip(mine, items)), 'secs': round(time.time() - t0, 1)}
print(json.dumps(res), flush=True)
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', f'tf_cpu_{a.model}.json'), 'w'))
