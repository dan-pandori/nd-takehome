#!/usr/bin/env python3
"""CPU tests for grpo_state.py (run `grpo-state`): gradient sanity and a tiny end-to-end smoke run, on a throwaway
`lean_staten` (arm SN) model that memorises 4 short fixture proofs.  Numbers from this model mean nothing beyond
"it runs and the gradient is the one the docstring states".

    ND_OFFLINE=1 python3 tests/test_grpo_state.py      # needs torch (CPU is enough) and Lean

1. On-policy trajectories: replaying every rollout's recorded action ids in a fresh Env (same name base) reproduces the
   recorded state ids at every step and the rollout's ND proof.
2. Gradient: pg_update's accumulated gradient equals autograd of -sum_i A_i log pi(rollout_i) / (P G divisor) computed
   directly (one forward over all pairs), and is independent of the chunk size (lp_batch 1 vs 512).
3. Zero advantages with kl = 0: no pairs, parameters unchanged.
4. Direction: a few steps with A = +1 on one rollout raise its sequence log-prob; A = -1 lowers it.
5. KL: with the reference equal to the policy, the k3 KL is 0 and the gradient equals the kl = 0 gradient.
6. Smoke: grpo_state.py --rounds 2 runs to DONE for each advantage variant, writes round_<r>.json / found_<r>.jsonl /
   found_transfer_<r>.jsonl and a checkpoint per boundary; found proofs are Lean-accepted; compute rows name phases
   sample / update / eval with attempts, actions, gen_tokens, train_steps, train_tokens.
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
ck = os.path.join(tmp, 'tiny_sn.pt')
cmd = [sys.executable, os.path.join(HERE, 'state_train.py'), '--data', os.path.join(tmp, 'tiny_x4.jsonl'), '--mode', 'lean_staten',
       '--cap', '0', '--steps', '400', '--recs', '8', '--n_layer', '2', '--d', '64', '--n_head', '4', '--warmup', '5',
       '--lr', '3e-3', '--log_every', '30', '--seed', '0', '--out', ck]
p = subprocess.run(cmd, capture_output=True, text=True, cwd=HERE, env=env, timeout=900)
check('state_train.py: tiny lean_staten model exit 0', p.returncode == 0, p.stderr[-800:])

if not fails:
    import torch
    from model import load_ckpt
    from state_env import Env
    from state_sample import prompt_ids, NAME_BASE_MAX
    import grpo_state as gs
    torch.manual_seed(0)
    model, tok, _ = load_ckpt(ck, 'cpu')
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
    # 3. zero advantages
    m4 = copy.deepcopy(model); before = [q.clone() for q in m4.parameters()]
    opt = torch.optim.AdamW(m4.parameters(), lr=1e-2)
    res = gs.pg_update(m4, None, tok, rolls, [0.0] * len(rolls), opt, 1.0, 0.0, 512)
    check('3. zero advantages, kl 0: no pairs, parameters unchanged', res[3] == 0 and all(torch.equal(a, b) for a, b in zip(before, m4.parameters())))
    # 4. direction
    j = max(range(len(rolls)), key=lambda i: len(rolls[i]['traj']))
    for sign in (1.0, -1.0):
        m5 = copy.deepcopy(model); m5.train()
        opt = torch.optim.AdamW(m5.parameters(), lr=1e-3, weight_decay=0.0)
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

    # 6. smoke runs, one per advantage variant
    from lean_judge import judge_many
    smoke_found, smoke_upd = {}, {}
    for adv_kind in ('default', 'unlikely', 'passk', 'distinct'):
        name = f'smoke_{adv_kind}'
        out = os.path.join(tmp, 'art'); ckd = os.path.join(tmp, 'ck')
        cmd = [sys.executable, os.path.join(HERE, 'grpo_state.py'), '--init', ck, '--name', name, '--outdir', out, '--ckptdir', ckd,
               '--targets', pool, '--transfer', pool, '--heldout', pool, '--rounds', '2', '--k', '4', '--prompts', '4', '--group', '4',
               '--adv', adv_kind, '--passk_k', '2', '--max_action', '64', '--max_steps', '12', '--batch', '16', '--lr', '1e-3',
               '--temperature', '1.0', '--seed', '0'] + (['--kl', '0.05'] if adv_kind == 'default' else [])
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

print('FAIL' if fails else 'PASS', f'({len(fails)} failures)')
sys.exit(1 if fails else 0)
