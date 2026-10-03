import json, sys, torch, mcts
from model import load_ckpt
from state_env import Env
m, tok, _ = load_ckpt(sys.argv[1], 'cuda')
lost = [json.loads(l) for l in open('data/mcts/debug_lost.jsonl')]
ps = [tok.encode_toks(Env(r['prompt'], canon=True, base=0, assign=True).state_tokens()) for r in lost]
print([len(p) for p in ps])
dec = lambda A: [' '.join(tok.decode_action(x[0])[0])[-60:] for x in A]
S = mcts.Sampler(m, tok, max_action=256, temp=1.0, seed=0)
a1, f1 = S([ps[1]], 4, want_feat=True)
S = mcts.Sampler(m, tok, max_action=256, temp=1.0, seed=0)
a3, f3 = S(ps, 4, want_feat=True)
print('alone  ', dec(a1[0]))
print('batched', dec(a3[1]))
print('feat diff', float((f1[0] - f3[1]).abs().max()))
