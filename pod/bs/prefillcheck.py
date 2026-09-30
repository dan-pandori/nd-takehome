# chunked prefill == one-shot prefill (greedy tokens; logits max diff) on a real best checkpoint, and its peak memory
import sys, time, json, torch
sys.path.insert(0, '.')
from model import load_ckpt
import best_model as BM
from sample import generate_ids_fast
from state_env import Env
from state_sample import prompt_ids
m, tok, _ = load_ckpt(sys.argv[1], 'cuda')
recs = [json.loads(l) for l in open('data/ladder/rl_targets.jsonl')][:256]
P = [prompt_ids(tok, Env(r['prompt'], canon=True, base=0, assign=True)) for r in recs]
def run(elems):
    BM.ALiBiGPT.PREFILL_ELEMS = elems
    torch.cuda.reset_peak_memory_stats()
    with torch.autocast('cuda', dtype=torch.bfloat16, enabled=len(sys.argv) < 3):
        o = generate_ids_fast(m, tok, P, greedy=True, max_new=64, early='eos')
    return o, torch.cuda.max_memory_allocated() / 2 ** 30
a, ma = run(2 ** 40); b, mb = run(2 ** 16)
print('rows differing', sum(x != y for x, y in zip(a, b)), 'of', len(a), 'peak GB one-shot', round(ma, 2), 'chunked', round(mb, 2))
