#!/usr/bin/env python3
"""B3: does removing the per-step search make the hard step types easy?  (run kalmar-complexity, pre-registration
addendum 2)

  python3 kalmar_complexity/b3_focus.py --arm STD|FOC --seed S [--size M] [--n_thm 8192] --out artifacts/kc/b3/<arm>_s<S>.json

FOC states = the standard (state_env, canonical) state with ['<nl>'] + the focus subformula inserted before '<act>' at
leaf-frame states whose target line is not yet in scope; the focus is the first needed node, in post-order, whose
literal is not in scope (programs/dtree/features.py `focus`, the decision tree's `fc` node).  Every other state, every
action and every proof is unchanged.  STD = the standard states.
Training: b2_preq.train_on (AdamW + early stopping, v1) on the Kalmár pairs of K12 theorems [0, n_thm), 10 % of them
held out for early stopping, seed-paired across arms.
Read-out on tf1200 (137,984 states; FOC-transformed for FOC): per state the code (nats) and exact = every action token
(+ <eos>) is the argmax given the correct prefix (= the greedy action is the algorithm's); per step type and per class
(opener = a state that gets a focus under FOC; other).
"""
import argparse, collections, json, os, pickle, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'kalmar_complexity'))
sys.path.insert(0, os.path.join(ROOT, 'kalmar_complexity/programs/policy'))
sys.path.insert(0, os.path.join(ROOT, 'kalmar_complexity/programs/dtree'))
import torch, torch.nn.functional as F
from state_env import decompose
from tokenizer import make_tokenizer
from state_train_best import to_device
import b2_preq as B2
from policy import Policy, val, ftok
from features import focus


def focus_of(st):
    """the focus formula tokens for a state, or None."""
    pol = Policy(st)
    pol.act()
    if not hasattr(pol, 'v') or len(pol.fr) != pol.leaf + 1:
        return None
    fp = next((i for i, p in enumerate(pol.prem) if not val(p, pol.v)), None)
    tgt = pol.prem[fp] if fp is not None else pol.goal
    fo = focus(pol, tgt)
    return ftok(fo) if fo is not None else None


def transform(st, arm):
    fo = focus_of(st)
    if arm == 'FOC' and fo is not None:
        return st[:-1] + ['<nl>'] + fo + ['<act>'], True
    return st, fo is not None


@torch.no_grad()
def read(model, enc, dev, bs_tokens=65536):
    """per pair: (code nats, loss tokens, exact)."""
    model.eval()
    ids, plen, lens_cpu, lens = to_device(enc, dev)
    order = torch.argsort(lens_cpu)
    N = len(lens_cpu)
    out = [None] * N
    i = 0
    while i < N:
        j = i + 1
        while j < N and (j - i + 1) * int(lens_cpu[order[j]]) <= bs_tokens:
            j += 1
        idx = order[i:j].to(dev)
        T = int(lens_cpu[order[j - 1]])
        x = ids[idx, :T].long()
        ar = torch.arange(T, device=dev)[None]
        m = (ar >= plen[idx, None]) & (ar < lens[idx, None])
        with torch.autocast('cuda', dtype=torch.bfloat16, enabled=dev == 'cuda'):
            h, _ = model.features(x[:, :-1])
            logits = model.head(model.ln_f(h)).float()
        tgt = x[:, 1:]
        mm = m[:, 1:]
        ce = F.cross_entropy(logits.reshape(-1, logits.size(-1)), tgt.reshape(-1), reduction='none').view(len(idx), T - 1)
        wrong = ((logits.argmax(-1) != tgt) & mm).sum(1)
        for a, c, k, w in zip(idx.tolist(), (ce * mm).sum(1).tolist(), mm.sum(1).tolist(), wrong.tolist()):
            out[a] = (c, k, w == 0)
        i = j
    model.train()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arm', required=True, choices=['STD', 'FOC'])
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--size', default='M', choices=list(B2.SIZES))
    ap.add_argument('--n_thm', type=int, default=8192)
    ap.add_argument('--lr', type=float, default=1e-3)
    ap.add_argument('--tok_budget', type=int, default=18432)
    ap.add_argument('--max_epochs', type=float, default=30)
    ap.add_argument('--min_steps', type=int, default=300)
    ap.add_argument('--cap', type=int, default=20000)
    ap.add_argument('--eval_every', type=int, default=1000)
    ap.add_argument('--patience_steps', type=int, default=0)
    ap.add_argument('--es_min', type=int, default=0)
    ap.add_argument('--tf_limit', type=int, default=0, help='smoke tests: read only the first N tf1200 records')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    tok = make_tokenizer('lean_staten')
    t0 = time.time()
    cache = os.path.join(ROOT, f'data/kc/b3_{a.arm}_{a.n_thm}.pkl')
    if os.path.exists(cache):
        recs = pickle.load(open(cache, 'rb'))
    else:
        base = B2.load_records('kal', a.n_thm)
        recs = [[(transform(st, a.arm)[0], act, tg) for st, act, tg in rec] for rec in base]
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        pickle.dump(recs, open(cache + '.tmp', 'wb'))
        os.replace(cache + '.tmp', cache)
    print(f'{a.arm}: {len(recs)} theorems, {sum(map(len, recs)):,} pairs, {time.time() - t0:.0f}s', flush=True)
    enc = B2.encode(recs, tok)
    import random
    th = list(range(len(recs)))
    random.Random(a.seed).shuffle(th)
    nva = max(1, len(th) // 10)
    va, tr = sorted(th[:nva]), sorted(th[nva:])
    model, info = B2.train_on([enc[i] for i in tr], [enc[i] for i in va], B2.flat_tags([recs[i] for i in va]), a, tok,
                              dev, a.seed * 1000 + 99)
    print('trained', json.dumps(info), flush=True)
    # tf1200 read-out
    rows, pairs = [], []
    for li, line in enumerate(open(os.path.join(ROOT, 'data/kalmar/tf1200_kal_sl.jsonl'))):
        if a.tf_limit and li >= a.tf_limit:
            break
        r = json.loads(line)
        kt = r['kal_tags']
        kt = json.loads(kt.replace("'", '"')) if isinstance(kt, str) else kt
        steps, toks, env = decompose(r['prompt'], r['proof'], canon=True)
        for (st, act, hs), tag in zip(steps, kt):
            st2, opener = transform(st, a.arm)
            pairs.append((bytes(tok.encode_toks(st2)), bytes(tok.encode_toks(act) + [tok.eos])))
            rows.append((tag, opener))
    res = read(model, [pairs], dev)
    agg = collections.defaultdict(lambda: [0, 0, 0.0, 0])        # key -> [states, exact, nats, tokens]
    for (tag, opener), (c, k, ex) in zip(rows, res):
        g = 'close' if tag.startswith('close:') else tag
        for key in (f'type:{g}', f'class:{"opener" if opener else "other"}', f'type_class:{g}|{"opener" if opener else "other"}', 'all'):
            v = agg[key]
            v[0] += 1; v[1] += ex; v[2] += c; v[3] += k
    out = {'args': vars(a), 'train': info, 'gpu': torch.cuda.get_device_name(0) if dev == 'cuda' else 'cpu',
           'secs': time.time() - t0,
           'read': {k: {'states': v[0], 'error': 1 - v[1] / v[0], 'bits_per_token': v[2] / v[3] / 0.6931471805599453}
                    for k, v in agg.items()},
           'per_state_exact': ''.join('1' if ex else '0' for _, _, ex in res)}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, 'w'))
    print('READ', json.dumps({k: round(v['error'], 4) for k, v in sorted(out['read'].items()) if not k.startswith('type_class')}), flush=True)


if __name__ == '__main__':
    main()
