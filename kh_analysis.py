#!/usr/bin/env python3
"""cap-horizon analysis: one row per arm x seed, re-derived from the pulled raw files.

  python3 kh_analysis.py --out artifacts/kh/summary.json

Every quantity is recomputed here from the coverage / ladder record files -- nothing is copied from
another run's write-up -- and TERM SIZE (formula nodes over the pruned proof, kh_size.py) is
reported beside every line count, for the inherited arms too.

Arms: K6 (cap 6) and K8flat (cap 8) are INHERITED (ds-composition C0 and A3, files under
artifacts/dsc_inherited/, pulled from the bucket by kh_pull_inherited.sh); K8add, K10, K12, K14 are
this run's (artifacts/kh/).

MODEL LABEL carried on every row: 3,214,336-parameter from-scratch GPT (4 layers, d 256, 8 heads),
`lean_seq` Lean surface form, Stage-1 6,000 steps bs 128 at the arm's cap.
"""
import argparse, collections, glob, json, os, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kh_size import term_size

PARAMS = 3214336
ARMS = {
    # arm    cap  size     dir                       tag   ckpt template                         training set
    'K6':     (6,  155000, 'artifacts/dsc_inherited', 'c0', 'ckpts/lf/stage1_a1_seq_s{s}.pt',     'data/p2/train_depth3_f0_a1.jsonl (ds-composition C0 = lean-format a1; flat 31,000 x lengths 2-6)'),
    'K8flat': (8,  155000, 'artifacts/dsc_inherited', 'a3', 'ckpts/dsc/stage1_a3_s{s}.pt',        'data/dsc/train_a3.jsonl.gz (ds-composition A3; flat 22,142/22,143 x lengths 2-8)'),
    'K8add':  (8,  217000, 'artifacts/kh',            'k8add', 'ckpts/kh/stage1_k8add_s{s}.pt',   'data/kh/train_k8add.jsonl.gz (C0s exact bins 2-6 PLUS 31,000 each at 7 and 8)'),
    'K10':    (10, 155000, 'artifacts/kh',            'k10', 'ckpts/kh/stage1_k10_s{s}.pt',       'data/kh/train_k10.jsonl.gz (flat over lengths 2-10)'),
    'K12':    (12, 155000, 'artifacts/kh',            'k12', 'ckpts/kh/stage1_k12_s{s}.pt',       'data/kh/train_k12.jsonl.gz (flat over lengths 2-12)'),
    'K14':    (14, 155000, 'artifacts/kh',            'k14', 'ckpts/kh/stage1_k14_s{s}.pt',       'data/kh/train_k14.jsonl.gz (flat over lengths 2-14)'),
}
TRANSFER = 'data/ladder/transfer.jsonl'


def lstar(solved_names, labels):
    """L* = max L with >= 5 solved theorems at L_true >= L (ladder_analysis.py's definition).
    NOTE the pool censors this at 14: transfer.jsonl has 23 theorems at L_true >= 13 and 10 at >= 14."""
    ge = {}
    for L in range(2, 20):
        ge[L] = sum(1 for n in solved_names if labels.get(n, 0) >= L)
    return max([L for L, c in ge.items() if c >= 5], default=0), ge


EXPECTED_N = {'redreq': 300, 'd3req': 300}


def cov_row(fn):
    """Coverage file -> solved, max pruned length, accepted-proof counts at >= 8/10/12 lines, term sizes, strata."""
    if not os.path.exists(fn):
        return None
    n_thm = solved = 0
    maxp = 0
    ge = collections.Counter()
    strata = collections.defaultdict(lambda: [0, 0])          # min_lines_ub -> [solved, n]
    samples = parse_fail = 0
    ts_of_longest = None
    pruned_hist = collections.Counter()
    ts_by_len = collections.defaultdict(list)
    longest_proof = None
    n_distinct_accepted = 0
    for l in open(fn):
        r = json.loads(l)
        n_thm += 1
        samples += r['n_tried']
        parse_fail += r['n_parse_fail']
        st = r.get('min_lines_ub')
        strata[str(st)][1] += 1
        hit = r['first_hit'] is not None
        if hit:
            solved += 1
            strata[str(st)][0] += 1
        for p in r['proofs']:
            n_distinct_accepted += 1
            pl = p['pruned']
            pruned_hist[pl] += 1
            for T in (8, 10, 12, 14):
                if pl >= T:
                    ge[T] += 1
            t = term_size(p['proof'])
            if t:
                ts_by_len[pl].append(t[1])
            if pl > maxp:
                maxp = pl
                ts_of_longest = t[1] if t else None
                longest_proof = {'name': r['name'], 'thm': r.get('thm'), 'pruned': pl, 'written': p['written'],
                                 'term_size': ts_of_longest, 'proof': p['proof']}
    allts = [v for vs in ts_by_len.values() for v in vs]
    exp = next((v for k, v in EXPECTED_N.items() if k in fn), None)
    if exp is not None and n_thm < exp:
        # a coverage file is written one theorem at a time and is resumable, so a file pulled while
        # the job is still running is a PARTIAL file.  Never report it as a result.
        return {'file': fn, 'theorems': n_thm, 'expected': exp, 'status': 'INCOMPLETE'}
    return {'file': fn, 'theorems': n_thm, 'solved': solved, 'max_pruned_len': maxp,
            'accepted_proofs_ge8': ge[8], 'ge10': ge[10], 'ge12': ge[12], 'ge14': ge[14],
            'distinct_accepted_proofs': n_distinct_accepted,
            'pruned_hist': dict(sorted(pruned_hist.items())),
            'term_size_of_longest': ts_of_longest,
            'mean_term_size': round(statistics.mean(allts), 2) if allts else None,
            'max_term_size': max(allts) if allts else None,
            'term_size_by_pruned_len': {str(L): {'mean': round(statistics.mean(v), 1), 'max': max(v), 'n': len(v)} for L, v in sorted(ts_by_len.items())},
            'strata_solved': {k: v for k, v in sorted(strata.items())},
            'samples': samples, 'parse_fail': parse_fail,
            'parse_fail_rate': round(parse_fail / samples, 6) if samples else None,
            'longest_proof': longest_proof}


def ladder_row(d, labels):
    """Ladder directory -> transfer solved, L*, per-bin solved, max pruned length, term sizes."""
    f8 = f'{d}/found_transfer_8.jsonl'
    if not os.path.exists(f8):
        rs = sorted(glob.glob(f'{d}/round_*.json'), key=lambda x: int(x.split('_')[-1][:-5]))
        return {'dir': d, 'status': 'incomplete', 'rounds_present': len(rs)} if rs else None
    solved = set()
    maxp = 0
    ts, longest = [], None
    per_bin = collections.Counter()
    for l in open(f8):
        r = json.loads(l)
        solved.add(r['name'])
        t = term_size(r['proof'])
        if t:
            ts.append(t[1])
        if r['pruned'] > maxp:
            maxp = r['pruned']
            longest = {'name': r['name'], 'L_true': r.get('L_true'), 'pruned': r['pruned'], 'term_size': t[1] if t else None}
    for n in solved:
        per_bin[labels.get(n, 0)] += 1
    ls, ge = lstar(solved, labels)
    return {'dir': d, 'transfer_solved': len(solved), 'transfer_n': len(labels), 'lstar': ls,
            'ge_L_true': {str(L): ge[L] for L in range(7, 15)},
            'solved_by_L_true': {str(L): per_bin[L] for L in sorted(per_bin)},
            'max_pruned_len': maxp, 'longest': longest,
            'mean_term_size': round(statistics.mean(ts), 2) if ts else None,
            'max_term_size': max(ts) if ts else None,
            'lstar_censored_at': 14}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='artifacts/kh/summary.json')
    a = ap.parse_args()
    labels = {}
    for l in open(TRANSFER):
        r = json.loads(l)
        labels[r['name']] = r['L_true']
    rows = []
    for arm, (cap, size, D, tag, ck, tset) in ARMS.items():
        for s in (0, 1):
            row = {'arm': arm, 'cap': cap, 'set_size': size, 'stage1_seed': s,
                   'model': {'ckpt': ck.format(s=s), 'params': PARAMS, 'arch': '4 layers, d 256, 8 heads',
                             'format': 'lean_seq', 'from_scratch': True, 'train_set': tset,
                             'stage1': '6,000 steps, bs 128, --cap %d' % cap},
                   'inherited': D.endswith('dsc_inherited')}
            hf = f'{D}/heldout_{tag}_s{s}.json'
            if os.path.exists(hf):
                h = json.load(open(hf))
                row['heldout'] = h
            for pool in ('redreq', 'd3req'):
                row[pool] = cov_row(f'{D}/cov_{tag}_s{s}_{pool}.s0.jsonl')
            if s == 0:
                for k, key in (('T1', 'ladder_T1'), ('frozen', 'ladder_frozen')):
                    row[key] = ladder_row(f'{D}/la_{k}_{tag}_s0', labels)
            rows.append(row)
    # max accepted pruned length ANYWHERE for this arm x seed, and per pool -- the uncensored
    # readout.  ds-composition's reviewer (B5) found cap-6 models write accepted 8-11-line proofs on
    # the depth-3 pools while stopping dead at 7 lines on the required-reductio pool, so a
    # single "max accepted length" for an arm would be meaningless: it is reported PER POOL.
    for row in rows:
        per_pool = {}
        for pool in ('redreq', 'd3req'):
            v = (row.get(pool) or {}).get('max_pruned_len')
            if v:
                per_pool[pool] = v
        for key, nm in (('ladder_T1', 'ladder_T1_transfer'), ('ladder_frozen', 'ladder_frozen_transfer')):
            v = (row.get(key) or {}).get('max_pruned_len')
            if v:
                per_pool[nm] = v
        row['max_pruned_len_by_pool'] = per_pool
        row['max_pruned_len_anywhere'] = max(per_pool.values()) if per_pool else None
        row['max_minus_cap_by_pool'] = {k: v - row['cap'] for k, v in per_pool.items()}

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump({'transfer_L_true_hist': dict(collections.Counter(labels.values())),
               'note': 'L* is hard-censored at 14 by this pool (23 theorems at L_true >= 13, 10 at >= 14)',
               'rows': rows}, open(a.out, 'w'), indent=1)
    # compact console table
    print(f'{"arm":8s} {"cap":>3s} {"seed":>4s} {"heldout":>8s} {"redreq":>7s} {"maxlen":>6s} {"ge8":>5s} {"ge10":>5s} {"ge12":>5s} {"d3req":>6s} {"T1 L*":>6s} {"fr L*":>6s} {"T1 solv":>8s} {"fr solv":>8s}')
    for r in rows:
        h = r.get('heldout') or {}
        acc = h.get('rate')
        rr = r.get('redreq') or {}
        dd = r.get('d3req') or {}
        t1 = r.get('ladder_T1') or {}
        fr = r.get('ladder_frozen') or {}
        f = lambda x, w=6: ('' if x is None else str(x)).rjust(w)
        print(f'{r["arm"]:8s} {r["cap"]:3d} {r["stage1_seed"]:4d} {f(round(acc,4) if isinstance(acc,float) else acc,8)} '
              f'{f(rr.get("solved"),7)} {f(rr.get("max_pruned_len"))} {f(rr.get("accepted_proofs_ge8"),5)} {f(rr.get("ge10"),5)} {f(rr.get("ge12"),5)} '
              f'{f(dd.get("solved"),6)} {f(t1.get("lstar"))} {f(fr.get("lstar"))} {f(t1.get("transfer_solved"),8)} {f(fr.get("transfer_solved"),8)}')


if __name__ == '__main__':
    main()
