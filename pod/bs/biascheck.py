import torch, sys
sys.path.insert(0, '.')
from model import load_ckpt
m, tok, _ = load_ckpt('ckpts/bs/stage1_best6_s0_b1200.pt', 'cuda')
B, L = 64, 300
pos = torch.randint(0, 900, (B, 1)).cuda() + torch.arange(L).cuda()[None]
keep = torch.rand(B, L, device='cuda') > 0.1
mask = (torch.tril(torch.ones(L, L, dtype=torch.bool, device='cuda'))[None, None] & keep[:, None, None, :]) | torch.eye(L, dtype=torch.bool, device='cuda')[None, None]
rel = pos[:, None, :, None] - pos[:, None, None, :]
old = (-m.slopes * rel.to(m.slopes.dtype)).masked_fill(~mask, float('-inf')).to(torch.bfloat16)
idx = torch.randint(2, tok.vocab_size, (B, L)).cuda()
cap = {}
orig = m.blocks[0].forward
def hook(x, cos, sin, mask=None, cache=None):
    cap['b'] = mask; return orig(x, cos, sin, mask, cache)
m.blocks[0].forward = hook
with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
    m(idx, pos=pos, mask=mask)
new = cap['b']
print('dtype', new.dtype, 'identical', torch.equal(old, new), 'maxdiff', (old.float() - new.float()).nan_to_num(0, 0, 0).abs().max().item())
print('torch', torch.__version__)
