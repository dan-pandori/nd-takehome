#!/usr/bin/env python3
"""rl-from-ckpt: the replay-only control for one start checkpoint.

The T1 ladder (`state_ladder_ei.py`) fine-tunes every round, once any target proof has been accepted, on its found
proofs (x rl_weight) **plus `--retain` 20,000 random K12 Stage-1 records** (600 steps x 128 proofs, lr 3e-4 -> 3e-5,
warmup 50).  From an early pretraining checkpoint that replay is itself more pretraining.  This control runs the same
8 fine-tunes with the same flags and the same per-round seeds, on the replay records alone (no sampling, no RL
records), so the ladder's solves can be compared with what its replay alone produces from the same start.

Each round's mix is 20,000 records drawn as the driver draws them (`random.Random(seed * 7919)`; the driver's rng has
also shuffled found proofs by then, so the draws are the same distribution, not the same records).  The control sees
the replay records more often than any ladder does (the ladder's mix is replay + RL records over the same 600 steps),
so it over-states the replay effect -- conservative for any "RL created it" reading.

  python3 rfc_replay.py --init <ckpt> --name rc_best12_s0_p1600 --seed 0 --train data/kh/train_k12.jsonl \
      --outdir artifacts/rfc --ckptdir ckpts/rfc/control
"""
import argparse, json, os, random, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import record


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--init', required=True)
    ap.add_argument('--name', required=True)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--train', required=True)
    ap.add_argument('--outdir', default='artifacts/rfc')
    ap.add_argument('--ckptdir', default='ckpts/rfc/control')
    ap.add_argument('--rounds', type=int, default=8)
    ap.add_argument('--ft_steps', type=int, default=600)
    ap.add_argument('--ft_lr', type=float, default=3e-4)
    ap.add_argument('--ft_recs', type=int, default=128)
    ap.add_argument('--retain', type=int, default=20000)
    ap.add_argument('--start_round', type=int, default=1)
    a = ap.parse_args()
    out = f'{a.outdir}/{a.name}'
    os.makedirs(out, exist_ok=True); os.makedirs(a.ckptdir, exist_ok=True)
    record.save_config(vars(a), out, arm=a.name)
    record.preflight()
    train_recs = [json.loads(l) for l in open(a.train) if l.strip()]
    rng = random.Random(a.seed * 7919)
    ckpt = a.init if a.start_round == 1 else f'{a.ckptdir}/{a.name}_r{a.start_round - 1}.pt'
    for r in range(1, a.rounds + 1):
        recs = rng.sample(train_recs, min(a.retain, len(train_recs)))    # drawn every round so a resume draws the same
        if r < a.start_round:
            continue
        t0 = time.time(); seed = a.seed * 1000 + r
        mix = f'{out}/mix_{r}.jsonl'
        with open(mix, 'w') as f:
            for x in recs:
                f.write(json.dumps({'prompt': x['prompt'], 'proof': x['proof'], 'n_lines': x['n_lines']}) + '\n')
        new_ckpt = f'{a.ckptdir}/{a.name}_r{r}.pt'
        cmd = ['python3', 'state_train.py', '--data', mix, '--init', ckpt, '--steps', str(a.ft_steps), '--lr', str(a.ft_lr),
               '--min_lr', str(a.ft_lr / 10), '--warmup', '50', '--cap', '0', '--out', new_ckpt, '--seed', str(seed),
               '--log_every', '200', '--recs', str(a.ft_recs)]
        print(' '.join(cmd), flush=True)
        with record.child('finetune', round=r):
            subprocess.run(cmd, check=True)
        ckpt = new_ckpt
        os.remove(mix)    # 20k K12 records; reproducible from the seed
        json.dump({'round': r, 'ckpt': new_ckpt, 'mix_replay_records': len(recs), 'secs': time.time() - t0},
                  open(f'{out}/round_{r}.json', 'w'), indent=1)
        print(f'=== control round {r} done in {time.time() - t0:.0f}s', flush=True)


if __name__ == '__main__':
    main()
