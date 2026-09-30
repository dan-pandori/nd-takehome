#!/usr/bin/env python3
"""Supervised training / fine-tuning on (prompt, proof) records.

  python train.py --data data/train.jsonl --heldout data/heldout.jsonl --mode rel --steps 6000 --out ckpts/stage1_rel.pt --cap 6
  python train.py --data mix.jsonl --init ckpts/stage1.pt --steps 800 --lr 3e-4 --out ckpts/r1.pt --cap 0

--cap N  : assert every record's verifier length n_lines <= N (N=0 disables; Stage 1 must use 6).
Loss is next-token cross-entropy on proof tokens only (prompt tokens masked out).

Run `stage1-dynamics` (2026-09-27) added instrumentation and schedules.  Every addition is OFF by
default, and with the new flags unset this file trains exactly as it did before (same rng draws in
the same order, so a seed reproduces its old trajectory):

  --val_bins            at every --log_every step, also report validation loss on the WHOLE --heldout
                        file, per verifier-length bin and for the depth-3 slice (pat.depth3).  The old
                        number -- the first 2,000 records, i.e. lengths 2 and 3 only in the project's
                        length-sorted held-out files -- is still printed as `val` and is recorded as
                        `val2k`.  The per-bin pass uses its own fixed name-shift presentation
                        (Random(VAL_SHIFT_SEED)) and its own rng, so it consumes nothing from the
                        training rng and adds no dependence of the trajectory on how much we validate.
  --metrics FILE        append one json line per logged step with every number above plus timings.
  --sched cosine|wsd    cosine (default) is the old schedule.  wsd: linear warmup over --warmup, then
                        constant --lr, then linear decay to --min_lr over the last --decay_frac of
                        --steps.  A wsd run's pre-decay prefix does not depend on --steps, so one
                        stable run can be branched into decayed runs of several lengths.
  --ckpt_every N        save weights every N steps to <out>.step<step>.pt (trajectory checkpoints).
  --state_at a,b,...    at these steps save a full resumable state (weights + optimiser + rng + step)
                        to <out>.state<step>.pt -- the decay branch points.
  --resume CKPT         resume from such a state file: the continuation is the run the state came from.

Run `fast-stage1` (2026-09-28) added `--impl fast` (fast_train.py): the same recipe on GPU-resident,
packed, compiled batches, the whole step one CUDA graph -- see FAST_STAGE1.md for its speed and its
equivalence test.  The default `--impl auto` uses it for from-scratch training on a GPU (the tested case)
and the unchanged legacy code below for `--init` fine-tunes and legacy `--resume` states; `--impl legacy`
reproduces a pre-2026-09-28 trajectory for a seed.
"""
import argparse, json, math, os, random, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch, torch.nn.functional as F
from tokenizer import make_tokenizer
from model import GPT, save_ckpt, load_ckpt
from nd_verify import verify_text


def load(fn, tok, cap, check_verify=False):
    out = []
    for l in open(fn):
        if not l.strip():
            continue
        r = json.loads(l)
        if cap:
            assert r['n_lines'] <= cap, f'record exceeds cap {cap}: {r}'
            if check_verify:
                ok, reason, nl = verify_text(r['prompt'] + ' ' + r['proof'])
                assert ok and nl == r['n_lines'] and nl <= cap, (reason, nl, r)
        ids = tok.encode_proof(r['proof'])
        if cap and hasattr(tok, 'statement'):      # Lean surface form: the rendered record must denote exactly the cap-checked ND proof
            assert tok.decode(ids) == r['proof'], r
        out.append((tok.encode_prompt(r['prompt']), ids))
    return out


def batch(data, idxs, tok, rng, dev):
    seqs, masks = [], []
    for i in idxs:
        p, q = data[i]
        q = tok.shift_abs(q, rng)
        seqs.append(p + q)
        masks.append([0] * len(p) + [1] * len(q))
    T = max(len(s) for s in seqs)
    x = torch.full((len(seqs), T), tok.pad, dtype=torch.long)
    m = torch.zeros((len(seqs), T), dtype=torch.bool)
    for i, (s, mk) in enumerate(zip(seqs, masks)):
        x[i, :len(s)] = torch.tensor(s)
        m[i, :len(s)] = torch.tensor(mk, dtype=torch.bool)
    return x.to(dev), m.to(dev)


def loss_on(model, x, m):
    logits = model(x[:, :-1])
    tgt = x[:, 1:]
    mk = m[:, 1:]
    l = F.cross_entropy(logits.reshape(-1, logits.size(-1)).float(), tgt.reshape(-1), reduction='none')
    return (l * mk.reshape(-1)).sum() / mk.sum()


# ---------------------------------------------------------------- per-length validation (run stage1-dynamics)
VAL_SHIFT_SEED = 12345      # fixed for every run, so the per-bin curves of different seeds/arms are on the same presentation


def load_val(fn, tok):
    """The WHOLE held-out file, tokenised once with a fixed name-shift presentation, plus the index
    sets the per-bin loss is reported on.  Returns (data, idx) where data is [(prompt_ids, proof_ids)]
    and idx maps a slice name -> list of positions in data."""
    vrng = random.Random(VAL_SHIFT_SEED)
    data, lens, d3 = [], [], []
    for l in open(fn):
        if not l.strip():
            continue
        r = json.loads(l)
        data.append((tok.encode_prompt(r['prompt']), tok.shift_abs(tok.encode_proof(r['proof']), vrng)))
        lens.append(r.get('n_lines'))
        d3.append(bool((r.get('pat') or {}).get('depth3')))
    idx = {'all': list(range(len(data)))}
    for L in sorted({x for x in lens if x is not None}):
        idx[f'len{L}'] = [i for i, x in enumerate(lens) if x == L]
    if any(d3):
        idx['depth3'] = [i for i, x in enumerate(d3) if x]
        idx['nodepth3_len6'] = [i for i, (x, L) in enumerate(zip(d3, lens)) if not x and L == 6]
    return data, idx


def batch_pre(data, idxs, tok, dev):
    """batch() without the name-shift augmentation: the ids are already in their fixed presentation."""
    seqs = [data[i][0] + data[i][1] for i in idxs]
    masks = [[0] * len(data[i][0]) + [1] * len(data[i][1]) for i in idxs]
    T = max(len(s) for s in seqs)
    x = torch.full((len(seqs), T), tok.pad, dtype=torch.long)
    m = torch.zeros((len(seqs), T), dtype=torch.bool)
    for i, (s, mk) in enumerate(zip(seqs, masks)):
        x[i, :len(s)] = torch.tensor(s)
        m[i, :len(s)] = torch.tensor(mk, dtype=torch.bool)
    return x.to(dev), m.to(dev)


def loss_sums(model, x, m):
    """(summed proof-token cross-entropy, number of proof tokens) -- so bins can be pooled exactly."""
    logits = model(x[:, :-1])
    tgt = x[:, 1:]
    mk = m[:, 1:]
    l = F.cross_entropy(logits.reshape(-1, logits.size(-1)).float(), tgt.reshape(-1), reduction='none')
    return float((l * mk.reshape(-1)).sum()), int(mk.sum())


def val_bins(model, vdata, vidx, tok, dev, bs=256):
    """Token-weighted mean loss per slice.  One forward pass over the file; slices share it."""
    per = [None] * len(vdata)
    order = sorted(range(len(vdata)), key=lambda i: len(vdata[i][0]) + len(vdata[i][1]))
    with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16, enabled=(dev == 'cuda')):
        for s in range(0, len(order), bs):
            ch = order[s:s + bs]
            x, m = batch_pre(vdata, ch, tok, dev)
            logits = model(x[:, :-1])
            l = F.cross_entropy(logits.reshape(-1, logits.size(-1)).float(), x[:, 1:].reshape(-1), reduction='none')
            mk = m[:, 1:]
            l = (l.reshape(mk.shape) * mk)
            ls = l.sum(1).tolist(); ns = mk.sum(1).tolist()
            for j, i in enumerate(ch):
                per[i] = (ls[j], ns[j])
    out = {}
    for name, ii in vidx.items():
        sl = sum(per[i][0] for i in ii); nn = sum(per[i][1] for i in ii)
        out[name] = sl / max(nn, 1)
    return out


def lr_at(a, s):
    """The learning rate at step s (1-based) under --sched."""
    if s < a.warmup:
        return a.lr * s / a.warmup
    if a.sched == 'wsd':
        d0 = max(a.warmup, int(round(a.steps * (1.0 - a.decay_frac))))
        if s <= d0:
            return a.lr
        f = min(1.0, (s - d0) / max(1, a.steps - d0))
        return a.lr + (a.min_lr - a.lr) * f
    return a.min_lr + 0.5 * (a.lr - a.min_lr) * (1 + math.cos(math.pi * (s - a.warmup) / max(1, a.steps - a.warmup)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', required=True)
    ap.add_argument('--heldout', default=None)
    ap.add_argument('--mode', default='rel')
    ap.add_argument('--init', default=None)
    ap.add_argument('--steps', type=int, default=6000)
    ap.add_argument('--bs', type=int, default=128)
    ap.add_argument('--lr', type=float, default=1e-3)
    ap.add_argument('--min_lr', type=float, default=1e-4)
    ap.add_argument('--warmup', type=int, default=200)
    ap.add_argument('--wd', type=float, default=0.1)
    ap.add_argument('--n_layer', type=int, default=4)
    ap.add_argument('--d', type=int, default=256)
    ap.add_argument('--n_head', type=int, default=8)
    ap.add_argument('--cap', type=int, default=6)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--data_seed', type=int, default=None,
                    help='run lit-measures (2026-09-29): seed of the data order and the per-step name-shift draws; the model '
                         'init stays on --seed.  Default: --seed, so every existing command trains exactly as before')
    ap.add_argument('--out', required=True)
    ap.add_argument('--log_every', type=int, default=200)
    ap.add_argument('--no_shift', action='store_true', help='abs mode ablation: no random start-index offset (N1..N6 only ever seen)')
    # ---- run stage1-dynamics additions; every default below reproduces the pre-2026-09-27 behaviour
    ap.add_argument('--val_bins', action='store_true', help='also report validation loss on the WHOLE --heldout file, per length bin and on the depth-3 slice')
    ap.add_argument('--val_bs', type=int, default=256)
    ap.add_argument('--metrics', default=None, help='append one json line per logged step')
    ap.add_argument('--sched', default='cosine', choices=('cosine', 'wsd'))
    ap.add_argument('--decay_frac', type=float, default=0.2, help='--sched wsd: fraction of --steps spent decaying lr -> --min_lr')
    ap.add_argument('--ckpt_every', type=int, default=0, help='save weights every N steps to <out>.step<N>.pt')
    ap.add_argument('--state_at', default='', help='comma-separated steps at which to save a resumable state to <out>.state<N>.pt')
    ap.add_argument('--resume', default=None, help='resume from a <out>.state<N>.pt written by an earlier run')
    # ---- run fast-stage1 (2026-09-28): the GPU-resident path; see fast_train.py and FAST_STAGE1.md
    ap.add_argument('--impl', default='auto', choices=('auto', 'legacy', 'fast'),
                    help='legacy: the per-row Python batching below (reproduces old trajectories); fast: fast_train.py; '
                         'auto (default): fast for from-scratch training on a GPU -- the case run fast-stage1 tested -- '
                         'and legacy for --init fine-tunes, legacy --resume states and CPU')
    ap.add_argument('--no_pack', action='store_true', help='--impl fast: right-pad instead of packing (no flex_attention)')
    ap.add_argument('--no_compile', action='store_true', help='--impl fast: do not torch.compile')
    ap.add_argument('--no_graph', action='store_true', help='--impl fast: do not capture the step as a CUDA graph')
    a = ap.parse_args()
    if a.data_seed is None:
        a.data_seed = a.seed
    import record    # results registry (REGISTRY.md): config + final losses; save_ckpt uploads each checkpoint
    record.save_config(vars(a), a.out, role='finetune' if a.init else 'stage1')
    record.preflight()    # ND_RUN_ID + hf CLI present, or ND_OFFLINE=1: checked before training, not at the first save
    torch.manual_seed(a.seed)                 # model init
    rng = random.Random(a.data_seed)          # data order + name shifts (legacy path)
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    st = None
    if a.resume:
        model, tok, ex = load_ckpt(a.resume, dev)
        a.mode = tok.mode
        st = ex['sd_state']
        assert st['data'] == a.data, f"resume state trained on {st['data']}, --data is {a.data}"
        assert st['seed'] == a.seed, f"resume state used seed {st['seed']}, --seed is {a.seed}"
        assert st.get('data_seed', st['seed']) == a.data_seed, f"resume state used data_seed {st.get('data_seed', st['seed'])}"
    elif a.init:
        model, tok, _ = load_ckpt(a.init, dev)
        a.mode = tok.mode
    else:
        tok = make_tokenizer(a.mode)
        model = GPT(tok.vocab_size, a.n_layer, a.d, a.n_head).to(dev)
    tok.shift = not a.no_shift
    if a.impl == 'auto':
        a.impl = 'fast' if (dev == 'cuda' and not a.init and not (st is not None and st.get('impl') != 'fast')) else 'legacy'
    if a.impl == 'fast':
        import fast_train
        return fast_train.run(a, model, tok, dev, load, lr_at, load_val, save_ckpt, VAL_SHIFT_SEED, st=st)
    print('params', model.n_params(), 'mode', tok.mode, 'shift', tok.shift, flush=True)
    data = load(a.data, tok, a.cap, check_verify=(a.cap > 0))
    held = load(a.heldout, tok, 0)[:2000] if a.heldout else None
    vdata, vidx = (load_val(a.heldout, tok) if (a.heldout and a.val_bins) else (None, None))
    if vidx:
        print('val slices', {k: len(v) for k, v in vidx.items()}, flush=True)
    mf = open(a.metrics, 'a') if a.metrics else None
    if mf:
        mf.write(json.dumps({'kind': 'args', 'utc': time.strftime('%FT%TZ', time.gmtime()), 'args': vars(a),
                             'n_params': model.n_params(), 'val_slices': {k: len(v) for k, v in (vidx or {}).items()},
                             'val_shift_seed': VAL_SHIFT_SEED}) + '\n')
        mf.flush()
    print('train records', len(data), 'max len', max(len(p) + len(q) for p, q in data), flush=True)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=a.wd, betas=(0.9, 0.95))
    sched = lambda s: lr_at(a, s)
    model.train()
    t0 = time.time()
    perm = []
    step0 = 0
    states = [int(x) for x in a.state_at.split(',') if x.strip()]
    val_s = [0.0]
    if st is not None:
        opt.load_state_dict(st['opt'])
        rng.setstate(tuple(tuple(x) if isinstance(x, list) else x for x in st['rng']))
        # load_ckpt maps every tensor in the state onto `dev`; the rng states must go back as cpu uint8
        torch.set_rng_state(st['torch_rng'].detach().cpu().to(torch.uint8))
        if dev == 'cuda' and st.get('cuda_rng') is not None:
            torch.cuda.set_rng_state(st['cuda_rng'].detach().cpu().to(torch.uint8))
        perm = list(st['perm'])
        step0 = st['step']
        print(f'resumed {a.resume} at step {step0} (sched {a.sched} to {a.steps}); lr now {sched(step0 + 1):.3e}', flush=True)

    def save_state(step):
        fn = (a.out[:-3] if a.out.endswith('.pt') else a.out) + f'.state{step:05d}.pt'
        save_ckpt(fn, model, tok.mode, extra={'args': vars(a), 'n_params': model.n_params(), 'secs': time.time() - t0,
                                              'sd_state': {'step': step, 'opt': opt.state_dict(), 'perm': perm,
                                                           'rng': rng.getstate(), 'torch_rng': torch.get_rng_state(),
                                                           'cuda_rng': torch.cuda.get_rng_state() if dev == 'cuda' else None,
                                                           'data': a.data, 'seed': a.seed, 'data_seed': a.data_seed, 'sched': a.sched,
                                                           'decay_frac': a.decay_frac, 'lr': a.lr, 'min_lr': a.min_lr,
                                                           'warmup': a.warmup, 'steps': a.steps, 'bs': a.bs}})
        print('saved state', fn, flush=True)

    for step in range(step0 + 1, a.steps + 1):
        if len(perm) < a.bs:
            perm = list(range(len(data)))
            rng.shuffle(perm)
        idxs = [perm.pop() for _ in range(a.bs)]
        x, m = batch(data, idxs, tok, rng, dev)
        for g in opt.param_groups:
            g['lr'] = sched(step)
        with torch.autocast('cuda', dtype=torch.bfloat16, enabled=(dev == 'cuda')):
            loss = loss_on(model, x, m)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        if step % a.log_every == 0 or step == a.steps:
            msg = f'step {step} loss {loss.item():.4f} lr {sched(step):.2e} {time.time()-t0:.0f}s'
            rec = {'kind': 'step', 'step': step, 'loss': loss.item(), 'lr': sched(step), 'secs': time.time() - t0}
            vl = None
            if held:
                model.eval()
                with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16, enabled=(dev == 'cuda')):
                    vl = sum(loss_on(model, *batch(held, range(s, min(s + 256, len(held))), tok, rng, dev)).item() * min(256, len(held) - s)
                             for s in range(0, len(held), 256)) / len(held)
                msg += f' val {vl:.4f}'
                rec['val2k'] = vl
                model.train()
            if vdata is not None:
                model.eval()
                tv = time.time()
                vb = val_bins(model, vdata, vidx, tok, dev, bs=a.val_bs)
                val_s[0] += time.time() - tv
                model.train()
                rec['val'] = vb
                rec['val_full_s'] = val_s[0]
                msg += ' | ' + ' '.join(f'{k}={v:.4f}' for k, v in vb.items())
            if mf:
                mf.write(json.dumps(rec) + '\n'); mf.flush()
            print(msg, flush=True)
        # after the logging block, so a resumed run picks the rng stream up exactly where this one left it
        if step in states:
            save_state(step)
        if a.ckpt_every and step % a.ckpt_every == 0 and step != a.steps:
            fn = (a.out[:-3] if a.out.endswith('.pt') else a.out) + f'.step{step:05d}.pt'
            save_ckpt(fn, model, tok.mode, extra={'args': vars(a), 'n_params': model.n_params(), 'secs': time.time() - t0, 'step': step})
    secs = time.time() - t0
    extra = {'args': vars(a), 'n_params': model.n_params(), 'secs': secs, 'val_full_s': val_s[0],
             'steps_run': a.steps - step0, 'step': a.steps}
    save_ckpt(a.out, model, tok.mode, extra=extra)
    import record
    record.train_rows(a, locals().get('rec', {}), extra)
    if mf:
        mf.write(json.dumps({'kind': 'done', 'utc': time.strftime('%FT%TZ', time.gmtime()), 'out': a.out, 'secs': secs,
                             'val_full_s': val_s[0], 'steps_run': a.steps - step0,
                             'val_full_overhead': val_s[0] / max(secs - val_s[0], 1e-9)}) + '\n')
        mf.close()
    print(f'saved {a.out} ({secs:.0f}s total, {val_s[0]:.0f}s in the per-bin validation = '
          f'{100 * val_s[0] / max(secs - val_s[0], 1e-9):.1f}% overhead on {a.steps - step0} steps)', flush=True)


if __name__ == '__main__':
    main()
