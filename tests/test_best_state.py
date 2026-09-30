#!/usr/bin/env python3
"""CPU tests for `state_train.py --recipe best` (run `best-state`: Robbie's network and pretraining recipe in the
proof-state format).  The model is the real 6 x 384 network trained for a few dozen steps on 4 short fixture proofs.

    ND_OFFLINE=1 python3 tests/test_best_state.py      # needs torch (CPU is enough) and Lean

1. Training: exit 0; the checkpoint records arch 'best', ~10M parameters, and a curve whose train loss falls; the val
   loss (held-out = the same 4 proofs) falls too.
2. Round trip: `model.load_ckpt` rebuilds an ALiBiGPT whose logits equal the trained weights' (save -> load -> save ->
   load is exact).
3. Cached decoding: `sample.generate_ids_fast` (left-padded batch, KV cache, compaction forced on) gives the same
   greedy tokens as a cache-free full forward per row, so the ALiBi key positions survive compaction.
4. One episode in the environment: `state_eval.py` greedy on the 4 memorised theorems runs, and Lean accepts >= 1.
5. The default (control) recipe is untouched: `--recipe` absent still builds the RoPE GPT.
"""
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
os.environ.setdefault('ND_OFFLINE', '1')
fails = []


def check(name, ok, detail=''):
    print(('PASS ' if ok else 'FAIL ') + name + ((' -- ' + str(detail)) if detail and not ok else ''))
    if not ok:
        fails.append(name)


tmp = tempfile.mkdtemp(prefix='ci_best_state_')
env = dict(os.environ, ND_REGISTRY_DIR=os.path.join(tmp, 'registry'), ND_REGISTRY_SYNC='0',
           LEAN_GATE_LOG=os.path.join(tmp, 'gate.jsonl'))
os.environ.update({k: env[k] for k in ('ND_REGISTRY_DIR', 'ND_REGISTRY_SYNC', 'LEAN_GATE_LOG')})
fixture = [json.loads(l) for l in open(os.path.join(HERE, 'tests/fixtures/proofs150.jsonl'))]
tiny = sorted(fixture, key=lambda r: len(r['proof']))[:4]
for i, r in enumerate(tiny):
    r['n_lines'] = r['proof'].count(' : '); r['thm'] = r['prompt']; r['name'] = f'tiny_{i}'; r['key'] = r['prompt']
pool = os.path.join(tmp, 'pool.jsonl')
with open(pool, 'w') as f:
    f.write(''.join(json.dumps(r) + '\n' for r in tiny))
data = os.path.join(tmp, 'tiny_x4.jsonl')
with open(data, 'w') as f:
    f.write(''.join(json.dumps(r) + '\n' for r in tiny) * 4)
ck = os.path.join(tmp, 'tiny_best.pt')
cmd = [sys.executable, os.path.join(HERE, 'state_train.py'), '--recipe', 'best', '--data', data, '--heldout', pool,
       '--mode', 'lean_staten', '--cap', '0', '--best_steps', '80', '--curve_every', '0', '--no_compile', '--seed', '0',
       '--out', ck]
p = subprocess.run(cmd, capture_output=True, text=True, cwd=HERE, env=env, timeout=1800)
check('state_train.py --recipe best exit 0', p.returncode == 0, p.stderr[-1500:])

if not fails:
    import torch
    from model import load_ckpt, save_ckpt
    from best_model import ALiBiGPT
    from sample import generate_ids_fast
    from state_sample import prompt_ids
    model, tok, extra = load_ckpt(ck)
    check('checkpoint: arch best, ALiBiGPT', model.cfg.get('arch') == 'best' and isinstance(model, ALiBiGPT), model.cfg)
    n = model.n_params()
    check('checkpoint: ~10M params (6 x 384, MLP 1280, MTP not saved)', 9e6 < n < 11.5e6, n)
    cv = extra['curve']
    check('loss falls on a small slice', cv[-1]['train_loss'] < 0.5 * cv[0]['train_loss'],
          (cv[0]['train_loss'], cv[-1]['train_loss']))
    check('val loss falls', cv[-1]['val_loss'] < 0.5 * cv[0]['val_loss'], (cv[0]['val_loss'], cv[-1]['val_loss']))
    check('extra records steps / secs / tok_budget', extra['steps'] == 80 and extra['tok_budget'] == 128 * 144, extra.get('steps'))

    # 2. round trip
    x = torch.randint(2, tok.vocab_size, (3, 40))
    with torch.no_grad():
        l1 = model(x)
    ck2 = os.path.join(tmp, 'rt.pt')
    save_ckpt(ck2, model, tok.mode, extra=extra)
    m2, _, _ = load_ckpt(ck2)
    with torch.no_grad():
        l2 = m2(x)
    same_sd = all(torch.equal(a, b) for a, b in zip(model.state_dict().values(), m2.state_dict().values()))
    check('round trip: identical weights and logits', same_sd and torch.equal(l1, l2), (l1 - l2).abs().max())

    # 3. cached, left-padded, compacted decoding == cache-free full forward
    from state_env import Env
    prompts = []
    for r in tiny:
        e = Env(r['prompt'], canon=True, base=0, assign=True)
        prompts.append(prompt_ids(tok, e))
    prompts.append(prompts[0][:5])     # a short, off-distribution prompt: finishes at a different time
    fast = generate_ids_fast(model, tok, prompts, greedy=True, max_new=40, early='eos', compact=True, compact_frac=0.999)
    ok, bad = True, None
    for i, pr in enumerate(prompts):
        ids = list(pr); outs = []
        with torch.no_grad():
            for t in range(40):
                nxt = int(model(torch.tensor([ids]))[0, -1].argmax())
                outs.append(nxt); ids.append(nxt)
                if nxt == tok.eos:
                    break
        got = fast[i][:len(outs)]
        if got != outs:
            ok, bad = False, (i, outs, got)
    check('fast sampler (KV cache, left pad, compaction) == full forward, greedy', ok, bad)

    # 4. one episode in the environment, judged by Lean
    summ = os.path.join(tmp, 'ev.json')
    p = subprocess.run([sys.executable, 'state_eval.py', '--ckpt', ck, '--in', pool, '--k', '1', '--temperature', '0',
                        '--batch', '8', '--summary', summ], capture_output=True, text=True, cwd=HERE, env=env, timeout=900)
    ev = json.load(open(summ)) if p.returncode == 0 else {}
    check('state_eval greedy episode runs; Lean accepts >= 1 of 4 memorised', ev.get('solved', 0) >= 1,
          (p.returncode, ev.get('solved'), p.stderr[-800:]))

    # 5. control recipe unchanged
    ck3 = os.path.join(tmp, 'ctl.pt')
    p = subprocess.run([sys.executable, 'state_train.py', '--data', data, '--mode', 'lean_staten', '--cap', '0', '--steps', '3',
                        '--recs', '4', '--n_layer', '1', '--d', '32', '--n_head', '2', '--out', ck3],
                       capture_output=True, text=True, cwd=HERE, env=env, timeout=600)
    if p.returncode == 0:
        m3, _, _ = load_ckpt(ck3)
        check('control recipe still builds the RoPE GPT', type(m3).__name__ == 'GPT' and 'arch' not in m3.cfg, m3.cfg)
    else:
        check('control recipe runs', False, p.stderr[-800:])

print('FAILED: ' + ', '.join(fails) if fails else 'ALL PASS')
sys.exit(1 if fails else 0)
