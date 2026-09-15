#!/usr/bin/env python3
"""Emit job lines for pod/runq.sh.  python phase2_jobs.py stage1|ei|frozen --sets TAG[,TAG..] --seeds 0,1 [--rounds 8]
TAG = <pattern>_f<freq> (a file data/p2/train_<TAG>.jsonl); pattern = TAG.rsplit('_f',1)[0]."""
import argparse, os
ap = argparse.ArgumentParser()
ap.add_argument('kind'); ap.add_argument('--sets', required=True); ap.add_argument('--seeds', default='0,1'); ap.add_argument('--rounds', type=int, default=8)
ap.add_argument('--batch', type=int, default=768); ap.add_argument('--k', type=int, default=32)
a = ap.parse_args()
for tag in a.sets.split(','):
    pat = tag.rsplit('_f', 1)[0]
    for s in a.seeds.split(','):
        if a.kind == 'stage1':
            print(f'stage1_{tag}_s{s} python3 train.py --data data/p2/train_{tag}.jsonl --heldout data/p2/heldout.jsonl --mode abs --steps 6000 --bs 128 --out ckpts/p2/stage1_{tag}_s{s}.pt --cap 6 --seed {s}')
        elif a.kind == 'ei':
            print(f'ei_{tag}_s{s} until [ -f ckpts/p2/stage1_{tag}_s{s}.pt ]; do sleep 30; done; python3 expert_iter.py --init ckpts/p2/stage1_{tag}_s{s}.pt --name p2/ei_{tag}_s{s} --targets data/p2/targets_{pat}.jsonl --transfer data/p2/transfer_{pat}.jsonl --heldout data/p2/heldout.jsonl --train data/p2/train_{tag}.jsonl --rounds {a.rounds} --k {a.k} --temperature 0.8 --seed {s} --batch {a.batch}')
        elif a.kind == 'cov':   # base-model pass@1e4 on the pattern targets (Phase-1 method), f=0 arms
            print(f'cov_{tag}_s{s} python3 coverage.py --ckpt ckpts/p2/stage1_{tag}_s{s}.pt --in data/p2/targets_{pat}.jsonl --k {a.k} --temperature 0.8 --out artifacts/p2/cov_{tag}_s{s}_targets --batch 4096 --seed {s}')
        elif a.kind == 'nov':   # base log-probs + surprisal loci of every proof the EI arm found (targets + transfer)
            print(f'nov_{tag}_s{s} python3 novelty.py --ckpts base=ckpts/p2/stage1_{tag}_s{s}.pt final=ckpts/p2/ei_{tag}_s{s}_r{a.rounds - 1}.pt --src ei_targets=artifacts/p2/ei_{tag}_s{s}/found_{a.rounds}.jsonl ei_transfer=artifacts/p2/ei_{tag}_s{s}/found_transfer_{a.rounds}.jsonl --out artifacts/p2/novelty_{tag}_s{s}')
        elif a.kind == 'frozen':
            print(f'frozen_{tag}_s{s} until [ -f ckpts/p2/stage1_{tag}_s{s}.pt ]; do sleep 30; done; python3 expert_iter.py --init ckpts/p2/stage1_{tag}_s{s}.pt --name p2/frozen_{tag}_s{s} --targets data/p2/targets_{pat}.jsonl --transfer data/p2/transfer_{pat}.jsonl --heldout data/p2/heldout.jsonl --train data/p2/train_{tag}.jsonl --rounds {a.rounds} --k {a.k} --temperature 0.8 --seed {s} --batch {a.batch} --no_train')
