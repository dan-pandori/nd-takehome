#!/usr/bin/env python3
"""The job graph of run stage1-dynamics, as sequential chains (one chain = one concurrent slot).

  python3 pod/sd/jobs.py chains            -> chain ids, one per line
  python3 pod/sd/jobs.py chain <id>        -> '<jobname>\t<command>' lines, to be run in order
  python3 pod/sd/jobs.py plan              -> the whole plan with step counts

Chain w<k> (k = 0..7, the control set): the 24,000-step WSD run with trajectory checkpoints every
1,000 steps and resumable states at the two decay branch points, then its two decay branches, then
the cosine 6,000-step control, then the Lean-alone held-out evaluations.
Chain f<k> (k = 0..3, the fresh 572,759-record set): the same 24,000-step WSD run and its trajectory.
"""
import sys

CTL = 'data/p2/train_depth3_f0_a1.jsonl'
FRESH = 'data/sd/train_fresh.jsonl'
HELD = 'data/p2/heldout.jsonl'
BASE = f'python3 train.py --heldout {HELD} --mode lean_seq --bs 128 --cap 6 --val_bins'
EV = f'python3 sd_eval.py --in {HELD} --outdir artifacts/sd/ev --batch 512'
WSEEDS = range(8)
FSEEDS = range(4)


def train(data, seed, steps, out, tag, sched='cosine', extra=''):
    return (f'{BASE} --data {data} --seed {seed} --steps {steps} --sched {sched} '
            f'--metrics artifacts/sd/m_{tag}.jsonl --out {out}{extra}').replace('  ', ' ')


def chain(cid):
    out = []
    if cid.startswith('w'):
        k = int(cid[1:])
        w = f'ckpts/sd/w_s{k}.pt'
        out.append((f'w_s{k}', train(CTL, k, 24000, w, f'w_s{k}', 'wsd',
                                     ' --decay_frac 0.2 --ckpt_every 1000 --state_at 4800,9600')))
        out.append((f'w6_s{k}', train(CTL, k, 6000, f'ckpts/sd/w6_s{k}.pt', f'w6_s{k}', 'wsd',
                                      f' --decay_frac 0.2 --resume ckpts/sd/w_s{k}.state04800.pt')))
        out.append((f'w12_s{k}', train(CTL, k, 12000, f'ckpts/sd/w12_s{k}.pt', f'w12_s{k}', 'wsd',
                                       f' --decay_frac 0.2 --resume ckpts/sd/w_s{k}.state09600.pt')))
        out.append((f'c_s{k}', train(CTL, k, 6000, f'ckpts/sd/c_s{k}.pt', f'c_s{k}', 'cosine')))
        out.append((f'ev_b_s{k}', f'{EV} --texts --skip_done --ckpts ckpts/sd/c_s{k}.pt '
                                  f'ckpts/sd/w6_s{k}.pt ckpts/sd/w12_s{k}.pt {w}'))
        out.append((f'ev_w_s{k}', f'{EV} --skip_done --ckpts ckpts/sd/w_s{k}.step*.pt '
                                  f'&& gzip -f artifacts/sd/ev/w_s{k}.step*.jsonl'))
    elif cid.startswith('f'):
        k = int(cid[1:])
        f = f'ckpts/sd/f_s{k}.pt'
        out.append((f'f_s{k}', train(FRESH, k, 24000, f, f'f_s{k}', 'wsd',
                                     ' --decay_frac 0.2 --ckpt_every 2000')))
        out.append((f'ev_ff_s{k}', f'{EV} --texts --skip_done --ckpts {f}'))
        out.append((f'ev_f_s{k}', f'{EV} --skip_done --ckpts ckpts/sd/f_s{k}.step*.pt '
                                  f'&& gzip -f artifacts/sd/ev/f_s{k}.step*.jsonl'))
    elif cid == 'smoke':
        # does --resume continue the run it branched from?  A 400-step wsd run with a state at 200,
        # and the same schedule resumed from that state: steps 300 and 400 must print the same loss.
        out.append(('smoke_a', train(CTL, 99, 400, 'ckpts/sd/smoke_a.pt', 'smoke_a', 'wsd',
                                     ' --decay_frac 0.2 --state_at 200 --log_every 100')))
        out.append(('smoke_b', train(CTL, 99, 400, 'ckpts/sd/smoke_b.pt', 'smoke_b', 'wsd',
                                     ' --decay_frac 0.2 --log_every 100 --resume ckpts/sd/smoke_a.state00200.pt')))
        out.append(('smoke_ev', f'{EV} --texts --ckpts ckpts/sd/smoke_a.pt'))
    else:
        raise SystemExit(f'unknown chain {cid}')
    return out


CHAINS = [f'w{k}' for k in WSEEDS] + [f'f{k}' for k in FSEEDS]

if __name__ == '__main__':
    what = sys.argv[1] if len(sys.argv) > 1 else 'chains'
    if what == 'chains':
        print('\n'.join(CHAINS))
    elif what == 'chain':
        for n, c in chain(sys.argv[2]):
            print(f'{n}\t{c}')
    elif what == 'plan':
        tot = 0
        for cid in CHAINS:
            js = chain(cid)
            st = sum(int(c.split('--steps ')[1].split()[0]) for _, c in js if '--steps' in c)
            # a resumed run only runs the tail
            if cid.startswith('w'):
                st = 24000 + 1200 + 2400 + 6000
            tot += st
            print(f'{cid}\t{len(js)} jobs\t{st} steps')
        print(f'TOTAL {tot} steps over {len(CHAINS)} chains')
