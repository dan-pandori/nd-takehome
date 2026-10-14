"""review_coep/harness_controls.py -- the Lean harness must be shown able to fail before its passes mean anything.

Positive: 1,000 Lean-accepted literal texts from the knockout s1 dump (own header) and their 1,000 ND strings through
the own renderer.  Negative: the same texts / proofs on a different theorem with the same premise count; a single
Or.inl<->Or.inr or .1<->.2 flip; truncation (last 40 % of tokens dropped); bare sorry; the renderer with one
ORI1<->ORI2 flip."""
import gzip, json, os, sys, random, time, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lean4

BIG = os.path.expanduser('~/review/coep_big')
rng = random.Random(11)
acc = [json.loads(l) for l in gzip.open(f'{BIG}/c5_accepted_sample.jsonl.gz', 'rt')][:1000]
npr = lambda p: len(lean4.sequent(p)[0])
by_np = collections.defaultdict(list)
for i, a in enumerate(acc):
    by_np[npr(a['prompt'])].append(i)

pos_lit = [(lean4.stmt(a['prompt']), a['text']) for a in acc]
pos_nd, nd_fail = [], 0
for a in acc:
    try:
        pos_nd.append((lean4.stmt(a['prompt']), lean4.nd_to_tactic(a['nd'], a['prompt'])))
    except Exception as e:
        nd_fail += 1
        pos_nd.append((lean4.stmt(a['prompt']), 'sorry'))


def other(i):
    """a different theorem (different sequent) with the same number of premises"""
    c = [j for j in by_np[npr(acc[i]['prompt'])] if lean4.sequent(acc[j]['prompt']) != lean4.sequent(acc[i]['prompt'])]
    return rng.choice(c) if c else None


neg_swap = []
for i, a in enumerate(acc):
    j = other(i)
    if j is not None:
        neg_swap.append((lean4.stmt(acc[j]['prompt']), a['text']))


def flip(text):
    toks = text.split(' ')
    idx = [k for k, t in enumerate(toks) if t in ('Or.inl', 'Or.inr') or t.endswith('.1') or t.endswith('.2')]
    if not idx:
        return None
    k = rng.choice(idx)
    t = toks[k]
    toks[k] = {'Or.inl': 'Or.inr', 'Or.inr': 'Or.inl'}.get(t, t[:-1] + ('2' if t.endswith('1') else '1'))
    return ' '.join(toks)


neg_flip = [(lean4.stmt(a['prompt']), f) for a in acc if (f := flip(a['text']))]
neg_trunc = [(lean4.stmt(a['prompt']), ' '.join(a['text'].split(' ')[:max(1, int(0.6 * len(a['text'].split(' '))))]))
             for a in acc[:300]]
neg_sorry = [(lean4.stmt(a['prompt']), 'sorry') for a in acc[:50]]


def ndflip(a):
    nd = a['nd']
    toks = nd.split()
    idx = [k for k, t in enumerate(toks) if t in ('ORI1', 'ORI2')]
    if not idx:
        return None
    k = rng.choice(idx)
    toks[k] = 'ORI2' if toks[k] == 'ORI1' else 'ORI1'
    try:
        return lean4.nd_to_tactic(' '.join(toks), a['prompt'])
    except Exception:
        return 'sorry'


neg_ndflip = [(lean4.stmt(a['prompt']), t) for a in acc if (t := ndflip(a))]

sets = dict(pos_literal=pos_lit, pos_rendered=pos_nd, neg_other_theorem=neg_swap, neg_flip=neg_flip,
            neg_truncated=neg_trunc, neg_sorry=neg_sorry, neg_rendered_ORI_flip=neg_ndflip)
out = {}
print('renderer exceptions on accepted ND strings:', nd_fail)
for name, items in sets.items():
    t0 = time.time()
    r = lean4.check(items)
    dt = time.time() - t0
    out[name] = dict(n=len(items), passed=sum(r), seconds=round(dt, 1))
    ex = [items[k][1][:160] for k in range(len(items)) if r[k] != name.startswith('pos')][:3]
    print(f'{name:24s} n {len(items):5d} passed {sum(r):5d}  ({dt:.0f} s, {len(items) / dt:.1f}/s)  odd examples: {ex}')
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out_harness_controls.json'), 'w'), indent=1)
