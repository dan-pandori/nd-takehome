#!/usr/bin/env python3
"""CI test (run lit-measures): `train.py --data_seed` splits the data-order seed from the init seed.

    ND_OFFLINE=1 python3 tests/test_data_seed.py      # needs torch (CPU is enough)

Four 20-step CPU runs of a throwaway 2-layer `lean_seq` model on tests/fixtures/proofs150.jsonl (legacy path):
  A  --seed 0                    B  --seed 0 --data_seed 0      (default = --seed: B's losses equal A's exactly)
  C  --seed 0 --data_seed 1      (same init, other order: step-1 losses differ)
  D  --seed 1 --data_seed 0      (other init, same order: step-1 losses differ)
The GPU path (fast_train.py) takes the same flag through `plan` and `draw`; its default is checked on a pod
(run_lit_measures.md).
"""
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('ND_OFFLINE', '1')
tmp = tempfile.mkdtemp(prefix='ci_dseed_')
env = dict(os.environ, ND_REGISTRY_DIR=os.path.join(tmp, 'registry'), ND_REGISTRY_SYNC='0')
fx = os.path.join(HERE, 'tests/fixtures/proofs150.jsonl')
fails = []


def run(tag, *extra):
    out = os.path.join(tmp, tag + '.pt'); met = os.path.join(tmp, tag + '.jsonl')
    cmd = [sys.executable, os.path.join(HERE, 'train.py'), '--data', fx, '--heldout', fx, '--mode', 'lean_seq', '--cap', '0',
           '--steps', '20', '--bs', '16', '--n_layer', '2', '--d', '64', '--n_head', '4', '--warmup', '5', '--log_every', '1',
           '--impl', 'legacy', '--out', out, '--metrics', met, *extra]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=HERE, env=env, timeout=600)
    if p.returncode:
        print(p.stderr[-800:]); fails.append(tag + ' exit'); return {}
    cfg = json.load(open(out + '.args.json'))
    ls = {m['step']: m['loss'] for m in map(json.loads, open(met)) if 'loss' in m and 'step' in m}
    return {'cfg': cfg, 'loss': ls}


def check(name, ok, detail=''):
    print(('PASS ' if ok else 'FAIL ') + name + ((' -- ' + str(detail)) if detail and not ok else ''))
    if not ok:
        fails.append(name)


A = run('A', '--seed', '0'); B = run('B', '--seed', '0', '--data_seed', '0')
C = run('C', '--seed', '0', '--data_seed', '1'); D = run('D', '--seed', '1', '--data_seed', '0')
if not fails:
    check('default data_seed = seed is recorded', A['cfg'].get('data_seed') == 0, A['cfg'].get('data_seed'))
    check('--seed 0 == --seed 0 --data_seed 0 (every step)', A['loss'] == B['loss'], (A['loss'], B['loss']))
    check('--data_seed 1 changes the trajectory', A['loss'][1] != C['loss'][1], (A['loss'][1], C['loss'][1]))
    check('--seed 1 --data_seed 0 changes the trajectory', A['loss'][1] != D['loss'][1], (A['loss'][1], D['loss'][1]))
print('FAIL' if fails else 'ALL PASS', fails)
sys.exit(1 if fails else 0)
