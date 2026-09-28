#!/usr/bin/env python3
"""support-followups D: where in a proof is the base model's improbability?  Forward passes only.

  python3 sf_steps.py --base ckpts/lf/stage1_a1_seq_s0.pt --ei ckpts/ladder/la_T1_sc_s0_r8.pt \
      --out artifacts/sf/d_steps.jsonl

Proof sets (preregistration/support-followups.md §D):
  S   every distinct EI s0 proof of the 29 falsifier survivors (support-curves raw records, all temperatures)
  C1  every distinct EI s0 proof of the other 53 forward-crux theorems (the base does solve them, rarely)
  C2  every distinct accepted proof of the base s0's own, stage 1 (T 0.8, k 10,000), all 383 theorems
  C3  (extra, not pre-registered) the base s0's own proofs of forward-crux theorems from stage 2

Per-token log p, EXACTLY marginalised over the lean_seq name offset.  The sequences for different offsets s are
identical up to the first name token and all distinct from it on (the first name is n_{1+s}), so the probability of
a prefix is p(prefix) before that token and sum_s p(prefix_s) from it on.  With cum_s(t) the log p of the first t+1
proof tokens at offset s:  L(t) = cum_0(t) for t < f,  logsumexp_s cum_s(t) for t >= f;  token t contributes
L(t) - L(t-1).  The contributions sum to log sum_s p(proof_s) = sc_secondary's / novelty.score's logp (checked).

Steps: one `have ... ;` (for a box-valued have, the head through the box's `fun ( n : A ) => by`), one `exact ...`
(with the `)`s / `<eos>` after it), or the opening of a second Or.elim branch `( fun ( n : B ) => by`.
Token classes: syntax / name (fresh | cite) / logic (formula | rule) -- see cls().
"""
import argparse, glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
import torch.nn.functional as F
from model import load_ckpt
from lean_tok import MAXN

FORM = {'P', 'Q', 'R', 'S', '¬', '∧', '∨', '→', 'False'}
RULE = {'.1', '.2', '.elim', 'Or.inl', 'Or.inr', 'Or.elim', 'Classical.byContradiction', '⟨'}


def steps_of(toks):
    """toks: proof token strings (incl. '<eos>').  Returns a step index per token and step kinds."""
    sid, kinds, cur = [], [], -1
    for t, x in enumerate(toks):
        prev = toks[t - 1] if t else None
        new = None
        if x == 'have':
            new = 'have'
        elif x == 'exact':
            new = 'exact'
        elif x == '(' and toks[t + 1:t + 3] == ['fun', '('] and prev == ')':
            new = 'box2'                        # second Or.elim branch opening
        if new or cur < 0:
            kinds.append(new or 'other'); cur += 1
        sid.append(cur)
    # a have whose term is a box: label it (rule of the step = what follows ':=')
    for k in range(len(kinds)):
        if kinds[k] == 'have':
            idx = [t for t, s in enumerate(sid) if s == k]
            try:
                j = next(t for t in idx if toks[t] == ':=')
                nxt = toks[j + 1]
                kinds[k] = 'have:' + ('box' if nxt == '(' else 'orelim' if nxt == 'Or.elim' else nxt if nxt in RULE
                                      else 'prem' if nxt.startswith('h') else 'name')
            except StopIteration:
                pass
    return sid, kinds


def cls(toks):
    out, seen = [], set()
    for t, x in enumerate(toks):
        prev = toks[t - 1] if t else None
        if x.startswith('n') and x[1:].isdigit():
            out.append('name:fresh' if x not in seen else 'name:cite'); seen.add(x)
        elif x.startswith('h') and x[1:].isdigit():
            out.append('name:cite')
        elif x in FORM:
            out.append('logic:formula')
        elif x in RULE or (x == '(' and prev == ':=' and toks[t + 1:t + 2] == ['fun']):
            out.append('logic:rule')
        else:
            out.append('syntax')
    return out


def cls_pos(toks):
    """Secondary class (added after the pre-registration, reported as such): every token inside a stated formula --
    between `have nX :` and `:=`, inside a binder `( nX : ... )`, or the `( nE : False )` ascription -- is
    logic:formula, brackets included (a formula's opening bracket is the choice to state a compound formula)."""
    out = cls(toks)
    t = 0
    while t < len(toks):
        if toks[t] == ':' and t >= 2 and toks[t - 2] == 'have':
            u = t + 1
            while toks[u] != ':=':
                out[u] = 'logic:formula'; u += 1
            t = u
        elif toks[t] == ':' and t >= 2 and toks[t - 2] == '(':
            u, dep = t + 1, 0
            while not (toks[u] == ')' and dep == 0):
                dep += (toks[u] == '(') - (toks[u] == ')'); out[u] = 'logic:formula'; u += 1
            t = u
        t += 1
    return out


def load_sets():
    surv = {l.strip() for l in open('data/sc/falsifier_survivors.txt') if l.strip()}
    cf = {l.strip() for l in open('data/sc/crux_forward.txt') if l.strip()}
    prompts, Lt = {}, {}
    for l in open('data/sc/theorems.jsonl'):
        if l.strip():
            r = json.loads(l); prompts[r['name']] = r['prompt']; Lt[r['name']] = r['L_true']
    sets = {'S': {}, 'C1': {}, 'C2': {}, 'C3': {}}

    def add(set_, r, src):
        for p in r['proofs']:
            k = (r['name'], p['proof'])
            e = sets[set_].setdefault(k, {'set': set_, 'name': r['name'], 'L_true': Lt[r['name']], 'prompt': prompts[r['name']],
                                          'proof': p['proof'], 'n_lines': p['n_lines'], 'term_size': p['term_size'],
                                          'count': 0, 'src': []})
            e['count'] += p['count']; e['src'].append(src)
    for f in sorted(glob.glob('artifacts/sc/s*_ei_*_s0.s*.jsonl')):
        for l in open(f):
            r = json.loads(l)
            if r['name'] in surv: add('S', r, os.path.basename(f))
            elif r['name'] in cf: add('C1', r, os.path.basename(f))
    for f in sorted(glob.glob('artifacts/sc/s1_base_T08_s0.s*.jsonl')):
        for l in open(f):
            add('C2', json.loads(l), os.path.basename(f))
    for f in sorted(glob.glob('artifacts/sc/s2*_base_*_s0.s*.jsonl')):
        for l in open(f):
            r = json.loads(l)
            if r['name'] in cf: add('C3', r, os.path.basename(f))
    return [e for s in sets.values() for e in s.values()]


@torch.no_grad()
def per_token(model, tok, recs, dev, batch, temps=(1.0, 0.8)):
    """recs[i]['tok_lp'][temp] = list of marginal per-token log p over the proof tokens."""
    jobs, nshift = [], {}
    for i, r in enumerate(recs):
        pid = tok.encode_prompt(r['prompt']); qid = tok.encode_proof(r['proof'])
        r['_toks'] = [tok.itos[x] for x in qid]
        mx = max((x - tok.ref0 + 1 for x in qid if x >= tok.ref0), default=0)
        nshift[i] = MAXN - mx + 1
        for s in range(0, MAXN - mx + 1):
            jobs.append((i, s, len(pid), pid + [x + s if x >= tok.ref0 else x for x in qid]))
    jobs.sort(key=lambda j: len(j[3]))
    per = {}                                   # (i, s) -> {temp: tensor of per-token lp}
    for b0 in range(0, len(jobs), batch):
        chunk = jobs[b0:b0 + batch]
        T = max(len(j[3]) for j in chunk)
        x = torch.full((len(chunk), T), tok.pad, dtype=torch.long)
        for k, (_, _, _, ids) in enumerate(chunk):
            x[k, :len(ids)] = torch.tensor(ids)
        x = x.to(dev)
        with torch.autocast('cuda', dtype=torch.bfloat16, enabled=(dev == 'cuda')):
            logits = model(x[:, :-1]).float()
        tgt = x[:, 1:, None]
        lps = {tp: F.log_softmax(logits / tp, -1).gather(-1, tgt).squeeze(-1).cpu() for tp in temps}
        for k, (i, s, lp, ids) in enumerate(chunk):
            per[(i, s)] = {tp: lps[tp][k, lp - 1:len(ids) - 1].double() for tp in temps}
    for i, r in enumerate(recs):
        shifts = range(nshift[i])
        qid_names = [t.startswith('n') and t[1:].isdigit() for t in r['_toks']]
        f = qid_names.index(True) if any(qid_names) else len(qid_names)
        r['tok_lp'], r['logp_total'] = {}, {}
        for tp in temps:
            M = torch.stack([per[(i, s)][tp] for s in shifts])       # [n_shift, n_tok]
            cum = M.cumsum(1)
            L = torch.where(torch.arange(M.shape[1]) < f, cum[0], torch.logsumexp(cum, 0))
            contrib = torch.diff(L, prepend=torch.zeros(1, dtype=L.dtype))
            r['tok_lp'][str(tp)] = contrib.tolist()
            r['logp_total'][str(tp)] = float(torch.logsumexp(cum[:, -1], 0))
            assert abs(contrib.sum().item() - r['logp_total'][str(tp)]) < 1e-6
        r['n_shifts'] = len(shifts)


def summarise(r, tp='1.0'):
    toks, lp = r['_toks'], r['tok_lp'][tp]
    sid, kinds = steps_of(toks)
    st = [0.0] * len(kinds)
    for s, v in zip(sid, lp):
        st[s] += v
    tot = sum(lp)
    o = sorted(st)
    c = cls(toks)
    c2 = cls_pos(toks)
    by, by2 = {}, {}
    for k, k2, v in zip(c, c2, lp):
        by[k] = by.get(k, 0.0) + v; by2[k2] = by2.get(k2, 0.0) + v
    worst = sorted(range(len(lp)), key=lambda t: lp[t])[:3]
    return {'steps': [{'kind': k, 'lp': round(v, 4)} for k, v in zip(kinds, st)], 'n_steps': len(kinds),
            'total': tot, 'w1': o[0], 'w2': o[1] if len(o) > 1 else 0.0,
            's1': o[0] / tot if tot < 0 else 0.0, 's2': (o[0] + (o[1] if len(o) > 1 else 0)) / tot if tot < 0 else 0.0,
            'worst_step_kind': kinds[st.index(o[0])],
            'class_lp': {k: round(v, 4) for k, v in by.items()}, 'class_lp_pos': {k: round(v, 4) for k, v in by2.items()},
            'worst_tokens': [{'tok': toks[t], 'cls': c[t], 'cls_pos': c2[t], 'pos': t, 'lp': round(lp[t], 4), 'step_kind': kinds[sid[t]]} for t in worst]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', required=True)
    ap.add_argument('--ei', default=None)
    ap.add_argument('--out', required=True)
    ap.add_argument('--batch', type=int, default=512)
    ap.add_argument('--limit', type=int, default=None)
    a = ap.parse_args()
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    recs = load_sets()
    if a.limit:
        recs = recs[:a.limit]
    print({s: sum(r['set'] == s for r in recs) for s in ('S', 'C1', 'C2', 'C3')}, 'proofs', flush=True)
    res = {}
    for label, path in [('base', a.base)] + ([('ei', a.ei)] if a.ei else []):
        model, tok, _ = load_ckpt(path, dev)
        assert tok.mode == 'lean_seq'
        model.eval()
        per_token(model, tok, recs, dev, a.batch)
        res[label] = [{'tok_lp': r.pop('tok_lp'), 'logp_total': r.pop('logp_total'), 'n_shifts': r.pop('n_shifts')} for r in recs]
        del model
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, 'w') as fo:
        for i, r in enumerate(recs):
            o = {k: v for k, v in r.items() if k not in ('_toks', 'prompt')}
            o['tokens'] = r['_toks']; o['token_cls'] = cls(r['_toks']); o['token_cls_pos'] = cls_pos(r['_toks'])
            o['base_ckpt'] = a.base; o['ei_ckpt'] = a.ei
            for label in res:
                r2 = dict(r, **res[label][i])
                o[label] = {'logp_total': r2['logp_total'], 'n_shifts': r2['n_shifts'], 'tok_lp': r2['tok_lp'],
                            'T1': summarise(r2, '1.0'), 'T08': summarise(r2, '0.8')}
            fo.write(json.dumps(o, ensure_ascii=False) + '\n')
    print('->', a.out, len(recs), 'proofs')


if __name__ == '__main__':
    main()
