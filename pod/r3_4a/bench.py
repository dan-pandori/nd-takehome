# decode-step timing for the three sizes (random weights; worst case = no EOS). usage: python3 pod/r3_4a/bench.py
import torch, time, sys
sys.path.insert(0, '.')
from model import GPT
from tokenizer import Tokenizer
from sample import generate_ids
tok = Tokenizer('abs')
for name, (L, d, h) in {'3.2M': (4, 256, 8), '25M': (8, 512, 8), '85M': (12, 768, 12)}.items():
    m = GPT(tok.vocab_size, L, d, h).cuda().eval()
    pid = tok.encode_prompt('THM ( ~ ( ( ~ P ) & Q ) ) , Q SEQ P PRF')
    for B in (1024, 2000, 4000):
        torch.cuda.synchronize(); t = time.time()
        with torch.autocast('cuda', dtype=torch.bfloat16):
            generate_ids(m, tok, [pid] * B, greedy=False, temperature=0.8, max_new=200, gen=None)
        torch.cuda.synchronize(); dt = time.time() - t
        print(name, m.n_params(), 'B', B, f'{dt:.1f}s per 200 steps, {B*200/dt:.0f} tok/s, mem {torch.cuda.max_memory_allocated()/2**30:.1f} GiB', flush=True)
    del m; torch.cuda.empty_cache()
