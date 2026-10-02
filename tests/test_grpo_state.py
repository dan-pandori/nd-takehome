#!/usr/bin/env python3
"""CPU tests for grpo_state.py (run `grpo-state`): gradient sanity and a tiny end-to-end smoke run, on a throwaway
`lean_staten` (arm SN) model that memorises 4 short fixture proofs.  Numbers from this model mean nothing beyond
"it runs and the gradient is the one the docstring states".

    ND_OFFLINE=1 python3 tests/test_grpo_state.py      # needs torch (CPU is enough) and Lean

1. On-policy trajectories: replaying every rollout's recorded action ids in a fresh Env (same name base) reproduces the
   recorded state ids at every step and the rollout's ND proof.
2. Gradient: pg_update's accumulated gradient equals autograd of -sum_i A_i log pi(rollout_i) / (P G divisor) computed
   directly (one forward over all pairs), and is independent of the chunk size (lp_batch 1 vs 512); at T = 0.8 it is
   the gradient of log softmax(logits / T).
3. Zero advantages with kl = 0: no pairs, parameters unchanged.
4. Direction: a few steps with A = +1 on one rollout raise its sequence log-prob; A = -1 lowers it.
5. KL: with the reference equal to the policy, the k3 KL is 0 and the gradient equals the kl = 0 gradient.
6. Smoke: grpo_state.py --rounds 2 runs to DONE for each advantage variant, writes round_<r>.json / found_<r>.jsonl /
   found_transfer_<r>.jsonl and a checkpoint per boundary; found proofs are Lean-accepted; compute rows name phases
   sample / update / eval with attempts, actions, gen_tokens, train_steps, train_tokens.
7. Train / sample consistency: at T 0.01 every recorded action token is the argmax of the teacher-forced logits that
   pg_update differentiates (batched, left-padded sampling with caches vs one right-padded forward).

ND_GRPO_TEST_ARCH=best (run `grpo-best`) runs 1-7 on a tiny copy of Robbie's ALiBiGPT (`state_train.py --recipe best
--best_dims 2,128,4,256`, as tests/test_best_state.py) instead of the 2 x 64 GPT, loaded through the same `load_ckpt`.
"""
import copy, glob, json, os, random, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
os.environ.setdefault('ND_OFFLINE', '1')
fails = []


def check(name, ok, detail=''):
    print(('PASS ' if ok else 'FAIL ') + name + ((' -- ' + str(detail)) if detail and not ok else ''))
    if not ok:
        fails.append(name)


tmp = tempfile.mkdtemp(prefix='ci_grpo_state_')
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
with open(os.path.join(tmp, 'tiny_x4.jsonl'), 'w') as f:
    f.write(''.join(json.dumps(r) + '\n' for r in tiny) * 4)
ARCH = os.environ.get('ND_GRPO_TEST_ARCH', 'sn')
ck = os.path.join(tmp, f'tiny_{ARCH}.pt')
if ARCH == 'best':
    cmd = [sys.executable, os.path.join(HERE, 'state_train.py'), '--recipe', 'best', '--data', os.path.join(tmp, 'tiny_x4.jsonl'),
           '--heldout', pool, '--mode', 'lean_staten', '--cap', '0', '--best_steps', '300', '--best_dims', '2,128,4,256',
           '--curve_every', '0', '--no_compile', '--seed', '0', '--out', ck]
else:
    cmd = [sys.executable, os.path.join(HERE, 'state_train.py'), '--data', os.path.join(tmp, 'tiny_x4.jsonl'), '--mode', 'lean_staten',
           '--cap', '0', '--steps', '400', '--recs', '8', '--n_layer', '2', '--d', '64', '--n_head', '4', '--warmup', '5',
           '--lr', '3e-3', '--log_every', '30', '--seed', '0', '--out', ck]
p = subprocess.run(cmd, capture_output=True, text=True, cwd=HERE, env=env, timeout=900)
check(f'state_train.py: tiny lean_staten model ({ARCH}) exit 0', p.returncode == 0, p.stderr[-800:])

if not fails:
    import torch
    from model import load_ckpt
    from state_env import Env
    from state_sample import prompt_ids, NAME_BASE_MAX
    import grpo_state as gs
    torch.manual_seed(0)
    model, tok, _ = load_ckpt(ck, 'cpu')
    print(f'   arch {ARCH}: {type(model).__name__}, {model.n_params()} params')
    check(f'0. checkpoint loads as the {ARCH} class', (type(model).__name__ == 'ALiBiGPT') == (ARCH == 'best'), type(model).__name__)
    prompts = [r['prompt'] for r in tiny[:2] for _ in range(4)]
    rolls = gs.env_rollouts(model, tok, prompts, temperature=1.0, max_action=64, max_steps=12, batch=8, seed=3)
    # 1. replay
    ok_replay = True
    for i, (pr, r) in enumerate(zip(prompts, rolls)):
        base = random.Random(3 * 1000003 + i).randint(0, NAME_BASE_MAX)
        e = Env(pr, canon=True, base=base, assign=True)
        for s, (sid, aid) in enumerate(r['traj']):
            ok_replay &= (prompt_ids(tok, e) == sid)
            atoks, ended = tok.decode_action(aid)
            if not ended or not e.apply(atoks)[0] or e.done:
                ok_replay &= (s == len(r['traj']) - 1)
                break
        nd = e.nd()
        ok_replay &= (r['nd'] == nd or r['nd'] == 'LEANREJ ' + nd or (r['nd'].startswith('LEAN') and nd.startswith('LEAN')))
    check('1. trajectories replay: recorded state ids and ND proof reproduced', ok_replay)
    nacc = sum(1 for r in rolls if not r['nd'].startswith('LEAN'))
    print(f'   ({nacc}/{len(rolls)} rollouts Lean-accepted; ends {[r["end"] for r in rolls]})')

    class NoStep:           # keeps the gradient readable: pg_update calls zero_grad / step
        def __init__(self, m): self.m = m
        def zero_grad(self, set_to_none=True): self.m.zero_grad(set_to_none=True)
        def step(self): pass
    adv = [0.7, -0.3, 0.0, 0.5, -1.0, 0.2, 0.0, -0.1]
    D = 1e6      # large divisor: the grad norm stays under the clip, so clipping does not rescale
    grads = []
    for lpb in (1, 512):
        m2 = copy.deepcopy(model); m2.train()
        gs.pg_update(m2, None, tok, rolls, adv, NoStep(m2), D, 0.0, lpb)
        grads.append([q.grad.clone() if q.grad is not None else torch.zeros_like(q) for q in m2.parameters()])
    m3 = copy.deepcopy(model); m3.train(); m3.zero_grad()
    pairs = [(j, pa) for j, r in enumerate(rolls) for pa in r['traj']]
    x, mk = gs.pair_batch(tok, [pa for _, pa in pairs], 'cpu')
    lp = gs.token_logprobs(m3, x, mk).sum(1)
    w = torch.tensor([adv[j] for j, _ in pairs])
    (-(w * lp).sum() / D).backward()
    direct = [q.grad.clone() for q in m3.parameters()]
    rel = lambda g1, g2: max(float((a - b).abs().max()) for a, b in zip(g1, g2)) / max(float(b.abs().max()) for b in g2)
    check('2. gradient == autograd of -sum A_i log pi(rollout_i) / (P G divisor)', rel(grads[1], direct) < 1e-4, rel(grads[1], direct))
    check('2. gradient independent of chunk size (lp_batch 1 vs 512)', rel(grads[0], grads[1]) < 1e-4, rel(grads[0], grads[1]))
    m7 = copy.deepcopy(model); m7.train()
    gs.pg_update(m7, None, tok, rolls, adv, NoStep(m7), D, 0.0, 512, temperature=0.8)
    g7 = [q.grad.clone() if q.grad is not None else torch.zeros_like(q) for q in m7.parameters()]
    m8 = copy.deepcopy(model); m8.train(); m8.zero_grad()
    (-(w * gs.token_logprobs(m8, x, mk, 0.8).sum(1)).sum() / D).backward()
    g8 = [q.grad.clone() for q in m8.parameters()]
    check('2. at T = 0.8 the gradient is of log softmax(logits / T) (the sampling distribution)', rel(g7, g8) < 1e-4 and rel(g7, grads[1]) > 1e-3,
          (rel(g7, g8), rel(g7, grads[1])))
    # 3. zero advantages
    m4 = copy.deepcopy(model); before = [q.clone() for q in m4.parameters()]
    opt = torch.optim.AdamW(m4.parameters(), lr=1e-2)
    res = gs.pg_update(m4, None, tok, rolls, [0.0] * len(rolls), opt, 1.0, 0.0, 512)
    check('3. zero advantages, kl 0: no pairs, parameters unchanged', res[3] == 0 and all(torch.equal(a, b) for a, b in zip(before, m4.parameters())))
    # 4. direction
    j = max(range(len(rolls)), key=lambda i: len(rolls[i]['traj']))
    for sign in (1.0, -1.0):
        m5 = copy.deepcopy(model); m5.train()
        opt = torch.optim.AdamW(m5.parameters(), lr=(3e-5 if ARCH == 'best' else 1e-3), weight_decay=0.0)   # best: the run's RL lr
                                                                         # (1e-3 overshoots the Muon-trained ALiBi copy: both signs lower it)
        l0 = gs.rollout_logprobs(m5, tok, [rolls[j]], 512)[0]
        a = [0.0] * len(rolls); a[j] = sign
        for _ in range(3):
            gs.pg_update(m5, None, tok, rolls, a, opt, 1.0, 0.0, 512)
        l1 = gs.rollout_logprobs(m5, tok, [rolls[j]], 512)[0]
        check(f'4. A = {sign:+.0f} moves the rollout log-prob that way ({l0:.3f} -> {l1:.3f})', (l1 - l0) * sign > 0)
    # 5. KL with ref == policy
    m6 = copy.deepcopy(model); m6.train(); ref = copy.deepcopy(model).eval()
    res = gs.pg_update(m6, ref, tok, rolls, adv, NoStep(m6), D, 0.1, 512)
    g6 = [q.grad.clone() if q.grad is not None else torch.zeros_like(q) for q in m6.parameters()]
    check('5. KL(pi || pi_ref) = 0 when ref == policy', res[1] is not None and abs(res[1]) < 1e-5, res[1])
    check('5. KL gradient is 0 there (grad == kl-0 grad)', rel(g6, grads[1]) < 1e-3, rel(g6, grads[1]))

    # 7. train / sample consistency (prompts of different lengths share decode batches)
    pr7 = [r['prompt'] for r in tiny for _ in range(2)]
    r7 = gs.env_rollouts(model, tok, pr7, temperature=0.01, max_action=64, max_steps=12, batch=8, seed=5)
    p7 = [pa for r in r7 for pa in r['traj']]
    x7, m7_ = gs.pair_batch(tok, p7, 'cpu')
    with torch.no_grad():
        lg = model(x7[:, :-1]).float()
    gap = lg.max(-1).values - lg.gather(-1, x7[:, 1:, None])[..., 0]    # 0 where the sampled token is the argmax
    agree = int(((gap == 0) & m7_[:, 1:]).sum()); tot = int(m7_[:, 1:].sum()); worst = float((gap * m7_[:, 1:]).max())
    # T 0.01 picks a near-tied runner-up with probability exp(-gap / 0.01): allow gaps < 0.05 (seen: 247 / 248 on CI)
    check(f'7. T 0.01 sampled action tokens == teacher-forced argmax up to near-ties ({agree}/{tot}, worst logit gap {worst:.4f})',
          tot > 0 and worst < 0.05 and agree >= tot - 2)

    # 6. smoke runs, one per advantage variant
    from lean_judge import judge_many
    smoke_found, smoke_upd = {}, {}
    for adv_kind in ('default', 'unlikely', 'passk', 'distinct'):
        name = f'smoke_{adv_kind}'
        out = os.path.join(tmp, 'art'); ckd = os.path.join(tmp, 'ck')
        cmd = [sys.executable, os.path.join(HERE, 'grpo_state.py'), '--init', ck, '--name', name, '--outdir', out, '--ckptdir', ckd,
               '--targets', pool, '--transfer', pool, '--heldout', pool, '--rounds', '2', '--k', '4', '--prompts', '4', '--group', '4',
               '--adv', adv_kind, '--passk_k', '2', '--max_action', '64', '--max_steps', '12', '--batch', '16', '--lr', '1e-3',
               '--temperature', ('1.5' if ARCH == 'best' else '1.0'), '--seed', '0']   # best: a hotter draw keeps groups mixed (pass@k) + (['--kl', '0.05'] if adv_kind == 'default' else [])
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=HERE, env=env, timeout=900)
        ok = p.returncode == 0 and 'DONE' in p.stdout
        check(f'6. smoke {adv_kind}: exit 0, DONE', ok, (p.stdout[-600:] + p.stderr[-1200:]))
        if not ok:
            continue
        files = [f'{out}/{name}/{x}_{r}.{e}' for r in (1, 2) for x, e in (('round', 'json'), ('found', 'jsonl'), ('found_transfer', 'jsonl'))]
        check(f'6. smoke {adv_kind}: round / found / found_transfer files for both boundaries', all(os.path.exists(f) for f in files))
        check(f'6. smoke {adv_kind}: a checkpoint per boundary', all(os.path.exists(f'{ckd}/{name}_r{r}.pt') for r in (1, 2)))
        fd = [json.loads(l) for l in open(f'{out}/{name}/found_2.jsonl')]
        v = judge_many([(x['prompt'], x['proof']) for x in fd]) if fd else []
        check(f'6. smoke {adv_kind}: every found proof Lean-accepted ({len(fd)})', all(ok for ok, _, _ in v))
        rj = json.load(open(f'{out}/{name}/round_2.json'))
        r1 = json.load(open(f'{out}/{name}/round_1.json'))
        smoke_found[adv_kind] = len(fd)
        smoke_upd[adv_kind] = sum(s_['update_pairs'] for s_ in r1['steps'] + rj['steps'])
        check(f'6. smoke {adv_kind}: round json has targets_cum / transfer_cum / heldout_greedy / steps',
              all(k in rj for k in ('targets_cum', 'transfer_cum', 'heldout_greedy', 'steps')))
    print('   smoke found proofs', smoke_found, 'update pairs', smoke_upd)
    check('6. smoke: found proofs and nonzero-advantage updates in every variant',
          len(smoke_found) == 4 and all(smoke_found.values()) and all(smoke_upd.values()), (smoke_found, smoke_upd))
    rows = []
    for fn in glob.glob(os.path.join(tmp, 'registry', '**', '*.jsonl'), recursive=True):
        rows += [json.loads(l) for l in open(fn) if l.strip()]
    comp = [r for r in rows if str(r.get('metric', '')).startswith(('gen_tokens', 'train_steps', 'attempts', 'actions', 'train_tokens', 'gpu_seconds'))
            and str(r.get('labels', {}).get('arm', r.get('arm', ''))).startswith('smoke_')]
    phases = {(r.get('labels') or {}).get('phase', r.get('phase')) for r in comp}
    mets = {r['metric'] for r in comp}
    check('6. compute rows: phases sample / update / eval', {'sample', 'update', 'eval'} <= phases, phases)
    check('6. compute rows: attempts, actions, gen_tokens, train_steps, train_tokens',
          {'attempts', 'actions', 'gen_tokens', 'train_steps', 'train_tokens'} <= mets, mets)

if not fails:
    # 8. --resume_round (run grpo-best): a 3-round run, then the same run "crashed" in its boundary-2 evaluation
    # (run to boundary 2 with --max_steps_total 2, then round_2 / found_2 / alloc_2 removed) resumes from <name>_r2.pt and reaches DONE;
    # the theorem order is replayed, so round 3 trains on the same theorems as the uninterrupted run.
    out = os.path.join(tmp, 'res'); ckd = os.path.join(tmp, 'resck')
    base = [sys.executable, os.path.join(HERE, 'grpo_state.py'), '--init', ck, '--outdir', out, '--ckptdir', ckd,
            '--targets', pool, '--transfer', pool, '--heldout', pool, '--rounds', '3', '--k', '4', '--prompts', '4', '--group', '4',
            '--adv', 'default', '--max_action', '64', '--max_steps', '12', '--batch', '16', '--lr', '1e-3',
            '--temperature', ('1.5' if ARCH == 'best' else '1.0'), '--seed', '0', '--steps_log']
    p1 = subprocess.run(base + ['--name', 'full'], capture_output=True, text=True, cwd=HERE, env=env, timeout=900)
    p2 = subprocess.run(base + ['--name', 'crash', '--max_steps_total', '2'], capture_output=True, text=True, cwd=HERE, env=env, timeout=900)
    d = os.path.join(out, 'crash')
    for f in ('round_2.json', 'found_2.jsonl', 'found_transfer_2.jsonl', 'alloc_2.json'):
        os.remove(os.path.join(d, f))
    p3 = subprocess.run(base + ['--name', 'crash', '--resume_round', '2'], capture_output=True, text=True, cwd=HERE, env=env, timeout=900)
    ok = p1.returncode == 0 and p3.returncode == 0 and 'DONE' in p3.stdout and 'RESUME' in p3.stdout
    check('8. resume: --resume_round 2 after a boundary-2 crash reaches DONE', ok, (p3.stdout[-500:] + p3.stderr[-1200:]))
    if ok:
        st = [json.loads(l) for l in open(os.path.join(d, 'steps.jsonl'))]
        fu = [json.loads(l) for l in open(os.path.join(out, 'full', 'steps.jsonl'))]
        check('8. resume: one steps.jsonl row per update, 1..last', [x['step'] for x in st] == [x['step'] for x in fu], ([x['step'] for x in st], len(fu)))
        check('8. resume: round_2 / round_3 / resume_r2.json written', all(os.path.exists(os.path.join(d, f)) for f in ('round_2.json', 'round_3.json', 'resume_r2.json')))
        r2 = json.load(open(os.path.join(d, 'round_2.json')))
        check('8. resume: boundary 2 re-evaluated (transfer / held-out greedy present)', 'heldout_greedy' in r2 and 'transfer_round' in r2)
        ri = json.load(open(os.path.join(d, 'resume_r2.json')))
        check('8. resume: AdamW state of boundary 2 reloaded', ri['optimizer'].startswith('AdamW state saved at boundary 2'), ri)

print('FAIL' if fails else 'PASS', f'({len(fails)} failures)')
sys.exit(1 if fails else 0)
