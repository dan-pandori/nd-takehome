#!/usr/bin/env python3
"""create-or-elicit Phase 2: sequence-level power sampling of a proof-state model -- target pi(x) ∝ p(x)^alpha over whole
attempts x = (a_1, ..., a_n) (actions, each a token sequence; the environment state is a deterministic function of the
theorem, the attempt's name base and the earlier actions, so p(x) = prod_j p(a_j | s_j)) -- by Metropolis-Hastings with
suffix resampling, block-wise (Karan & Du 2025, "Reasoning with Sampling", Alg. 1, adapted to step boundaries).

Proposal: keep actions < m (m uniform over the current n actions), resample actions m.. up to the block horizon from the
SAME model at token temperature 1/alpha, so q(tok) = p(tok)^alpha / Z(ctx), Z(ctx) = sum_v p(v|ctx)^alpha.  Then
    log A = sum_{tokens of the new suffix} log Z  -  sum_{tokens of the old suffix} log Z  +  log n - log n'
(the alpha log p terms cancel against log q; the last term is the position-choice correction for variable length).
Block-wise: for blocks k = 1..K, extend every chain to horizon k*B steps with the proposal, then N_MCMC MH steps whose
suffixes run to that horizon (or to the end of the attempt).  The output of a chain is its final state ("single shot");
an attempt counts iff Lean accepts the literal text (lean_gate, as everywhere).  Proofs merely *visited* by a chain are
reported separately ("visited", a verifier-in-the-loop variant -- not p^alpha).

Token accounting: every decoded token (first extensions and every proposal, accepted or not) and every prefill token.
--mode plain samples independent attempts at --temperature until each theorem has spent the given per-theorem decoded-
token budget (--budget_from a power run's output, times --budget_mult), so the comparison is at matched sampled tokens.

  python3 coe/power_sample.py --ckpt C --in F.jsonl --alpha 4 --chains 8 --block 4 --n_mcmc 8 --out artifacts/coe/power/X
  python3 coe/power_sample.py --ckpt C --in F.jsonl --mode plain --temperature 0.8 --budget_from artifacts/coe/power/X.json --out ...
  python3 coe/power_sample.py --selftest --ckpt C        # alpha = 1: log Z sums must vanish (|.| < 1e-3 nats per action)
"""
import argparse, collections, json, math, os, random, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import torch
import record
from model import load_ckpt
from state_env import Env
from state_sample import prompt_ids, NAME_BASE_MAX
from guided_sample import clone
from sample import _gumbel_pick


@torch.no_grad()
def decode_scored(model, tok, pids, temperature, alpha, seed, max_new, compact_frac=0.75):
    """sample.generate_ids_fast(early='eos', compact=True) that also returns, per row, the sums over its decoded tokens
    (through <eos>) of log p(tok) at T = 1 and of log Z_alpha(ctx) = logsumexp(alpha * log_softmax(logits)).
    -> list of (ids through <eos> or max_new, sum log p, sum log Z, n decoded tokens)."""
    dev = next(model.parameters()).device
    B0 = len(pids)
    L = max(len(p) for p in pids)
    idx = torch.full((B0, L), tok.pad, dtype=torch.long, device=dev)
    keep = torch.zeros((B0, L), dtype=torch.bool, device=dev)
    for i, p in enumerate(pids):
        idx[i, L - len(p):] = torch.tensor(p, device=dev)
        keep[i, L - len(p):] = True
    pos = (keep.cumsum(1) - 1).clamp(min=0)
    causal = torch.tril(torch.ones(L, L, dtype=torch.bool, device=dev))
    mask = causal[None, None] & keep[:, None, None, :]
    mask = mask | torch.eye(L, dtype=torch.bool, device=dev)[None, None]
    caches = [{'max': L + max_new} for _ in model.blocks]
    logits = model(idx, pos=pos, mask=mask, caches=caches)[:, -1]
    del mask, causal, idx
    out = torch.full((B0, max_new), tok.pad, dtype=torch.long, device=dev)
    declen = torch.full((B0,), max_new, dtype=torch.long, device=dev)
    slp = torch.zeros(B0, dtype=torch.float64, device=dev)
    slz = torch.zeros(B0, dtype=torch.float64, device=dev)
    keepb = torch.ones((B0, L + max_new), dtype=torch.bool, device=dev)
    keepb[:, :L] = keep
    act = torch.arange(B0, device=dev)
    done = torch.zeros(B0, dtype=torch.bool, device=dev)
    cur_pos = pos[:, -1]
    rgen = torch.Generator(device=dev)
    for t in range(max_new):
        nxt = _gumbel_pick(logits, temperature, rgen, seed, t, B0, act)
        live = ~done
        lsm = torch.log_softmax(logits.float(), -1)
        lp = lsm.gather(1, nxt[:, None])[:, 0].double()
        lz = torch.logsumexp(alpha * lsm, -1).double()
        zero = torch.zeros_like(lp)
        slp[act] = slp[act] + torch.where(live, lp, zero)
        slz[act] = slz[act] + torch.where(live, lz, zero)
        keepv = out[act, t]
        out[act, t] = torch.where(live, nxt, keepv)
        newfin = live & (nxt == tok.eos)
        declen[act] = torch.where(newfin, torch.full_like(declen[act], t + 1), declen[act])
        done = done | newfin
        nxt = torch.where(done, torch.full_like(nxt, tok.pad), nxt)
        if t % 16 == 15 or t == max_new - 1:
            n_live = int((~done).sum())
            if n_live == 0:
                break
            if n_live < compact_frac * done.numel():
                sel = (~done).nonzero(as_tuple=True)[0]
                act = act[sel]; nxt = nxt[sel]; cur_pos = cur_pos[sel]; keepb = keepb[sel]
                done = torch.zeros(n_live, dtype=torch.bool, device=dev)
                for c in caches:
                    for key in [key for key, v in c.items() if torch.is_tensor(v)]:
                        nk = c[key][sel].contiguous(); del c[key]; c[key] = nk
        cur_pos = cur_pos + 1
        logits = model(nxt[:, None], pos=cur_pos[:, None], mask=keepb[:, None, None, :L + t + 1], caches=caches)[:, -1]
    o = out.tolist(); dl = declen.tolist(); a_lp = slp.tolist(); a_lz = slz.tolist()
    return [(o[i][:dl[i]], a_lp[i], a_lz[i], dl[i]) for i in range(B0)]


class Chain:
    __slots__ = ('tid', 'cid', 'prompt', 'base', 'acts', 'envs', 'status', 'tokens', 'prefill', 'accepts', 'proposals',
                 'visited')

    def __init__(self, tid, cid, prompt, base):
        self.tid, self.cid, self.prompt, self.base = tid, cid, prompt, base
        e = Env(prompt, canon=True, base=base, assign=True)
        self.acts = []            # [(ids, sum log p, sum log Z, n tokens)]
        self.envs = [e]           # envs[j] = environment BEFORE action j (snapshots); envs[len(acts)] = current
        self.status = 'live'      # live | done | fail | trunc | cap
        self.tokens = 0; self.prefill = 0; self.accepts = 0; self.proposals = 0
        self.visited = set()


def rollout(model, tok, starts, horizon, temperature, alpha, seed, max_action, max_steps, batch, counter):
    """starts: list of (key, env snapshot, n actions so far).  Samples actions until horizon steps, termination or the step
    cap.  -> {key: (new actions, env snapshots after each action, status, decoded tokens, prefill tokens)}"""
    res = {}
    live = [(k, clone(e), n, [], [], 0, 0) for k, e, n in starts]
    while live:
        nxt_live = []
        for s in range(0, len(live), batch):
            chunk = live[s:s + batch]
            pids = [prompt_ids(tok, x[1]) for x in chunk]
            with torch.autocast('cuda', dtype=torch.bfloat16, enabled=torch.cuda.is_available()):
                outs = decode_scored(model, tok, pids, temperature, alpha, seed * 1000003 + counter[0], max_action)
            counter[0] += 1
            for (k, e, n, acts, snaps, ntok, npre), pid, (ids, lp, lz, nt) in zip(chunk, pids, outs):
                ntok += nt; npre += len(pid)
                atoks, ended = tok.decode_action(ids)
                acts.append((ids, lp, lz, nt)); n += 1
                if not ended:
                    res[k] = (acts, snaps + [None], 'trunc', ntok, npre); continue
                ok, why = e.apply(atoks)
                if not ok:
                    res[k] = (acts, snaps + [None], 'fail', ntok, npre); continue
                snaps.append(clone(e))
                if e.done:
                    res[k] = (acts, snaps, 'done', ntok, npre); continue
                if n >= max_steps:
                    res[k] = (acts, snaps, 'cap', ntok, npre); continue
                if n >= horizon:
                    res[k] = (acts, snaps, 'live', ntok, npre); continue
                nxt_live.append((k, e, n, acts, snaps, ntok, npre))
        live = nxt_live
    return res


def run_power(model, tok, recs, a):
    rng = random.Random(a.seed)
    chains = []
    for ti, r in enumerate(recs):
        for c in range(a.chains):
            base = random.Random(a.seed * 1000003 + ti * 1009 + c).randint(0, NAME_BASE_MAX)
            chains.append(Chain(ti, c, r['prompt'], base))
    T = 1.0 / a.alpha
    counter = [0]
    n_blocks = (a.max_steps + a.block - 1) // a.block
    acc_log = collections.Counter()
    t0 = time.time()
    for k in range(n_blocks):
        H = min((k + 1) * a.block, a.max_steps)
        ext = [c for c in chains if c.status == 'live']
        if ext:
            out = rollout(model, tok, [((c.tid, c.cid), c.envs[-1], len(c.acts)) for c in ext], H, T, a.alpha, a.seed,
                          a.max_action, a.max_steps, a.batch, counter)
            for c in ext:
                acts, snaps, st, ntok, npre = out[(c.tid, c.cid)]
                c.acts += acts; c.envs += snaps; c.status = st; c.tokens += ntok; c.prefill += npre
                if st == 'done':
                    c.visited.add(c.envs[-1].nd())
        for it in range(a.n_mcmc):
            props = []
            for c in chains:
                n = len(c.acts)
                if n == 0:
                    continue
                m = rng.randrange(n)
                props.append((c, m))
            out = rollout(model, tok, [((c.tid, c.cid), c.envs[m], m) for c, m in props], H, T, a.alpha, a.seed,
                          a.max_action, a.max_steps, a.batch, counter)
            for c, m in props:
                acts, snaps, st, ntok, npre = out[(c.tid, c.cid)]
                c.tokens += ntok; c.prefill += npre; c.proposals += 1
                n, n2 = len(c.acts), m + len(acts)
                logA = sum(x[2] for x in acts) - sum(x[2] for x in c.acts[m:]) + math.log(n) - math.log(n2)
                if st == 'done':
                    c.visited.add(snaps[-1].nd())
                if math.log(max(rng.random(), 1e-300)) < logA:
                    c.acts = c.acts[:m] + acts
                    c.envs = c.envs[:m + 1] + snaps      # aligned: envs[j] = state before action j (None after a failed one)
                    c.status = st; c.accepts += 1
                    acc_log[(k, 'acc')] += 1
                acc_log[(k, 'prop')] += 1
        print(f'block {k + 1}/{n_blocks} (horizon {H}): live {sum(1 for c in chains if c.status == "live")}, '
              f'done {sum(1 for c in chains if c.status == "done")}, accept rate this block '
              f'{acc_log[(k, "acc")] / max(1, acc_log[(k, "prop")]):.3f}, {time.time() - t0:.0f}s', flush=True)
        if all(c.status != 'live' for c in chains) and H >= max(len(c.acts) for c in chains):
            break
    return chains, {f'{kk[0]}_{kk[1]}': v for kk, v in acc_log.items()}, time.time() - t0


def judge_final(tok, chains):
    """Lean on the literal text of every chain's final state (lean_gate.gate, as env_generate does)."""
    from lean_gate import gate
    prompts, nds, texts, idx = [], [], [], []
    for i, c in enumerate(chains):
        if c.status != 'done':
            continue
        e = c.envs[-1]
        nd = e.nd()
        if nd.startswith('LEANPARSE'):
            continue
        prompts.append(c.prompt); nds.append(nd); texts.append(tok.text(e.text)); idx.append(i)
    ok = [False] * len(chains)
    if prompts:
        g = gate(tok, prompts, nds, texts)
        for i, x in zip(idx, g):
            ok[i] = not x.startswith('LEAN')
    return ok


def judge_visited(chains, recs):
    from lean_judge import judge_many
    pairs = sorted({(recs[c.tid]['prompt'], nd) for c in chains for nd in c.visited if not nd.startswith('LEANPARSE')})
    res = judge_many(pairs) if pairs else []
    good = {p for p, r in zip(pairs, res) if r[0]}
    return good


def run_plain(model, tok, recs, budgets, a):
    """independent attempts at --temperature, per theorem until its decoded-token budget is spent (the last attempt may
    overshoot; it is counted)."""
    spent = [0] * len(recs); prefill = [0] * len(recs)
    ok = [0] * len(recs); tried = [0] * len(recs)
    accepted = [collections.Counter() for _ in recs]       # accepted ND proofs with multiplicity (added 2026-10-12)
    counter = [0]
    rnd = 0
    t0 = time.time()
    while True:
        todo = [i for i in range(len(recs)) if spent[i] < budgets[i]]
        if not todo:
            break
        # one wave: per theorem, enough attempts to cover the remaining budget at the mean cost seen so far
        starts = []
        for i in todo:
            mean = (spent[i] / tried[i]) if tried[i] else 300.0
            kk = max(1, min(256, int(math.ceil((budgets[i] - spent[i]) / max(mean, 1.0)))))
            for j in range(kk):
                base = random.Random(a.seed * 7919 + i * 100003 + tried[i] + j).randint(0, NAME_BASE_MAX)
                starts.append(((i, tried[i] + j), Env(recs[i]['prompt'], canon=True, base=base, assign=True), 0))
        out = rollout(model, tok, starts, a.max_steps, a.temperature, 1.0, a.seed + 77 * rnd, a.max_action, a.max_steps,
                      a.batch, counter)
        rnd += 1
        fin = []
        for (i, j), _, _ in starts:
            acts, snaps, st, ntok, npre = out[(i, j)]
            tried[i] += 1; spent[i] += ntok; prefill[i] += npre
            if st == 'done':
                fin.append((i, snaps[-1]))
        from lean_gate import gate
        if fin:
            g = gate(tok, [recs[i]['prompt'] for i, _ in fin], [e.nd() for _, e in fin], [tok.text(e.text) for _, e in fin])
            for (i, _), x in zip(fin, g):
                if not x.startswith('LEAN'):
                    ok[i] += 1
                    accepted[i][x] += 1
        print(f'plain wave {rnd}: theorems left {sum(1 for i in range(len(recs)) if spent[i] < budgets[i])}, '
              f'solved {sum(1 for x in ok if x)}, {time.time() - t0:.0f}s', flush=True)
    run_plain.accepted = accepted
    return ok, tried, spent, prefill, time.time() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpt', required=True)
    ap.add_argument('--in', dest='inp')
    ap.add_argument('--out')
    ap.add_argument('--mode', default='power', choices=['power', 'plain'])
    ap.add_argument('--alpha', type=float, default=4.0)
    ap.add_argument('--chains', type=int, default=8)
    ap.add_argument('--block', type=int, default=4, help='steps per block')
    ap.add_argument('--n_mcmc', type=int, default=8)
    ap.add_argument('--temperature', type=float, default=0.8, help='plain mode only')
    ap.add_argument('--budget_from', default=None)
    ap.add_argument('--budget_mult', type=float, default=1.0)
    ap.add_argument('--max_action', type=int, default=512)
    ap.add_argument('--max_steps', type=int, default=96)
    ap.add_argument('--batch', type=int, default=1024)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--names', default=None)
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.out:
        record.save_config(vars(a), a.out + '.json')
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    model, tok, extra = load_ckpt(a.ckpt, dev)
    model.eval()
    assert getattr(tok, 'canon', False), 'lean_staten checkpoints only'
    if a.selftest:
        recs = [json.loads(l) for l in open(a.inp or 'data/coe/read1054.jsonl')][:16]
        e = [Env(r['prompt'], canon=True, base=3, assign=True) for r in recs]
        for alpha in (1.0, 4.0):
            with torch.autocast('cuda', dtype=torch.bfloat16, enabled=(dev == 'cuda')):
                outs = decode_scored(model, tok, [prompt_ids(tok, x) for x in e], 1.0 / alpha, alpha, 123, a.max_action)
            mlz = sum(abs(o[2]) for o in outs) / len(outs)
            mlp = sum(o[1] for o in outs) / len(outs)
            print(f'selftest alpha {alpha}: mean |sum log Z| per action {mlz:.6f}, mean sum log p {mlp:.3f}, mean tokens {sum(o[3] for o in outs) / len(outs):.1f}')
            if alpha == 1.0:
                assert mlz < 1e-3, 'log Z must vanish at alpha 1'
        print('selftest ok')
        return
    recs = [json.loads(l) for l in open(a.inp) if l.strip()]
    if a.names:
        keep = set(open(a.names[1:]).read().split()) if a.names.startswith('@') else set(a.names.split(','))
        recs = [r for r in recs if r.get('name') in keep]
    if a.limit:
        recs = recs[:a.limit]
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    gpu = torch.cuda.get_device_name(0) if dev == 'cuda' else 'cpu'
    if a.mode == 'power':
        with record.compute(phase='power', ckpt=a.ckpt, alpha=a.alpha):
            chains, acc_log, secs = run_power(model, tok, recs, a)
            ok = judge_final(tok, chains)
            good_visited = judge_visited(chains, recs)
        per = collections.defaultdict(lambda: {'chains': 0, 'ok': 0, 'tokens': 0, 'prefill': 0, 'accepts': 0, 'proposals': 0,
                                               'status': collections.Counter(), 'visited_ok': 0, 'final_proofs': collections.Counter(),
                                               'final_logp': []})
        for c, o in zip(chains, ok):
            p = per[c.tid]
            p['chains'] += 1; p['ok'] += int(o); p['tokens'] += c.tokens; p['prefill'] += c.prefill
            p['accepts'] += c.accepts; p['proposals'] += c.proposals; p['status'][c.status] += 1
            p['final_logp'].append(round(sum(x[1] for x in c.acts), 3))
            if o:
                p['final_proofs'][c.envs[-1].nd()] += 1
        for c in chains:
            per[c.tid]['visited_ok'] = max(per[c.tid]['visited_ok'],
                                           sum(1 for nd in c.visited if (recs[c.tid]['prompt'], nd) in good_visited))
        rows = []
        for ti, r in enumerate(recs):
            p = per[ti]
            rows.append({'name': r['name'], 'set': r.get('set'), 'chains': p['chains'], 'ok': p['ok'], 'solved': p['ok'] > 0,
                         'visited_solved': p['visited_ok'] > 0, 'tokens': p['tokens'], 'prefill': p['prefill'],
                         'accept_rate': p['accepts'] / max(1, p['proposals']), 'status': dict(p['status']),
                         'final_proofs': dict(p['final_proofs']), 'final_logp': p['final_logp']})
        summ = {'mode': 'power', 'ckpt': a.ckpt, 'in': a.inp, 'alpha': a.alpha, 'chains': a.chains, 'block': a.block,
                'n_mcmc': a.n_mcmc, 'seed': a.seed, 'batch': a.batch, 'gpu': gpu, 'secs': secs, 'n_theorems': len(recs),
                'solved': sum(r['solved'] for r in rows), 'visited_solved': sum(r['visited_solved'] for r in rows),
                'tokens': sum(r['tokens'] for r in rows), 'prefill': sum(r['prefill'] for r in rows),
                'accept_log': acc_log, 'rows': rows}
    else:
        b = json.load(open(a.budget_from))
        bt = {r['name']: r['tokens'] for r in b['rows']}
        recs = [r for r in recs if r['name'] in bt]
        budgets = [a.budget_mult * bt[r['name']] for r in recs]
        with record.compute(phase='plain_matched', ckpt=a.ckpt):
            ok, tried, spent, prefill, secs = run_plain(model, tok, recs, budgets, a)
        acc = getattr(run_plain, 'accepted', [{}] * len(recs))
        rows = [{'name': r['name'], 'set': r.get('set'), 'ok': o, 'solved': o > 0, 'tried': t, 'tokens': s, 'prefill': pf,
                 'budget': bb, 'accepted': dict(ac)} for r, o, t, s, pf, bb, ac in zip(recs, ok, tried, spent, prefill, budgets, acc)]
        summ = {'mode': 'plain', 'ckpt': a.ckpt, 'in': a.inp, 'temperature': a.temperature, 'budget_from': a.budget_from,
                'budget_mult': a.budget_mult, 'seed': a.seed, 'batch': a.batch, 'gpu': gpu, 'secs': secs,
                'n_theorems': len(recs), 'solved': sum(r['solved'] for r in rows), 'tokens': sum(r['tokens'] for r in rows),
                'rows': rows}
    json.dump(summ, open(a.out + '.json', 'w'))
    print(json.dumps({k: v for k, v in summ.items() if k not in ('rows', 'accept_log')}))


if __name__ == '__main__':
    main()
