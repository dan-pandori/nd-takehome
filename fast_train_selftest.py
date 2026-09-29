#!/usr/bin/env python3
"""Self-test of fast_train.py against train.py's legacy path (run fast-stage1).  Needs a GPU.

  python3 fast_train_selftest.py --data data/p2/train_depth3_f0_a1.jsonl --out artifacts/fs/selftest.json

1. augmentation, lean_seq: every GPU-augmented record equals tok.shift_abs's transform for the offset it drew;
   the drawn offsets are uniform on {0..64-mx} per mx (chi-square), and their distribution matches draws from
   tok.shift_abs itself (two-sample chi-square), over 200 draws of each of 2,000 records.
2. augmentation, lean_rand: injective, names outside the proof untouched, first-name image uniform on 0..63.
3. loss equivalence, fp32 (no autocast): the packed-stream loss and its gradient, and the padded loss, equal
   train.loss_on on the same un-augmented batch (legacy batch()), on 8 random batches of 128.
4. the block-granularity BlockMask equals create_block_mask's for a packed batch (same flex output).
"""
import argparse, json, math, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
import train, fast_train as ft
from model import GPT
from tokenizer import make_tokenizer


def chi2_uniform(counts):
    n = sum(counts); k = len(counts); e = n / k
    return sum((c - e) ** 2 / e for c in counts), k - 1


def chi2_p(x, df):
    # Wilson-Hilferty normal approximation to the chi-square upper tail
    if df <= 0:
        return 1.0
    z = ((x / df) ** (1 / 3) - (1 - 2 / (9 * df))) / math.sqrt(2 / (9 * df))
    return 0.5 * math.erfc(z / math.sqrt(2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--n', type=int, default=2000)
    a = ap.parse_args()
    import record as ndrec; ndrec.save_config(vars(a), a.out)    # the resolved config next to the outputs
    dev = 'cuda'
    res = {}
    tok = make_tokenizer('lean_seq')
    recs = []
    for i, l in enumerate(open(a.data)):
        if i >= a.n:
            break
        r = json.loads(l)
        recs.append((tok.encode_prompt(r['prompt']), tok.encode_proof(r['proof'])))
    d = ft.GPUData(ft.pack_records(recs), tok, dev)
    B = len(recs)
    idx = torch.arange(B, device=dev)
    T = ft.round_up(int(d.lens.sum()), 2 * ft.BLOCK)
    M = ft.maxn(tok)
    mx_py = [max((x - tok.ref0 + 1 for x in q if x >= tok.ref0), default=0) for _, q in recs]
    assert d.mx.tolist() == mx_py, 'mx mismatch'

    # 1. lean_seq offsets
    gen = torch.Generator(device=dev); gen.manual_seed(1)
    x0, pos, doc, lm = ft.gather_packed(d, idx, T, 'none', M, None)
    base = [p + q for p, q in recs]
    assert [x0[0, doc == j].tolist() for j in range(5)] == base[:5]
    cnt_gpu = {}; bad = 0; R = 200
    for rep in range(R):
        x, _, _, _ = ft.gather_packed(d, idx, T, 'offset', M, gen)
        xs = x[0, :int(d.lens.sum())].tolist()
        o = 0
        for j, (p, q) in enumerate(recs):
            seg = xs[o:o + len(p) + len(q)]; o += len(p) + len(q)
            mx = mx_py[j]
            if mx == 0:
                bad += seg != p + q; continue
            s = next(y - x_ for y, x_ in zip(seg[len(p):], q) if x_ >= tok.ref0)
            bad += seg != p + [t + s if t >= tok.ref0 else t for t in q]
            bad += not (0 <= s <= M - mx)
            cnt_gpu.setdefault(mx, [0] * (M - mx + 1))[s] += 1
    rng = random.Random(7); cnt_py = {}
    for rep in range(R):
        for j, (p, q) in enumerate(recs):
            mx = mx_py[j]
            if mx == 0:
                continue
            q2 = tok.shift_abs(q, rng)
            s = next(y - x_ for y, x_ in zip(q2, q) if x_ >= tok.ref0)
            cnt_py.setdefault(mx, [0] * (M - mx + 1))[s] += 1
    per_mx = {}
    for mx in sorted(cnt_gpu):
        c2, df = chi2_uniform(cnt_gpu[mx])
        # two-sample (homogeneity) chi-square GPU vs shift_abs
        g, pyc = cnt_gpu[mx], cnt_py[mx]
        ng, npy = sum(g), sum(pyc)
        h = sum(((gi - (gi + pi) * ng / (ng + npy)) ** 2 / ((gi + pi) * ng / (ng + npy)) +
                 (pi - (gi + pi) * npy / (ng + npy)) ** 2 / ((gi + pi) * npy / (ng + npy)))
                for gi, pi in zip(g, pyc) if gi + pi > 0)
        per_mx[mx] = {'draws': ng, 'chi2_uniform': c2, 'df': df, 'p_uniform': chi2_p(c2, df),
                      'chi2_vs_shift_abs': h, 'p_vs_shift_abs': chi2_p(h, df)}
    res['lean_seq_offset'] = {'records': B, 'repeats': R, 'transform_mismatches': int(bad), 'per_mx': per_mx,
                              'min_p_uniform': min(v['p_uniform'] for v in per_mx.values()),
                              'min_p_vs_shift_abs': min(v['p_vs_shift_abs'] for v in per_mx.values())}

    # 2. lean_rand permutation
    first = [0] * M; bad2 = 0
    for rep in range(50):
        x, _, _, _ = ft.gather_packed(d, idx, T, 'perm', M, gen)
        xs = x[0, :int(d.lens.sum())].tolist(); o = 0
        for j, (p, q) in enumerate(recs):
            seg = xs[o:o + len(p) + len(q)]; o += len(p) + len(q)
            bad2 += seg[:len(p)] != p
            mp = {}
            for y, x_ in zip(seg[len(p):], q):
                if x_ >= tok.ref0:
                    if mp.setdefault(x_, y) != y:
                        bad2 += 1
                elif y != x_:
                    bad2 += 1
            bad2 += len(set(mp.values())) != len(mp)
            if mp:
                first[mp[tok.ref0] - tok.ref0] += 1
    c2, df = chi2_uniform(first)
    res['lean_rand_perm'] = {'violations': int(bad2), 'chi2_first_name_uniform': c2, 'df': df, 'p': chi2_p(c2, df)}

    # 3. loss / gradient equivalence in fp32
    torch.manual_seed(0)
    model = GPT(tok.vocab_size, 4, 256, 8).to(dev)
    rng = random.Random(0)
    tok.shift = False
    worst = {'packed_loss': 0.0, 'padded_loss': 0.0, 'packed_grad_rel': 0.0}
    for b in range(8):
        ii = rng.sample(range(B), 128)
        xl, ml = train.batch(recs, ii, tok, rng, dev)
        model.zero_grad(); ll = train.loss_on(model, xl, ml); ll.backward()
        g0 = torch.cat([p.grad.flatten() for p in model.parameters()])
        it = torch.tensor(ii, device=dev)
        Tp = ft.round_up(int(d.lens[it].sum()), 2 * ft.BLOCK)
        x, pos, doc, lm = ft.gather_packed(d, it, Tp, 'none', M, None)
        model.zero_grad()
        l = ft.tok_losses_packed(model, x, pos, ft.make_block_mask(doc, Tp))
        lp = (l * lm.float()).sum() / lm.float().sum(); lp.backward()
        g1 = torch.cat([p.grad.flatten() for p in model.parameters()])
        xp, lmp = ft.gather_padded(d, it, int(d.lens[it].max()), 'none', M, None)
        with torch.no_grad():
            l2 = ft.tok_losses_padded(model, xp); lq = (l2 * lmp.float()).sum() / lmp.float().sum()
        worst['packed_loss'] = max(worst['packed_loss'], abs(lp.item() - ll.item()))
        worst['padded_loss'] = max(worst['padded_loss'], abs(lq.item() - ll.item()))
        worst['packed_grad_rel'] = max(worst['packed_grad_rel'], float((g1 - g0).norm() / g0.norm()))
    res['fp32_equivalence'] = {'batches': 8, 'max_abs_loss_diff_packed': worst['packed_loss'],
                               'max_abs_loss_diff_padded': worst['padded_loss'],
                               'max_rel_grad_diff_packed': worst['packed_grad_rel']}

    # 4. block mask vs create_block_mask
    from torch.nn.attention.flex_attention import create_block_mask, flex_attention
    it = torch.tensor(rng.sample(range(B), 128), device=dev)
    Tp = ft.round_up(int(d.lens[it].sum()), 2 * ft.BLOCK)
    _, _, doc, _ = ft.gather_packed(d, it, Tp, 'none', M, None)
    bm1 = ft.make_block_mask(doc, Tp)
    bm2 = create_block_mask(lambda b, h, q, kv: (doc[q] == doc[kv]) & (q >= kv), None, None, Tp, Tp, device=dev, BLOCK_SIZE=ft.BLOCK)
    q = torch.randn(1, 8, Tp, 32, device=dev); k = torch.randn_like(q); v = torch.randn_like(q)
    y1 = flex_attention(q, k, v, block_mask=bm1); y2 = flex_attention(q, k, v, block_mask=bm2)
    res['block_mask'] = {'T': Tp, 'max_abs_diff_vs_create_block_mask': float((y1 - y2).abs().max())}

    ok = (res['lean_seq_offset']['transform_mismatches'] == 0 and res['lean_seq_offset']['min_p_vs_shift_abs'] > 1e-3
          and res['lean_rand_perm']['violations'] == 0 and res['lean_rand_perm']['p'] > 1e-3
          and worst['packed_loss'] < 1e-4 and worst['padded_loss'] < 1e-4 and worst['packed_grad_rel'] < 1e-3
          and res['block_mask']['max_abs_diff_vs_create_block_mask'] < 1e-4)
    res['PASS'] = bool(ok)
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    json.dump(res, open(a.out, 'w'), indent=1)
    print(json.dumps({k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items() if kk != 'per_mx'}) for k, v in res.items()}, indent=1))


if __name__ == '__main__':
    main()
