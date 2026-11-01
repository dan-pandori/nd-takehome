#!/usr/bin/env python3
"""coe-dose01: offline Lean re-check of the held-out proofs that count toward the bar.  For each ladder, the proof of
each strict sigma-covered held-out member from the round that first solved it (the first such row in
artifacts/coe/rounds/heldout_proofs_<ladder>.jsonl.gz, written by coe/d01_heldout_proofs.py from found_transfer_<last>):
  * accepted?  lean_judge.judge_many (nd2lean + Lean 4 core, as create-or-elicit's re-check) -- must all be accepted;
  * negative control: the same proof against the goal-negated theorem ( ~ G ) -- must all be rejected;
  * term size and ND lines: nd2lean.translate + lean_check.check (Lean elaborated-term size).
VPS: LEAN_GATE_WORKERS=2, at most 2 Lean processes.  Writes a JSON report and prints a table.
  LEAN_GATE_WORKERS=2 python3 coe/d01_lean_recheck.py --out artifacts/coe-dose01/lean_recheck.json"""
import argparse, gzip, json, os, statistics as st, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import lean_judge, lean_check, nd2lean


def negate(prompt):
    body = prompt.split('THM', 1)[1].rsplit('PRF', 1)[0]
    prem, concl = (' ' + body + ' ').split(' SEQ ')
    return f"THM {prem.strip()} SEQ ( ~ {concl.strip()} ) PRF".replace('THM  SEQ', 'THM SEQ')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ladders', nargs='+', default=['la_dose01_s0', 'la_dose01_s1', 'la_dose01_s2', 'la_ko_s1_r32'])
    ap.add_argument('--dir', default='artifacts/coe/rounds')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    rep = {}
    for lad in a.ladders:
        fn = os.path.join(a.dir, f'heldout_proofs_{lad}.jsonl.gz')
        if not os.path.exists(fn):
            print(f'{lad}: missing {fn}'); continue
        rows = [json.loads(l) for l in gzip.open(fn, 'rt')]
        first = {}
        for r in rows:                      # rows keep the ladder's order; keep the earliest round's first proof per member
            if r['name'] not in first or r['round'] < first[r['name']]['round']:
                first[r['name']] = r
        recs = sorted(first.values(), key=lambda r: (r['round'], r['name']))
        pos = lean_judge.judge_many([(r['prompt'], r['proof']) for r in recs])
        neg = lean_judge.judge_many([(negate(r['prompt']), r['proof']) for r in recs])
        srcs, idx = [], []
        for i, r in enumerate(recs):
            try:
                srcs.append(nd2lean.translate(r['prompt'], r['proof'], require_all_pr=False)); idx.append(i)
            except Exception:
                pass
        sizes = [None] * len(recs)
        if srcs:
            res, _, _ = lean_check.check(srcs, workers=2)
            for i, x in zip(idx, res):
                sizes[i] = x['size'] if x['ok'] else None
        out = []
        for r, p, n, sz in zip(recs, pos, neg, sizes):
            out.append({'name': r['name'], 'family': r['family'], 'round': r['round'], 'accepted': bool(p[0]),
                        'reason': '' if p[0] else str(p[1])[:200], 'goal_negated_rejected': not n[0],
                        'nd_lines': r['written'], 'pruned_lines': r['pruned'], 'term_size': sz})
        ok = sum(o['accepted'] for o in out); rej = sum(o['goal_negated_rejected'] for o in out)
        tz = [o['term_size'] for o in out if o['term_size'] is not None]
        rep[lad] = {'file': fn, 'members': len(out), 'accepted': ok, 'goal_negated_rejected': rej,
                    'median_term_size': st.median(tz) if tz else None, 'median_nd_lines': st.median(o['nd_lines'] for o in out) if out else None,
                    'rows': out}
        print(f"{lad}: {len(out)} members (first-solving proofs) — Lean accepts {ok}, goal-negated rejected {rej}; "
              f"median term size {rep[lad]['median_term_size']}, median ND lines {rep[lad]['median_nd_lines']}")
    rep['judge_stats'] = lean_judge.stats()
    json.dump(rep, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
