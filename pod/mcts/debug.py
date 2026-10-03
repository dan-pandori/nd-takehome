import json, sys, torch, mcts, collections
from model import load_ckpt
m, tok, _ = load_ckpt(sys.argv[1], 'cuda')
lost = [json.loads(l) for l in open('data/mcts/debug_lost.jsonl')]
n_other = int(sys.argv[2])
others = [json.loads(l)['prompt'] for l in open('data/mcts/tune200.jsonl')][:n_other]
P = [r['prompt'] for r in lost] + others
trees = []
orig = mcts.Tree
class T2(orig):
    def __init__(s, *a, **k):
        super().__init__(*a, **k); trees.append(s)
mcts.Tree = T2
cfg = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
cfg.setdefault('max_expansions', 300)
out, st = mcts.run_search(m, tok, P, cfg=cfg, lean=False, seed=1)
print('solved', [o['solved'] for o in out[:3]], sum(o['solved'] for o in out), len(out), st)
t = trees[1]
def show(nd, ind=0, maxd=12):
    if ind > maxd: return
    ch = sorted(zip(nd.children, nd.P), key=lambda x: -x[0].N)
    s = ' '.join(nd.env.hist[-10:]) if nd.parent else 'ROOT'
    print('  ' * ind + f'N={nd.N} vl={nd.vl} W={nd.W:.2f} ns={nd.n_sampled} ch={len(nd.children)} P={[round(p,2) for c,p in ch[:4]]} dead={nd.dead} exp={nd.expanded} | {s[-80:]}')
    for c, p in ch[:2]:
        show(c, ind + 1, maxd)
show(t.root)
print('ROOT prompt', t.prompt[:120])
print('ROOT state', ' '.join(t.root.env.state_tokens())[:200])
for k in list(t.root.acts)[:8]:
    c = mcts.clone(t.root.env); ok, why = c.apply(k.split())
    print(ok, why, k[:150])
