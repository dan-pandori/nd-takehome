#!/usr/bin/env python3
"""Reviewer check of the RASP-L Kalmár policy (run kalmar-complexity).

  python3 rv_rasp.py metrics                 # own walk of the program graph: ops by kind, attention depth, flags
  python3 rv_rasp.py test --n 1000 --seed 271828     # every state of a fresh sample vs the builder's action
  python3 rv_rasp.py naive --n 40 --seed 161803      # own naive per-position evaluator (scalar fn, plain loops)
                                                     # vs the executor's numpy kernels on every state of n theorems

The program (kalmar_policy.build_decision) and its plain-Python content renderer are the artefacts under test; states
come from state_env.decompose(canonical) of kalmar.build(prompt, 'sl'), called here directly.
"""
import json, os, random, sys, time, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.expanduser('~/review/kalmar-complexity')
RD = os.path.join(WS, 'kalmar_complexity', 'programs', 'rasp')
sys.path.insert(0, WS); sys.path.insert(0, os.path.join(WS, 'kalmar')); sys.path.insert(0, RD)
sys.path.insert(0, os.path.join(WS, 'kalmar_complexity', 'programs', 'policy'))


def states_for(n, seed):
    import kalmar
    from state_env import decompose
    ps = [json.loads(l)['prompt'] for l in open(os.path.join(WS, 'data/kh/train_k12.jsonl'))]
    idx = sorted(random.Random(seed).sample(range(len(ps)), n))
    out = []
    for ti, i in enumerate(idx):
        p = ps[i]
        r = kalmar.build(p, 'sl')
        steps, toks, env = decompose(p, r['proof'], canon=True)
        assert len(steps) == len(r['tags'])
        for (st, act, _h), tag in zip(steps, r['tags']):
            out.append((ti, list(st), list(act), tag))
    return out


def graph(outs_list):
    seen, stack = {}, list(outs_list)
    while stack:
        n = stack.pop()
        if n.id in seen:
            continue
        seen[n.id] = n
        stack.extend(n.args)
    return [seen[i] for i in sorted(seen)]          # ids increase with creation = topological


def metrics():
    import kalmar_policy as KP
    outs, info = KP.build_decision(9)
    res = {}
    for name, roots in [('decision outputs', list(outs.values())),
                        ('decision outputs + span starts', list(outs.values()) + [info['start']])]:
        nodes = graph(roots)
        kinds = collections.Counter(n.kind for n in nodes)
        free = {'tokens', 'indices', 'const'}
        depth = {}
        for n in nodes:                       # attention layers on the longest path
            d = max((depth[a.id] for a in n.args), default=0)
            depth[n.id] = d + (1 if n.kind in ('aggregate', 'sel_width') else 0)
        flagged = [n for n in nodes if n.flags]
        fl = collections.Counter(f for n in flagged for f in n.flags)
        comp = sum(1 for n in nodes if n.vt == 'comp')
        multisel = sum(1 for n in nodes if n.kind == 'select' and len(n.args) > 2)
        fnpred = sum(1 for n in nodes if n.kind == 'select' and n.pred.kind == 'fn')
        res[name] = {'nodes': len(nodes), 'by_kind': dict(kinds),
                     'ops_excl_inputs_consts': sum(v for k, v in kinds.items() if k not in free),
                     'ops_excl_inputs_consts_selects': sum(v for k, v in kinds.items() if k not in free | {'select'}),
                     'attn_depth': max(depth[r.id] for r in roots),
                     'flagged_nodes': len(flagged), 'flags': dict(fl), 'composite_valued_nodes': comp,
                     'multi_field_selects': multisel, 'fn_predicate_selects': fnpred,
                     'aggregates_by_reduction': dict(collections.Counter(n.red for n in nodes if n.kind == 'aggregate'))}
    os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
    json.dump(res, open(os.path.join(HERE, 'out', 'rasp_metrics.json'), 'w'), indent=1)
    print(json.dumps(res, indent=1))


def test(n, seed):
    import rasp as R, kalmar_policy as KP
    t0 = time.time()
    states = states_for(n, seed)
    outs, info = KP.build_decision(9)
    names = list(outs)
    seqs = [KP.encode(s[1]) for s in states]
    res = R.run_program([outs[k] for k in names], seqs, batch=256, bucket=32)
    st_res = R.run_program([info['start']], seqs, batch=256, all_positions=True, bucket=32)[info['start']]
    ok = collections.Counter(); tot = collections.Counter(); bad_thm = set()
    for i, (ti, st, act, tag) in enumerate(states):
        c = {k: int(res[outs[k]][i]) for k in names}
        tot[tag] += 1
        try:
            got = KP.render_content(c, st, np.array(st_res[i]))
        except Exception as e:
            got = ['<err>']
        if got == act:
            ok[tag] += 1
        else:
            bad_thm.add(ti)
    out = {'n_theorems': n, 'seed': seed, 'n_states': len(states), 'exact': sum(ok.values()),
           'theorems_all_exact': n - len(bad_thm), 'per_tag': {t: [ok[t], tot[t]] for t in tot},
           'seconds': time.time() - t0}
    json.dump(out, open(os.path.join(HERE, 'out', f'rasp_test_s{seed}.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))


# ------------------------------------------------------------------ naive reference evaluator
def naive_eval(nodes, toks):
    """values at every position of every node, plain Python, scalar map functions, causal attention by loops."""
    N = len(toks)
    val = {}
    for n in nodes:
        k = n.kind
        if k == 'tokens':
            v = list(toks)
        elif k == 'indices':
            v = list(range(N))
        elif k == 'const':
            v = [n.fn] * N
        elif k == 'tok_map':
            x = val[n.args[0].id]
            f = n.fn if n.fn is not None else (lambda a, g=n.vfn: int(g(np.array([a]))[0]))
            v = [int(f(int(a))) for a in x]
        elif k == 'seq_map':
            x, y = val[n.args[0].id], val[n.args[1].id]
            f = n.fn if n.fn is not None else (lambda a, b, g=n.vfn: int(np.asarray(g(np.array([a]), np.array([b])))[0]))
            v = [int(f(int(a), int(b))) for a, b in zip(x, y)]
        elif k == 'select':
            continue
        elif k in ('aggregate', 'sel_width'):
            sel = n.args[0]
            nk = sel.fn
            K = [val[a.id] for a in sel.args[:nk]]
            Q = [val[a.id] for a in sel.args[nk:]]
            p = sel.pred
            Karr = [np.array(kk, dtype=np.int64) for kk in K]
            v = []
            for q in range(N):
                keys = range(q + 1)
                if p.kind == 'eq':
                    m = [all(K[f][j] == Q[f][q] for f in range(nk)) for j in keys]
                elif p.kind in ('lt', 'le', 'gt', 'ge'):
                    op = {'lt': lambda a, b: a < b, 'le': lambda a, b: a <= b, 'gt': lambda a, b: a > b,
                          'ge': lambda a, b: a >= b}[p.kind]
                    m = [op(K[0][j], Q[0][q]) for j in keys]
                elif p.kind == 'true':
                    m = [True for j in keys]
                elif p.kind == 'kflag':
                    mm = np.asarray(p.fn(*[ka[:q + 1] for ka in Karr]))
                    m = [bool(x) for x in np.broadcast_to(mm, (q + 1,))]
                elif p.kind == 'fn':
                    qs = [np.full(q + 1, Q[f][q], dtype=np.int64) for f in range(len(Q))]
                    mm = np.asarray(p.fn(*[ka[:q + 1] for ka in Karr], *qs))
                    m = [bool(x) for x in np.broadcast_to(mm, (q + 1,))]
                else:
                    raise ValueError(p.kind)
                sel_idx = [j for j in keys if m[j]]
                if k == 'sel_width':
                    v.append(len(sel_idx))
                    continue
                V = val[n.args[1].id]
                if not sel_idx:
                    v.append(int(n.default)); continue
                xs = [V[j] for j in sel_idx]
                if n.red == 'mean':
                    s = sum(xs); c = len(xs)
                    v.append(int(np.trunc(s / c)))
                elif n.red == 'max':
                    v.append(max(xs))
                elif n.red == 'min':
                    v.append(min(xs))
                elif n.red == 'and':
                    a = -1
                    for x in xs:
                        a &= x
                    v.append(a)
                else:
                    raise ValueError(n.red)
        else:
            raise ValueError(k)
        val[n.id] = v
    return val


def naive(n, seed):
    import rasp as R, kalmar_policy as KP
    t0 = time.time()
    states = states_for(n, seed)
    outs, info = KP.build_decision(9)
    names = list(outs)
    roots = [outs[k] for k in names] + [info['start']]
    nodes = graph(roots)
    seqs = [KP.encode(s[1]) for s in states]
    fast = R.run_program([outs[k] for k in names], seqs, batch=256, bucket=32)
    agree = 0; disagree = []; act_ok = 0
    for i, (ti, st, act, tag) in enumerate(states):
        vals = naive_eval(nodes, seqs[i])
        c = {k: int(vals[outs[k].id][-1]) for k in names}
        cf = {k: int(fast[outs[k]][i]) for k in names}
        if c == cf:
            agree += 1
        elif len(disagree) < 5:
            disagree.append({'i': i, 'tag': tag, 'naive': c, 'fast': cf})
        got = KP.render_content(c, st, np.array(vals[info['start'].id]))
        act_ok += got == act
    out = {'n_theorems': n, 'seed': seed, 'n_states': len(states), 'naive_eq_fast_content': agree,
           'naive_render_exact': act_ok, 'disagreements': disagree, 'seconds': time.time() - t0}
    json.dump(out, open(os.path.join(HERE, 'out', f'rasp_naive_s{seed}.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('what')
    ap.add_argument('--n', type=int, default=1000)
    ap.add_argument('--seed', type=int, default=271828)
    a = ap.parse_args()
    os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
    {'metrics': metrics, 'test': lambda: test(a.n, a.seed), 'naive': lambda: naive(a.n, a.seed)}[a.what]()
