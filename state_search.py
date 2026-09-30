#!/usr/bin/env python3
"""Search experts in the step environment (run `search-expert`): best-first search and truncate-and-resume.

  StepFilter(tok)                  per-step, reject-only type check of the action just applied (prefilter's checker)
  clone(env)                       an independent copy of an `Env` (the search tree's nodes)
  search_generate(model, tok, prompts, budgets, ...)   best-first over (theorem, state) nodes     -> ND strings, info
  resume_generate(model, tok, prompts, budgets, ...)   truncate-and-resume chains                 -> ND strings, info

Both return, like `state_sample.env_generate`, one ND string per prompt after the Lean gate (a clean ND string where
Lean accepted the assembled `lean_seq` text; `LEANREJ <nd>` / `LEANPARSE <reason>` otherwise), plus a per-prompt info
list (`actions` generated, `expansions` / `attempts`, `steps` of the proof).  **Lean alone decides**: the step filter
only ends branches whose text Lean is certain to reject (`lean_prefilter`: a `have` whose term does not have its
declared type up to `¬A := A -> False`); every proof that is counted went through `lean_gate` from its literal text.

Best-first (BFS-Prover 2502.03438v3 Eq. 1): a node is a partial proof; its priority is Σ log p / L^alpha over its L
actions, log p the model's log-probability (temperature 1) of each action's tokens.  Each expansion pops the best node
of a theorem and samples `width` actions from its state at `temperature` (deduplicated; every sampled action counts
against the budget).  A child whose action the environment or the filter rejects is dropped; a child whose state was
already reached in this theorem's tree is dropped; a finished child ends the theorem's search (proved, pending Lean).
When every node of a tree has been expanded, the expanded nodes return to the frontier with their priorities (sampling
is stochastic, so a re-expansion can draw new actions).  A theorem stops when proved or when its action budget cannot
pay for another expansion.  Expansions are batched
across theorems (several nodes per theorem per wave only when fewer than batch / width theorems are open), so the
decode batch stays full.

Truncate-and-resume (DeepSeek-Prover-V1.5 2408.08152v1 §3.1): `chains` attempts per theorem run in parallel as in the
sampling loop; when an action fails, the next attempt of that chain starts from the state before the failing action
instead of from scratch.  After `resume_max` consecutive failures from the same state, or at the step cap, the chain
restarts from the theorem's first state.  A theorem stops when proved or when its budget is spent.
"""
import collections, heapq, os, random, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
import record
from sample import generate_ids_fast
from state_env import Env, Frame, BOT as ENV_BOT
from state_sample import prompt_ids, NAME_BASE_MAX
from lean_tok import ftoks
import lean_prefilter as LP


# ------------------------------------------------------------------ the per-step filter
class StepFilter:
    """Called on an environment right after `apply` succeeded.  Returns None (pass) or a reason string.
    It checks the one thing the environment does not: that the term of the `have` just applied has the declared type
    (premise lines: the premise's formula), with `lean_prefilter`'s checker, which rejects only what Lean certainly
    rejects.  Box openings, `Or.elim` heads and `exact` are already checked by the environment (binder, major premise,
    goal)."""

    def __init__(self, tok):
        self.tok = tok
        self._prem = {}
        self._f = {}
        self.n = 0
        self.rej = collections.Counter()

    def lp(self, f):
        g = self._f.get(f)
        if g is None:
            g = LP._P(ftoks(f)).formula()
            self._f[f] = g
        return g

    def prem(self, prompt):
        p = self._prem.get(prompt)
        if p is None:
            p = LP.parse_statement(self.tok.statement(prompt))[0]
            self._prem[prompt] = p
        return p

    def __call__(self, e):
        act = e._eff
        if not act or act[0] != 'have':
            return None
        j = act.index(':=')
        t = act[j + 1]
        if t == '(' or t == 'Or.elim':
            return None
        self.n += 1
        nm = act[1]
        try:
            scope = {}
            for fr in e.frames:
                for n, f in fr.names.items():
                    if n != nm:
                        scope[n] = self.lp(f)
            want = self.lp(e.frames[-1].names[nm])
            LP._term(LP._P(list(act[j + 1:])), scope, want, self.prem(e.prompt))
        except LP._Reject as r:
            self.rej[str(r)] += 1
            return str(r)
        except (LP._Pass, RecursionError, KeyError, IndexError):
            return None
        return None


# ------------------------------------------------------------------ cloning
def _clone_frame(f):
    g = Frame.__new__(Frame)
    g.kind = f.kind; g.goal = f.goal; g.pending = f.pending; g.ore_right = f.ore_right
    g.htoks = list(f.htoks); g.names = dict(f.names); g.last = f.last
    return g


def clone(e):
    c = Env.__new__(Env)
    c.__dict__.update(e.__dict__)
    c.frames = [_clone_frame(f) for f in e.frames]
    c.text = list(e.text)
    c.hist = list(e.hist)
    return c


def _root(prompt, tok, rng_seed):
    if getattr(tok, 'canon', False):
        base = random.Random(rng_seed).randint(0, NAME_BASE_MAX)
        return Env(prompt, canon=True, base=base, assign=True)
    return Env(prompt)


def _decode(model, tok, pids, temperature, max_action, seed, st, want_lp):
    dev = next(model.parameters()).device
    lps = [] if want_lp else None
    with torch.autocast('cuda', dtype=torch.bfloat16, enabled=(dev.type == 'cuda')):
        outs = generate_ids_fast(model, tok, pids, goals=None, greedy=False, temperature=temperature,
                                 max_new=max_action, seed=seed, early='eos', compact=True, stats=st, logp=lps)
    return outs, lps


def _finish_gate(tok, prompts, res_env, st, t0, gate):
    dev_cuda = torch.cuda.is_available()
    res_nd, res_tx = [], []
    for i, e in enumerate(res_env):
        if e is None:
            res_nd.append('LEANPARSE search: unsolved'); res_tx.append(None); continue
        nd = e.nd()
        res_nd.append(nd)
        res_tx.append(tok.text(e.text) if e.done and not nd.startswith('LEANPARSE') else None)
    st['env_wall_s'] = st.get('env_wall_s', 0.0) + time.time() - t0
    if dev_cuda:
        st['peak_alloc_gb'] = torch.cuda.max_memory_allocated() / 2 ** 30
        st['peak_reserved_gb'] = torch.cuda.max_memory_reserved() / 2 ** 30
        torch.cuda.empty_cache()
    if gate:
        from lean_gate import gate as _gate
        res_nd = _gate(tok, prompts, res_nd, res_tx)
    return res_nd


# ------------------------------------------------------------------ best-first
class _Tree:
    __slots__ = ('heap', 'used', 'exp', 'seen', 'root', 'proof', 'cnt', 'maxd', 'closed', 'reopen')

    def __init__(self, root):
        self.root = root
        self.heap = [(0.0, 0, root, 0.0, 0)]     # (-priority, tiebreak, env, sum log p, depth)
        self.used = 0; self.exp = 0; self.cnt = 1; self.maxd = 0; self.closed = []; self.reopen = 0
        self.seen = {tuple(root.state_tokens())}
        self.proof = None


@torch.no_grad()
def search_generate(model, tok, prompts, budgets, width=4, alpha=1.0, temperature=0.8, max_action=256, max_steps=48,
                    batch=2048, seed=0, stats=None, gate=True, step_filter=None):
    st = stats if stats is not None else {}
    cnt = st.setdefault('env_end', collections.Counter())
    why_cnt = st.setdefault('env_fail_reason', collections.Counter())
    t0 = time.time()
    N = len(prompts)
    trees = [_Tree(_root(p, tok, seed * 1000003 + i)) for i, p in enumerate(prompts)]
    record.count(attempts=N)
    active = [i for i in range(N) if budgets[i] >= width]
    maxexp = max(1, batch // width)
    wave = 0
    while active:
        # --- choose the expansions of this wave (rotate so every open theorem is served in turn)
        rot = (wave * maxexp) % len(active)
        order = active[rot:] + active[:rot]
        per = max(1, maxexp // len(active))
        sel = []
        for i in order:
            T = trees[i]
            for q in range(per):
                if len(sel) >= maxexp or T.used + width > budgets[i]:
                    break
                if not T.heap:                          # every open node is expanded: they all return to the frontier
                    if q > 0 or not T.closed:           # (not while this wave's expansions of this tree are pending)
                        break
                    T.heap = T.closed; T.closed = []; heapq.heapify(T.heap); T.reopen += 1
                item = heapq.heappop(T.heap)
                T.closed.append(item)
                _, _, node, lsum, depth = item
                sel.append((i, node, lsum, depth)); T.used += width; T.exp += 1; T.maxd = max(T.maxd, depth)
            if len(sel) >= maxexp:
                break
        if not sel:
            break
        pids = []
        for _, node, _, _ in sel:
            p = prompt_ids(tok, node)
            pids += [p] * width
        record.count(actions=len(pids))
        st['prompt_tokens'] = st.get('prompt_tokens', 0) + sum(len(p) for p in pids)
        outs, lps = _decode(model, tok, pids, temperature, max_action, seed * 100003 + wave, st, True)
        wave += 1
        for s, (i, node, lsum, depth) in enumerate(sel):
            T = trees[i]
            if T.proof is not None:
                continue
            seen_act = set()
            for w in range(width):
                o = outs[s * width + w]
                atoks, ended = tok.decode_action(o)
                if not ended:
                    cnt['truncated'] += 1; continue
                key = tuple(atoks)
                if key in seen_act:
                    cnt['dup_action'] += 1; continue
                seen_act.add(key)
                c = clone(node)
                ok, why = c.apply(atoks)
                if ok and step_filter is not None:
                    why = step_filter(c)
                    if why:
                        ok = False; why = 'filter ' + why
                if not ok:
                    cnt['filter' if why.startswith('filter') else 'syntax'] += 1; why_cnt[why] += 1; continue
                if c.done:
                    cnt['done'] += 1; T.proof = c; break
                if c.steps >= max_steps:
                    cnt['step_cap'] += 1; continue
                sk = tuple(c.state_tokens())
                if sk in T.seen:
                    cnt['dup_state'] += 1; continue
                T.seen.add(sk)
                l2 = lsum + lps[s * width + w]; d2 = depth + 1
                T.cnt += 1
                heapq.heappush(T.heap, (-(l2 / d2 ** alpha), T.cnt, c, l2, d2))
                cnt['child'] += 1
        active = [i for i in active if trees[i].proof is None and trees[i].used + width <= budgets[i]]
        for i in range(N):                              # free finished trees
            T = trees[i]
            if (T.heap or T.closed) and (T.proof is not None or T.used + width > budgets[i]):
                T.heap = []; T.seen = set(); T.closed = []
    st['env_waves'] = st.get('env_waves', 0) + wave
    res_env = [T.proof for T in trees]
    info = [{'actions': T.used, 'expansions': T.exp, 'max_depth': T.maxd, 'reopen': T.reopen, 'steps': (T.proof.steps if T.proof is not None else None)} for T in trees]
    st['search_actions'] = st.get('search_actions', 0) + sum(T.used for T in trees)
    st['search_expansions'] = st.get('search_expansions', 0) + sum(T.exp for T in trees)
    st['search_budget'] = st.get('search_budget', 0) + int(sum(budgets))
    st['search_proved_env'] = st.get('search_proved_env', 0) + sum(T.proof is not None for T in trees)
    return _finish_gate(tok, prompts, res_env, st, t0, gate), info


# ------------------------------------------------------------------ truncate-and-resume
@torch.no_grad()
def resume_generate(model, tok, prompts, budgets, chains=32, resume_max=4, temperature=0.8, max_action=256,
                    max_steps=48, batch=2048, seed=0, stats=None, gate=True, step_filter=None):
    st = stats if stats is not None else {}
    cnt = st.setdefault('env_end', collections.Counter())
    why_cnt = st.setdefault('env_fail_reason', collections.Counter())
    t0 = time.time()
    N = len(prompts)
    roots = [_root(p, tok, seed * 1000003 + i) for i, p in enumerate(prompts)]
    used = [0] * N; attempts = [0] * N; proof = [None] * N
    # a chain: [theorem, env, consecutive failures from this env]
    pending = collections.deque((i, c) for i in range(N) for c in range(chains) if budgets[i] > 0)
    live = []
    wave = 0
    record.count(attempts=len(pending))
    while pending or live:
        while len(live) < batch and pending:
            i, _ = pending.popleft()
            if proof[i] is None and used[i] < budgets[i]:
                live.append([i, clone(roots[i]), 0]); attempts[i] += 1
        left = {}
        kept = []
        for ch in live:                                 # at most the theorem's remaining budget of chains act this wave
            i = ch[0]
            if proof[i] is not None:
                continue
            left.setdefault(i, budgets[i] - used[i])
            if left[i] > 0:
                left[i] -= 1; kept.append(ch)
        live = kept
        if not live:
            continue
        pids = [prompt_ids(tok, ch[1]) for ch in live]
        record.count(actions=len(live))
        for ch in live:
            used[ch[0]] += 1
        st['prompt_tokens'] = st.get('prompt_tokens', 0) + sum(len(p) for p in pids)
        outs, _ = _decode(model, tok, pids, temperature, max_action, seed * 100003 + wave, st, False)
        wave += 1
        keep = []
        for ch, o in zip(live, outs):
            i, e, nfail = ch
            if proof[i] is not None:
                continue
            atoks, ended = tok.decode_action(o)
            ok, why = False, 'action truncated'
            c = None
            if ended:
                c = clone(e)
                ok, why = c.apply(atoks)
                if ok and step_filter is not None:
                    why = step_filter(c)
                    if why:
                        ok = False; why = 'filter ' + why
            if ok and c.done:
                cnt['done'] += 1; proof[i] = c; continue
            if ok and c.steps < max_steps:
                keep.append([i, c, 0]); continue
            # the attempt failed at this action: resume from the state before it (or restart)
            if not ended:
                cnt['truncated'] += 1
            elif ok:
                cnt['step_cap'] += 1
            else:
                cnt['filter' if why.startswith('filter') else 'syntax'] += 1; why_cnt[why] += 1
            if used[i] >= budgets[i]:
                continue
            attempts[i] += 1
            if ok or nfail + 1 >= resume_max:          # step cap / stuck: start again from the first state
                cnt['restart'] += 1
                keep.append([i, clone(roots[i]), 0])
            else:
                cnt['resume'] += 1
                keep.append([i, e, nfail + 1])
        live = keep
    st['env_waves'] = st.get('env_waves', 0) + wave
    info = [{'actions': used[i], 'attempts': attempts[i], 'steps': (proof[i].steps if proof[i] is not None else None)} for i in range(N)]
    st['search_actions'] = st.get('search_actions', 0) + sum(used)
    st['search_budget'] = st.get('search_budget', 0) + int(sum(budgets))
    st['search_proved_env'] = st.get('search_proved_env', 0) + sum(p is not None for p in proof)
    return _finish_gate(tok, prompts, proof, st, t0, gate), info
