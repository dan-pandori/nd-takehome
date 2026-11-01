#!/usr/bin/env python3
"""Reviewer (coe-dose01): k 256 reads on read1054 (base plain x0, base guided g0, r16 plain x0, knockout s1 r32 plain x0)
and the p2 held-out greedy (5,000).  Own counting from the per-theorem rows:
  strict held-out solved = strict members (common.strict_members) with >= 1 accepted attempt;
  family acquired = >= 50 % of the family's strict members solved;
  cut-offs per stratum = attempts whose failure reason is an action truncation / step cap / eof, over attempts.
textbook72 rows are counted as a stratum only; no statement is printed."""
import collections, json, os, sys
sys.path.insert(0, '/home/dan/work/coe-dose01/review_cd01')
from common import BIG, REPO, jl, strict_members

SM = strict_members()
FAMS = collections.Counter(SM.values())
CUT = ('truncat', 'step cap', 'step_cap', 'eof', 'max_new', 'too long')


def reasons_list(x):
    r = x.get('reasons')
    if isinstance(r, dict):
        return [k for k, v in r.items() for _ in range(v)]
    return r or []


def plain(fn):
    rows = list(jl(fn))
    names = {x['name'] for x in rows}
    solved = {x['name'] for x in rows if x['n_ok'] > 0}
    strict_solved = sorted(n for n in SM if n in solved)
    fam = collections.Counter(SM[n] for n in strict_solved)
    acq = sorted(f for f in FAMS if fam[f] / FAMS[f] >= 0.5)
    strata = collections.defaultdict(lambda: [0, 0])          # stratum -> [cut, tried]
    tried_ok = collections.defaultdict(lambda: [0, 0])
    for x in rows:
        st = 'strict106' if x['name'] in SM else 'tb72' if x['name'].startswith('textbook_') else 'other'
        cut = sum(1 for r in reasons_list(x) if any(c in r for c in CUT))
        for s in (st, 'all'):
            strata[s][0] += cut; strata[s][1] += x['n_tried']
            tried_ok[s][0] += x['n_ok']; tried_ok[s][1] += x['n_tried']
        if x['name'] in SM:
            fs = 'fam:' + SM[x['name']]
            strata[fs][0] += cut; strata[fs][1] += x['n_tried']
    n_tried = collections.Counter(x['n_tried'] for x in rows)
    return dict(file=fn, n_rows=len(rows), strict_in_read=sum(1 for n in SM if n in names), n_tried_hist=dict(n_tried),
                strict_solved=len(strict_solved), strict_solved_names=strict_solved, by_family={f: f'{fam[f]}/{FAMS[f]}' for f in FAMS},
                families_acquired=acq, solved_all=len(solved), tb72_solved=sum(1 for n in solved if n.startswith('textbook_')),
                cutoff={s: (c, t, round(c / t, 5) if t else None) for s, (c, t) in sorted(strata.items())},
                sample_acc={s: round(a / b, 5) for s, (a, b) in tried_ok.items()})


def guided(fn):
    rows = list(jl(fn))
    solved = {x['name'] for x in rows if x['n_ok'] > 0}
    strict_solved = sorted(n for n in SM if n in solved)
    fam = collections.Counter(SM[n] for n in strict_solved)
    acq = sorted(f for f in FAMS if fam[f] / FAMS[f] >= 0.5)
    st = collections.Counter(s for x in rows for s in x['status'])
    ks = collections.Counter(x['k'] for x in rows)
    return dict(file=fn, n_rows=len(rows), k_hist=dict(ks), strict_solved=len(strict_solved), by_family={f: f'{fam[f]}/{FAMS[f]}' for f in FAMS},
                families_acquired=acq, solved_all=len(solved), tb72_solved=sum(1 for n in solved if n.startswith('textbook_')),
                status=dict(st))


def greedy(fn):
    rows = list(jl(fn))
    return dict(file=fn, n=len(rows), solved=sum(1 for x in rows if x['n_ok'] > 0), rate=sum(1 for x in rows if x['n_ok'] > 0) / len(rows),
                n_tried=dict(collections.Counter(x['n_tried'] for x in rows)))


def main():
    out = {}
    for S in (0, 1, 2):
        out[f'dose01_s{S}'] = dict(base_x0=plain(f'{BIG}/reads/pend_dose01_s{S}_x0.jsonl.gz'),
                                   base_g0=guided(f'{BIG}/reads/pend_dose01_s{S}_g0.rows.jsonl.gz'),
                                   r16_x0=plain(f'{BIG}/reads/r16_dose01_s{S}_x0.jsonl.gz'),
                                   heldout_p2=greedy(f'{BIG}/reads/heldout_dose01_s{S}.jsonl'))
    out['ko_s1'] = dict(r32_x0=plain(f'{BIG}/reads/r32_ko_s1_x0.jsonl.gz'))
    json.dump(out, open(f'{REPO}/review_cd01/out/reads.json', 'w'), indent=1)
    for k, v in out.items():
        for rd, o in v.items():
            if rd == 'heldout_p2':
                print(f"{k} {rd}: {o['solved']}/{o['n']} = {o['rate']:.4f} (n_tried {o['n_tried']})")
                continue
            extra = ''
            if 'cutoff' in o:
                extra = f"; cut-offs strict106 {o['cutoff'].get('strict106')}, all {o['cutoff'].get('all')}, tb72 {o['cutoff'].get('tb72')}, max family " + \
                        str(max(((s, c) for s, c in o['cutoff'].items() if s.startswith('fam:')), key=lambda z: z[1][2] or 0))
            print(f"{k} {rd}: strict solved {o['strict_solved']}/106 {o['by_family']} acquired {o['families_acquired']}; all solved {o['solved_all']}/{o['n_rows']}, tb72 {o['tb72_solved']}{extra}")


if __name__ == '__main__':
    main()
