#!/usr/bin/env python3
"""Lean-vs-nd_verify agreement for run ds-rendering, and a classification of every disagreement.

The brief makes Lean the checker of record and requires the agreement with `nd_verify` to be reported, on the
grounds that a disagreement is a bug.  It is worth being precise about whose bug.  Acceptance in this run is the
CONJUNCTION (Lean 4.34 on the literal sampled text AND nd_verify on the denoted ND proof), so a disagreement never
produces a counted proof -- but it does say which checker is doing the work.

Reads  artifacts/dsr/<pod>/gate_*.jsonl           per-gate totals written by lean_gate
       artifacts/dsr/<pod>/gate_*.disagree.jsonl  one row per disagreeing (prompt, lean_text, nd, nd_ok, lean_ok)

  python3 dsr_disagree.py
"""
import json, glob, re, collections

ARM = {'dsr-c0': 'C0 lean_seq', 'dsr-r1': 'R1 lean_seq_noprem', 'dsr-r2': 'R2 lean_seq_intro',
       'dsr-r3': 'R3 lean_seq_nofml', 'dsr-r4': 'R4 lean_seq_funbare', 'dsr-s': 'seed sweep (mixed)'}


def nd_lines(nd):
    """'N3 | | F : NEGE N1 N2' -> {'N3': ('F', 'NEGE', ['N1','N2'])}; box bars dropped."""
    out = {}
    for seg in nd.split(' ; '):
        seg = seg.strip()
        if seg == 'QED':
            continue
        m = re.match(r'(N\d+)\s+((?:\| )*)(.*?)\s*:\s*([A-Z]+[0-9]*)\s*(.*)$', seg)
        if m:
            out[m.group(1)] = (m.group(3).strip(), m.group(4), m.group(5).split())
    return out


def classify(r):
    """-> short name of the reason nd_verify rejected a text Lean accepted."""
    d = nd_lines(r['nd'])
    for n, (fml, rule, refs) in d.items():
        # BOTE renders as `nA.elim`.  Sound only for nA : False (False.elim : False -> b).  For nA : ~a Lean
        # resolves the SAME surface text to Not.elim : ~a -> a -> b, which typechecks whenever the goal is `a -> _`.
        if rule == 'BOTE' and refs and d.get(refs[0], ('',))[0] != 'F':
            return 'BOTE cited a non-F line (Not.elim : ~a -> a -> b)'
        # NEGE renders as `nB nA`.  ~A is DEFINITIONALLY A -> False, so nB : ~(A -> False) applied to nA : ~A
        # also typechecks, though it is not the A / ~A pair the ND rule requires.
        if rule == 'NEGE' and len(refs) == 2:
            a, b = d.get(refs[0], ('',))[0], d.get(refs[1], ('',))[0]
            if b != f'( ~ {a} )' and a != f'( ~ {b} )':
                return 'NEGE refs not A/~A (~ unfolds to A -> False)'
    # nd_verify requires every declared premise to be introduced as a PR line; Lean does not care how a premise
    # was obtained.  These proofs are logically valid -- a convention difference, not a soundness hole.
    pre = r['prompt'].split('SEQ')[0].replace('THM', '').strip()
    nprem = 0 if not pre else pre.count(',') + 1
    if len(re.findall(r':\s*PR\b', r['nd'])) < nprem:
        return 'fewer PR lines than the theorem has premises (convention, not soundness)'
    return 'unclassified'


def main():
    tot = collections.Counter()
    checked, dis = collections.Counter(), collections.Counter()
    reasons = collections.Counter()
    for fn in sorted(glob.glob('artifacts/dsr/*/gate_*.jsonl')):
        pod = fn.split('/')[2]
        if fn.endswith('.disagree.jsonl'):
            for l in open(fn):
                r = json.loads(l)
                dis[pod] += 1
                reasons[classify(r)] += 1
            continue
        for l in open(fn):
            r = json.loads(l)
            for k in ('samples', 'parse_fail', 'distinct_checked', 'both_ok', 'nd_ok_lean_rej', 'nd_rej_lean_ok',
                      'both_rej'):
                tot[k] += r.get(k, 0)
            checked[pod] += r['distinct_checked']

    n = tot['distinct_checked']
    d = tot['nd_ok_lean_rej'] + tot['nd_rej_lean_ok']
    print(f"samples drawn            {tot['samples']:>10,}")
    print(f"outside strict grammar   {tot['parse_fail']:>10,}")
    print(f"checked by BOTH          {n:>10,}")
    print(f"accepted by both (counted){tot['both_ok']:>9,}")
    print(f"rejected by both         {tot['both_rej']:>10,}")
    print()
    print(f"nd_verify accepts, Lean rejects   {tot['nd_ok_lean_rej']:>6,}")
    print(f"Lean accepts, nd_verify rejects   {tot['nd_rej_lean_ok']:>6,}")
    print(f"agreement                         {100 * (n - d) / max(n, 1):.4f}%")
    print()
    print('disagreements by cause:')
    for k, v in reasons.most_common():
        print(f'  {v:4d}  ({100 * v / max(sum(reasons.values()), 1):5.1f}%)  {k}')
    print()
    print(f"{'arm':22} {'checked':>10} {'Lean-only':>10} {'per 100k':>9}")
    for p in sorted(checked, key=lambda p: 1e5 * dis[p] / max(checked[p], 1)):
        print(f'{ARM.get(p, p):22} {checked[p]:10,} {dis[p]:10d} {1e5 * dis[p] / max(checked[p], 1):9.1f}')


if __name__ == '__main__':
    main()
