"""The GPU-resident Stage-1 training path (run fast-stage1, 2026-09-28): `train.py --impl fast`.

Same recipe as `train.py --impl legacy` -- same model init for a seed, same batch size, schedule, loss
(mean cross-entropy over the batch's proof tokens), optimiser hyper-parameters, clipping, and the same
name-augmentation DISTRIBUTION -- computed differently:

  * the training set is tokenised once and cached (`$ND_TRAIN_CACHE`, default ~/.cache/nd_train), then
    held on the GPU as one flat token array plus per-record start / length / prompt length / max name;
  * batches are drawn as in legacy (one shuffled permutation per epoch, `bs` records per step without
    replacement, the < bs remainder dropped), but from a CUDA generator, and gathered on the GPU;
  * the name augmentation is applied on the GPU: `lean_seq` / `abs` add one offset per record, uniform on
    {0 .. MAXN - mx}; `lean_rand` maps names through the first mx entries of a uniform random permutation
    (= random.sample(range(MAXN), mx)).  `fast_train_selftest.py` tests both against `tok.shift_abs`;
  * the batch's sequences are PACKED end to end into one stream of a fixed length (the longest batch of the
    whole run, rounded up to 256), with document-causal attention (flex_attention) and RoPE positions
    restarting at 0 in every record, so no pad token is computed except the stream's tail.  `--no_pack`
    instead right-pads to the longest record of the run (causal attention needs no mask then);
  * the loss function is `torch.compile`d; AdamW is the fused kernel; there is no host sync per step
    except at logging steps.
Validation (`--val_bins`, and the old 2,000-record `val`) runs on the same packed machinery over
pre-tokenised tensors, with the legacy fixed presentation (train.VAL_SHIFT_SEED).  The old `val` used the
training rng for its name shifts; here it is the token-weighted loss of the first 2,000 held-out records in
that fixed presentation (so it is not bit-comparable with a legacy log, and consumes no training rng).
RNG: model init uses torch.manual_seed(seed) exactly as legacy (same init for a seed); the epoch
permutations and the per-step augmentation draws come from CUDA generators seeded from (seed, epoch) and
(seed, step), so a --resume state is just (weights, optimiser, step).
"""
import hashlib, json, math, os, random, time
import torch, torch.nn.functional as F

CACHE = os.environ.get('ND_TRAIN_CACHE', os.path.expanduser('~/.cache/nd_train'))
BLOCK = 128                         # flex_attention block size; the stream length is a multiple of 2 * BLOCK


def aug_kind(tok):
    if not getattr(tok, 'shift', False):
        return 'none'
    m = tok.mode
    if m in ('abs', 'lean_seq'):
        return 'offset'
    if m == 'lean_rand':
        return 'perm'
    return 'none'                   # rel: shift_abs is the identity


def maxn(tok):
    if tok.mode.startswith('lean'):
        from lean_tok import MAXN
    else:
        from tokenizer import MAXN
    return MAXN


# ---------------------------------------------------------------- pre-tokenised data
def _cache_key(fn, tok, cap, head=None):
    st = os.stat(fn)
    h = hashlib.sha1(f'{os.path.abspath(fn)}|{st.st_size}|{st.st_mtime_ns}|{tok.mode}|{cap}|{head}|v1'.encode()).hexdigest()[:16]
    return os.path.join(CACHE, f'{os.path.basename(fn)}.{tok.mode}.cap{cap}.{h}.pt')


def pretokenise(fn, tok, cap, loader):
    """[(prompt_ids, proof_ids)] -> flat int16 tokens + int64 starts + int32 lens/plens; cached on disk.
    `loader` is train.load (so the legacy per-record checks run once, when the cache is built)."""
    path = _cache_key(fn, tok, cap)
    if os.path.exists(path):
        return torch.load(path), True
    recs = loader(fn, tok, cap, check_verify=(cap > 0))
    d = pack_records(recs)
    os.makedirs(CACHE, exist_ok=True)
    tmp = path + f'.tmp{os.getpid()}'
    torch.save(d, tmp); os.replace(tmp, path)
    return d, False


def pack_records(recs):
    lens = [len(p) + len(q) for p, q in recs]
    flat = [t for p, q in recs for t in p + q]
    starts = [0]
    for L in lens[:-1]:
        starts.append(starts[-1] + L)
    return {'toks': torch.tensor(flat, dtype=torch.int16), 'starts': torch.tensor(starts, dtype=torch.int64),
            'lens': torch.tensor(lens, dtype=torch.int32), 'plens': torch.tensor([len(p) for p, _ in recs], dtype=torch.int32)}


class GPUData:
    def __init__(self, d, tok, dev):
        self.toks = d['toks'].to(dev).long()
        self.starts = d['starts'].to(dev)
        self.lens = d['lens'].to(dev).long()
        self.plens = d['plens'].to(dev).long()
        self.lens_h = d['lens'].long()
        self.n = len(d['lens'])
        self.ref0 = tok.ref0
        # max name index in each record's proof (mx of shift_abs), computed once
        pos = torch.arange(len(self.toks), device=dev)
        rec = torch.repeat_interleave(torch.arange(self.n, device=dev), self.lens)
        isname = (self.toks >= self.ref0) & (pos - self.starts[rec] >= self.plens[rec])
        v = torch.where(isname, self.toks - self.ref0 + 1, torch.zeros_like(self.toks))
        self.mx = torch.zeros(self.n, dtype=torch.long, device=dev).scatter_reduce_(0, rec, v, 'amax')


# ---------------------------------------------------------------- augmentation (GPU)
def draw_u(kind, B, M, gen, dev):
    """The per-step random draws the augmentation consumes (drawn outside the CUDA graph, from `gen`)."""
    if kind == 'offset':
        return torch.rand(B, generator=gen, device=dev, dtype=torch.float64)
    if kind == 'perm':
        return torch.rand(B, M, generator=gen, device=dev)
    return None


def augment(tok_stream, is_name, doc, mx, kind, M, ref0, u):
    """tok_stream: (T,) token ids; is_name: (T,) bool, name tokens of the proof part; doc: (T,) record slot
    0..B-1 (pads: B); mx: (B,) max name index per record; u: draw_u()'s uniforms."""
    if kind == 'offset':
        s = torch.floor(u * (M - mx + 1).double()).long()          # uniform on {0 .. M - mx}
        s = torch.minimum(s, M - mx)                                  # guard u*k rounding to k
        s = torch.cat([s, s.new_zeros(1)])
        return torch.where(is_name, tok_stream + s[doc], tok_stream)
    if kind == 'perm':
        perm = torch.argsort(u, dim=1)                                # a uniform random permutation per record
        perm = torch.cat([perm, perm.new_zeros(1, M)])
        k = (tok_stream - ref0).clamp(0, M - 1)
        return torch.where(is_name, ref0 + perm[doc, k], tok_stream)
    return tok_stream


# ---------------------------------------------------------------- batch plans
def epoch_perm(n, seed, epoch, dev):
    g = torch.Generator(device=dev)
    g.manual_seed((seed * 1000003 + epoch * 7919 + 17) % (2 ** 63))
    return torch.randperm(n, generator=g, device=dev)


def plan(data, bs, steps, seed, dev):
    """All steps' record indices, (steps, bs) on the GPU, legacy semantics: epoch permutations, remainder dropped."""
    per = data.n // bs
    ne = (steps + per - 1) // per
    idx = torch.cat([epoch_perm(data.n, seed, e, dev)[:per * bs].view(per, bs) for e in range(ne)])[:steps]
    tot = data.lens[idx].sum(1)
    mxl = data.lens[idx].max(1).values
    return idx, tot.cpu(), mxl.cpu()


def round_up(x, m):
    return (int(x) + m - 1) // m * m


def gather_packed(data, idx, T, kind, M, gen=None, u=None):
    """Pack records idx (B,) into one stream of length T.  Returns x (1,T), pos (T,), doc (T,), lm (T,) loss mask
    for predicting x[t+1] from x[:t+1]."""
    dev = idx.device
    B = idx.shape[0]
    lens = data.lens[idx]
    cum = torch.cumsum(lens, 0)
    tot = cum[-1]
    t = torch.arange(T, device=dev)
    doc = torch.searchsorted(cum, t, right=True)                    # slot of each stream position; B past the end
    valid = doc < B
    docc = doc.clamp(max=B - 1)
    first = cum[docc] - lens[docc]
    pos = torch.where(valid, t - first, torch.zeros_like(t))
    src = data.starts[idx][docc] + pos
    x = torch.where(valid, data.toks[src], torch.zeros_like(t))
    plen = data.plens[idx][docc]
    isproof = valid & (pos >= plen)
    is_name = isproof & (x >= data.ref0)
    mx = data.mx[idx]
    if u is None and kind != 'none':
        u = draw_u(kind, B, M, gen, dev)
    x = augment(x, is_name, doc, mx, kind, M, data.ref0, u)
    lm = torch.zeros(T, dtype=torch.bool, device=dev)
    lm[:-1] = isproof[1:] & (doc[1:] == doc[:-1])
    return x.view(1, T), pos, doc, lm


def gather_padded(data, idx, T, kind, M, gen=None, u=None):
    """Right-pad records idx (B,) to (B,T).  Returns x (B,T), lm (B,T) loss mask for predicting x[:, t+1]."""
    dev = idx.device
    B = idx.shape[0]
    lens = data.lens[idx]
    t = torch.arange(T, device=dev)[None, :].expand(B, T)
    valid = t < lens[:, None]
    src = data.starts[idx][:, None] + t
    x = torch.where(valid, data.toks[src.clamp(max=len(data.toks) - 1)], torch.zeros_like(t))
    isproof = valid & (t >= data.plens[idx][:, None])
    is_name = isproof & (x >= data.ref0)
    doc = torch.arange(B, device=dev)[:, None].expand(B, T)
    if u is None and kind != 'none':
        u = draw_u(kind, B, M, gen, dev)
    x = augment(x.reshape(-1), is_name.reshape(-1), doc.reshape(-1), data.mx[idx], kind, M, data.ref0, u).view(B, T)
    lm = torch.zeros(B, T, dtype=torch.bool, device=dev)
    lm[:, :-1] = isproof[:, 1:]
    return x, lm


# ---------------------------------------------------------------- the model on a packed stream
def make_block_mask(doc, T):
    """Document-causal BlockMask built at block granularity from the (non-decreasing) slot ids, without
    evaluating the T x T mask: block pair (q, kv), kv <= q, is non-empty iff their slot ranges intersect
    and FULL iff both blocks lie inside one record and kv < q.  Partial blocks get the exact mask_mod."""
    from torch.nn.attention.flex_attention import BlockMask
    nb = T // BLOCK
    d = doc.view(nb, BLOCK)
    lo, hi = d[:, 0], d[:, -1]
    qi = torch.arange(nb, device=doc.device)
    causal = qi[:, None] >= qi[None, :]
    anyb = causal & (hi[None, :] >= lo[:, None])
    single = lo == hi
    full = anyb & (qi[:, None] > qi[None, :]) & single[:, None] & single[None, :] & (lo[:, None] == lo[None, :])
    part = anyb & ~full

    def enc(m):
        n = m.sum(1, dtype=torch.int32)
        ind = torch.argsort((~m).to(torch.int8), dim=1, stable=True).to(torch.int32)
        return n[None, None].contiguous(), ind[None, None].contiguous()

    def mm(b, h, q, kv):
        return (doc[q] == doc[kv]) & (q >= kv)
    kn, ki = enc(part)
    fn, fi = enc(full)
    return BlockMask.from_kv_blocks(kn, ki, fn, fi, BLOCK_SIZE=BLOCK, mask_mod=mm)


def packed_logits(model, x, pos, bm):
    from torch.nn.attention.flex_attention import flex_attention
    from model import rope_cache, apply_rope
    B, T = x.shape
    cos_all, sin_all = rope_cache(model.cfg['max_len'], model.hd, x.device)
    cos, sin = cos_all[pos], sin_all[pos]
    h = model.emb(x)
    for b in model.blocks:
        a = b.ln1(h)
        D = a.shape[-1]
        q, k, v = b.qkv(a).view(B, T, 3, b.h, D // b.h).permute(2, 0, 3, 1, 4)
        q, k = apply_rope(q, cos, sin).to(v.dtype), apply_rope(k, cos, sin).to(v.dtype)   # as SDPA does under autocast
        y = flex_attention(q, k, v, block_mask=bm)
        h = h + b.proj(y.transpose(1, 2).reshape(B, T, D))
        h = h + b.fc2(F.gelu(b.fc1(b.ln2(h))))
    return model.head(model.ln_f(h))


def tok_losses_packed(model, x, pos, bm):
    """(T,) cross-entropy of predicting x[t+1] at every t (the last position is garbage; mask it)."""
    logits = packed_logits(model, x, pos, bm)[0]
    tgt = torch.roll(x[0], -1)
    return F.cross_entropy(logits.float(), tgt, reduction='none')


def tok_losses_padded(model, x):
    logits = model(x)
    tgt = torch.roll(x, -1, dims=1)
    return F.cross_entropy(logits.reshape(-1, logits.size(-1)).float(), tgt.reshape(-1), reduction='none').view(x.shape)


# ---------------------------------------------------------------- validation on pre-tokenised tensors
class Val:
    """Per-record (loss sum, token count) over a held-out file in a fixed presentation, on the packed machinery."""

    def __init__(self, vdata, vidx, tok, dev, T, pack):
        self.d = GPUData(pack_records(vdata), tok, dev)
        self.vidx = vidx
        self.T, self.pack, self.dev = T, pack, dev
        # greedy chunks of consecutive records that fit in T
        lens = self.d.lens_h.tolist()
        self.chunks, cur, s = [], [], 0
        for i, L in enumerate(lens):
            if L > T:
                raise ValueError(f'held-out record {i} has {L} tokens > stream length {T}')
            if cur and (s + L > T or (not pack and len(cur) >= 256)):
                self.chunks.append(cur); cur, s = [], 0
            cur.append(i); s += L
        if cur:
            self.chunks.append(cur)
        self.chunks = [torch.tensor(c, device=dev) for c in self.chunks]
        self.slices = {k: torch.tensor(v, device=dev, dtype=torch.long) for k, v in (vidx or {}).items()}

        # the presentation is fixed, so every chunk's inputs (and block mask) are built once
        self.inp = []
        for ch in self.chunks:
            if pack:
                x, pos, doc, lm = gather_packed(self.d, ch, T, 'none', 0)
                self.inp.append((ch, x, pos, doc, make_block_mask(doc, T), lm.float()))
            else:
                x, lm = gather_padded(self.d, ch, T, 'none', 0)
                self.inp.append((ch, x, None, None, None, lm.float()))

    @torch.no_grad()
    def per_record(self, loss_fn):
        n = self.d.n
        ls = torch.zeros(n, device=self.dev); ns = torch.zeros(n, device=self.dev)
        for ch, x, pos, doc, bm, w in self.inp:
            l = loss_fn(x, pos, bm)
            if self.pack:
                slot = ch[doc.clamp(max=len(ch) - 1)]
                ls.index_add_(0, slot, l * w); ns.index_add_(0, slot, w)
            else:
                ls.index_add_(0, ch, (l * w).sum(1)); ns.index_add_(0, ch, w.sum(1))
        return ls, ns

    def bins(self, loss_fn, k=2000):
        """(per-slice token-weighted loss, loss of the first k records) from one pass."""
        ls, ns = self.per_record(loss_fn)
        names = list(self.slices)
        vals = torch.stack([ls[self.slices[n]].sum() / ns[self.slices[n]].sum().clamp(min=1) for n in names]
                           + [ls[:k].sum() / ns[:k].sum().clamp(min=1)]).tolist()
        return dict(zip(names, vals[:-1])), vals[-1]


# ---------------------------------------------------------------- the training loop
def run(a, model, tok, dev, loader, lr_at, load_val, save_ckpt, VAL_SHIFT_SEED, st=None):
    assert dev == 'cuda', '--impl fast needs a GPU'
    t_setup = time.time()
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    raw, cached = pretokenise(a.data, tok, a.cap, loader)
    data = GPUData(raw, tok, dev)
    kind, M = aug_kind(tok), maxn(tok)
    pack = not a.no_pack
    print('params', model.n_params(), 'mode', tok.mode, 'shift', tok.shift, 'aug', kind, 'impl fast', 'pack', pack,
          'cache', 'hit' if cached else 'built', flush=True)
    step0 = 0
    if st is not None:
        assert st.get('impl') == 'fast', 'resume a --impl fast state with --impl fast'
        step0 = st['step']
    idx_all, tot, mxl = plan(data, a.bs, a.steps, a.seed, dev)
    PADQ = 32
    T = round_up(tot.max(), 2 * BLOCK) if pack else round_up(mxl.max(), PADQ)
    Tb = [T] * a.steps if pack else [round_up(m, PADQ) for m in mxl.tolist()]   # --no_pack: each batch to its own max, in steps of 32
    useful = int(tot.sum())                                           # tokens the legacy path would call real
    computed = T * a.steps if pack else sum(Tb) * a.bs
    legacy_pad = int((mxl.long() * a.bs).sum())                       # what the legacy pad-to-batch-max computed
    print(f'train records {data.n}  stream T {T}  useful tokens {useful}  computed {computed} '
          f'(waste {computed / useful:.3f}x; legacy pad-to-max {legacy_pad / useful:.3f}x)', flush=True)

    # validation
    held = vd = None
    if a.heldout:
        vdata, vidx = load_val(a.heldout, tok)
        if not a.val_bins:
            vdata, vidx = vdata[:2000], None
        vd = Val(vdata, vidx, tok, dev, max(T, round_up(max(len(p) + len(q) for p, q in vdata), 2 * BLOCK)) if pack else
                 round_up(max(len(p) + len(q) for p, q in vdata), 8), pack)
        if vidx:
            print('val slices', {k: len(v) for k, v in vidx.items()}, flush=True)
    mf = open(a.metrics, 'a') if a.metrics else None
    if mf:
        mf.write(json.dumps({'kind': 'args', 'utc': time.strftime('%FT%TZ', time.gmtime()), 'args': vars(a),
                             'n_params': model.n_params(), 'val_slices': {k: len(v) for k, v in ((vd.vidx if vd else None) or {}).items()},
                             'val_shift_seed': VAL_SHIFT_SEED, 'impl': 'fast', 'pack': pack, 'T': T,
                             'useful_tokens': useful, 'computed_tokens': computed, 'legacy_computed_tokens': legacy_pad}) + '\n')
        mf.flush()

    from model import rope_cache
    rope_cache(model.cfg['max_len'], model.hd, next(model.parameters()).device)   # fill the memo (key 'cuda:0') before compiling, else a guard on it recompiles
    if pack:
        lossf = torch.compile(lambda x, pos, bm: tok_losses_packed(model, x, pos, bm), disable=a.no_compile, mode=os.environ.get('ND_COMPILE_MODE') or None)
        bmf = lambda doc, TT: make_block_mask(doc, TT)
        vloss = lambda x, pos, bm: lossf(x, pos, bm)
    else:
        lossf = torch.compile(lambda x: tok_losses_padded(model, x), disable=a.no_compile, mode=os.environ.get('ND_COMPILE_MODE') or None)
        vloss = lambda x, pos, bm: lossf(x)
    graph = pack and not a.no_graph and not a.no_compile
    params = list(model.parameters())
    opt = torch.optim.AdamW(params, lr=torch.tensor(a.lr, device=dev) if graph else a.lr, weight_decay=a.wd,
                            betas=(0.9, 0.95), fused=True, capturable=graph)
    gen = torch.Generator(device=dev)
    states = [int(x) for x in a.state_at.split(',') if x.strip()]
    val_s = 0.0
    first_step_s = None
    stem = a.out[:-3] if a.out.endswith('.pt') else a.out
    B = a.bs

    def draw(step):
        gen.manual_seed((a.seed * 1000003 + step * 104729 + 3) % (2 ** 63))
        return draw_u(kind, B, M, gen, dev)

    def body(idx, u, Tn):
        """One optimiser step on records idx.  Returns the (detached) batch loss."""
        with torch.autocast('cuda', dtype=torch.bfloat16):
            if pack:
                x, pos, doc, lm = gather_packed(data, idx, Tn, kind, M, u=u)
                l = lossf(x, pos, make_block_mask(doc, Tn))
            else:
                x, lm = gather_padded(data, idx, Tn, kind, M, u=u)
                l = lossf(x)
            lmf = lm.float()
            loss = (l * lmf).sum() / lmf.sum()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(params, 1.0, foreach=True)
        opt.step()
        opt.zero_grad(set_to_none=not graph)
        return loss.detach()

    t0 = time.time()
    if graph:
        # The whole step (gather, augmentation, block mask, forward, backward, clip, AdamW) is one CUDA graph,
        # replayed with fresh inputs copied into its static buffers.  Capturing needs warm-up steps, which
        # change the weights and the optimiser state: both are snapshotted before and copied back after, into
        # the same tensors, so step 1 starts from the untouched initial (or resumed) state.
        s_idx = idx_all[0].clone()
        s_u = draw(1)
        snap = [p.detach().clone() for p in params]
        for p in params:
            p.grad = torch.zeros_like(p)
        side = torch.cuda.Stream()
        side.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(side):
            for _ in range(3):
                body(s_idx, s_u, T)
        torch.cuda.current_stream().wait_stream(side)
        g = torch.cuda.CUDAGraph()
        with torch.cuda.graph(g):
            s_loss = body(s_idx, s_u, T)
        with torch.no_grad():
            for p, sp in zip(params, snap):
                p.copy_(sp)
                p.grad.zero_()
            for i, p in enumerate(params):
                stt = opt.state[p]
                if st is not None:
                    src = st['opt']['state'][i]
                    for k in ('exp_avg', 'exp_avg_sq', 'step'):
                        stt[k].copy_(src[k])
                else:
                    for k in ('exp_avg', 'exp_avg_sq', 'step'):
                        stt[k].zero_()
        del snap
        torch.cuda.synchronize()
        print(f'captured the training step as one CUDA graph ({time.time() - t0:.1f}s incl. compile)', flush=True)
    elif st is not None:
        opt.load_state_dict(st['opt'])
    if st is not None:
        print(f'resumed {a.resume} at step {step0}', flush=True)

    def save_state(step):
        fn = stem + f'.state{step:05d}.pt'
        save_ckpt(fn, model, tok.mode, extra={'args': vars(a), 'n_params': model.n_params(), 'secs': time.time() - t0,
                                              'sd_state': {'impl': 'fast', 'step': step, 'opt': opt.state_dict(),
                                                           'data': a.data, 'seed': a.seed, 'sched': a.sched,
                                                           'decay_frac': a.decay_frac, 'lr': a.lr, 'min_lr': a.min_lr,
                                                           'warmup': a.warmup, 'steps': a.steps, 'bs': a.bs}})
        print('saved state', fn, flush=True)

    torch.cuda.reset_peak_memory_stats()
    model.train()
    for step in range(step0 + 1, a.steps + 1):
        if graph:
            s_idx.copy_(idx_all[step - 1])
            if s_u is not None:
                s_u.copy_(draw(step))
            opt.param_groups[0]['lr'].fill_(lr_at(a, step))
            g.replay()
            loss = s_loss
        else:
            for pg in opt.param_groups:
                pg['lr'] = lr_at(a, step)
            loss = body(idx_all[step - 1], draw(step), T if pack else Tb[step - 1])
        if first_step_s is None:
            torch.cuda.synchronize(); first_step_s = time.time() - t0
            print(f'first step (incl. compile) {first_step_s:.1f}s', flush=True)
        if step % a.log_every == 0 or step == a.steps:
            lv = loss.item()
            el = time.time() - t0
            msg = f'step {step} loss {lv:.4f} lr {lr_at(a, step):.2e} {el:.0f}s'
            rec = {'kind': 'step', 'step': step, 'loss': lv, 'lr': lr_at(a, step), 'secs': el}
            if vd is not None:
                model.eval()
                tv = time.time()
                with torch.autocast('cuda', dtype=torch.bfloat16):
                    vb, rec['val2k'] = vd.bins(vloss)
                    msg += f" val {rec['val2k']:.4f}"
                    if vd.vidx:
                        rec['val'] = vb
                        msg += ' | ' + ' '.join(f'{k}={v:.4f}' for k, v in vb.items())
                torch.cuda.synchronize()
                val_s += time.time() - tv
                rec['val_full_s'] = val_s
                model.train()
            if mf:
                mf.write(json.dumps(rec) + '\n'); mf.flush()
            print(msg, flush=True)
        if step in states:
            save_state(step)
        if a.ckpt_every and step % a.ckpt_every == 0 and step != a.steps:
            save_ckpt(stem + f'.step{step:05d}.pt', model, tok.mode,
                      extra={'args': vars(a), 'n_params': model.n_params(), 'secs': time.time() - t0, 'step': step})
    torch.cuda.synchronize()
    secs = time.time() - t0
    peak = torch.cuda.max_memory_allocated()
    n_run = a.steps - step0
    train_s = secs - val_s
    frac = useful * (n_run / a.steps)
    extra = {'args': vars(a), 'n_params': model.n_params(), 'secs': secs, 'val_full_s': val_s, 'steps_run': n_run,
             'step': a.steps, 'impl': 'fast', 'pack': pack, 'T': T, 'first_step_s': first_step_s,
             'setup_s': t0 - t_setup, 'peak_mem': peak, 'useful_tokens': useful, 'computed_tokens': computed,
             'useful_tok_per_s_train': frac / max(train_s, 1e-9)}
    save_ckpt(a.out, model, tok.mode, extra=extra)
    if mf:
        mf.write(json.dumps({'kind': 'done', 'utc': time.strftime('%FT%TZ', time.gmtime()), 'out': a.out, 'secs': secs,
                             'val_full_s': val_s, 'steps_run': n_run, 'val_full_overhead': val_s / max(train_s, 1e-9),
                             **{k: v for k, v in extra.items() if k != 'args'}}) + '\n')
        mf.close()
    print(f'saved {a.out} ({secs:.1f}s total, {val_s:.1f}s validation, first step {first_step_s:.1f}s, setup '
          f'{t0 - t_setup:.1f}s, peak {peak / 2**30:.2f} GiB, {frac / max(train_s, 1e-9):.0f} useful tok/s in training)', flush=True)
