"""Reviewer (fast-stage1): torch-free fp32 numpy re-implementation of model.GPT + greedy KV-cache decoding.
Written independently of sample.py; uses lean_tok only for the vocabulary / prompt tokens / text rendering.
  python3 rv/npgpt.py OUT.jsonl CKPT [CKPT ...] --idx rv/sample_idx.json
"""
import sys, os, json, time, argparse
import numpy as np
from scipy.special import erf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ptread
from lean_tok import LeanTokenizer


def ln(x, w, b, eps=1e-5):
    m = x.mean(-1, keepdims=True)
    v = ((x - m) ** 2).mean(-1, keepdims=True)
    return (x - m) / np.sqrt(v + eps) * w + b


class NPGPT:
    def __init__(self, path):
        d = ptread.load(path)
        self.cfg, self.S, self.extra = d['cfg'], {k: np.asarray(v, dtype=np.float32) for k, v in d['state'].items()}, d['extra']
        self.mode = d['tok_mode']
        self.L, self.D, self.H = self.cfg['n_layer'], self.cfg['d'], self.cfg['n_head']
        self.hd = self.D // self.H
        inv = 1.0 / (10000.0 ** (np.arange(0, self.hd, 2, dtype=np.float32) / self.hd))
        ang = np.arange(2048, dtype=np.float32)[:, None] * inv[None, :]
        self.cos, self.sin = np.cos(ang), np.sin(ang)

    def rope(self, x, p):            # x: (H, T, hd), p: positions (T,)
        c, s = self.cos[p][None], self.sin[p][None]
        x1, x2 = x[..., 0::2], x[..., 1::2]
        out = np.empty_like(x)
        out[..., 0::2] = x1 * c - x2 * s
        out[..., 1::2] = x1 * s + x2 * c
        return out

    def step(self, ids, p0, cache):
        """ids: new tokens (T,), positions p0..p0+T-1; cache: list per layer of [K (H,n,hd), V]. Returns last logits."""
        S, H, hd = self.S, self.H, self.hd
        T = len(ids)
        p = np.arange(p0, p0 + T)
        x = S['emb.weight'][ids]
        for i in range(self.L):
            pre = f'blocks.{i}.'
            a = ln(x, S[pre + 'ln1.weight'], S[pre + 'ln1.bias'])
            qkv = a @ S[pre + 'qkv.weight'].T + S[pre + 'qkv.bias']
            q, k, v = [qkv[:, j * self.D:(j + 1) * self.D].reshape(T, H, hd).transpose(1, 0, 2) for j in range(3)]
            q, k = self.rope(q, p), self.rope(k, p)
            if cache[i] is None:
                cache[i] = [k, v]
            else:
                cache[i] = [np.concatenate([cache[i][0], k], 1), np.concatenate([cache[i][1], v], 1)]
            K, V = cache[i]
            n = K.shape[1]
            att = q @ K.transpose(0, 2, 1) / np.sqrt(hd)                     # (H, T, n)
            qpos = p[:, None]; kpos = np.arange(n)[None, :]
            att = np.where(kpos <= qpos, att, -np.inf)
            att = att - att.max(-1, keepdims=True)
            att = np.exp(att); att /= att.sum(-1, keepdims=True)
            y = (att @ V).transpose(1, 0, 2).reshape(T, self.D)
            x = x + y @ S[pre + 'proj.weight'].T + S[pre + 'proj.bias']
            h = ln(x, S[pre + 'ln2.weight'], S[pre + 'ln2.bias']) @ S[pre + 'fc1.weight'].T + S[pre + 'fc1.bias']
            h = 0.5 * h * (1.0 + erf(h / np.sqrt(2.0)))
            x = x + h @ S[pre + 'fc2.weight'].T + S[pre + 'fc2.bias']
        x = ln(x[-1:], S['ln_f.weight'], S['ln_f.bias'])
        return (x @ S['head.weight'].T)[0]

    def greedy(self, prompt_ids, eos, max_new=400):
        cache = [None] * self.L
        logits = self.step(np.array(prompt_ids), 0, cache)
        out, margins = [], []
        pos = len(prompt_ids)
        for _ in range(max_new):
            srt = np.sort(logits)
            margins.append(float(srt[-1] - srt[-2]))
            t = int(np.argmax(logits))
            out.append(t)
            if t == eos:
                break
            logits = self.step(np.array([t]), pos, cache)
            pos += 1
        return out, min(margins)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('ckpts', nargs='+')
    ap.add_argument('--idx', required=True)
    ap.add_argument('--heldout', default='data/p2/heldout.jsonl')
    a = ap.parse_args()
    recs = [json.loads(l) for l in open(a.heldout) if l.strip()]
    idx = json.load(open(a.idx))
    tok = LeanTokenizer('lean_seq')
    done = set()
    if os.path.exists(a.out):
        done = {(json.loads(l)['ckpt'], json.loads(l)['i']) for l in open(a.out)}
    f = open(a.out, 'a')
    for ck in a.ckpts:
        m = NPGPT(ck)
        assert m.mode == 'lean_seq'
        t0 = time.time()
        for i in idx:
            if (ck, i) in done:
                continue
            r = recs[i]
            ids, margin = m.greedy(tok.encode_prompt(r['prompt']), tok.eos)
            ended = ids and ids[-1] == tok.eos
            toks = [tok.itos[t] for t in (ids[:-1] if ended else ids)]
            f.write(json.dumps({'ckpt': ck, 'i': i, 'name': r['name'], 'n_lines': r['n_lines'],
                                'depth3': bool((r.get('pat') or {}).get('depth3')), 'ended': bool(ended),
                                'min_margin': margin, 'text': tok.text(toks) if ended else None}) + '\n')
            f.flush()
        print(ck, f'{time.time() - t0:.0f}s', flush=True)


if __name__ == '__main__':
    main()
