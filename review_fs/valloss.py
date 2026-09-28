"""Reviewer: recompute --val_bins token-weighted loss at step 6000 with the numpy forward (fp32), fixed presentation
re-implemented from the spec: random.Random(12345), per record in file order, shift_abs(encode_proof(proof))."""
import sys, os, json, random, numpy as np
sys.path.insert(0, 'rv'); sys.path.insert(0, '.')
from npgpt import NPGPT
from lean_tok import LeanTokenizer, MAXN
ck, mf = sys.argv[1], sys.argv[2]
tok = LeanTokenizer('lean_seq')
vr = random.Random(12345)
recs = [json.loads(l) for l in open('data/p2/heldout.jsonl')]
m = NPGPT(ck)
S = {}
import time; T0 = time.time()
N = int(os.environ.get('RV_N', len(recs)))
for ri, r in enumerate(recs[:N]):
    if ri % 100 == 0: print(ri, round(time.time() - T0), flush=True, file=sys.stderr)
    p = tok.encode_prompt(r['prompt']); q = tok.encode_proof(r['proof'])
    mx = max((x - tok.ref0 + 1 for x in q if x >= tok.ref0), default=0)
    if mx:
        s = vr.randint(0, MAXN - mx); q = [x + s if x >= tok.ref0 else x for x in q]
    x = np.array(p + q)
    # full-sequence logits: reuse step() on all tokens but we need every position's logits
    cache = [None] * m.L
    # replicate step() without the last-position slice
    import npgpt
    Sd = m.S; H, hd, T = m.H, m.hd, len(x); pos = np.arange(T); h = Sd['emb.weight'][x]
    for i in range(m.L):
        pre = f'blocks.{i}.'
        a = npgpt.ln(h, Sd[pre+'ln1.weight'], Sd[pre+'ln1.bias']); qkv = a @ Sd[pre+'qkv.weight'].T + Sd[pre+'qkv.bias']
        qq, kk, vv = [qkv[:, j*m.D:(j+1)*m.D].reshape(T, H, hd).transpose(1, 0, 2) for j in range(3)]
        qq, kk = m.rope(qq, pos), m.rope(kk, pos)
        att = qq @ kk.transpose(0, 2, 1) / np.sqrt(hd); att = np.where(pos[None, :] <= pos[:, None], att, -np.inf)
        att = np.exp(att - att.max(-1, keepdims=True)); att /= att.sum(-1, keepdims=True)
        h = h + (att @ vv).transpose(1, 0, 2).reshape(T, m.D) @ Sd[pre+'proj.weight'].T + Sd[pre+'proj.bias']
        g = npgpt.ln(h, Sd[pre+'ln2.weight'], Sd[pre+'ln2.bias']) @ Sd[pre+'fc1.weight'].T + Sd[pre+'fc1.bias']
        g = 0.5 * g * (1 + npgpt.erf(g / np.sqrt(2))); h = h + g @ Sd[pre+'fc2.weight'].T + Sd[pre+'fc2.bias']
    lg = npgpt.ln(h, Sd['ln_f.weight'], Sd['ln_f.bias']) @ Sd['head.weight'].T
    lg = lg[len(p) - 1:-1]; tg = x[len(p):]
    lg = lg - lg.max(-1, keepdims=True); lse = np.log(np.exp(lg).sum(-1))
    nll = lse - lg[np.arange(len(tg)), tg]
    d3 = bool((r.get('pat') or {}).get('depth3')); L = r['n_lines']
    for k in ['all', f'len{L}'] + (['depth3'] if d3 else []) + (['nodepth3_len6'] if (L == 6 and not d3) else []):
        a = S.setdefault(k, [0.0, 0]); a[0] += nll.sum(); a[1] += len(tg)
R = [json.loads(l) for l in open(mf)]; logged = [r for r in R if r.get('kind') == 'step'][-1]['val']
for k in logged:
    mine = S[k][0] / S[k][1]
    print(f'{k:14s} mine(fp32) {mine:.5f} logged {logged[k]:.5f} rel diff {(logged[k]-mine)/mine:+.4f}')
