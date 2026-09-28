"""Reviewer: numpy re-implementation of the GPT forward pass and train.val_bins' token-weighted per-slice loss on
half A (fp32; the pod used bf16 autocast, so agreement is expected to ~1e-3 relative, not bit-exact)."""
import sys, json, random, math, numpy as np
sys.path.insert(0, '..')
import ptread
from tokenizer import make_tokenizer

def ln(x, w, b): m = x.mean(-1, keepdims=True); v = ((x - m) ** 2).mean(-1, keepdims=True); return (x - m) / np.sqrt(v + 1e-5) * w + b
def gelu(x):
    from math import erf
    return 0.5 * x * (1 + np.vectorize(erf)(x / math.sqrt(2))) if False else 0.5 * x * (1 + erf_np(x / math.sqrt(2)))
def erf_np(x):  # Abramowitz-Stegun 7.1.26 is too coarse; use numpy via math.erf ufunc
    return np.frompyfunc(math.erf, 1, 1)(x).astype(np.float64)

def forward(S, cfg, ids):
    d, h = cfg['d'], cfg['n_head']; hd = d // h; T = len(ids)
    x = S['emb.weight'][ids].astype(np.float64)
    pos = np.arange(T, dtype=np.float64); inv = 1.0 / (10000.0 ** (np.arange(0, hd, 2) / hd)); ang = pos[:, None] * inv[None]
    cos, sin = np.cos(ang), np.sin(ang)
    def rope(z):
        z1, z2 = z[..., ::2], z[..., 1::2]
        return np.stack([z1 * cos - z2 * sin, z1 * sin + z2 * cos], -1).reshape(z.shape)
    causal = np.triu(np.full((T, T), -np.inf), 1)
    for l in range(cfg['n_layer']):
        p = lambda n: S[f'blocks.{l}.{n}']
        a = ln(x, p('ln1.weight'), p('ln1.bias'))
        qkv = (a @ p('qkv.weight').T + p('qkv.bias')).reshape(T, 3, h, hd).transpose(1, 2, 0, 3)
        q, k, v = rope(qkv[0]), rope(qkv[1]), qkv[2]
        att = q @ k.transpose(0, 2, 1) / math.sqrt(hd) + causal
        att = np.exp(att - att.max(-1, keepdims=True)); att /= att.sum(-1, keepdims=True)
        y = (att @ v).transpose(1, 0, 2).reshape(T, d)
        x = x + y @ p('proj.weight').T + p('proj.bias')
        a = ln(x, p('ln2.weight'), p('ln2.bias'))
        f = a @ p('fc1.weight').T + p('fc1.bias')
        x = x + (gelu(f) @ p('fc2.weight').T + p('fc2.bias'))
    x = ln(x, S['ln_f.weight'], S['ln_f.bias'])
    return x @ S['head.weight'].T

def val(path, recs, tok, idxsets):
    c = ptread.load(path); S = {k: np.asarray(v, dtype=np.float64) for k, v in c['state'].items()}
    vrng = random.Random(12345)
    per = []
    for r in recs:
        pi = tok.encode_prompt(r['prompt']); pr = tok.shift_abs(tok.encode_proof(r['proof']), vrng)
        per.append((pi, pr))
    out = {}
    need = sorted(set(i for ii in idxsets.values() for i in ii))
    ls = {}
    for i in need:
        pi, pr = per[i]; s = pi + pr
        lg = forward(S, c['cfg'], np.array(s[:-1]))
        lg = lg - lg.max(-1, keepdims=True); lp = lg - np.log(np.exp(lg).sum(-1, keepdims=True))
        tgt = np.array(s[1:]); m = np.array([0] * len(pi) + [1] * len(pr))[1:]
        nll = -lp[np.arange(len(tgt)), tgt]
        ls[i] = ((nll * m).sum(), m.sum())
    for n, ii in idxsets.items():
        out[n] = sum(ls[i][0] for i in ii) / sum(ls[i][1] for i in ii)
    return out

if __name__ == '__main__':
    recs = [json.loads(l) for l in open('../data/ca/heldout_A.jsonl')]
    tok = make_tokenizer('lean_seq')
    d3 = [i for i, r in enumerate(recs) if r['pat']['depth3']]
    l6 = [i for i, r in enumerate(recs) if r['n_lines'] == 6]
    VL = {json.loads(l)['ckpt']: json.loads(l)['loss'] for l in open('../artifacts/ca/valloss_A.jsonl')}
    for ck in sys.argv[1:]:
        o = val(f'/tmp/rv_ca/sd/{ck}.pt', recs, tok, {'depth3': d3, 'len6': l6})
        v = VL[f'ckpts/sd/{ck}.pt']
        print(ck, ' '.join(f'{k}: mine {o[k]:.5f} pod {v[k]:.5f} rel {abs(o[k] - v[k]) / v[k]:.1e}' for k in o), flush=True)
