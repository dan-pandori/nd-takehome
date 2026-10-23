"""Shared pieces of run `style-edl`: proof encoding, scoring (bits), fine-tuning (algorithm A) and the prequential code.

Scoring convention (pre-registered, `preregistration/style-edl.md`):
  - a proof is cut into the (state, action) pairs the learner was trained on (`state_env.decompose`, canonical names);
  - every n-name is shifted by one per-theorem base b(x) in [0, 32] (`thm_base`), the states the sampler shows
    (`state_sample.NAME_BASE_MAX`), the same base for every stream and every model;
  - the code length is the teacher-forced NLL of the action tokens + <eos> (`state_train.loss_on`'s positions), in
    bits, fp32.  **Primary: the names the environment assigns are not coded** (`kalmar/tf_agree.masked` positions:
    the `have` name and a box / Or.elim binder).  The environment overwrites them (`Env._assign_names`), so they carry
    no choice, and the first one is uniform over the trainer's random shift (memory note: name-shift first-state
    artifact).  Secondary: every action token coded (`all`).
Fine-tuning (algorithm A): from the learner's weights, AdamW (0.9, 0.95, wd 0), constant lr, clip 1, batches of
`recs` whole proofs (all their pairs), the Stage-1 trainer's random name shift per pair (`state_train_best.make_batch`);
A_ES (primary) = early stopping on a quarter of the prefix, then a refit (`finetune_es`); A_fixed = E passes (`finetune`);
loss on the coded tokens (default `loss_mask='names'`: the action tokens + <eos> without the environment-assigned
names, i.e. exactly the code length; 'all' = Stage-1's loss), MTP off, bf16 autocast on GPU.
"""
import hashlib, json, math, os, random, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'kalmar'))
import torch
import torch.nn.functional as F
from state_env import decompose
from lean_tok import MAXN
from tf_agree import masked, shift

NAME_BASE_MAX = 32
LN2 = math.log(2)


def thm_base(name):
    """per-theorem name base in [0, 32], fixed for the whole run (sha1 of the theorem name)."""
    return int(hashlib.sha1(f'style-edl:{name}'.encode()).hexdigest(), 16) % (NAME_BASE_MAX + 1)


def encode_proof(prompt, nd, tok, base):
    """-> list of (state ids, action ids + <eos>, env-assigned name positions within the action).  Raises ParseFail if
    the proof does not replay in the environment."""
    steps, toks, env = decompose(prompt, nd, canon=True)
    out = []
    for st, act, hs in steps:
        mk = masked(act)
        out.append((tok.encode_toks(shift(st, base)), tok.encode_toks(shift(act, base)) + [tok.eos],
                    [i for i, t in enumerate(mk) if t == '<def>']))
    return out


def canon_key(prompt, nd):
    """the canonical action sequence of a proof (names canonical, base 0): two proofs are the same iff keys match."""
    steps, toks, env = decompose(prompt, nd, canon=True)
    return ' '.join(toks)


def flat(enc_proofs, idxs=None):
    """-> list of (proof index, pair index, state ids, action ids, name positions) over the chosen proofs."""
    idxs = range(len(enc_proofs)) if idxs is None else idxs
    return [(i, j, s, a, nm) for i in idxs for j, (s, a, nm) in enumerate(enc_proofs[i])]


def _pack(rows, budget):
    """sort pair rows by length and cut into micro-batches of <= budget padded tokens -> list of lists of rows."""
    rows = sorted(rows, key=lambda r: len(r[2]) + len(r[3]))
    out, cur, T = [], [], 0
    for r in rows:
        L = len(r[2]) + len(r[3])
        if cur and max(T, L) * (len(cur) + 1) > budget:
            out.append(cur); cur, T = [], 0
        cur.append(r); T = max(T, L)
    if cur:
        out.append(cur)
    return out


def _tensors(rows, tok, dev):
    T = max(len(s) + len(a) for _, _, s, a, _ in rows)
    x = torch.full((len(rows), T), tok.pad, dtype=torch.long)
    m_all = torch.zeros((len(rows), T), dtype=torch.bool)
    m_nm = torch.zeros((len(rows), T), dtype=torch.bool)
    for k, (_, _, s, a, nm) in enumerate(rows):
        x[k, :len(s) + len(a)] = torch.tensor(s + a)
        m_all[k, len(s):len(s) + len(a)] = True
        m_nm[k, len(s):len(s) + len(a)] = True
        for p in nm:
            m_nm[k, len(s) + p] = False
    return x.to(dev), m_all.to(dev), m_nm.to(dev)


def logits_of(model, x):
    h, _ = model.features(x[:, :-1])
    return model.head(model.ln_f(h))


@torch.no_grad()
def score(model, enc_proofs, tok, dev, idxs=None, budget=65536, agree=False):
    """fp32 teacher-forced code lengths.  -> dict proof index -> {'bits': masked-name bits, 'bits_all': all action
    tokens, 'tok': coded tokens (masked), 'tok_all', 'acts': n actions, 'act_bits': [bits per action (masked)],
    'agree': [per action: every coded token is the argmax] (if agree)}"""
    was = model.training
    model.eval()
    res = {}
    idxs = list(range(len(enc_proofs))) if idxs is None else list(idxs)
    for i in idxs:
        n = len(enc_proofs[i])
        res[i] = {'bits': 0.0, 'bits_all': 0.0, 'tok': 0, 'tok_all': 0, 'acts': n, 'act_bits': [0.0] * n}
        if agree:
            res[i]['agree'] = [True] * n
    for rows in _pack(flat(enc_proofs, idxs), budget):
        x, m_all, m_nm = _tensors(rows, tok, dev)
        lg = logits_of(model, x).float()
        ce = F.cross_entropy(lg.reshape(-1, lg.size(-1)), x[:, 1:].reshape(-1), reduction='none').view(len(rows), -1)
        ma, mn = m_all[:, 1:], m_nm[:, 1:]
        b_all = (ce * ma).sum(1) / LN2
        b_nm = (ce * mn).sum(1) / LN2
        k_all, k_nm = ma.sum(1), mn.sum(1)
        if agree:
            hit = (lg.argmax(-1) == x[:, 1:]) | ~mn
            ok = hit.all(1)
        for r, (i, j, _, _, _) in enumerate(rows):
            d = res[i]
            d['bits'] += float(b_nm[r]); d['bits_all'] += float(b_all[r])
            d['tok'] += int(k_nm[r]); d['tok_all'] += int(k_all[r])
            d['act_bits'][j] = float(b_nm[r])
            if agree:
                d['agree'][j] = bool(ok[r])
    model.train(was)
    return res


def shift_names(x, tok, gen):
    """the Stage-1 trainer's augmentation (state_train_best.make_batch): one random offset per pair, s ~ U[0, MAXN - max
    name in the pair], applied to every n-name of state and action."""
    isref = x >= tok.ref0
    mx = torch.where(isref, x - tok.ref0 + 1, torch.zeros_like(x)).amax(1)
    room = MAXN - mx
    s = (torch.rand(len(x), device=x.device, generator=gen) * (room + 1)).long().clamp(max=room)
    return torch.where(isref, x + s[:, None], x)


def _step(model, opt, params, rows, tok, dev, gen, budget, loss_mask, use_amp):
    tot_tok = sum(len(a) - (len(nm) if loss_mask == 'names' else 0) for _, _, _, a, nm in rows)
    opt.zero_grad(set_to_none=True)
    for mb in _pack(rows, budget):
        x, m_all, m_nm = _tensors(mb, tok, dev)
        m = m_nm if loss_mask == 'names' else m_all
        x = shift_names(x, tok, gen)
        with torch.autocast('cuda', dtype=torch.bfloat16, enabled=use_amp):
            lg = logits_of(model, x)
        ce = F.cross_entropy(lg.float().reshape(-1, lg.size(-1)), x[:, 1:].reshape(-1), reduction='none')
        loss = (ce * m[:, 1:].reshape(-1)).sum() / tot_tok
        loss.backward()
    torch.nn.utils.clip_grad_norm_(params, 1.0)
    opt.step()
    return sum(len(s) + len(a) for _, _, s, a, _ in rows)


def _passes(model, opt, params, enc, idxs, passes, recs, rng, gen, tok, dev, budget, loss_mask, use_amp, after_pass=None):
    """`passes` passes over idxs; each pass a fresh shuffle cut into batches of <= recs proofs.  after_pass(p) -> True
    stops early.  -> (steps, train tokens, passes done)"""
    steps = ntr = 0
    for p in range(1, passes + 1):
        order = list(idxs); rng.shuffle(order)
        for k in range(0, len(order), recs):
            ntr += _step(model, opt, params, flat(enc, order[k:k + recs]), tok, dev, gen, budget, loss_mask, use_amp)
            steps += 1
        if after_pass is not None and after_pass(p):
            return steps, ntr, p
    return steps, ntr, passes


def _opt(model, lr):
    params = [q for q in model.parameters() if q.requires_grad]
    return params, torch.optim.AdamW(params, lr=lr, betas=(0.9, 0.95), weight_decay=0.0, eps=1e-8)


def _amp(dev):
    return dev == 'cuda' or (isinstance(dev, torch.device) and dev.type == 'cuda')


def finetune(model, init_state, enc_proofs, n, lr, epochs, tok, dev, seed, recs=8, budget=32768, loss_mask='names'):
    """A_fixed: `epochs` passes over proofs [0, n) (stream order) from init_state.  -> info dict.  n == 0: the learner."""
    model.load_state_dict(init_state)
    if n == 0 or epochs == 0:
        model.eval()
        return {'steps': 0, 'train_tokens': 0, 'passes': 0}
    model.train()
    params, opt = _opt(model, lr)
    rng = random.Random(seed)
    gen = torch.Generator(device=dev); gen.manual_seed(seed)
    steps, ntr, _ = _passes(model, opt, params, enc_proofs, range(n), int(epochs), recs, rng, gen, tok, dev, budget,
                            loss_mask, _amp(dev))
    model.eval()
    return {'steps': steps, 'train_tokens': ntr, 'passes': int(epochs)}


def finetune_es(model, init_state, enc_proofs, n, lr, tok, dev, seed, recs=8, max_passes=8, patience=2, budget=32768,
                loss_mask='names'):
    """A_ES (primary): early stopping, then refit.  Proofs [0, n) in stream order; validation = positions i % 4 == 3
    (a quarter, >= 2 proofs for n >= 8), training = the rest.  Train up to max_passes passes; after every pass code the
    validation proofs (bits, the scoring convention); stop when `patience` passes bring no improvement.  p* = the pass
    count with the lowest validation code (0 = the learner itself; ties -> fewer passes).  Then reset to init_state and
    train p* passes on all n proofs.  -> info dict (p*, validation curve, steps / tokens of both phases)."""
    model.load_state_dict(init_state)
    if n == 0:
        model.eval()
        return {'steps': 0, 'train_tokens': 0, 'passes': 0, 'es_steps': 0, 'es_tokens': 0, 'val_curve': []}
    va = [i for i in range(n) if i % 4 == 3]
    tr = [i for i in range(n) if i % 4 != 3]
    use_amp = _amp(dev)

    def vbits():
        sc = score(model, enc_proofs, tok, dev, idxs=va)
        return sum(sc[i]['bits'] for i in va)

    curve = [vbits()]
    best = [curve[0], 0]
    model.train()
    params, opt = _opt(model, lr)
    rng = random.Random(seed)
    gen = torch.Generator(device=dev); gen.manual_seed(seed)

    def after(p):
        v = vbits(); curve.append(v)
        model.train()
        if v < best[0]:
            best[0], best[1] = v, p
        return p - best[1] >= patience

    es_steps, es_tok, _ = _passes(model, opt, params, enc_proofs, tr, max_passes, recs, rng, gen, tok, dev, budget,
                                  loss_mask, use_amp, after_pass=after)
    pstar = best[1]
    info = finetune(model, init_state, enc_proofs, n, lr, pstar, tok, dev, seed + 7, recs=recs, budget=budget,
                    loss_mask=loss_mask)
    info.update(es_steps=es_steps, es_tokens=es_tok, val_curve=[round(v, 4) for v in curve], n_val=len(va))
    return info


def blocks_of(prefixes, n_all):
    """prefixes (0, 8, 16, 32, 64, 128) -> coding blocks [(0, 8), (8, 16), ..., (64, 128)]"""
    b = list(prefixes) + ([n_all] if prefixes[-1] < n_all else [])
    return [(b[k], b[k + 1]) for k in range(len(b) - 1)]
