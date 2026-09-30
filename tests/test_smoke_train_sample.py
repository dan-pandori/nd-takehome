#!/usr/bin/env python3
"""CI smoke tests (run repo-hygiene): 50 CPU training steps, then the sampler, on a throwaway 114k-parameter
`lean_seq` model trained on tests/fixtures/proofs150.jsonl.  Numbers from this model mean nothing beyond "it runs".

    ND_OFFLINE=1 python3 tests/test_smoke_train_sample.py      # needs torch (CPU is enough) and Lean

Checks: train.py runs 50 steps on CPU and writes a checkpoint, a metrics file and `<out>.args.json` (the resolved
config, `record.save_config`), with a finite loss that falls from step 25 to step 50 and a registry row naming the
config file; on a second model that memorises 4 fixture proofs (100 steps) the sampler (`sample.generate`, fast path)
reproduces them greedily and Lean accepts them, sampling is deterministic for a fixed seed, `raw` ids are filled;
the compute rows (record.compute, run compute-record) equal independent counts of the tokens trained on and sampled and
of the texts sent to Lean.
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

    # compute rows (run compute-record): the counters equal independent counts of the work done
    import record, train
    from tokenizer import make_tokenizer
    allrows = lambda: [json.loads(l) for f in glob.glob(os.path.join(tmp, 'registry', '*.jsonl')) for l in open(f)]
    crow = lambda rs, m, **kw: [r for r in rs if r['metric'] == m and 'compute_id' in r['labels']
                                and all(r['labels'].get(k, r.get(k)) == v for k, v in kw.items())]
    rs = allrows()
    tiny_cfg = lambda r: r['labels'].get('config_file', '').endswith('tiny.pt.args.json')
    ntok = sum(len(p) + len(q) for p, q in train.load(os.path.join(tmp, 'tiny.jsonl'), make_tokenizer('lean_seq'), 0))
    got = [r['value'] for r in crow(rs, 'train_tokens') if tiny_cfg(r)]
    check('compute: train.py train_tokens = 100 steps x the 16 records\' tokens (bs 16 = one epoch a step)',
          got == [100 * ntok], (got, 100 * ntok))
    check('compute: train.py train_steps rows (50 and 100)', sorted(r['value'] for r in crow(rs, 'train_steps')) == [50, 100],
          [r['value'] for r in crow(rs, 'train_steps')])
    g = crow(rs, 'gpu_seconds', phase='job')
    check('compute: train.py gpu_seconds rows, device=cpu, arm / seed labels', len(g) == 2 and all(
          r['labels']['device'] == 'cpu' and r['value'] > 0 and r['seed'] == 0 for r in g), [r['labels'] for r in g])
    raw = np.full((len(prompts), 96), tok.pad, dtype=np.int64)
    glog = os.environ['LEAN_GATE_LOG']
    n_gate0 = sum(1 for _ in open(glog)) if os.path.exists(glog) else 0
    with record.compute(phase='sample', round=1, arm='smoke', seed=0) as c:
        s3 = sample.generate(model, tok, prompts, greedy=False, temperature=1.0, max_new=96, batch=16, seed=11, raw=raw)
    ind = sum(list(row).index(tok.eos) + 1 if tok.eos in row else 96 for row in raw.tolist())   # decoded through <eos>
    gl = [json.loads(l) for l in open(glog)][n_gate0:]
    check('compute: gen_tokens = tokens in the sampled ids through <eos>', c.gen_tokens == ind > 0, (c.gen_tokens, ind))
    check('compute: attempts = prompts sampled', c.attempts == len(prompts), c.attempts)
    check('compute: lean_checks = texts the gate sent to Lean', len(gl) == 1 and c.lean_checks == gl[0]['lean_texts'] > 0
          and c.lean_s > 0, (c.lean_checks, gl))
    rs = allrows()
    lab = [(r['arm'], r['seed'], r['labels'].get('round'), r['labels']['device']) for r in crow(rs, 'gen_tokens', phase='sample')]
    check('compute: sample block rows labelled arm, seed, labels.round, device', lab == [('smoke', 0, 1, 'cpu')], lab)
    fresh = [r for r in fixture if r['prompt'] not in {t['prompt'] for t in tiny}][:6]
    pairs = [(r['prompt'], r['proof']) for r in fresh]
    with record.compute(phase='judge', arm='smoke', seed=0) as cj:
        v1 = lean_judge.judge_many(pairs + pairs)
    with record.compute(phase='judge_again', arm='smoke', seed=0) as cj2:
        v2 = lean_judge.judge_many(pairs)
    check('compute: judge_many counts distinct texts sent to Lean (6), not duplicates or cache hits (0)',
          cj.lean_checks == 6 and cj2.lean_checks == 0 and all(ok for ok, _, _ in v1 + v2), (cj.lean_checks, cj2.lean_checks))
    check('compute: a CPU block with no counted work writes no rows', not crow(allrows(), 'gpu_seconds', phase='judge_again'))

print(f'{len(fails)} failed' if fails else 'ALL PASS')
sys.exit(1 if fails else 0)
