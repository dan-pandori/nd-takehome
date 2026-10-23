#!/usr/bin/env python3
"""R2 (reviewer, phase 1): Lean 4 re-check of the stream proofs.
  (a) every distinct stream proof (638 (prompt, ND) pairs over 6 streams x 3 seeds x 256 theorems), rendered by MY
      ND -> Lean translator (rv_core.nd_to_lean);
  (b) the literal sampled texts the streams came from (greedy of each base, greedy of each r8 ladder, first accepted
      k 4 attempt of each base) for the 256 theorems, wrapped as theorems (rv_core.ls_wrap), plus a vocabulary scan;
  (c) negative controls: mutated copies of (a) and (b) must be rejected.
  python3 r2_lean_streams.py -> out/r2_lean_streams.json
"""
import json, os, random, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_core as C

WS = C.WS
R = f'{WS}/artifacts/style_edl/reads'


def main():
    t0 = time.time()
    items = C.jl(os.path.join(C.HERE, 'out', 'r1_lean_items.jsonl'))
    srcs = []
    for i, it in enumerate(items):
        srcs.append(C.nd_to_lean(it['prompt'], C.parse_nd(it['nd']), f'nd{i}'))
    names = [r['name'] for r in C.jl(f'{WS}/data/style_edl/sets/all256.jsonl')]
    tf = {r['name']: r for r in C.jl(f'{WS}/data/kalmar/tf1200_kal_sl.jsonl')}
    lit = []
    for s in (0, 1, 2):
        g = {r['name']: r for r in C.jl(f'{R}/base_s{s}__tf1200_greedy.rows.jsonl.gz')}
        r8 = {r['name']: r for r in C.jl(f'{R}/r8_s{s}__tf1200_greedy.rows.jsonl.gz')}
        k4 = {r['name']: r for r in C.jl(f'{R}/base_s{s}__tf1200_plain_k4_seed3.rows.jsonl.gz')}
        for nm in names:
            lit.append((f'greedy_s{s}', tf[nm]['prompt'], g[nm]['text']))
            lit.append((f'r8_s{s}', tf[nm]['prompt'], r8[nm]['text']))
            lit.append((f'k4first_s{s}', tf[nm]['prompt'], next(iter(k4[nm]['accepted']))))
    vocab_bad = [x for x in lit if not C.vocab_ok(x[2]) or C.BAD_TOK.search(x[2])]
    lsrc = [C.ls_wrap(pr, tx, f'ls{i}') for i, (_, pr, tx) in enumerate(lit)]
    # negative controls
    rng = random.Random(7)
    neg = []
    for i in rng.sample(range(len(items)), 120):
        it = items[i]
        L = C.parse_nd(it['nd'])
        prems, concl = C.parse_prompt(it['prompt'])
        # mutation 1: last line claims the negated conclusion
        d, f, r, refs = L[-1]
        L2 = L[:-1] + [(d, ('not', f), r, refs)]
        try:
            neg.append(('nd_concl_neg', C.nd_to_lean(it['prompt'], L2, f'neg{len(neg)}').replace(
                f'theorem neg{len(neg)} (P Q R S : Prop)', f'theorem neg{len(neg)} (P Q R S : Prop)')))
        except C.Bad:
            pass
    for j, i in enumerate(rng.sample(range(len(lit)), 120)):
        tag, pr, tx = lit[i]
        # mutation 2: change the first atom occurrence inside the first have's formula
        m = re.search(r'have n\d+ : (.*?) :=', tx)
        seg = m.group(1)
        k = next((q for q, ch in enumerate(seg) if ch in 'PQRS'), None)
        if k is None:
            continue
        a = seg[k]
        seg2 = seg[:k] + {'P': 'Q', 'Q': 'R', 'R': 'S', 'S': 'P'}[a] + seg[k + 1:]
        tx2 = tx[:m.start(1)] + seg2 + tx[m.end(1):]
        neg.append(('ls_atom_swap', C.ls_wrap(pr, tx2, f'neg{len(neg)}')))
    print(f'checking {len(srcs)} ND renders, {len(lsrc)} literal texts, {len(neg)} negatives', flush=True)
    ra = C.lean_check(srcs, tag='nd')
    print('nd done', time.time() - t0, flush=True)
    rb = C.lean_check(lsrc, tag='ls')
    print('ls done', time.time() - t0, flush=True)
    rc = C.lean_check([s for _, s in neg], tag='neg', chunk=20)
    out = {'nd_distinct': len(srcs), 'nd_accepted': sum(ok for ok, _ in ra),
           'nd_rejected_examples': [(items[i]['src'], e) for i, (ok, e) in enumerate(ra) if not ok][:10],
           'nd_by_stream_accepted': {},
           'literal_texts': len(lsrc), 'literal_accepted': sum(ok for ok, _ in rb),
           'literal_by_source': {}, 'literal_rejected_examples': [(lit[i][0], e) for i, (ok, e) in enumerate(rb) if not ok][:10],
           'literal_vocab_or_forbidden_token': len(vocab_bad),
           'negatives': len(neg), 'negatives_rejected': sum(not ok for ok, _ in rc),
           'negatives_by_kind': {}, 'secs': round(time.time() - t0, 1)}
    for it, (ok, _) in zip(items, ra):
        for s in it['src']:
            a = out['nd_by_stream_accepted'].setdefault(s, [0, 0]); a[0] += ok; a[1] += 1
    for (tag, _, _), (ok, _) in zip(lit, rb):
        a = out['literal_by_source'].setdefault(tag, [0, 0]); a[0] += ok; a[1] += 1
    for (kind, _), (ok, _) in zip(neg, rc):
        a = out['negatives_by_kind'].setdefault(kind, [0, 0]); a[0] += (not ok); a[1] += 1
    json.dump(out, open(os.path.join(C.HERE, 'out', 'r2_lean_streams.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
