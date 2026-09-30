#!/usr/bin/env python3
"""long-pool re-read: sample one checkpoint k times per theorem of a pool and judge with Lean (no training).
  python3 lpool_reread.py --ckpt ckpts/lp/la_T1_S_s0_r8.pt --in data/ladder/transfer_long.jsonl --k 256 --temperature 0.8 \
      --out artifacts/lpool/rr/T1_S_s0.jsonl --summary artifacts/lpool/rr/T1_S_s0.json --batch 4096 --max_new 512
Whole-proof (`lean_seq`) checkpoints go through `sample.generate` (fast path defaults), state-conditioned ones
(`lean_state*`) through `state_sample.env_generate` in the environment, exactly as `eval_set.py` / `state_eval.py` do;
judging is `eval_set.judge` (lean_judge: strict `lean_seq` grammar + Lean).  Rows keep every distinct accepted proof,
n_ok / n_tried and a failure-reason tally.  The summary adds the fraction of samples that hit `max_new` (whole-proof)
or the env's action / step caps, and the peak CUDA memory.
"""
import argparse, json, os, sys, time, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from model import load_ckpt
from eval_set import judge, summarize


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpt', required=True); ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True); ap.add_argument('--summary', required=True)
    ap.add_argument('--k', type=int, default=256); ap.add_argument('--temperature', type=float, default=0.8)
    ap.add_argument('--seed', type=int, default=0); ap.add_argument('--batch', type=int, default=4096)
    ap.add_argument('--max_new', type=int, default=512)
    ap.add_argument('--max_action', type=int, default=256); ap.add_argument('--max_steps', type=int, default=48)
    ap.add_argument('--lenfield', default='L_true')
    a = ap.parse_args()
    import record as ndrec; ndrec.save_config(vars(a), a.out)    # the resolved config next to the outputs
    recs = [json.loads(l) for l in open(a.inp) if l.strip()]
    model, tok, _ = load_ckpt(a.ckpt, 'cuda')
    torch.cuda.reset_peak_memory_stats()
    state = getattr(tok, 'state_mode', False)
    prompts = [r['prompt'] for r in recs for _ in range(a.k)]
    st = {}; t0 = time.time()
    if state:
        from state_sample import env_generate, env_stats_json
        flat = env_generate(model, tok, prompts, greedy=False, temperature=a.temperature, max_action=a.max_action,
                            max_steps=a.max_steps, batch=a.batch, seed=a.seed, stats=st)
    else:
        from sample import generate
        flat = generate(model, tok, prompts, greedy=False, temperature=a.temperature, max_new=a.max_new, batch=a.batch,
                        seed=a.seed, stats=st)
    gen_s = time.time() - t0
    per = [flat[i * a.k:(i + 1) * a.k] for i in range(len(recs))]
    rows = judge(recs, per, a.lenfield)
    summ = summarize(rows, a.lenfield, f'{os.path.basename(a.ckpt)} on {os.path.basename(a.inp)} k={a.k}')
    summ.update({'ckpt': a.ckpt, 'in': a.inp, 'k': a.k, 'temperature': a.temperature, 'seed': a.seed, 'batch': a.batch,
                 'state_mode': bool(state), 'tok_mode': getattr(tok, 'mode', None), 'gen_s': gen_s, 'wall_s': time.time() - t0,
                 'peak_mem_gb': torch.cuda.max_memory_allocated() / 2 ** 30, 'n_samples': len(prompts)})
    if state:
        summ['env'] = env_stats_json(st); summ['max_action'] = a.max_action; summ['max_steps'] = a.max_steps
    else:
        dl = st.get('declen', [])
        summ['max_new'] = a.max_new
        summ['trunc_frac'] = (sum(1 for d in dl if int(d) >= a.max_new) / len(dl)) if dl else None
        summ['declen_max'] = int(max(dl)) if dl else None
        summ['sample_stats'] = {k: v for k, v in st.items() if isinstance(v, (int, float))}
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    with open(a.out, 'w') as f:
        for r in rows:
            r['reasons'] = dict(collections.Counter(r['reasons']))
            f.write(json.dumps(r) + '\n')
    json.dump(summ, open(a.summary, 'w'), indent=1)
    print(json.dumps({k: v for k, v in summ.items() if k not in ('by_len', 'env')}))


if __name__ == '__main__':
    main()
