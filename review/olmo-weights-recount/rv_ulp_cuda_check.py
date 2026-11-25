import torch
def ulp_bf16(a):   # copied verbatim from olmo_weights/engine.py
    e = (a.view(torch.int16).to(torch.int32) >> 7) & 0xFF
    return torch.ldexp(torch.ones(e.shape, dtype=torch.float32, device=a.device), (e.clamp(min=1) - 134))
g = torch.Generator().manual_seed(0)
a = (torch.randn(50_000_000, generator=g) * 0.02).to(torch.bfloat16)
uc = ulp_bf16(a)
ug = ulp_bf16(a.cuda()).cpu()
print("engine ulp f32: cuda vs cpu differ", int((uc != ug).sum()), "of", a.numel())
e = ((a.view(torch.int16).to(torch.int32) >> 7) & 0xFF).clamp(min=1) - 134
exact = torch.tensor(2.0, dtype=torch.float64) ** e.double()
print("cpu vs exact", int((uc.double() != exact).sum()), "cuda vs exact", int((ug.double() != exact).sum()))
for n in (10, 1000, 100000, 10_000_000):
    x = a[:n].cuda()
    print(n, int((ulp_bf16(x).cpu() != uc[:n]).sum()))
