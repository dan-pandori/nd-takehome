#!/usr/bin/env python3
"""Reviewer's independent recount for ladder-A (phase 1). Nothing here imports the executor's analysis code;
only `nd_verify` (the exam's verifier) is imported. Own normaliser, own line counter, own renaming-class key,
own L*, own Wilson interval.

  python3 rv_recount.py            -> review_out/recount.json + printed tables
"""
import json, os, sys, math, collections, itertools, re, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nd_verify import verify_text

A = 'artifacts/ladder'
ARMS = {  # arm -> list of run dirs whose transfer proofs are unioned (T6: two siblings)
    'frozen_s0': ['la_frozen_s0'], 'frozen_s1': ['la_frozen_s1'],
    'T1_s0': ['la_T1_s0'], 'T1_s1': ['la_T1_s1'], 'T2_s0': ['la_T2_s0'], 'T2_s1': ['la_T2_s1'],
    'T3_s0': ['la_T3_s0'], 'T3_s1': ['la_T3_s1'], 'T4_s0': ['la_T4_s0'], 'T4_s1': ['la_T4_s1'],
    'T5_s0': ['la_T5_s0'], 'T5_s1': ['la_T5_s1'],
    'T6_s0': ['la_T6_s0a', 'la_T6_s0b'], 'T6_s1': ['la_T6_s1a', 'la_T6_s1b'],
}
ROUNDS = 8


def rd(fn):
    with open(fn) as f:
        return [json.loads(l) for l in f if l.strip()]


# ---------- own start-index normaliser: split into lines on ';', read the first label, shift every N<int> token
def rv_norm(proof):
    toks = proof.split()
    first = next((t for t in toks if len(t) > 1 and t[0] == 'N' and t[1:].isdigit()), None)
    if first is None:
        return ' '.join(toks)
    off = int(first[1:]) - 1
    return ' '.join('N%d' % (int(t[1:]) - off) if (len(t) > 1 and t[0] == 'N' and t[1:].isdigit()) else t for t in toks)


def rv_nlines(proof):
    """lines = ';'-terminated segments before QED"""
    body = proof.split('QED')[0]
    return sum(1 for seg in body.split(';') if seg.strip())


def rv_depth(proof):
    body = proof.split('QED')[0]
    return max((seg.split().count('|') for seg in body.split(';') if seg.strip()), default=0)


# ---------- own renaming class: min over all injective renamings of the atoms used (24 perms), premise order kept;
# and a stronger class that also sorts premises.
ATOMS = 'PQRS'


def rv_split(thm):
    left, right = thm.split('|-')
    prem, cur, depth = [], [], 0
    for t in left.split():
        if t == ',' and depth == 0:
            prem.append(' '.join(cur)); cur = []
            continue
        depth += (t == '(') - (t == ')')
        cur.append(t)
    if cur:
        prem.append(' '.join(cur))
    return prem, ' '.join(right.split())


def rv_key(thm, sort_prem=False):
    prem, concl = rv_split(thm)
    best = None
    for perm in itertools.permutations(ATOMS):
        m = dict(zip(ATOMS, perm))
        ren = lambda s: ' '.join(m.get(t, t) for t in s.split())
        ps = [ren(p) for p in prem]
        if sort_prem:
            ps = sorted(ps)
        k = ' , '.join(ps) + ' |- ' + ren(concl)
        if best is None or k < best:
            best = k
    return best


def prompt_to_thm(prompt):
    assert prompt.startswith('THM') and prompt.endswith('PRF'), prompt
    body = prompt[3:-3].strip()
    l, r = body.split('SEQ')
    return (l.strip() + ' |- ' + r.strip()).strip()


def wilson(k, n, z=1.959964):
    if n == 0:
        return (0.0, 0.0)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def lstar(solved_L, need=5):
    best = 0
    for L in range(1, 30):
        if sum(1 for x in solved_L if x >= L) >= need:
            best = L
    return best


def main():
    out = {}
    transfer = rd('data/ladder/transfer.jsonl'); targets = rd('data/ladder/rl_targets.jsonl')
    T = {r['name']: r for r in transfer}; G = {r['name']: r for r in targets}
    out['pool'] = {'transfer_n': len(transfer), 'targets_n': len(targets),
                   'transfer_bins': dict(sorted(collections.Counter(r['L_true'] for r in transfer).items())),
                   'targets_bins': dict(sorted(collections.Counter(r['L_true'] for r in targets).items()))}
    assert all(r['L_true'] == r['n_lines'] for r in transfer + targets)
    assert all(prompt_to_thm(r['prompt']) == ' '.join(r['thm'].split()) for r in transfer + targets)
    vcache = {}

    def check(prompt, proof):
        k = (prompt, proof)
        if k not in vcache:
            ok, reason, nl = verify_text(prompt + ' ' + proof)
            vcache[k] = (ok, nl)
        return vcache[k]

    for arm, dirs in ARMS.items():
        res = {}
        for pool, recs, fnpat in (('transfer', T, 'found_transfer_%d.jsonl'), ('targets', G, 'found_%d.jsonl')):
            per_round = {}
            for R in range(1, ROUNDS + 1):
                proofs = collections.defaultdict(set)    # name -> set of my-normalised proofs
                n_raw = n_bad = n_short = n_prompt_mismatch = 0
                short = []
                for d in dirs:
                    fn = f'{A}/{d}/' + fnpat % R
                    if not os.path.exists(fn):
                        res.setdefault('missing', []).append(fn); continue
                    for x in rd(fn):
                        n_raw += 1
                        rec = recs.get(x['name'])
                        if rec is None or rec['prompt'] != x['prompt']:
                            n_prompt_mismatch += 1; continue
                        if x['round'] > R:
                            n_bad += 1; continue
                        if R == ROUNDS:                       # verify every counted proof at the final round
                            ok, nl = check(rec['prompt'], x['proof'])
                            if not ok:
                                n_bad += 1; continue
                            assert nl == rv_nlines(x['proof']), (nl, x['proof'])
                            if nl < rec['L_true']:
                                n_short += 1; short.append((x['name'], rec['L_true'], nl))
                        proofs[x['name']].add(rv_norm(x['proof']))
                solved_L = [recs[n]['L_true'] for n in proofs]
                bins = {}
                tot = collections.Counter(r['L_true'] for r in recs.values())
                sol = collections.Counter(solved_L)
                for L in sorted(tot):
                    lo, hi = wilson(sol[L], tot[L])
                    bins[L] = {'solved': sol[L], 'n': tot[L], 'rate': sol[L] / tot[L], 'ci': [lo, hi]}
                per_round[R] = {'solved': len(proofs), 'distinct_proofs': sum(len(v) for v in proofs.values()), 'lstar': lstar(solved_L),
                                'ge': {L: sum(1 for x in solved_L if x >= L) for L in range(7, 15)}, 'bins': bins,
                                'n_raw': n_raw, 'n_bad': n_bad, 'n_prompt_mismatch': n_prompt_mismatch}
                if R == ROUNDS:
                    per_round[R]['n_shorter_than_L_true'] = n_short; per_round[R]['short_examples'] = short[:10]
                    per_round[R]['n_verified'] = n_raw - n_prompt_mismatch
                    # by source / schema
                    bysrc = collections.defaultdict(lambda: [0, 0])
                    for r in recs.values():
                        key = r['source'] if r['source'] != 'textbook' else 'textbook'
                        bysrc[key][1] += 1; bysrc[key][0] += (r['name'] in proofs)
                    per_round[R]['by_source'] = {k: v for k, v in bysrc.items()}
                    bysch = collections.defaultdict(lambda: [0, 0])
                    for r in recs.values():
                        if r.get('schema'):
                            bysch[r['schema']][1] += 1; bysch[r['schema']][0] += (r['name'] in proofs)
                    per_round[R]['by_schema'] = dict(bysch)
                    per_round[R]['max_depth_hist'] = dict(sorted(collections.Counter(rv_depth(p) for v in proofs.values() for p in v).items()))
                    per_round[R]['solved_names'] = sorted(proofs)
            res[pool] = per_round
        # attempts: targets from alloc_8 (tried), transfer = rounds*k per dir
        att = {}
        for d in dirs:
            al = json.load(open(f'{A}/{d}/alloc_{ROUNDS}.json'))
            tr = al['tried']
            att[d] = {'targets_total': sum(tr.values()), 'per_target_mean': sum(tr.values()) / len(targets),
                      'min': min(tr.get(t['name'], 0) for t in targets), 'max': max(tr.values()),
                      'k': json.load(open(f'{A}/{d}/args.json'))['k']}
            ks = [sum(json.load(open(f'{A}/{d}/alloc_{r}.json'))['k'].values()) for r in range(1, ROUNDS + 1)]
            att[d]['per_round_total'] = ks
        res['attempts'] = att
        out[arm] = res
        f8 = res['transfer'][8]; g8 = res['targets'][8]
        print(f"{arm:10s} transfer: solved {f8['solved']:4d} L*={f8['lstar']:2d} ge={ {L: f8['ge'][L] for L in (7,8,9,10,11,12)} } proofs={f8['distinct_proofs']} bad={f8['n_bad']} short={f8['n_shorter_than_L_true']}"
              f" | targets: solved {g8['solved']:4d} L*={g8['lstar']:2d} ge={ {L: g8['ge'][L] for L in (8,9,10,11,12)} } proofs={g8['distinct_proofs']} bad={g8['n_bad']} short={g8['n_shorter_than_L_true']}", flush=True)
    os.makedirs('review_out', exist_ok=True)
    json.dump(out, open('review_out/recount.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
