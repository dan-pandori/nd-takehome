"""lean-prefilter C1: sample a checkpoint over the ladder pools at several temperatures with the gate in shadow mode
(every parsed text goes to Lean; the pre-filter's verdict is logged beside Lean's).  Run with
LEAN_PREFILTER=shadow LEAN_GATE_DUMP=<dump> LEAN_GATE_LOG=<log>.  The dump is the soundness corpus."""
import argparse, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from model import load_ckpt
from sample import generate
import lean_gate

ap = argparse.ArgumentParser()
ap.add_argument('--ckpt', required=True); ap.add_argument('--name', required=True)
ap.add_argument('--pools', default='data/ladder/rl_targets.jsonl,data/ladder/transfer.jsonl,data/p2/heldout.jsonl')
ap.add_argument('--k', type=int, default=12); ap.add_argument('--temps', default='0.8,1.0,1.2')
ap.add_argument('--batch', type=int, default=4096); ap.add_argument('--max_new', type=int, default=512)
ap.add_argument('--seed', type=int, default=0); ap.add_argument('--outdir', default='artifacts/lp/corpus')
a = ap.parse_args()
import record as ndrec; ndrec.save_config(vars(a), a.outdir + '/')    # the resolved config next to the outputs
assert lean_gate.PREFILTER == 'shadow' and os.environ.get('LEAN_GATE_DUMP'), 'run with LEAN_PREFILTER=shadow and LEAN_GATE_DUMP'
os.makedirs(a.outdir, exist_ok=True)
model, tok, extra = load_ckpt(a.ckpt, 'cuda')
meta = {'ckpt': a.ckpt, 'params': sum(p.numel() for p in model.parameters()), 'tok_mode': tok.mode, 'args': vars(a), 'calls': []}
for pool in a.pools.split(','):
    prompts = sorted({json.loads(l)['prompt'] for l in open(pool)})
    for ti, T in enumerate(float(x) for x in a.temps.split(',')):
        st = {}
        t0 = time.time()
        torch.cuda.reset_peak_memory_stats()
        generate(model, tok, [p for p in prompts for _ in range(a.k)], greedy=False, temperature=T, batch=a.batch,
                 max_new=a.max_new, seed=a.seed * 1000 + ti * 100 + len(meta['calls']), stats=st)
        meta['calls'].append({'pool': pool, 'prompts': len(prompts), 'T': T, 'k': a.k, 'secs': time.time() - t0,
                              'sample_wall_s': st.get('sample_wall_s'), 'peak_alloc_gb': st.get('peak_alloc_gb')})
        print(json.dumps(meta['calls'][-1]), flush=True)
        json.dump(meta, open(f'{a.outdir}/{a.name}.meta.json', 'w'), indent=1)
open(f'{a.outdir}/{a.name}.done', 'w').close()
