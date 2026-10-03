import json, sys, torch, mcts
from model import load_ckpt
from state_env import Env
m, tok, _ = load_ckpt(sys.argv[1], 'cuda')
lost = [json.loads(l) for l in open('data/mcts/debug_lost.jsonl')]
e = Env(lost[1]['prompt'], canon=True, base=0, assign=True)
p = tok.encode_toks(e.state_tokens())
dec = lambda A: [(' '.join(tok.decode_action(x[0])[0])[:70], round(x[1], 1), x[2]) for x in A]
for ma in (96, 256):
    S = mcts.Sampler(m, tok, max_action=ma, temp=1.0, seed=0)
    a, f = S([p], 6)
    print('max_action', ma, dec(a[0]))
torch.backends.cuda.enable_flash_sdp(False); torch.backends.cuda.enable_mem_efficient_sdp(False)
S = mcts.Sampler(m, tok, max_action=256, temp=1.0, seed=0)
a, f = S([p], 6)
print('math sdp 256', dec(a[0]))
