#!/usr/bin/env python3
"""mcts.py -- PUCT search over proof states with an optional learned value (run `mcts-a`, proposal 22, Phase 0).

One tree per theorem; many trees are searched together so the policy's GPU batch stays full.

  node     a state of `state_env.Env` (deduplicated within a tree by `state_key`: two action sequences that reach the
           same frames -- hypotheses, goals, pending boxes -- are one node).
  expand   K actions sampled from the policy at the node's state (temperature `temp`); each is applied to a copy of
           the environment.  Actions the environment rejects, or whose term Lean is certain to reject (`step_reject`,
           the per-step form of `lean_prefilter`'s sound type check), are discarded.  The survivors are merged by
           resulting state; a child's prior is (sum of pi(a) over its distinct actions)^(1/tau), normalised.
  widen    progressive sampling: a visited node with n(s) <= C * N(s)^alpha sampled actions gets K more.
  select   PUCT, AlphaProof's exploration factor c(s) = c_init + log((N(s) + c_base + 1) / c_base):
               a* = argmax Q(s,a) + c(s) * P(s,a) * sqrt(N(s)) / (1 + N(s,a))
           with virtual loss so one tree can contribute several leaves to a round.
  value    with a value head (`value_head.py`): v(s) = sigmoid(solvable logit) * gamma^(predicted steps-to-go).
           Without: v = 0 at every non-terminal leaf, so selection is the prior plus visit counts (proposal 20's E1).
           A finished proof that Lean accepts is worth 1 and ends the tree; one Lean rejects is a dead leaf (value 0).
           Values are discounted by gamma per step on the way up (AlphaProof's Q = gamma^(steps-to-go)).
  Lean     decides every finished proof (lean_gate.gate on the literal `lean_seq` text, as state_sample does).

`search(model, tok, prompts, cfg, value=None)` -> per theorem a dict: solved, proof (ND), the wall / GPU seconds at
which it was found, nodes, expansions, sampled actions and generated tokens; plus a run-level stats dict.
"""
import collections, math, os, random, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
import torch.nn.functional as F
from state_env import Env, Frame
from lean_tok import ParseFail
import lean_prefilter as LP

NAME_BASE_MAX = 32      # as state_sample: canonical names start at n<base+1>, base ~ U[0, 32] per tree


# ---------------------------------------------------------------------------------------------------------- env glue
def clone(e):
    """a deep-enough copy of an Env (frames are mutated by apply; formulas are immutable tuples)."""
    c = Env.__new__(Env)
    c.__dict__.update(e.__dict__)
    fs = []
    for f in e.frames:
        g = Frame(f.kind, f.goal, f.pending, f.ore_right)
        g.htoks = list(f.htoks)          # lines are never mutated after creation
        g.names = dict(f.names)
        g.last = f.last
        fs.append(g)
    c.frames = fs
    c.text = list(e.text)
    c.hist = list(e.hist)
    return c


def state_key(e):
    """everything the future of an attempt depends on: per frame its kind, goal, pending `have`, Or.elim right
    disjunct, hypotheses (in order) and last statement; plus the premise counter (premise lines must come first)."""
    return (e.n_pr, e.seen_non_pr, e.maxname if not e.canon else 0,
            tuple((f.kind, f.goal, f.pending, f.ore_right, tuple(tuple(x) for x in f.htoks), f.last) for f in e.frames))


def scope(e):
    d = {}
    for f in e.frames:
        d.update(f.names)
    return d


def step_reject(e, act):
    """For an atomic `have` the environment accepted: a reason string if Lean is certain to reject its term
    (lean_prefilter's sound type check on the one step), else None.  Box and premise steps are checked by the
    environment itself (binder formula, premise order); `exact` by formula equality."""
    if not act or act[0] != 'have':
        return None
    try:
        i = act.index(':=')
    except ValueError:
        return None
    if act[i + 1] in ('(', 'Or.elim'):
        return None
    try:
        p = LP._P(LP._split(' '.join(act[1:i])))
        p.eat()                                   # the name
        p.eat(':')
        f = p.formula()
        q = LP._P(LP._split(' '.join(act[i + 1:])))
        sc = scope(e)
        LP._term(q, sc, f, e.prem)
        return None
    except LP._Reject as r:
        return str(r)
    except (LP._Pass, RecursionError, IndexError):
        return None


# --------------------------------------------------------------------------------------------------------- the tree
class Node:
    __slots__ = ('env', 'key', 'parent', 'depth', 'children', 'P', 'N', 'W', 'vl', 'n_sampled', 'acts', 'expanded',
                 'dead', 'v', 'proof', 'logpi')

    def __init__(self, env, parent, depth):
        self.env = env
        self.key = None
        self.parent = parent
        self.depth = depth
        self.children = []       # Node list
        self.P = []              # prior per child (normalised)
        self.logpi = []          # per child: log(sum of pi over its distinct actions), unnormalised
        self.N = 0
        self.W = 0.0
        self.vl = 0              # virtual visits in flight
        self.n_sampled = 0       # actions sampled here so far
        self.acts = {}           # distinct action text -> child index or -1 (rejected)
        self.expanded = False
        self.dead = False
        self.v = None            # leaf value estimate
        self.proof = None


class Tree:
    def __init__(self, idx, prompt, base, cfg):
        self.idx = idx
        self.prompt = prompt
        e = Env(prompt, canon=True, base=base, assign=True)
        self.root = Node(e, None, 0)
        self.root.key = state_key(e)
        self.nodes = {self.root.key: self.root}
        self.cfg = cfg
        self.solved = False
        self.proof = None
        self.proof_text = None
        self.proof_node = None
        self.t_found = None
        self.gpu_found = None
        self.expansions = 0
        self.sampled = 0
        self.gen_tokens = 0
        self.lean_checks = 0
        self.lean_rej = 0
        self.dead = False
        self.pending = []        # (node, child env) finished proofs awaiting Lean

    def c_puct(self, n):
        c = self.cfg
        return c['c_init'] + math.log((n + c['c_base'] + 1) / c['c_base'])

    def needs_widen(self, nd):
        c = self.cfg
        return nd.expanded and nd.n_sampled < c['max_samples'] and nd.n_sampled <= c['C'] * max(nd.N, 1) ** c['alpha']

    def select(self):
        """one descent with virtual loss -> the leaf to expand (or widen), or None if the tree has nothing to do.  A
        descent that finds a node with every child dead and no samples left marks it dead and starts again."""
        for _ in range(64):
            r = self._descend()
            if r is not False:
                return r
        return None

    def _descend(self):
        nd = self.root
        path = [nd]
        while True:
            if nd.dead:
                return None
            if not nd.expanded or self.needs_widen(nd):
                break
            Nn = nd.N + nd.vl
            cs = self.c_puct(Nn) * math.sqrt(max(Nn, 1))
            best, bs = None, -1e9
            for ch, p in zip(nd.children, nd.P):
                if ch.dead:
                    continue
                n = ch.N + ch.vl
                q = ch.W / n if n else self.cfg['fpu']
                s = q + cs * p / (1 + n)
                if s > bs:
                    best, bs = ch, s
            if best is None:                                    # every child dead: this node is dead
                if nd.n_sampled < self.cfg['max_samples']:
                    break                                       # ... unless more samples could still find one
                self.mark_dead(nd)
                return None if self.root.dead else False
            nd = best
            path.append(nd)
        for x in path:
            x.vl += 1
        return nd

    def mark_dead(self, nd):
        nd.dead = True
        p = nd.parent
        while p is not None and p.expanded and p.n_sampled >= self.cfg['max_samples'] and all(c.dead for c in p.children):
            p.dead = True
            p = p.parent
        if self.root.dead:
            self.dead = True

    def backup(self, nd, v):
        g = self.cfg['gamma']
        x = nd
        while x is not None:
            x.vl = max(0, x.vl - 1)
            x.N += 1
            x.W += v
            v *= g
            x = x.parent

    def clear_vl(self, nd):
        x = nd
        while x is not None:
            x.vl = max(0, x.vl - 1)
            x = x.parent

    def renorm(self, nd):
        tau = self.cfg['tau']
        if not nd.logpi:
            nd.P = []
            return
        m = max(nd.logpi)
        w = [math.exp((l - m) / tau) for l in nd.logpi]
        s = sum(w)
        nd.P = [x / s for x in w]


# ------------------------------------------------------------------------------------------------- batched sampler
class Sampler:
    """K actions per state, with each action's log-probability, and the trunk feature of the state for the value
    head -- one prefill per distinct state, the KV cache fanned out K ways, row-chunked to bound memory."""

    def __init__(self, model, tok, max_action=64, temp=1.0, row_tokens=1_200_000, seed=0):
        self.model, self.tok = model, tok
        self.dev = next(model.parameters()).device
        self.max_action = max_action
        self.temp = temp
        self.row_tokens = row_tokens          # rows x (prompt + max_action) per decode chunk
        self.gen = torch.Generator(device=self.dev)
        self.gen.manual_seed(seed)
        self.gpu_s = 0.0
        self.gen_tokens = 0
        self.prompt_tokens = 0
        self.calls = 0
        self.rows = 0

    @torch.no_grad()
    def __call__(self, pids, K, want_feat=False):
        """pids: list of token-id lists (states).  -> (acts, feats): acts[i] = list of K (ids, logp, ended);
        feats[i] = the feature vector (ln_f of the last state token) or None."""
        out = [None] * len(pids)
        feats = [None] * len(pids)
        order = sorted(range(len(pids)), key=lambda i: len(pids[i]))
        j = 0
        while j < len(order):
            L = len(pids[order[j]])
            k = j
            while k < len(order) and (k - j + 1) * K * (len(pids[order[k]]) + self.max_action) <= self.row_tokens:
                k += 1
            k = max(k, j + 1)
            ch = order[j:k]
            a, f = self._chunk([pids[i] for i in ch], K, want_feat)
            for t, i in enumerate(ch):
                out[i] = a[t]
                feats[i] = None if f is None else f[t]
            j = k
        return out, feats

    def _chunk(self, pids, K, want_feat):
        m, tok, dev = self.model, self.tok, self.dev
        if dev.type == 'cuda':
            torch.cuda.synchronize()
        t0 = time.time()
        B = len(pids)
        L = max(len(p) for p in pids)
        idx = torch.full((B, L), tok.pad, dtype=torch.long, device=dev)
        keep = torch.zeros((B, L), dtype=torch.bool, device=dev)
        for i, p in enumerate(pids):
            idx[i, L - len(p):] = torch.tensor(p, device=dev)
            keep[i, L - len(p):] = True
        pos = (keep.cumsum(1) - 1).clamp(min=0)
        causal = torch.tril(torch.ones(L, L, dtype=torch.bool, device=dev))
        mask = causal[None, None] & keep[:, None, None, :]
        mask = mask | torch.eye(L, dtype=torch.bool, device=dev)[None, None]
        T = L + self.max_action
        caches = [{'max': T} for _ in m.blocks]
        with torch.autocast('cuda', dtype=torch.bfloat16, enabled=(dev.type == 'cuda')):
            x, _ = m.features(idx, pos=pos, mask=mask, caches=caches)
            h = m.ln_f(x[:, -1])
            logits = m.head(h).float()
            feat = None
            if want_feat:       # value-head input: ln_f of the last state token ++ ln_f of the mean over the state
                kf = keep[:, :, None].to(x.dtype)
                mean = (x * kf).sum(1) / kf.sum(1)
                feat = torch.cat([h, m.ln_f(mean)], -1).float()
        del x
        # fan out K ways
        R = B * K
        for c in caches:
            c['k'] = c['k'][:, :, :T].repeat_interleave(K, 0)
            c['v'] = c['v'][:, :, :T].repeat_interleave(K, 0)
        caches[0]['pos'] = caches[0]['pos'].repeat_interleave(K, 0)
        keepb = torch.zeros((R, T), dtype=torch.bool, device=dev)
        keepb[:, :L] = keep.repeat_interleave(K, 0)
        logits = logits.repeat_interleave(K, 0)
        cur = pos[:, -1].repeat_interleave(K, 0)
        outs = torch.full((R, self.max_action), tok.pad, dtype=torch.long, device=dev)
        logp = torch.zeros(R, device=dev)
        done = torch.zeros(R, dtype=torch.bool, device=dev)
        ntok = torch.zeros(R, dtype=torch.long, device=dev)
        for t in range(self.max_action):
            lp = F.log_softmax(logits, -1)
            if self.temp == 1.0:
                pr = lp.exp()
            else:
                pr = F.softmax(logits / self.temp, -1)
            nxt = torch.multinomial(pr, 1, generator=self.gen).squeeze(1)
            nxt = torch.where(done, torch.full_like(nxt, tok.pad), nxt)
            logp += torch.where(done, torch.zeros_like(logp), lp.gather(1, nxt[:, None]).squeeze(1))
            ntok += (~done).long()
            outs[:, t] = nxt
            done = done | (nxt == tok.eos)
            if bool(done.all()):
                break
            keepb[:, L + t] = True
            cur = cur + 1
            mk = keepb[:, None, None, :L + t + 1]
            with torch.autocast('cuda', dtype=torch.bfloat16, enabled=(dev.type == 'cuda')):
                x, _ = m.features(nxt[:, None], pos=cur[:, None], mask=mk, caches=caches)
                logits = m.head(m.ln_f(x[:, -1])).float()
        outs_c = outs.cpu().tolist()
        logp_c = logp.cpu().tolist()
        done_c = done.cpu().tolist()
        if dev.type == 'cuda':
            torch.cuda.synchronize()
        self.gpu_s += time.time() - t0
        self.gen_tokens += int(ntok.sum())
        self.prompt_tokens += sum(len(p) for p in pids)
        self.calls += 1
        self.rows += R
        res = []
        for b in range(B):
            res.append([(outs_c[b * K + r], logp_c[b * K + r], done_c[b * K + r]) for r in range(K)])
        return res, feat


# ------------------------------------------------------------------------------------------------------- the search
DEFAULT = dict(K=8, C=1.0, alpha=0.5, max_samples=64, c_init=1.25, c_base=19652, tau=1.0, gamma=0.95, fpu=0.0,
               leaves_per_tree=8, max_depth=96, max_expansions=400, temp=1.0, max_action=256)


def run_search(model, tok, prompts, cfg=None, value=None, seed=0, budget_s=None, log=None, lean=True,
               progress_every=60.0, sampler=None, bases=None):
    """Search every prompt's tree together until each is solved, dead, or out of expansions (or the wall budget is
    spent).  -> (per-tree result dicts, stats)."""
    c = dict(DEFAULT); c.update(cfg or {})
    rng = random.Random(seed)
    if bases is None:
        bases = [rng.randint(0, NAME_BASE_MAX) for _ in prompts]
    trees = [Tree(i, p, b, c) for i, (p, b) in enumerate(zip(prompts, bases))]
    S = sampler or Sampler(model, tok, max_action=c['max_action'], temp=c['temp'], seed=seed)
    st = collections.Counter()
    t0 = time.time()
    last = t0
    rounds = 0
    lean_s = 0.0
    while True:
        live = [t for t in trees if not t.solved and not t.dead and t.expansions < c['max_expansions']]
        if not live:
            break
        if budget_s is not None and time.time() - t0 >= budget_s:     # wall clock of the job = its GPU-seconds
            break
        leaves = []                              # (tree, node)
        for t in live:
            got = 0
            seen = set()
            for _ in range(c['leaves_per_tree'] * 2):
                if got >= c['leaves_per_tree'] or t.expansions + got >= c['max_expansions']:
                    break
                nd = t.select()
                if nd is None:
                    break
                if id(nd) in seen:               # the same leaf again: undo this descent's virtual loss
                    t.clear_vl(nd)
                    continue
                seen.add(id(nd))
                leaves.append((t, nd)); got += 1
            if got == 0 and not t.root.dead:
                st['stalled'] += 1
                t.dead = True
        if not leaves:
            break
        pids = [tok.encode_toks(nd.env.state_tokens()) for _, nd in leaves]
        want = value is not None
        acts, feats = S(pids, c['K'], want_feat=want)
        vals = [0.0] * len(leaves)
        if want:
            need = [i for i, (_, nd) in enumerate(leaves) if nd.v is None]
            if need:
                vv = value.value(torch.stack([feats[i] for i in need]))
                for i, x in zip(need, vv):
                    leaves[i][1].v = x
            vals = [nd.v for _, nd in leaves]
        finished = []
        for (t, nd), A, v in zip(leaves, acts, vals):
            t.expansions += 1
            t.sampled += len(A)
            nd.n_sampled += len(A)
            st['sampled'] += len(A)
            for ids, lp, ended in A:
                t.gen_tokens += len(ids)
                if not ended:
                    st['truncated'] += 1; continue
                atoks, ok_end = tok.decode_action(ids)
                key_a = ' '.join(atoks)
                if key_a in nd.acts:
                    st['dup_action'] += 1; continue
                e = clone(nd.env)
                ok, why = e.apply(atoks)
                if not ok:
                    nd.acts[key_a] = -1; st['env_reject'] += 1; st['why_env:' + why] += 1; continue
                r = step_reject(nd.env, e.hist[len(nd.env.hist):]) if not e.done else None
                if r is not None:
                    nd.acts[key_a] = -1; st['type_reject'] += 1; st['why_type:' + r] += 1; continue
                k = state_key(e)
                hit = None
                for ci, ch in enumerate(nd.children):
                    if ch.key == k:
                        hit = ci; break
                if hit is not None:                          # same resulting state: merge the prior mass
                    a, b = max(nd.logpi[hit], lp), min(nd.logpi[hit], lp)
                    nd.logpi[hit] = a + math.log1p(math.exp(b - a))
                    nd.acts[key_a] = hit; st['dup_state'] += 1; continue
                if k in t.nodes and not e.done:              # a transposition from elsewhere in the tree: drop
                    nd.acts[key_a] = -1; st['transposition'] += 1; continue
                ch = Node(e, nd, nd.depth + 1)
                ch.key = k
                nd.children.append(ch); nd.logpi.append(lp)
                nd.acts[key_a] = len(nd.children) - 1
                t.nodes[k] = ch
                st['children'] += 1
                if e.done:
                    finished.append((t, ch))
                elif ch.depth >= c['max_depth']:
                    ch.dead = True
            nd.expanded = True
            t.renorm(nd)
            if not nd.children and nd.n_sampled >= c['max_samples']:
                t.mark_dead(nd)
            t.backup(nd, v if not nd.dead else 0.0)
        # Lean decides the finished ones (batched over trees)
        if finished:
            tl = time.time()
            texts = [tok.text(ch.env.text) for _, ch in finished]
            nds = [ch.env.nd() for _, ch in finished]
            pr = [t.prompt for t, _ in finished]
            pre = [LP.reject_reason(tok.statement(p), x) for p, x in zip(pr, texts)]
            todo = [i for i, r in enumerate(pre) if r is None and not nds[i].startswith('LEANPARSE')]
            res = [None] * len(finished)
            if todo and lean:
                from lean_gate import gate
                g = gate(tok, [pr[i] for i in todo], [nds[i] for i in todo], [texts[i] for i in todo])
                for i, r in zip(todo, g):
                    res[i] = r
            elif todo:
                for i in todo:
                    res[i] = nds[i]
            lean_s += time.time() - tl
            for (t, ch), r in zip(finished, res):
                t.lean_checks += 1
                if r is not None and not r.startswith('LEAN'):
                    st['proof_ok'] += 1
                    if not t.solved:
                        t.solved = True
                        t.proof, t.proof_text, t.proof_node = r, tok.text(ch.env.text), ch
                        t.t_found = time.time() - t0
                        t.gpu_found = S.gpu_s
                    t.backup(ch, 1.0)
                else:
                    st['proof_rej'] += 1
                    t.lean_rej += 1
                    ch.dead = True
                    t.backup(ch, 0.0)
        rounds += 1
        if log and time.time() - last > progress_every:
            last = time.time()
            ns = sum(t.solved for t in trees)
            log(f'round {rounds} wall {last - t0:.0f}s gpu {S.gpu_s:.0f}s solved {ns}/{len(trees)} live {len(live)} '
                f'leaves {len(leaves)}')
    wall = time.time() - t0
    out = []
    for t in trees:
        hard = None
        if t.solved:
            hard = proof_path_stats(t)
        out.append(dict(i=t.idx, solved=t.solved, proof=t.proof, text=t.proof_text, t_found=t.t_found,
                        gpu_found=t.gpu_found, nodes=len(t.nodes), expansions=t.expansions, sampled=t.sampled,
                        gen_tokens=t.gen_tokens, lean_checks=t.lean_checks, lean_rej=t.lean_rej, dead=t.dead,
                        path=hard))
    stats = dict(st)
    stats.update(wall_s=wall, gpu_s=S.gpu_s, lean_s=lean_s, rounds=rounds, gen_tokens=S.gen_tokens,
                 prompt_tokens=S.prompt_tokens, sampler_calls=S.calls, sampler_rows=S.rows)
    return out, stats


def proof_path_stats(t):
    """along the found proof: per step the depth, the child's prior rank / prior, and its visit count -- where the
    hard (low-prior) steps sit."""
    path = []
    x = t.proof_node
    while x.parent is not None:
        p = x.parent
        i = p.children.index(x)
        rank = 1 + sum(1 for q in p.P if q > p.P[i])
        path.append(dict(depth=p.depth, logpi=round(p.logpi[i], 3), prior=round(p.P[i], 4), rank=rank,
                         n_children=len(p.children), N_parent=p.N, sampled=p.n_sampled))
        x = p
    return path[::-1]
