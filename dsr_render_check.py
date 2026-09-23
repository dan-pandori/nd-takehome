#!/usr/bin/env python3
"""Render check for the ds-rendering variants (proposal 10's protocol).

For each mode:
  (1) round-trip: N records render -> encode -> shift_abs -> decode -> the IDENTICAL ND proof string;
  (2) Lean accepts M literal rendered texts (statement + tactic block), through lean_gate.lean_check;
  (3) K theorem-swapped negatives are rejected by Lean (the text of record i under the statement of record j);
  (4) token counts per proof, and the vocabulary size.

  python dsr_render_check.py --data data/p2/train_depth3_f0_a1.jsonl --n 3000 --lean 1000 --neg 300 --out artifacts/dsr/render_check.json
"""
import argparse, json, os, random, sys, time, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lean_tok import LeanTokenizer, MODES
from nd_verify import verify_text

ALL = ['lean_seq', 'lean_seq_noprem', 'lean_seq_nofml', 'lean_seq_intro']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', default='data/p2/train_depth3_f0_a1.jsonl')
    ap.add_argument('--n', type=int, default=3000)
    ap.add_argument('--lean', type=int, default=1000)
    ap.add_argument('--neg', type=int, default=300)
    ap.add_argument('--modes', default=','.join(ALL))
    ap.add_argument('--out', default='artifacts/dsr/render_check.json')
    a = ap.parse_args()
    rng = random.Random(0)
    recs = []
    with open(a.data) as f:
        for i, l in enumerate(f):
            if i >= 200000:
                break
            if l.strip():
                recs.append(json.loads(l))
    sample = rng.sample(recs, min(a.n, len(recs)))
    print(f'{len(recs)} records read, {len(sample)} sampled', flush=True)
    from lean_gate import lean_check
    out = {'data': a.data, 'n_round_trip': len(sample), 'n_lean': a.lean, 'n_neg': a.neg, 'modes': {}}
    for mode in a.modes.split(','):
        t0 = time.time()
        tok = LeanTokenizer(mode)
        r = {'vocab_size': tok.vocab_size, 'round_trip_ok': 0, 'round_trip_fail': [], 'ntok': [], 'nd_lines': [], 'text_haves': []}
        srng = random.Random(1)
        texts = []
        for k, rec in enumerate(sample):
            ids = tok.encode_proof(rec['proof'])
            ids = tok.shift_abs(ids, srng)
            got = tok.decode(ids, rec['prompt'])
            if got == rec['proof']:
                r['round_trip_ok'] += 1
            elif len(r['round_trip_fail']) < 5:
                r['round_trip_fail'].append({'prompt': rec['prompt'], 'want': rec['proof'], 'got': got, 'text': tok.last_text})
            r['ntok'].append(len(ids))
            r['nd_lines'].append(rec['n_lines'])
            r['text_haves'].append(tok.last_text.split().count('have'))
            texts.append((tok.statement(rec['prompt']), tok.last_text))
        r['mean_tokens'] = sum(r['ntok']) / len(r['ntok'])
        r['len_hist_nd'] = dict(sorted(collections.Counter(r['nd_lines']).items()))
        r['len_hist_text'] = dict(sorted(collections.Counter(r['text_haves']).items()))
        r.pop('ntok'); r.pop('nd_lines'); r.pop('text_haves')
        # (2) Lean on literal texts
        pos = texts[:a.lean]
        ok, wall, cpu = lean_check(pos)
        r['lean_ok'] = sum(ok); r['lean_n'] = len(ok); r['lean_wall_s'] = wall
        r['lean_rejected_examples'] = [{'stmt': pos[i][0], 'text': pos[i][1]} for i, o in enumerate(ok) if not o][:5]
        # (3) theorem-swapped negatives: text of record i under the statement of a different record
        neg = []
        for i in range(a.neg):
            j = (i + 7) % len(texts)
            if texts[i][0] != texts[j][0]:
                neg.append((texts[j][0], texts[i][1]))
        nok, _, _ = lean_check(neg)
        r['neg_n'] = len(nok); r['neg_accepted'] = sum(nok)
        r['secs'] = time.time() - t0
        out['modes'][mode] = r
        print(f'{mode}: vocab {r["vocab_size"]} round-trip {r["round_trip_ok"]}/{len(sample)} '
              f'lean {r["lean_ok"]}/{r["lean_n"]} neg-accepted {r["neg_accepted"]}/{r["neg_n"]} '
              f'mean tokens {r["mean_tokens"]:.1f} ({r["secs"]:.0f}s)', flush=True)
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    json.dump(out, open(a.out, 'w'), indent=1, ensure_ascii=False)
    print('wrote', a.out)


if __name__ == '__main__':
    main()
