#!/usr/bin/env python3
"""Per-state measures on tf1200 for Q4 (run kalmar-complexity).

  python3 kalmar_complexity/q4_states.py --out artifacts/kc/q4/states_tf1200.json.gz

For every state the algorithm visits on tf1200 (data/kalmar/tf1200_kal_sl.jsonl; `state_env.decompose`, canonical
names; the same 137,984 states, in the same order, as kalmar-pretrain's E1 verdict strings `artifacts/kalmar/tf/*`):
  tag        builder step tag (kalmar.TAGS, close:<t>, end)
  depth      open frames before the action
  act_len    tokens of the algorithm's action (lean_seq)
  decl_len   tokens of the formula the action declares (0 for `exact`)
  state_len  tokens of the state; n_hyp  hypotheses in scope
  ref_dist   largest distance, in hypotheses from the end of the state, of a hypothesis the action cites (0 if none)
  focus_h    height of the focus node (the subformula whose literal the step writes) at leaf-frame states, of the box's
             binder inside a lemma box, else 0 = how deep the truth-value computation behind the step's case goes
  target_h   height of the leaf target (goal, or the first false premise) at leaf states, else 0
  explored   nodes visited by the post-order focus search at leaf states (in-scope lookups), else 0
  ops        elementary operations of policy.py for this state (formula evaluations + in-scope lookups +
             lemma-recursion calls), for Levin's Kt = program bits + log2 ops
"""
import argparse, gzip, json, os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'kalmar_complexity/programs/policy'))
sys.path.insert(0, os.path.join(ROOT, 'kalmar_complexity/programs/dtree'))
from state_env import decompose
import policy as PO
from features import focus as focus_node, needed_children


def height(f):
    return 0 if f[0] in ('atom', 'bot') else 1 + max(height(g) for g in f[1:])


class Count:
    def __init__(self):
        self.n = 0


def instrumented_policy(st, C):
    """run policy.py on one state counting val / lookup / nxt calls (monkey-patched counters)."""
    ov, ol, on = PO.val, PO.Policy.lookup, PO.Policy.nxt

    def val(f, v):
        C.n += 1
        return ov(f, v)

    def lookup(self, f, skip=0):
        C.n += 1
        return ol(self, f, skip)

    def nxt(self, f):
        C.n += 1
        return on(self, f)
    PO.val, PO.Policy.lookup, PO.Policy.nxt = val, lookup, nxt
    try:
        pol = PO.Policy(st)
        act, tag = pol.act()
    finally:
        PO.val, PO.Policy.lookup, PO.Policy.nxt = ov, ol, on
    return pol, act, tag


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', default=os.path.join(ROOT, 'data/kalmar/tf1200_kal_sl.jsonl'))
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    t0 = time.time()
    rows = []
    for ri, line in enumerate(open(a.data)):
        r = json.loads(line)
        kt = r['kal_tags']
        kt = json.loads(kt.replace("'", '"')) if isinstance(kt, str) else kt
        steps, toks, env = decompose(r['prompt'], r['proof'], canon=True)
        for si, ((st, act, hs), tag) in enumerate(zip(steps, kt)):
            C = Count()
            pol, pact, ptag = instrumented_policy(st, C)
            assert pact == act and ptag == tag, (r['name'], si)
            names = [st[i] for i in range(1, len(st)) if st[i - 1] in ('<st>', '<nl>')]
            cited = [t for t in act[act.index(':=') + 1:]] if ':=' in act else act[1:]
            cited = [t for t in cited if t[:1] in 'nh' and t[1:].isdigit()]
            dist = [len(names) - names.index(c) for c in cited if c in names]
            decl = act[act.index(':') + 1:act.index(':=')] if act[0] == 'have' else []
            fh = th = ex = 0
            if hasattr(pol, 'v') and len(pol.fr) == pol.leaf + 1:
                v = pol.v
                fp = next((i for i, p in enumerate(pol.prem) if not PO.val(p, v)), None)
                tgt = pol.prem[fp] if fp is not None else pol.goal
                th = height(tgt)
                cnt = [0]

                def walk(f):
                    cnt[0] += 1
                    lit = f if PO.val(f, v) else PO.neg(f)
                    if pol.lookup(lit) is not None:
                        return None
                    for c in needed_children(f, v):
                        q = walk(c)
                        if q is not None:
                            return q
                    return f
                fo = walk(tgt)
                ex = cnt[0]
                fh = height(fo) if fo is not None else 0
            elif hasattr(pol, 'v'):                                   # inside a box opened at the leaf: its binder
                fh = height(pol.fr[-1].binder[1])
            rows.append({'rec': ri, 'name': r['name'], 'i': si, 'tag': tag, 'depth': len(pol.fr) - 1,
                         'act_len': len(act), 'decl_len': len(decl), 'state_len': len(st), 'n_hyp': len(names),
                         'ref_dist': max(dist) if dist else 0, 'focus_h': fh, 'target_h': th, 'explored': ex,
                         'ops': C.n, 'n_atoms': r.get('n_atoms')})
        if ri % 200 == 0:
            print(ri, len(rows), f'{time.time() - t0:.0f}s', flush=True)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with gzip.open(a.out, 'wt') as fh:
        json.dump(rows, fh)
    print('states', len(rows), f'{time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
