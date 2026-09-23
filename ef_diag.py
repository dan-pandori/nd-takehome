#!/usr/bin/env python3
"""Run efficiency, step 2: why does (or does not) the terminator fire?  Decides between
  (a) the model never learned a terminator,
  (b) the rendering does not end with one,
  (c) the prompt is longer than anything in training,
  (d) the sampler ignores it,
from the data. Writes artifacts/ef/diag.json."""
import os, sys, json, gzip, random, collections
import numpy as np, torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model import load_ckpt

dev = 'cuda' if torch.cuda.is_available() else 'cpu'
model, tok, _ = load_ckpt('ckpts/ef/stage1_full_seq_s0.pt', dev)
rec = {}

# (b) does every training rendering end with <eos>?
tr = []
with (gzip.open('data/train.jsonl.gz', 'rt') if os.path.exists('data/train.jsonl.gz') else open('data/train.jsonl')) as f:
    for i, l in enumerate(f):
        tr.append(json.loads(l))
sample = random.Random(0).sample(tr, 5000)
ends = collections.Counter(); plen = []; blen = []
for r in sample:
    ids = tok.encode_proof(r['proof'])
    ends[tok.itos[ids[-1]]] += 1
    plen.append(len(tok.encode_prompt(r['prompt']))); blen.append(len(ids))
rec['b_training_last_token'] = dict(ends)
rec['train_prompt_len'] = {'mean': round(float(np.mean(plen)), 1), 'p95': int(np.percentile(plen, 95)), 'max': int(max(plen))}
rec['train_proof_len'] = {'mean': round(float(np.mean(blen)), 1), 'p95': int(np.percentile(blen, 95)), 'max': int(max(blen))}

# (c) are the targets' prompts longer than anything in training?
tg = [json.loads(l) for l in open('artifacts/ef/targets200.jsonl')]
tp = [len(tok.encode_prompt(t['prompt'])) for t in tg]
rec['target_prompt_len'] = {'mean': round(float(np.mean(tp)), 1), 'p95': int(np.percentile(tp, 95)), 'max': int(max(tp))}
rec['c_frac_targets_longer_than_train_max'] = round(float(np.mean(np.array(tp) > max(plen))), 4)

# (a) the model's probability of <eos> at the true end, teacher-forced
def eos_prob(rows, n=400):
    ps = []
    for r in rows[:n]:
        try:
            pi = tok.encode_prompt(r['prompt']); bi = tok.encode_proof(r['proof'])
        except Exception:
            continue
        ids = torch.tensor([pi + bi], device=dev)
        with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16, enabled=(dev == 'cuda')):
            lg = model(ids)[0]
        j = len(pi) + len(bi) - 2                      # position predicting the final <eos>
        ps.append(float(torch.softmax(lg[j].float(), -1)[tok.eos]))
    return ps

ho = [json.loads(l) for l in open('data/heldout.jsonl')]
p_ho = eos_prob(ho)
rec['a_p_eos_at_true_end_heldout'] = {'n': len(p_ho), 'mean': round(float(np.mean(p_ho)), 4),
                                      'median': round(float(np.median(p_ho)), 4), 'p05': round(float(np.percentile(p_ho, 5)), 4),
                                      'frac_above_0.5': round(float(np.mean(np.array(p_ho) > .5)), 4)}
# the same on the ladder targets, using the proofs this model actually got accepted (out of distribution: 7-12 lines)
acc = []
fn = 'artifacts/ef/base_rr_accept.jsonl.gz'
if os.path.exists(fn):
    with gzip.open(fn, 'rt') as f:
        for l in f:
            d = json.loads(l)
            if d.get('proof', '').startswith('N'):
                acc.append({'prompt': d['prompt'], 'proof': d['proof']})
if acc:
    p_ac = eos_prob(acc)
    rec['a_p_eos_at_true_end_ladder_accepted'] = {'n': len(p_ac), 'mean': round(float(np.mean(p_ac)), 4),
                                                  'median': round(float(np.median(p_ac)), 4),
                                                  'frac_above_0.5': round(float(np.mean(np.array(p_ac) > .5)), 4)}

# (d) what the sampler actually produced: where rows stopped, and what the rows that never terminate look like
d = np.load('artifacts/ef/base_rr_tokens.npz', allow_pickle=True)
ids, dl = d['ids'], d['declen']
EOS = tok.eos
n_noeos = int((dl >= ids.shape[1]).sum())
rec['d_rows'] = {'n': int(ids.shape[0]), 'no_eos': n_noeos, 'frac_eos': round(1 - n_noeos / ids.shape[0], 6)}
# of the rows that did terminate, did the two tokens before <eos> read `exact n<k>` at top level?
EX = tok.stoi['exact']; LP = tok.stoi['(']; RP = tok.stoi[')']
good = bad = 0
badex = collections.Counter()
for i in range(0, ids.shape[0], 7):                     # every 7th row: 7,315 rows, enough for the shape
    n = int(dl[i])
    if n >= ids.shape[1]:
        continue
    row = ids[i, :n]
    if n >= 3 and row[n - 3] == EX and row[n - 2] >= tok.ref0:
        dep = int((row[:n - 3] == LP).sum() - (row[:n - 3] == RP).sum())
        (good := good) if dep else None
        if dep == 0: good += 1
        else: bad += 1; badex[f'exact at depth {dep}'] += 1
    else:
        bad += 1
        badex['no `exact n<k>` before <eos>'] += 1
rec['d_terminating_rows_shape'] = {'sampled': good + bad, 'eos_right_after_top_level_exact': good,
                                   'other': bad, 'other_kinds': dict(badex.most_common(5))}
# the no-eos rows: what are they doing at the cap?
ex = [i for i in range(ids.shape[0]) if dl[i] >= ids.shape[1]][:6]
rec['d_no_eos_examples'] = []
for i in ex:
    toks = [tok.itos[int(x)] for x in ids[i] if int(x) != tok.pad]
    rec['d_no_eos_examples'].append({'n_tokens': len(toks), 'head': ' '.join(toks[:40]), 'tail': ' '.join(toks[-40:])})
json.dump(rec, open('artifacts/ef/diag.json', 'w'), indent=1)
print(json.dumps({k: v for k, v in rec.items() if k != 'd_no_eos_examples'}, indent=1))
