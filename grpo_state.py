#!/usr/bin/env python3
"""GRPO **in the proof-state environment** (run `grpo-state`): groups of G rollouts per theorem from the same start
state, reward 1 iff Lean accepts the literal assembled proof, every action of a rollout carries the rollout's
advantage, policy-gradient loss on the action tokens given the state (+ optional KL to the initial policy).

  python3 grpo_state.py --init ckpts/sc12/stage1_SN_cap12_s0.pt --name grpo_default_s0 --seed 0 --adv default
  python3 grpo_state.py ... --adv unlikely --beta_rank 0.25        # He et al. 2506.02355v2 §4.1
  python3 grpo_state.py ... --adv passk --passk_k 4                # Chen et al. 2508.10751v1 §2.4 (PKPO-equivalent)
  python3 grpo_state.py ... --adv distinct --bonus 0.5             # distinct-proof bonus
(advantage definitions and their unit tests: grpo_adv.py, tests/test_grpo_adv.py)

Budget and bookkeeping follow `state_ladder_ei.py`, so every read-out script applies unchanged: the target sample
budget is --rounds x --k x N (EI's), split into --rounds round-equivalents.  At each boundary r it writes, in
<outdir>/<name>/: found_<r>.jsonl (every distinct Lean-accepted proof of a target sampled DURING TRAINING so far,
with the round-equivalent it first appeared in; the state ladder's fields), found_transfer_<r>.jsonl (transfer sampled
k times per theorem at the boundary with `state_sample.env_generate`, cumulative over boundaries as in the ladder, never
trained on), round_<r>.json (targets_cum / transfer_cum with L* and L_true bins, greedy transfer and held-out, the
per-step training diagnostics) and <ckptdir>/<name>_r<r>.pt; results-registry rows via record.round_stats and compute
rows per (phase, round) via record.phase.  Unlike the ladder, the boundary evaluations are of the policy *after*
round-equivalent r (the ladder's round r evaluates the checkpoint it samples from, i.e. after r - 1 fine-tunes).

Update (one per step, on-policy): P prompts (cycling a shuffled order) x G rollouts at temperature T;
  loss = - sum_rollouts A_i sum_actions sum_tokens log pi(a_t | state, a_<t) / (P G divisor)
       + kl * sum_rollouts sum_tokens k3(pi, pi_ref) / (P G divisor),     k3 = exp(ref - lp) - (ref - lp) - 1
with the divisor fixed (--divisor; not the length), grad-norm clip 1.0, AdamW.  Log-probs are at temperature 1 on the
exact ids the sampler fed and produced (the state prompt, then the action up to and including <eos>; a truncated action
is all its tokens).  Every sampled action is in the loss, including the one that failed: it was the policy's choice.
"""
import argparse, collections, copy, json, math, os, random, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch, torch.nn.functional as F
from model import load_ckpt, save_ckpt
from sample import generate_ids_fast
from state_env import Env
from state_sample import prompt_ids, NAME_BASE_MAX, env_stats_json
from lean_judge import judge_many    # Lean alone decides (Dan, 2026-09-27)
from prune import pruned_length
from normalize import norm
from eval_set import judge, summarize
import state_ladder_ei as sl
from grpo_adv import group_advantages, VARIANTS


@torch.no_grad()
def env_rollouts(model, tok, prompts, temperature=0.8, max_action=256, max_steps=48, batch=2048, seed=0, stats=None):
    """`state_sample.env_generate` (same worklist, name bases, decode seeding, gate), keeping every rollout's
    trajectory.  -> list of {'nd': ND string (clean iff Lean accepted), 'traj': [(state ids, action ids)], 'end': how}"""
    dev = next(model.parameters()).device
    st = stats if stats is not None else {}
    cnt = st.setdefault('env_end', collections.Counter())
    steps_hist = st.setdefault('env_steps', collections.Counter())
    res = [None] * len(prompts)
    res_tx = [None] * len(prompts)
    trajs = [[] for _ in prompts]
    live, nxt, wave = [], 0, 0
    import record
    record.count(attempts=len(prompts))

    def finish(i, e, how):
        nd = e.nd()
        res[i] = {'nd': nd, 'traj': trajs[i], 'end': how}
        res_tx[i] = tok.text(e.text) if e.done and not nd.startswith('LEANPARSE') else None
        steps_hist[e.steps] += 1; cnt[how] += 1

    while nxt < len(prompts) or live:
        while len(live) < batch and nxt < len(prompts):
            if getattr(tok, 'canon', False):
                base = random.Random(seed * 1000003 + nxt).randint(0, NAME_BASE_MAX)
                e = Env(prompts[nxt], canon=True, base=base, assign=True)
            else:
                e = Env(prompts[nxt])
            live.append((nxt, e)); nxt += 1
        pids = [prompt_ids(tok, e) for _, e in live]
        record.count(actions=len(live))
        with torch.autocast('cuda', dtype=torch.bfloat16, enabled=(dev.type == 'cuda')):
            outs = generate_ids_fast(model, tok, pids, goals=None, greedy=False, temperature=temperature,
                                     max_new=max_action, seed=seed * 100003 + wave, early='eos', compact=True, stats=st)
        wave += 1
        keep = []
        for (i, e), p, o in zip(live, pids, outs):
            aid = []
            for x in o:
                if x == tok.pad:
                    continue
                aid.append(x)
                if x == tok.eos:
                    break
            trajs[i].append((list(p), aid))
            atoks, ended = tok.decode_action(o)
            if not ended:
                e.failed = 'action truncated'; finish(i, e, 'truncated'); continue
            ok, why = e.apply(atoks)
            if not ok:
                finish(i, e, 'syntax'); continue
            if e.done:
                finish(i, e, 'done'); continue
            if e.steps >= max_steps:
                e.failed = 'step cap'; finish(i, e, 'step_cap'); continue
            keep.append((i, e))
        live = keep
    st['env_waves'] = st.get('env_waves', 0) + wave
    from lean_gate import gate
    nds = gate(tok, prompts, [r['nd'] for r in res], res_tx)
    for r, nd in zip(res, nds):
        r['nd'] = nd
    return res


def pair_batch(tok, pairs, dev):
    """[(state ids, action ids)] -> right-padded x, action mask (as state_train.batch, without the name shift: these are
    the exact ids the policy saw and wrote)."""
    seqs = [p + a for p, a in pairs]
    T = max(len(s) for s in seqs)
    x = torch.full((len(seqs), T), tok.pad, dtype=torch.long)
    m = torch.zeros((len(seqs), T), dtype=torch.bool)
    for i, ((p, a), s) in enumerate(zip(pairs, seqs)):
        x[i, :len(s)] = torch.tensor(s)
        m[i, len(p):len(s)] = True
    return x.to(dev), m.to(dev)


def token_logprobs(model, x, m):
    """-> (B, T-1) log pi of each next token, zero off the action mask."""
    dev = x.device
    with torch.autocast('cuda', dtype=torch.bfloat16, enabled=(dev.type == 'cuda')):
        logits = model(x[:, :-1])
    lp = -F.cross_entropy(logits.reshape(-1, logits.size(-1)).float(), x[:, 1:].reshape(-1), reduction='none').view(x.size(0), -1)
    return lp * m[:, 1:]


@torch.no_grad()
def rollout_logprobs(model, tok, rolls, lp_batch):
    """sequence log-prob of each rollout (sum over its actions' tokens) under `model` -> list of floats."""
    dev = next(model.parameters()).device
    flat = [(j, pa) for j, r in enumerate(rolls) for pa in r['traj']]
    out = [0.0] * len(rolls)
    for s in range(0, len(flat), lp_batch):
        ch = flat[s:s + lp_batch]
        x, m = pair_batch(tok, [pa for _, pa in ch], dev)
        v = token_logprobs(model, x, m).sum(1).tolist()
        for (j, _), y in zip(ch, v):
            out[j] += y
    return out


def pg_update(model, ref, tok, rolls, adv, opt, norm_div, kl, lp_batch):
    """one accumulated policy-gradient (+ KL) step over the rollouts' (state, action) pairs.
    -> (loss, kl_mean_per_token or None, grad norm, pairs, train tokens)"""
    dev = next(model.parameters()).device
    use = [j for j in range(len(rolls)) if adv[j] != 0 or kl > 0]
    flat = [(j, pa) for j in use for pa in rolls[j]['traj']]
    if not flat:
        return 0.0, None, 0.0, 0, 0
    opt.zero_grad(set_to_none=True)
    loss_t, kl_sum, kl_n = 0.0, 0.0, 0
    for s in range(0, len(flat), lp_batch):
        ch = flat[s:s + lp_batch]
        x, m = pair_batch(tok, [pa for _, pa in ch], dev)
        lp = token_logprobs(model, x, m)
        w = torch.tensor([adv[j] for j, _ in ch], device=dev, dtype=torch.float32)
        l = -(w[:, None] * lp).sum() / norm_div
        if kl > 0:
            with torch.no_grad():
                lr_ = token_logprobs(ref, x, m)
            d = (lr_ - lp) * m[:, 1:]
            k3 = (torch.exp(d) - d - 1) * m[:, 1:]
            l = l + kl * k3.sum() / norm_div
            kl_sum += float(k3.sum()); kl_n += int(m[:, 1:].sum())
        l.backward(); loss_t += float(l)
    gn = float(torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0))
    opt.step()
    ntok = sum(len(p) + len(a) for _, (p, a) in flat)
    return loss_t, (kl_sum / kl_n if kl_n else None), gn, len(flat), ntok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--init', required=True); ap.add_argument('--name', required=True)
    ap.add_argument('--outdir', default='artifacts/grpo_state'); ap.add_argument('--ckptdir', default='ckpts/grpo_state')
    ap.add_argument('--targets', default='data/ladder/rl_targets.jsonl')
    ap.add_argument('--transfer', default='data/ladder/transfer.jsonl')
    ap.add_argument('--heldout', default='data/heldout.jsonl')
    ap.add_argument('--rounds', type=int, default=8)
    ap.add_argument('--k', type=int, default=32, help='EI-equivalent attempts per target per round (sets the budget); also transfer pass@k')
    ap.add_argument('--group', type=int, default=8); ap.add_argument('--prompts', type=int, default=256, help='theorems per step')
    ap.add_argument('--adv', default='default', choices=VARIANTS)
    ap.add_argument('--beta_rank', type=float, default=0.25); ap.add_argument('--passk_k', type=int, default=4)
    ap.add_argument('--bonus', type=float, default=0.5); ap.add_argument('--adv_std', action='store_true', help='divide group advantages by their std (GRPO / Chen et al. sigma)')
    ap.add_argument('--kl', type=float, default=0.0, help='KL(pi || pi_init) coefficient (k3 estimator); 0 = none, as run 4')
    ap.add_argument('--temperature', type=float, default=0.8); ap.add_argument('--lr', type=float, default=1e-4)
    ap.add_argument('--divisor', type=float, default=400.0, help='fixed loss divisor per rollout (grpo.py: max_new = 400)')
    ap.add_argument('--max_action', type=int, default=256); ap.add_argument('--max_steps', type=int, default=48)
    ap.add_argument('--batch', type=int, default=2048, help='decode batch (rollouts in flight)')
    ap.add_argument('--lp_batch', type=int, default=512, help='(state, action) pairs per forward/backward chunk')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--max_steps_total', type=int, default=0, help='smoke tests: stop after this many updates (0 = the budget)')
    ap.add_argument('--steps_log', action='store_true', help='append every step\'s stats to <out>/steps.jsonl as it happens')
    ap.add_argument('--no_eval', action='store_true', help='smoke tests: skip the boundary transfer / greedy evaluations')
    a = ap.parse_args()
    out = f'{a.outdir}/{a.name}'
    os.makedirs(out, exist_ok=True); os.makedirs(a.ckptdir, exist_ok=True)
    import record    # results registry (REGISTRY.md)
    record.save_config(vars(a), out, arm=a.name)
    record.preflight()
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    torch.manual_seed(a.seed); rng = random.Random(a.seed)
    model, tok, _ = load_ckpt(a.init, dev)
    assert getattr(tok, 'state_mode', False), 'grpo_state needs a lean_state* checkpoint'
    ref = None
    if a.kl > 0:
        ref = copy.deepcopy(model).eval()
        for p in ref.parameters():
            p.requires_grad_(False)
    model.train()
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=0.0, betas=(0.9, 0.95))
    targets, transfer, heldout = sl.read(a.targets), sl.read(a.transfer), sl.read(a.heldout)
    sl.ENV['max_action'] = a.max_action; sl.ENV['max_steps'] = a.max_steps
    N = len(targets); budget = a.rounds * a.k * N
    per_step = a.prompts * a.group; steps = max(1, budget // per_step)
    if a.adv == 'passk':
        assert a.passk_k <= a.group
    boundaries = {max(1, int(round(r * steps / a.rounds))): r for r in range(1, a.rounds + 1)}
    last = steps if not a.max_steps_total else min(steps, a.max_steps_total)
    if a.max_steps_total:
        boundaries = {s: r for s, r in boundaries.items() if s <= last} or {last: 1}
    norm_div = a.prompts * a.group * a.divisor
    print(f'{N} targets, budget {budget} rollouts = {steps} steps of {per_step} ({a.prompts} x G {a.group}); adv {a.adv}; '
          f'boundaries {sorted(boundaries)}; params {model.n_params()} mode {tok.mode}', flush=True)
    found = collections.defaultdict(list)          # target name -> [{proof, norm, written, pruned, round}]
    found_keys = collections.defaultdict(set)
    found_t = collections.defaultdict(list)
    tried, okc = collections.Counter(), collections.Counter()
    order = list(range(N)); rng.shuffle(order); ptr = 0
    stats_steps = []
    env_st = {}
    t0 = time.time(); samples = 0
    for step in range(1, last + 1):
        rnum = min((r for s, r in boundaries.items() if s >= step), default=a.rounds)
        record.phase('sample', round=rnum)
        idxs = []
        for _ in range(a.prompts):
            if ptr >= N:
                rng.shuffle(order); ptr = 0
            idxs.append(order[ptr]); ptr += 1
        flat_t = [targets[i] for i in idxs for _ in range(a.group)]
        model.eval()
        ts = time.time()
        rolls = env_rollouts(model, tok, [t['prompt'] for t in flat_t], temperature=a.temperature, max_action=a.max_action,
                             max_steps=a.max_steps, batch=a.batch, seed=a.seed * 1000003 + step, stats=env_st)
        verdicts = judge_many([(t['prompt'], r['nd']) for t, r in zip(flat_t, rolls)])    # registry hits after the gate
        t_sample = time.time() - ts
        R, novel = [], []
        new_step = 0
        for t, r, (ok, reason, nl) in zip(flat_t, rolls, verdicts):
            R.append(1 if ok else 0); tried[t['name']] += 1
            key = None
            if ok:
                okc[t['name']] += 1
                pn = norm(r['nd'])
                if pn not in found_keys[t['name']]:
                    key = pn
            novel.append(key)
        for t, r, (ok, reason, nl), key in zip(flat_t, rolls, verdicts, novel):    # archive update after the novelty keys
            if key is not None and key not in found_keys[t['name']]:
                found_keys[t['name']].add(key)
                found[t['name']].append({'proof': r['nd'], 'norm': key, 'written': nl, 'pruned': pruned_length(t['prompt'], r['nd']), 'round': rnum})
                new_step += 1
        samples += len(rolls)
        logp = None
        mixed = [g for g in range(a.prompts) if 0 < sum(R[g * a.group:(g + 1) * a.group]) < a.group]
        if a.adv == 'unlikely' and mixed:
            sel = [j for g in mixed for j in range(g * a.group, (g + 1) * a.group)]
            lps = rollout_logprobs(model, tok, [rolls[j] for j in sel], a.lp_batch)
            logp = [0.0] * len(rolls)
            for j, v in zip(sel, lps):
                logp[j] = v
        adv = []
        for g in range(a.prompts):
            sl_ = slice(g * a.group, (g + 1) * a.group)
            adv += group_advantages(a.adv, R[sl_], logp=(logp[sl_] if logp else None), novel_keys=novel[sl_], k=a.passk_k,
                                    beta_rank=a.beta_rank, bonus=a.bonus, std=a.adv_std)
        record.phase('update', round=rnum)
        model.train()
        tu = time.time()
        loss, klm, gn, npairs, ntok = pg_update(model, ref, tok, rolls, adv, opt, norm_div, a.kl, a.lp_batch)
        if npairs:
            record.count(train_steps=1, train_tokens=ntok)
        Rg = [sum(R[g * a.group:(g + 1) * a.group]) / a.group for g in range(a.prompts)]
        st = {'step': step, 'round': rnum, 'mean_reward': sum(R) / len(R), 'frac_groups_with_variance': len(mixed) / a.prompts,
              'frac_groups_nonzero_adv': sum(1 for g in range(a.prompts) if any(adv[g * a.group:(g + 1) * a.group])) / a.prompts,
              'frac_groups_all_fail': sum(1 for x in Rg if x == 0) / a.prompts, 'new_proofs': new_step,
              'actions': sum(len(r['traj']) for r in rolls), 'update_pairs': npairs, 'update_tokens': ntok,
              'loss': loss, 'kl_per_token': klm, 'grad_norm': gn, 'samples': samples, 'secs': time.time() - t0,
              'sample_judge_s': t_sample, 'update_s': time.time() - tu,
              'peak_alloc_gb': torch.cuda.max_memory_allocated() / 2 ** 30 if dev == 'cuda' else None}
        stats_steps.append(st)
        if step % 10 == 0 or step == last:
            print(f"step {step}/{steps} r{rnum} reward {st['mean_reward']:.3f} var-groups {st['frac_groups_with_variance']:.2f} "
                  f"new {new_step} loss {loss:.4f} gn {gn:.2f} t {t_sample:.0f}+{st['update_s']:.0f}s solved {sum(1 for v in found.values() if v)}/{N} {time.time()-t0:.0f}s", flush=True)
        if a.steps_log:
            with open(f'{out}/steps.jsonl', 'a') as f:
                f.write(json.dumps(st) + '\n')
        if step not in boundaries:
            continue
        # ---- round-equivalent boundary: the state ladder's bookkeeping
        r = boundaries[step]
        record.phase('eval', round=r)
        model.eval()
        ck = f'{a.ckptdir}/{a.name}_r{r}.pt'
        save_ckpt(ck, model, tok.mode, extra={'grpo_round': r, 'step': step, 'adv': a.adv})
        seed = a.seed * 1000 + r
        stats = {'round': r, 'ckpt': ck, 'k': a.k, 'temperature': a.temperature, 'seed': seed, 'adv': a.adv, 'step': step,
                 'samples': samples, 'group': a.group, 'prompts_per_step': a.prompts}
        rs = [s for s in stats_steps if s['round'] == r]
        stats['target_samples'] = len(rs) * per_step
        stats['target_sample_acc'] = sum(s['mean_reward'] for s in rs) / max(1, len(rs))
        stats['new_proofs_this_round'] = sum(s['new_proofs'] for s in rs)
        stats['frac_groups_with_variance_mean'] = sum(s['frac_groups_with_variance'] for s in rs) / max(1, len(rs))
        stats['frac_groups_all_fail_mean'] = sum(s['frac_groups_all_fail'] for s in rs) / max(1, len(rs))
        if not a.no_eval:
            sl.ENV['stats'] = {}
            prompts = [t['prompt'] for t in transfer for _ in range(a.k)]
            flat = sl.generate(model, tok, prompts, greedy=False, temperature=a.temperature, batch=a.batch, seed=seed + 500)
            rows_t = judge(transfer, [flat[i * a.k:(i + 1) * a.k] for i in range(len(transfer))], 'n_lines')
            stats['transfer_round'] = summarize(rows_t, 'n_lines', f'[{a.name} r{r}] transfer (boundary, pass@{a.k})')
            stats['transfer_sample_acc'] = sum(x['n_ok'] for x in rows_t) / sum(x['n_tried'] for x in rows_t)
            for t, row in zip(transfer, rows_t):
                have = {x['norm'] for x in found_t[t['name']]}
                for p, wl, pl in zip(row['proofs'], row['written_lens'], row['pruned_lens']):
                    pn = norm(p)
                    if pn not in have:
                        have.add(pn); found_t[t['name']].append({'proof': p, 'norm': pn, 'written': wl, 'pruned': pl, 'round': r})
            g = sl.generate(model, tok, [t['prompt'] for t in transfer], greedy=True, batch=a.batch)
            stats['transfer_greedy'] = summarize(judge(transfer, [[p] for p in g], 'n_lines'), 'n_lines', f'[{a.name} r{r}] transfer greedy')
            g = sl.generate(model, tok, [t['prompt'] for t in heldout], greedy=True, batch=a.batch)
            stats['heldout_greedy'] = summarize(judge(heldout, [[p] for p in g], 'n_lines'), 'n_lines', f'[{a.name} r{r}] heldout greedy')
            stats['env_eval'] = env_stats_json(sl.ENV['stats'])
        for pool, fd, recs in (('targets', found, targets), ('transfer', found_t, transfer)):
            if pool == 'transfer' and a.no_eval:
                continue
            ls, ge = sl.lstar(fd, recs)
            stats[f'{pool}_cum'] = {'solved': sum(1 for t in recs if fd.get(t['name'])), 'n': len(recs), 'lstar': ls, 'ge': ge,
                                    'by_bin': sl.by_bin(fd, recs), 'distinct_proofs': sum(len(v) for v in fd.values()),
                                    'attempts_per_theorem': (sum(tried.values()) / len(recs)) if pool == 'targets' else r * a.k}
            print(f"[{a.name} r{r}] {pool} cumulative: solved {stats[f'{pool}_cum']['solved']}/{len(recs)} L*={ls}", flush=True)
        for fn, fd, recs in ((f'{out}/found_{r}.jsonl', found, targets), (f'{out}/found_transfer_{r}.jsonl', found_t, transfer)):
            with open(fn, 'w') as f:
                for t in recs:
                    for x in fd[t['name']]:
                        f.write(json.dumps({'name': t['name'], 'thm': t['thm'], 'prompt': t['prompt'], 'L_true': t['n_lines'], 'gen_lines': t.get('gen_lines'),
                                            'source': t.get('source'), 'schema': t.get('schema'), **x}) + '\n')
        json.dump({'tried': dict(tried), 'accepted': dict(okc)}, open(f'{out}/alloc_{r}.json', 'w'))
        stats['env'] = env_stats_json(env_st)
        stats['steps'] = rs
        stats['secs'] = time.time() - t0
        json.dump(stats, open(f'{out}/round_{r}.json', 'w'), indent=1)
        record.round_stats(stats, f'{out}/round_{r}.json', init=a.init, frozen=False)
        model.train()
    print('DONE', flush=True)


if __name__ == '__main__':
    main()
