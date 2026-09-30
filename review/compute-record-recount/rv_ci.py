#!/usr/bin/env python3
"""Reviewer (compute-record), CPU, run in GitHub Actions (the VPS has no torch).  My own counts, not the executor's tests:
  1. train.py train_tokens / train_steps at a batch size that does NOT divide the data (bs 100 over 150 records, 3 steps
     = exactly 2 epochs) -> 2 x the summed record tokens (I tokenise the file myself with the repo tokenizer).
  2. sample.generate gen_tokens / attempts on every decode path (fast+compact, fast no compact, base), short max_new so
     many rows are cut off: my count = per row, position of the first <eos> + 1, else max_new, from `raw`.
  3. early='exact' (fast path): the counter vs the same raw count (the shortcut writes tokens the model never decoded).
  4. lean_checks for one generate() call vs the gate log's lean_texts; a second identical call.
  5. registry rows of 1-4 as written (labels).
Prints one JSON line per check; exit 0 always (the reviewer reads the numbers)."""
import glob, json, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, HERE)
tmp = tempfile.mkdtemp(prefix='rv_cr_')
os.environ.update({'ND_OFFLINE': '1', 'ND_REGISTRY_DIR': os.path.join(tmp, 'reg'), 'ND_REGISTRY_SYNC': '0',
                   'LEAN_GATE_LOG': os.path.join(tmp, 'gate.jsonl'), 'ND_RUN_ID': 'rv'})
out = {}
def emit(k, v):
    out[k] = v; print(json.dumps({k: v}), flush=True)

from tokenizer import make_tokenizer
fx = os.path.join(HERE, 'tests/fixtures/proofs150.jsonl')
recs = [json.loads(l) for l in open(fx) if l.strip()]
tk = make_tokenizer('lean_seq')
S = sum(len(tk.encode_prompt(r['prompt'])) + len(tk.encode_proof(r['proof'])) for r in recs)
ck = os.path.join(tmp, 'm.pt')
p = subprocess.run([sys.executable, 'train.py', '--data', fx, '--mode', 'lean_seq', '--cap', '0', '--steps', '3', '--bs', '100',
                    '--n_layer', '2', '--d', '64', '--n_head', '4', '--warmup', '1', '--log_every', '3', '--seed', '0', '--out', ck],
                   cwd=HERE, capture_output=True, text=True)
rows = [json.loads(l) for f in glob.glob(os.path.join(tmp, 'reg', '*.jsonl')) for l in open(f)]
cr = {r['metric']: r['value'] for r in rows if 'compute_id' in (r.get('labels') or {})}
emit('train', {'rc': p.returncode, 'records': len(recs), 'my_tokens_per_epoch': S, 'expected_2_epochs': 2 * S,
               'rows': cr, 'equal': cr.get('train_tokens') == 2 * S and cr.get('train_steps') == 3, 'err': p.stderr[-400:]})
# a model that decodes something: 150 steps on the fixture
p = subprocess.run([sys.executable, 'train.py', '--data', fx, '--mode', 'lean_seq', '--cap', '0', '--steps', '150', '--bs', '32',
                    '--n_layer', '2', '--d', '64', '--n_head', '4', '--warmup', '5', '--lr', '3e-3', '--log_every', '150',
                    '--seed', '1', '--out', ck], cwd=HERE, capture_output=True, text=True)
emit('train2_rc', p.returncode)
import numpy as np, torch, record, sample
from model import load_ckpt
model, tok, _ = load_ckpt(ck)
model.eval()
prompts = [r['prompt'] for r in recs[:60]]
def mine(raw, mx):
    return sum(row.index(tok.eos) + 1 if tok.eos in row else mx for row in raw.tolist())
def gl():
    f = os.environ['LEAN_GATE_LOG']
    return [json.loads(l) for l in open(f)] if os.path.exists(f) else []
for name, kw, mx in [('fast_compact', dict(path='fast', compact=True), 40), ('fast_nocompact', dict(path='fast', compact=False), 40),
                     ('base', dict(path='base'), 40), ('fast_compact_mx200', dict(path='fast', compact=True), 200),
                     ('fast_exact', dict(path='fast', compact=True, early='exact'), 200)]:
    raw = np.full((len(prompts), mx), tok.pad, dtype=np.int64)
    n0 = len(gl())
    with torch.no_grad(), record.compute(phase=name, arm='rv', seed=0) as c:
        s = sample.generate(model, tok, prompts, greedy=False, temperature=1.0, max_new=mx, batch=16, seed=3, raw=raw, **kw)
    g = gl()[n0:]
    emit(name, {'gen_tokens': c.gen_tokens, 'mine': mine(raw, mx), 'cut_off': sum(1 for r in raw.tolist() if tok.eos not in r),
                'attempts': c.attempts, 'n_prompts': len(prompts), 'lean_checks': c.lean_checks,
                'gate_lean_texts': sum(x['lean_texts'] for x in g), 'accepted': sum(not x.startswith('LEAN') for x in s)})
# the same greedy call twice: is the second one's Lean work counted again (a per-call Gate) ?
for i in range(2):
    n0 = len(gl())
    with torch.no_grad(), record.compute(phase=f'greedy{i}', arm='rv', seed=0) as c:
        s = sample.generate(model, tok, prompts, greedy=True, max_new=200, batch=16)
    g = gl()[n0:]
    emit(f'greedy{i}', {'lean_checks': c.lean_checks, 'gate_lean_texts': sum(x['lean_texts'] for x in g),
                        'accepted': sum(not x.startswith('LEAN') for x in s)})
rows = [json.loads(l) for f in glob.glob(os.path.join(tmp, 'reg', '*.jsonl')) for l in open(f)]
emit('rows', sorted([r['metric'], r['value'], r.get('arm'), r.get('seed'), r['labels'].get('phase'), r['labels'].get('device')]
                    for r in rows if 'compute_id' in (r.get('labels') or {}) and r['metric'] != 'gpu_seconds'))
json.dump(out, open(os.path.join(tmp, 'rv_ci.json'), 'w'), indent=1)
print('RV DONE', tmp)
