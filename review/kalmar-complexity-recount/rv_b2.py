#!/usr/bin/env python3
"""Reviewer recount of B2 (block-wise prequential code) from the per-block rows the pods wrote.

  python3 rv_b2.py count          # own loss-token / pair counts of theorems [0, 16884) for kal and k12 (per record)
  python3 rv_b2.py recount        # every artifacts/kc/b2/*.json: block tokens vs own counts, totals, EDL, shares

Own counts use the same segmentation as rv_b1.py (canonical lean_seq cut into actions; loss tokens = action + <eos>).
eval: 16 pairs per theorem, action one token + <eos> = 2 loss tokens per pair.
"""
import gzip, json, math, os, sys, collections, glob
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.expanduser('~/review/kalmar-complexity')
sys.path.insert(0, WS); sys.path.insert(0, HERE)
LN2 = math.log(2)
NTH = 16884


def count():
    from state_env import canonicalise
    from rv_b1 import segment
    out = {}
    for task, fn in [('k12', 'data/kh/train_k12.jsonl'), ('kal', 'data/kalmar/train_kal_sl.jsonl.gz')]:
        op = gzip.open if fn.endswith('.gz') else open
        recs = []
        with op(os.path.join(WS, fn), 'rt') as fh:
            for i, line in enumerate(fh):
                if i >= NTH:
                    break
                r = json.loads(line)
                acts = segment(canonicalise(r['prompt'], r['proof']))
                tags = r.get('tags')
                if isinstance(tags, str):
                    tags = json.loads(tags.replace("'", '"'))
                per = collections.Counter(); pert = collections.Counter()
                for j, a in enumerate(acts):
                    tg = tags[j] if tags else 'k12'
                    per[tg] += 1; pert[tg] += a + 1
                recs.append({'pairs': len(acts), 'loss': sum(a + 1 for a in acts), 'tag_pairs': dict(per),
                             'tag_tokens': dict(pert), 'prompt': r['prompt']})
        out[task] = recs
        print(task, len(recs), sum(r['loss'] for r in recs), flush=True)
    json.dump(out, open(os.path.join(HERE, 'out', 'b2_counts.json'), 'w'))


def recount():
    C = json.load(open(os.path.join(HERE, 'out', 'b2_counts.json')))
    res = {}
    for f in sorted(glob.glob(os.path.join(WS, 'artifacts/kc/b2/*.json'))):
        d = json.load(open(f))
        a = d['args']
        task, V = a['task'], d['vocab']
        name = os.path.basename(f)[:-5]
        B = d['blocks']

        def own_tokens(lo, hi):
            if task == 'eval':
                return 32 * (hi - lo)
            return sum(r['loss'] for r in C[task][lo:hi])
        rows = []
        tok_mismatch = []
        for blk in B:
            lo, hi = blk['block']
            mine = own_tokens(lo, hi)
            if mine != blk['loss_tokens']:
                tok_mismatch.append([lo, hi, blk['loss_tokens'], mine])
            rows.append({'block': [lo, hi], 'bits': blk['bits'], 'tokens': blk['loss_tokens'],
                         'bits_per_tok': blk['bits'] / blk['loss_tokens'], 'asym': blk.get('asymptote_block', False),
                         'steps': blk.get('steps'), 'max_steps': blk.get('max_steps'), 'best_step': blk.get('best_step'),
                         'secs': blk.get('secs'), 'train_tokens': blk.get('train_tokens')})
        # uniform first block
        b0 = B[0]
        uni_ok = abs(b0['bits'] - b0['loss_tokens'] * math.log2(V)) < 1e-6 * b0['bits']
        pre = [r for r in rows if not r['asym']]
        L = sum(r['bits'] for r in pre)
        N = sum(r['tokens'] for r in pre)
        linf = rows[-1]['bits_per_tok']
        edl = L - N * linf

        def prefix(T):
            """prequential code of [0, T) and EDL with L_inf = per-token code of the block that starts at T"""
            p = [r for r in rows if r['block'][1] <= T]
            nxt = [r for r in rows if r['block'][0] == T]
            if not p or p[-1]['block'][1] != T or not nxt:
                return None
            LT = sum(r['bits'] for r in p); NT = sum(r['tokens'] for r in p)
            li = nxt[0]['bits_per_tok']
            return {'L': LT, 'N': NT, 'L_inf_bits_per_tok': li, 'EDL': LT - NT * li,
                    'block0_share_of_L': rows[0]['bits'] / LT, 'EDL_without_block0': (LT - rows[0]['bits']) - (NT - rows[0]['tokens']) * li}
        res[name] = {'task': task, 'size': a['size'], 'seed': a['seed'], 'max_thm': a['max_thm'],
                     'v2': bool(a.get('patience_steps')), 'gpu': d.get('gpu'),
                     'uniform_block0_ok': uni_ok, 'block0_bits': b0['bits'], 'block0_tokens': b0['loss_tokens'],
                     'token_mismatches': tok_mismatch,
                     'L_preq': L, 'N': N, 'L_inf_bits_per_tok': linf, 'EDL': edl, 'block0_share_of_L': b0['bits'] / L,
                     'block0_share_of_EDL': (b0['bits'] - b0['loss_tokens'] * linf) / edl if edl else None,
                     'summary_reported': d.get('summary'),
                     'prefix_8192': prefix(8192), 'prefix_4096': prefix(4096),
                     'cap_hits': sum(1 for r in rows[1:] if r['steps'] == r['max_steps']),
                     'gpu_secs': sum((r['secs'] or 0) for r in rows[1:]),
                     'train_tokens': sum((r['train_tokens'] or 0) for r in rows[1:]),
                     'train_steps': sum((r['steps'] or 0) for r in rows[1:]),
                     'blocks': rows}
        s = res[name]
        print(f"{name:16} {task:4} {a['size']} s{a['seed']} v2={s['v2']!s:5} L={L:12.5g} N={N:10,} Linf={linf:.4f} "
              f"EDL={edl:12.5g} b0share L={s['block0_share_of_L']:.2f} EDL={s['block0_share_of_EDL']:.2f} "
              f"tokmis={len(tok_mismatch)} uni={uni_ok} caps={s['cap_hits']}")
    json.dump(res, open(os.path.join(HERE, 'out', 'b2_recount.json'), 'w'), indent=1)


if __name__ == '__main__':
    {'count': count, 'recount': recount}[sys.argv[1]]()
