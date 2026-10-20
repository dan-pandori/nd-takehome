#!/usr/bin/env python3
"""B2: block-wise prequential code length (Blier & Ollivier 2018; Voita & Titov 2020) of three tasks under three sizes
of kalmar-pretrain's architecture (run kalmar-complexity).

  python3 kalmar_complexity/b2_preq.py --task kal|k12|eval --size S|M|L --max_thm 16384 --out artifacts/kc/b2/kal_L.json

Data, in K12's record order (data/kh/train_k12.jsonl; data/kalmar/train_kal_sl.jsonl.gz is the same theorems in the same
order), theorems [0, max_thm + 500):
  kal   the Kalmár (sl) proof's (state, action) pairs (`state_env.decompose`, canonical names = mode lean_staten), each
        with its step tag;
  k12   K12's own proof's pairs (the control's training data);
  eval  the theorem's goal formula under each of the 16 valuations of P Q R S: state `<st> h1 : <P or ¬P> <nl> … h4 :
        <S or ¬S> <nl> ⊢ goal <act>`, action `Or.inl` if the goal is true else `Or.inr` (one token + <eos>).
Loss tokens are the action tokens + <eos>, as in state_train.  Block boundaries b_k = 64 · 2^k ≤ max_thm.  Block
[0, 64) costs the uniform code (log2 V bits per loss token, V = 111).  For each k a fresh model is trained on theorems
[0, b_k) (10 % of those theorems held out for early stopping) and codes block [b_k, b_{k+1}); the last model also
codes 500 theorems after max_thm, giving the asymptotic per-token loss L_inf.  Absorbed bits (EDL) = prequential code
of [0, max_thm) − (loss tokens of [0, max_thm)) × L_inf.

Training: ALiBiGPT (best_model, as kalmar-pretrain), AdamW lr 1e-3 → 1e-4 cosine, warmup 100, wd 0.1, betas (0.9, 0.95),
grad clip 1, bf16 autocast, token-budget batches of 18,432 padded tokens with the trainer's random name shift; validation
every `eval_every` steps; the best validation checkpoint codes the next block; stop after 4 evaluations without
improvement or at max(min_steps, min(max_epochs, cap) steps).  Sizes: S 2 × 128 (4 heads, d_ff 512), M 4 × 256 (8, 1024),
L 6 × 384 (8, 1280) = KAL-D's network.
"""
import argparse, collections, gzip, json, math, os, pickle, random, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import torch, torch.nn.functional as F
import best_model as BM
from state_env import decompose
from tokenizer import make_tokenizer
from state_train_best import to_device, token_batches, make_batch

SIZES = {'S': (2, 128, 4, 512), 'M': (4, 256, 8, 1024), 'L': (6, 384, 8, 1280)}
ATOMS = ('P', 'Q', 'R', 'S')


def ev(f, v):
    t = f[0]
    if t == 'atom':
        return v[f[1]]
    if t == 'bot':
        return False
    if t == 'not':
        return not ev(f[1], v)
    a, b = ev(f[1], v), ev(f[2], v)
    return (a and b) if t == 'and' else (a or b) if t == 'or' else ((not a) or b)


def load_records(task, n):
    """-> list of per-theorem [(state toks, action toks, tag)]"""
    out = []
    if task == 'kal':
        fh = gzip.open(os.path.join(ROOT, 'data/kalmar/train_kal_sl.jsonl.gz'), 'rt')
    else:
        fh = open(os.path.join(ROOT, 'data/kh/train_k12.jsonl'))
    sys.path.insert(0, os.path.join(ROOT, 'kalmar_complexity/programs/policy'))
    from policy import parse_f, ftok
    for i, line in enumerate(fh):
        if i >= n:
            break
        r = json.loads(line)
        if task == 'eval':
            steps, toks, env = decompose(r['prompt'], r['proof'], canon=True)
            st0 = steps[0][0]
            g, _ = parse_f(st0, st0.index('⊢') + 1)
            recs = []
            for bits in range(16):
                v = {a: bool(bits >> j & 1) for j, a in enumerate(ATOMS)}
                st = ['<st>']
                for j, a in enumerate(ATOMS):
                    st += [f'h{j + 1}', ':'] + (ftok(('atom', a)) if v[a] else ftok(('not', ('atom', a)))) + ['<nl>']
                st += ['⊢'] + ftok(g) + ['<act>']
                recs.append((st, ['Or.inl' if ev(g, v) else 'Or.inr'], 'eval'))
            out.append(recs)
            continue
        steps, toks, env = decompose(r['prompt'], r['proof'], canon=True)
        tags = r.get('tags')
        if isinstance(tags, str):
            tags = json.loads(tags.replace("'", '"'))
        out.append([(st, act, tags[j] if tags else 'k12') for j, (st, act, hs) in enumerate(steps)])
    return out


def encode(recs, tok):
    return [[(bytes(tok.encode_toks(st)), bytes(tok.encode_toks(act) + [tok.eos])) for st, act, tg in rec] for rec in recs]


@torch.no_grad()
def code_pairs(model, data, tags, dev, bs_tokens=65536, return_pairs=False):
    """per-pair code length in nats (sum over loss tokens), no name shift.  -> (total nats, n loss tokens, per-tag)"""
    model.eval()
    ids, plen, lens_cpu, lens = to_device(data, dev)
    order = torch.argsort(lens_cpu)
    tot, ntok = 0.0, 0
    per = collections.defaultdict(lambda: [0.0, 0])
    i = 0
    N = len(lens_cpu)
    pp = [0.0] * N
    while i < N:
        j = i + 1
        while j < N and (j - i + 1) * int(lens_cpu[order[j]]) <= bs_tokens:
            j += 1
        idx = order[i:j].to(dev)
        T = int(lens_cpu[order[j - 1]])
        x = ids[idx, :T].long()
        ar = torch.arange(T, device=dev)[None]
        m = (ar >= plen[idx, None]) & (ar < lens[idx, None])
        with torch.autocast('cuda', dtype=torch.bfloat16, enabled=dev == 'cuda'):
            h, _ = model.features(x[:, :-1])
            logits = model.head(model.ln_f(h))
        ce = F.cross_entropy(logits.float().reshape(-1, logits.size(-1)), x[:, 1:].reshape(-1), reduction='none')
        ce = (ce.view(len(idx), T - 1) * m[:, 1:]).sum(1)
        k = m[:, 1:].sum(1)
        for a, b, c in zip(idx.tolist(), ce.tolist(), k.tolist()):
            pp[a] = b
            tot += b
            ntok += c
            p = per[tags[a]]
            p[0] += b
            p[1] += c
        i = j
    model.train()
    if return_pairs:
        return tot, ntok, {t: v for t, v in per.items()}, pp
    return tot, ntok, {t: v for t, v in per.items()}


def flat_tags(recs):
    return [tg for rec in recs for _, _, tg in rec]


def train_on(trd, vad, va_tags, a, tok, dev, seed):
    torch.manual_seed(seed)
    nl, d, nh, dff = SIZES[a.size]
    model = BM.ALiBiGPT(tok.vocab_size, nl, d, nh, d_ff=dff).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, betas=(0.9, 0.95), weight_decay=0.1,
                            fused=dev == 'cuda')
    ids, plen, lens_cpu, lens = to_device(trd, dev)
    gen_cpu = torch.Generator(); gen_cpu.manual_seed(seed)
    gen = torch.Generator(device=dev); gen.manual_seed(seed)
    rng = random.Random(seed)
    spe = len(token_batches(lens_cpu, torch.Generator().manual_seed(seed + 1), random.Random(seed + 1), a.tok_budget)[1])
    max_steps = max(a.min_steps, min(int(a.max_epochs * spe), a.cap))
    eval_every = max(50, min(spe, a.eval_every))
    best, best_state, bad, step, cuts, tr_tokens, best_step = float('inf'), None, 0, 0, [], 0, 0
    t0 = time.time()
    model.train()
    while step < max_steps:
        if not cuts:
            order, cuts = token_batches(lens_cpu, gen_cpu, rng, a.tok_budget)
        s, e, T, ntok = cuts.pop()
        step += 1
        frac = step / max_steps
        lr = a.lr * step / 100 if step < 100 else a.lr * (0.1 + 0.45 * (1 + math.cos(math.pi * frac)))
        for g in opt.param_groups:
            g['lr'] = lr
        idx = order[s:e].to(dev)
        x, m = make_batch(ids, plen, lens, idx, T, tok, gen)
        with torch.autocast('cuda', dtype=torch.bfloat16, enabled=dev == 'cuda'):
            loss = BM.mtp_loss(model, None, x, m, weight=0)[1]
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        tr_tokens += ntok
        if step % eval_every == 0 or step == max_steps:
            vl, vn, _ = code_pairs(model, vad, va_tags, dev)
            v = vl / max(1, vn)
            if v < best - 1e-5:
                best, bad, best_step = v, 0, step
                best_state = {k: t.detach().clone() for k, t in model.state_dict().items()}
            else:
                bad += 1
                if a.patience_steps:                  # v2: patience in steps, no early stop before es_min
                    if step >= a.es_min and step - best_step >= a.patience_steps:
                        break
                elif bad >= 4:
                    break
    model.load_state_dict(best_state)
    return model, {'steps': step, 'max_steps': max_steps, 'steps_per_epoch': spe, 'train_tokens': tr_tokens, 'best_step': best_step,
                   'best_val_nats_per_tok': best, 'secs': time.time() - t0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--task', required=True, choices=['kal', 'k12', 'eval'])
    ap.add_argument('--size', required=True, choices=list(SIZES))
    ap.add_argument('--max_thm', type=int, default=16384)
    ap.add_argument('--block0', type=int, default=64)
    ap.add_argument('--asym', type=int, default=500)
    ap.add_argument('--lr', type=float, default=1e-3)
    ap.add_argument('--tok_budget', type=int, default=18432)
    ap.add_argument('--max_epochs', type=float, default=30)
    ap.add_argument('--min_steps', type=int, default=300)
    ap.add_argument('--cap', type=int, default=20000)
    ap.add_argument('--eval_every', type=int, default=1000)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--out', required=True)
    ap.add_argument('--prep_only', action='store_true', help='build the data cache and exit')
    ap.add_argument('--patience_steps', type=int, default=0, help='v2: stop after this many steps without improvement')
    ap.add_argument('--es_min', type=int, default=0, help='v2: no early stop before this step')
    a = ap.parse_args()
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    tok = make_tokenizer('lean_staten')
    t0 = time.time()
    cache = os.path.join(ROOT, f'data/kc/b2_{a.task}_{a.max_thm + a.asym}.pkl')
    if os.path.exists(cache):
        recs = pickle.load(open(cache, 'rb'))
    else:
        recs = load_records(a.task, a.max_thm + a.asym)
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        pickle.dump(recs, open(cache + '.tmp', 'wb'))
        os.replace(cache + '.tmp', cache)
    print(f'{a.task}: {len(recs)} theorems, {sum(map(len, recs)):,} pairs, load {time.time() - t0:.0f}s', flush=True)
    if a.prep_only:
        return
    enc = encode(recs, tok)
    V = tok.vocab_size
    b = [a.block0]
    while b[-1] * 2 <= a.max_thm:
        b.append(b[-1] * 2)
    res = {'args': vars(a), 'vocab': V, 'boundaries': b, 'blocks': [], 'gpu': torch.cuda.get_device_name(0) if dev == 'cuda' else 'cpu'}
    n0 = sum(len(q) for rec in enc[:b[0]] for p, q in rec)
    per0 = collections.Counter()
    for rec in recs[:b[0]]:
        for st, act, tg in rec:
            per0[tg] += len(act) + 1
    res['blocks'].append({'block': [0, b[0]], 'coder': 'uniform', 'bits': n0 * math.log2(V), 'loss_tokens': n0,
                          'per_tag_bits': {t: c * math.log2(V) for t, c in per0.items()}, 'per_tag_tokens': dict(per0)})
    rng = random.Random(a.seed)
    for k, bk in enumerate(b):
        nxt = b[k + 1] if k + 1 < len(b) else a.max_thm + a.asym
        lo = bk
        th = list(range(bk))
        rng.shuffle(th)
        nva = max(1, bk // 10)
        va, tr = sorted(th[:nva]), sorted(th[nva:])
        trd = [enc[i] for i in tr]
        vad = [enc[i] for i in va]
        va_tags = flat_tags([recs[i] for i in va])
        model, info = train_on(trd, vad, va_tags, a, tok, dev, a.seed * 1000 + k)
        blk = enc[lo:nxt]
        tot, ntok, per = code_pairs(model, blk, flat_tags(recs[lo:nxt]), dev)
        row = {'block': [lo, nxt], 'coder': f'model trained on [0, {bk})', 'bits': tot / math.log(2), 'loss_tokens': ntok,
               'nats_per_token': tot / max(1, ntok), 'per_tag_bits': {t: v[0] / math.log(2) for t, v in per.items()},
               'per_tag_tokens': {t: v[1] for t, v in per.items()}, 'asymptote_block': nxt > a.max_thm, **info}
        res['blocks'].append(row)
        print(f"k {k} train [0,{bk}) {info['steps']} steps ({info['steps_per_epoch']}/ep) val {info['best_val_nats_per_tok']:.4f}"
              f" -> block [{lo},{nxt}) {row['nats_per_token']:.4f} nats/tok, {row['bits']:.4g} bits, {info['secs']:.0f}s", flush=True)
        del model
        torch.cuda.empty_cache() if dev == 'cuda' else None
        json.dump(res, open(a.out, 'w'), indent=1)
    pre = [r for r in res['blocks'] if not r.get('asymptote_block')]
    L = sum(r['bits'] for r in pre)
    N = sum(r['loss_tokens'] for r in pre)
    linf = res['blocks'][-1]['nats_per_token'] / math.log(2)
    res['summary'] = {'theorems': a.max_thm, 'prequential_bits': L, 'loss_tokens': N, 'L_inf_bits_per_token': linf,
                      'EDL_bits': L - N * linf, 'secs': time.time() - t0,
                      'peak_mem_gb': torch.cuda.max_memory_allocated() / 2 ** 30 if dev == 'cuda' else None}
    json.dump(res, open(a.out, 'w'), indent=1)
    print('SUMMARY', json.dumps(res['summary']), flush=True)


if __name__ == '__main__':
    main()
