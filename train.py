#!/usr/bin/env python3
"""Supervised training / fine-tuning on (prompt, proof) records.

  python train.py --data data/train.jsonl --heldout data/heldout.jsonl --mode rel --steps 6000 --out ckpts/stage1_rel.pt --cap 6
  python train.py --data mix.jsonl --init ckpts/stage1.pt --steps 800 --lr 3e-4 --out ckpts/r1.pt --cap 0

--cap N  : assert every record's verifier length n_lines <= N (N=0 disables; Stage 1 must use 6).
Loss is next-token cross-entropy on proof tokens only (prompt tokens masked out).
"""
import argparse, json, math, os, random, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch, torch.nn.functional as F
from tokenizer import Tokenizer, RULES
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
        out.append((tok.encode_prompt(r['prompt']), tok.encode_proof(r['proof'])))
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


def token_labels(tok, q):
    """Per proof-token labels for the held-out breakdown (round3-run3): (rule of the line the token belongs to, token
    class).  Classes: idx (line index N<i>), bar ('|'), formula (formula symbols), sep (':' ';'), rule (rule name),
    ref (cited N<j>), qed.  Positional, so unaffected by shift_abs (which only changes N ids)."""
    RULESET = set(RULES)
    toks = [tok.itos[i] for i in q]
    # split into lines at ';'
    lines, cur = [], []
    for t in toks:
        cur.append(t)
        if t == ';':
            lines.append(cur); cur = []
    if cur:
        lines.append(cur)
    out = []
    for ln in lines:
        rule = ln[ln.index(':') + 1] if ':' in ln and ln.index(':') + 1 < len(ln) and ln[ln.index(':') + 1] in RULESET else 'NONE'
        seen_colon = False; seen_rule = False
        for j, t in enumerate(ln):
            if t == 'QED':
                out.append(('QED', 'qed')); continue
            if j == 0 and t.startswith('N'):
                cls = 'idx'
            elif t == '|':
                cls = 'bar'
            elif t in (':', ';'):
                cls = 'sep'; seen_colon = seen_colon or t == ':'
            elif seen_colon and not seen_rule and t in RULESET:
                cls = 'rule'; seen_rule = True
            elif seen_rule and t.startswith('N'):
                cls = 'ref'
            else:
                cls = 'formula'
            out.append((rule, cls))
    assert len(out) == len(q)
    return out


def breakdown_eval(model, held, tok, rng, dev):
    """Held-out cross-entropy grouped by rule of the line (all tokens of the line), by rule at the rule-name position
    only, and by token class.  -> dict of {group: {'sum', 'n', 'mean'}}."""
    import collections
    acc = {'by_rule': collections.defaultdict(lambda: [0.0, 0]), 'by_rule_name_pos': collections.defaultdict(lambda: [0.0, 0]),
           'by_class': collections.defaultdict(lambda: [0.0, 0])}
    model.eval()
    with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16, enabled=(dev == 'cuda')):
        for s in range(0, len(held), 256):
            idxs = list(range(s, min(s + 256, len(held))))
            x, m = batch(held, idxs, tok, rng, dev)
            logits = model(x[:, :-1]); tgt = x[:, 1:]; mk = m[:, 1:]
            l = F.cross_entropy(logits.reshape(-1, logits.size(-1)).float(), tgt.reshape(-1), reduction='none').reshape(tgt.shape).cpu()
            mk = mk.cpu()
            for bi, i in enumerate(idxs):
                p, q = held[i]
                labs = token_labels(tok, q)
                # target position t (in x[:,1:]) holds token x[:, t+1]; proof tokens start at x[:, len(p)]
                for k, (rule, cls) in enumerate(labs):
                    t = len(p) + k - 1
                    assert bool(mk[bi, t]), (t, len(p), k)
                    v = float(l[bi, t])
                    acc['by_rule'][rule][0] += v; acc['by_rule'][rule][1] += 1
                    acc['by_class'][cls][0] += v; acc['by_class'][cls][1] += 1
                    if cls == 'rule':
                        acc['by_rule_name_pos'][rule][0] += v; acc['by_rule_name_pos'][rule][1] += 1
    model.train()
    return {g: {k: {'sum': v[0], 'n': v[1], 'mean': v[0] / v[1]} for k, v in sorted(d.items())} for g, d in acc.items()}


def loss_on(model, x, m):
    logits = model(x[:, :-1])
    tgt = x[:, 1:]
    mk = m[:, 1:]
    l = F.cross_entropy(logits.reshape(-1, logits.size(-1)).float(), tgt.reshape(-1), reduction='none')
    return (l * mk.reshape(-1)).sum() / mk.sum()


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
    ap.add_argument('--out', required=True)
    ap.add_argument('--log_every', type=int, default=200)
    ap.add_argument('--no_shift', action='store_true', help='abs mode ablation: no random start-index offset (N1..N6 only ever seen)')
    a = ap.parse_args()
    torch.manual_seed(a.seed)
    rng = random.Random(a.seed)
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    if a.init:
        model, tok, _ = load_ckpt(a.init, dev)
        a.mode = tok.mode
    else:
        tok = Tokenizer(a.mode)
        model = GPT(tok.vocab_size, a.n_layer, a.d, a.n_head).to(dev)
    tok.shift = not a.no_shift
    print('params', model.n_params(), 'mode', tok.mode, 'shift', tok.shift, flush=True)
    data = load(a.data, tok, a.cap, check_verify=(a.cap > 0))
    held_all = load(a.heldout, tok, 0) if a.heldout else None
    held = held_all[:2000] if held_all else None      # the running 'val' number: unchanged (first 2,000 records = the 2- and 3-line proofs)
    print('train records', len(data), 'max len', max(len(p) + len(q) for p, q in data), flush=True)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=a.wd, betas=(0.9, 0.95))
    sched = lambda s: a.lr * s / a.warmup if s < a.warmup else a.min_lr + 0.5 * (a.lr - a.min_lr) * (1 + math.cos(math.pi * (s - a.warmup) / max(1, a.steps - a.warmup)))
    model.train()
    t0 = time.time()
    perm = []
    for step in range(1, a.steps + 1):
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
            if held:
                model.eval()
                with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16, enabled=(dev == 'cuda')):
                    vl = sum(loss_on(model, *batch(held, range(s, min(s + 256, len(held))), tok, rng, dev)).item() * min(256, len(held) - s)
                             for s in range(0, len(held), 256)) / len(held)
                msg += f' val {vl:.4f}'
                model.train()
            print(msg, flush=True)
    extra = {'args': vars(a), 'n_params': model.n_params(), 'secs': time.time() - t0}
    if held:
        bd = breakdown_eval(model, held_all, tok, rng, dev)     # breakdown over the FULL held-out file (all lengths 2-6; NEGI/DN/ORE occur only at 4-6)
        extra['heldout_breakdown'] = bd
        print('heldout_breakdown ' + json.dumps(bd), flush=True)
    save_ckpt(a.out, model, tok.mode, extra=extra)
    print('saved', a.out, flush=True)


if __name__ == '__main__':
    main()
