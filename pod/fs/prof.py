# Profile one fast-path training step's parts (run fast-stage1).  Prints ms per part and the top CUDA kernels.
import sys, os, time, torch
sys.path.insert(0, os.getcwd())
import fast_train as ft, train
from model import GPT, rope_cache
from tokenizer import make_tokenizer
torch.backends.cuda.matmul.allow_tf32 = True
dev = 'cuda'; tok = make_tokenizer('lean_seq'); torch.manual_seed(0)
model = GPT(tok.vocab_size, 4, 256, 8).to(dev)
raw, _ = ft.pretokenise('data/p2/train_depth3_f0_a1.jsonl', tok, 6, train.load)
d = ft.GPUData(raw, tok, dev); M = ft.maxn(tok)
idx_all, tot, mxl = ft.plan(d, 128, 400, 0, dev); T = ft.round_up(tot.max(), 256)
rope_cache(model.cfg['max_len'], model.hd, dev)
mode = sys.argv[1] if len(sys.argv) > 1 else 'default'
lossf = torch.compile(lambda x, pos, bm: ft.tok_losses_packed(model, x, pos, bm), mode=None if mode == 'default' else mode)
opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.1, betas=(0.9, 0.95), fused=True)
gen = torch.Generator(device=dev); gen.manual_seed(0)
def step(i, parts=None):
    e = [torch.cuda.Event(enable_timing=True) for _ in range(5)]
    e[0].record()
    with torch.autocast('cuda', dtype=torch.bfloat16):
        x, pos, doc, lm = ft.gather_packed(d, idx_all[i], T, 'offset', M, gen)
        bm = ft.make_block_mask(doc, T)
        e[1].record()
        l = lossf(x, pos, bm); lmf = lm.float(); loss = (l * lmf).sum() / lmf.sum()
    e[2].record()
    opt.zero_grad(set_to_none=True); loss.backward()
    e[3].record()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0, foreach=True); opt.step()
    e[4].record()
    if parts is not None:
        torch.cuda.synchronize(); parts.append([e[j].elapsed_time(e[j + 1]) for j in range(4)])
for i in range(20): step(i)
torch.cuda.synchronize(); t = time.time()
for i in range(20, 220): step(i)
torch.cuda.synchronize(); print(mode, 'ms/step (no per-step sync)', (time.time() - t) / 200 * 1000)
parts = []
for i in range(220, 260): step(i, parts)
import statistics as st
print('gather+mask / fwd / bwd / clip+opt (ms, synced):', [round(st.median(p[j] for p in parts), 2) for j in range(4)])
from torch.profiler import profile, ProfilerActivity
with profile(activities=[ProfilerActivity.CUDA, ProfilerActivity.CPU]) as prof:
    for i in range(260, 270): step(i)
    torch.cuda.synchronize()
print(prof.key_averages().table(sort_by='cuda_time_total', row_limit=18, max_name_column_width=60))
