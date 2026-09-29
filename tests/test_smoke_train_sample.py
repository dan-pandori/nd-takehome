#!/usr/bin/env python3
"""CI smoke tests (run repo-hygiene): 50 CPU training steps, then the sampler, on a throwaway 114k-parameter
`lean_seq` model trained on tests/fixtures/proofs150.jsonl.  Numbers from this model mean nothing beyond "it runs".

    ND_OFFLINE=1 python3 tests/test_smoke_train_sample.py      # needs torch (CPU is enough) and Lean

Checks: train.py runs 50 steps on CPU and writes a checkpoint, a metrics file and `<out>.args.json` (the resolved
config, `record.save_config`), with a finite loss that falls from step 25 to step 50 and a registry row naming the
config file; on a second model that memorises 4 fixture proofs (100 steps) the sampler (`sample.generate`, fast path)
reproduces them greedily and Lean accepts them, sampling is deterministic for a fixed seed, `raw` ids are filled.
"""
import glob, json, math, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
os.environ.setdefault('ND_OFFLINE', '1')
fails = []


def check(name, ok, detail=''):
    print(('PASS ' if ok else 'FAIL ') + name + ((' -- ' + str(detail)) if detail and not ok else ''))
    if not ok:
        fails.append(name)


tmp = tempfile.mkdtemp(prefix='ci_smoke_')
env = dict(os.environ, ND_REGISTRY_DIR=os.path.join(tmp, 'registry'), ND_REGISTRY_SYNC='0',
           LEAN_GATE_LOG=os.path.join(tmp, 'gate.jsonl'))
os.environ.update({k: env[k] for k in ('ND_REGISTRY_DIR', 'ND_REGISTRY_SYNC', 'LEAN_GATE_LOG')})
fx = os.path.join(HERE, 'tests/fixtures/proofs150.jsonl')
ck = os.path.join(tmp, 'm.pt')
cmd = [sys.executable, os.path.join(HERE, 'train.py'), '--data', fx, '--heldout', fx, '--mode', 'lean_seq', '--cap', '0',
       '--steps', '50', '--bs', '16', '--n_layer', '2', '--d', '64', '--n_head', '4', '--warmup', '5', '--log_every', '25',
       '--seed', '0', '--out', ck, '--metrics', os.path.join(tmp, 'metrics.jsonl')]
p = subprocess.run(cmd, capture_output=True, text=True, cwd=HERE, env=env, timeout=600)
check('train.py: 50 CPU steps exit 0', p.returncode == 0, p.stderr[-800:])
check('train.py: checkpoint written', os.path.exists(ck))
cfg = json.load(open(ck + '.args.json')) if os.path.exists(ck + '.args.json') else {}
check('train.py: <out>.args.json holds the resolved config', cfg.get('steps') == 50 and cfg.get('mode') == 'lean_seq'
      and cfg.get('_meta', {}).get('script') == 'train.py', cfg)
ms = [json.loads(l) for l in open(os.path.join(tmp, 'metrics.jsonl'))] if os.path.exists(os.path.join(tmp, 'metrics.jsonl')) else []
loss = {m['step']: m['loss'] for m in ms if 'loss' in m and 'step' in m}
check('train.py: loss finite and falling (step 25 -> 50)', 25 in loss and 50 in loss and math.isfinite(loss[50])
      and loss[50] < loss[25], loss)
rows = [json.loads(l) for f in glob.glob(os.path.join(tmp, 'registry', '*.jsonl')) for l in open(f)]
check('registry: rows name the config file', rows and all(r['labels'].get('config_file', '').endswith('m.pt.args.json')
                                                          for r in rows), [r['labels'] for r in rows][:2])

if not fails:
    # sampler: a second throwaway model memorises the 4 shortest fixture proofs (100 steps, no name offset), so the
    # fast sampler -> lean_seq decode -> Lean gate path is exercised on samples that finish and are accepted
    import numpy as np, torch
    from model import load_ckpt
    import sample, lean_judge
    fixture = [json.loads(l) for l in open(fx)]
    tiny = sorted(fixture, key=lambda r: len(r['proof']))[:4]
    with open(os.path.join(tmp, 'tiny.jsonl'), 'w') as f:
        f.write(''.join(json.dumps(r) + '\n' for r in tiny) * 4)
    ck2 = os.path.join(tmp, 'tiny.pt')
    cmd2 = [sys.executable, os.path.join(HERE, 'train.py'), '--data', os.path.join(tmp, 'tiny.jsonl'), '--mode', 'lean_seq',
            '--cap', '0', '--steps', '100', '--bs', '16', '--n_layer', '2', '--d', '64', '--n_head', '4', '--warmup', '5',
            '--lr', '3e-3', '--log_every', '50', '--no_shift', '--seed', '0', '--out', ck2]
    p = subprocess.run(cmd2, capture_output=True, text=True, cwd=HERE, env=env, timeout=600)
    check('train.py: 100-step memorisation run exit 0', p.returncode == 0, p.stderr[-800:])
    model, tok, _ = load_ckpt(ck2)
    prompts = [r['prompt'] for r in tiny] * 8
    gold = [r['proof'] for r in tiny] * 8
    raw = np.zeros((len(prompts), 96), dtype=np.int64)
    st = {}
    g = sample.generate(model, tok, prompts, greedy=True, max_new=96, batch=16)
    s1 = sample.generate(model, tok, prompts, greedy=False, temperature=1.0, max_new=96, batch=16, seed=7, raw=raw, stats=st)
    s2 = sample.generate(model, tok, prompts, greedy=False, temperature=1.0, max_new=96, batch=16, seed=7)
    ok_form = lambda r: r.startswith('N1 ') or r.startswith('LEANREJ') or r.startswith('LEANPARSE')
    check('sampler: one result per prompt', len(g) == len(s1) == len(prompts))
    check('sampler: every result is a clean ND proof or a reject marker', all(map(ok_form, g + s1)))
    check('sampler: greedy reproduces the 4 memorised proofs, Lean-accepted (32/32)', g == gold,
          sum(a == b for a, b in zip(g, gold)))
    n_acc = sum(not r.startswith('LEAN') for r in s1)
    check('sampler: sampled T=1, >= 8/32 Lean-accepted (14 on torch 2.8 CPU, 2026-09-29)', n_acc >= 8, n_acc)
    check('sampler: same seed, same samples', s1 == s2)
    check('sampler: raw token ids filled', bool((raw != 0).any()))
    res = lean_judge.judge_many(list(zip(prompts, s1)))
    check('sampler: judge_many agrees with the gate', all((not r.startswith('LEAN')) == ok for r, (ok, _, _) in zip(s1, res)))

print(f'{len(fails)} failed' if fails else 'ALL PASS')
sys.exit(1 if fails else 0)
