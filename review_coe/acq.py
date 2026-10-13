#!/usr/bin/env python3
"""Reviewer recount of every arm's acquisition table from the raw reads (plain state_eval rows and guided rows).

Per read: strict sigma-covered held-out members solved (106 = 105 family + la_transfer_916), per family, families at the
bar (>= 50 % of the family's strict held-out members solved), primary indicator (>= 1 family), and the same on the
original (pre-registered) 178 set and the 123 key-step held-out members.  Plus cut-off fractions per stratum.
Tests (one-sided, full > knockout, r16 x0): Boschloo exact (own implementation, scipy cross-check), per family with Holm,
exact Mann-Whitney (permutation over the 924 splits).  Output: review_coe/out_acq.json + stdout."""
import collections, gzip, itertools, json, math, os, sys, ast
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

RV = C.RV
EV = f'{RV}/artifacts/coe/eval'
FAM = json.load(open(f'{RV}/review_coe/out_families.json'))
HO = {r['name']: r for r in C.rows(f'{RV}/data/ladder/transfer.jsonl')}
R1054 = list(C.rows(f'{RV}/data/coe/read1054.jsonl'))
STRICT = FAM['strict_heldout']; ORIG = FAM['orig_sigma_heldout']; KEY = FAM['keystep_heldout']
FAMS = FAM['classical_families']
famof = {n: HO[n]['schema'] for n in HO}
p2name = {HO[n]['prompt']: n for n in HO}
set_of_prompt = {r['prompt']: r['set'] for r in R1054}
tb_dev = {r['prompt'] for r in C.rows(f'{RV}/data/eval_only/textbook72/textbook_dev.jsonl')}
tb_train = {r['prompt'] for r in C.rows(f'{RV}/data/eval_only/textbook72/textbook_train.jsonl')}


def load_plain(tag):
    p = f'{EV}/{tag}.jsonl.gz'
    if not os.path.exists(p):
        return None
    out = {}
    for r in C.rows(p):
        nt = r['n_tried']; nok = r['n_ok']
        cut = sum(1 for x in (r.get('reasons') or []) if ('truncated' in x or 'step cap' in x))
        assert bool(r['solved']) == (nok > 0), (tag, r['name'])
        assert (nok == 0) or len(r['proofs']) >= 1, (tag, r['name'], 'solved without stored proof')
        out[r['prompt']] = {'ok': nok, 'n': nt, 'cut': cut, 'nproofs': len(r['proofs']), 'nreasons': len(r.get('reasons') or [])}
    return out


def load_guided(tag):
    p = f'{EV}/{tag}.rows.jsonl.gz'
    if not os.path.exists(p):
        return None
    out = {}
    for r in C.rows(p):
        ok = r['ok'] if isinstance(r['ok'], list) else ast.literal_eval(r['ok'])
        nok = int(r['n_ok']); k = int(r['k'])
        assert sum(ok) == nok and len(ok) == k, (tag, r['name'])
        st = r['status'] if isinstance(r['status'], list) else ast.literal_eval(r['status'])
        cut = sum(1 for s in st if ('trunc' in s or 'step' in s or 'max_steps' in s))
        acc = r['accepted'] if isinstance(r['accepted'], dict) else ast.literal_eval(r['accepted'])
        assert (nok == 0) or len(acc) >= 1
        out[r['prompt']] = {'ok': nok, 'n': k, 'cut': cut, 'nproofs': len(acc)}
    return out


def merged(tag_e, tag_h, loader):
    a = loader(tag_e); b = loader(tag_h)
    if a is None or b is None:
        return None
    m = dict(a); m.update(b)
    return m


def summarize(rows):
    res = {}
    for nm, S in (('strict', STRICT), ('orig178', ORIG), ('key123', KEY)):
        miss = [n for n in S if HO[n]['prompt'] not in rows]
        solved = [n for n in S if HO[n]['prompt'] in rows and rows[HO[n]['prompt']]['ok'] > 0]
        per = {}
        for f in FAMS:
            mem = [n for n in S if famof.get(n) == f]
            s = sum(1 for n in mem if n in solved)
            per[f] = (s, len(mem))
        acq = [f for f in FAMS if per[f][1] and per[f][0] >= 0.5 * per[f][1]]
        res[nm] = {'solved': len(solved), 'of': len(S), 'missing': len(miss), 'per_family': per, 'acquired': acq,
                   'gen_solved': [n for n in solved if not famof.get(n)]}
    res['t916'] = rows.get(HO['la_transfer_916']['prompt'], {}).get('ok')
    # strata
    st = collections.defaultdict(lambda: [0, 0, 0, 0])     # solved, theorems, cut, attempts
    for p, v in rows.items():
        s = set_of_prompt.get(p, 'track')
        keys = [s]
        if s == 'tb72':
            keys.append('tb_dev58' if p in tb_dev else ('tb_train14' if p in tb_train else 'tb_other'))
        if p in p2name and p2name[p] in STRICT:
            keys.append('strict')
        for k in keys:
            st[k][0] += v['ok'] > 0; st[k][1] += 1; st[k][2] += v['cut']; st[k][3] += v['n']
    res['strata'] = {k: {'solved': v[0], 'n': v[1], 'cut_frac': v[2] / max(1, v[3])} for k, v in st.items()}
    return res


READS = {}
arms = [('ko', s) for s in range(6)] + [('full', s) for s in range(3, 6)] + [('dose1', s) for s in range(3)]
for arm, s in arms:
    for ck in ('pend', 'r8', 'r16', 'r20', 'r24'):
        for dr in ('x0', 'x1', 'g0'):
            tag = f'{ck}_{arm}_s{s}_{dr}'
            rows = load_guided(tag) if dr == 'g0' else load_plain(tag)
            if rows is not None:
                READS[tag] = summarize(rows)
for s in range(3):
    for ck in ('pend', 'r8', 'r16'):
        for dr in ('x0', 'x1', 'g0'):
            tag = f'{ck}_full_s{s}_{dr}'
            rows = merged(tag + 'e', tag + 'h', load_guided if dr == 'g0' else load_plain)
            if rows is not None:
                READS[tag] = summarize(rows)
print(f'{len(READS)} reads summarised')
print(f'{"read":22s} {"strict/106":>10s} ' + ' '.join(f'{f[:10]:>10s}' for f in FAMS) + '  acquired   | orig178 key123 t916  cut(strict) cut(all-max)')
for tag in sorted(READS, key=lambda t: (t.split('_')[1], int(t.split('_')[2][1:]), ['pend', 'r8', 'r16', 'r20', 'r24'].index(t.split('_')[0]), t.split('_')[3])):
    r = READS[tag]; s = r['strict']
    cutmax = max(v['cut_frac'] for v in r['strata'].values())
    print(f'{tag:22s} {s["solved"]:4d}/{s["of"]:<5d} ' + ' '.join(f'{s["per_family"][f][0]:>4d}/{s["per_family"][f][1]:<5d}' for f in FAMS) +
          f'  {",".join(x[:8] for x in s["acquired"]) or "-":10s} | {r["orig178"]["solved"]:4d} {r["key123"]["solved"]:4d} {str(r["t916"]):>4s}  '
          f'{r["strata"].get("strict", {}).get("cut_frac", 0):.4f} {cutmax:.4f}' + (f' MISSING {s["missing"]}' if s['missing'] else ''))


# ---------------------------------------------------------------- exact tests (own implementations)
def fisher_p_one_sided(x1, n1, x2, n2):
    """P(X1 >= x1 | margins), hypergeometric; H1: p1 > p2."""
    m = x1 + x2; N = n1 + n2
    lo = max(0, m - n2); hi = min(n1, m)
    den = math.comb(N, m)
    return sum(math.comb(n1, k) * math.comb(n2, m - k) for k in range(x1, hi + 1)) / den


def boschloo(x1, n1, x2, n2, grid=2001):
    pobs = fisher_p_one_sided(x1, n1, x2, n2)
    crit = [(a, b) for a in range(n1 + 1) for b in range(n2 + 1) if fisher_p_one_sided(a, n1, b, n2) <= pobs + 1e-12]
    best = 0.0
    for i in range(grid):
        p = i / (grid - 1)
        pr = sum(math.comb(n1, a) * p ** a * (1 - p) ** (n1 - a) * math.comb(n2, b) * p ** b * (1 - p) ** (n2 - b) for a, b in crit)
        best = max(best, pr)
    return best


def mw_exact_greater(xs, ys):
    """exact permutation p-value of U (xs > ys), midrank ties, over all C(n, len(xs)) splits."""
    allv = list(xs) + list(ys); n1 = len(xs)

    def U(a, b):
        return sum((1.0 if u > v else 0.5 if u == v else 0.0) for u in a for v in b)
    u0 = U(xs, ys); cnt = 0; tot = 0
    for idx in itertools.combinations(range(len(allv)), n1):
        a = [allv[i] for i in idx]; b = [allv[i] for i in range(len(allv)) if i not in idx]
        tot += 1; cnt += U(a, b) >= u0 - 1e-9
    return u0, cnt / tot


def table(ck='r16', dr='x0', setname='strict'):
    out = {}
    for arm, seeds in (('full', range(6)), ('ko', range(6)), ('dose1', range(3))):
        for s in seeds:
            tag = f'{ck}_{arm}_s{s}_{dr}'
            if tag in READS:
                out[(arm, s)] = READS[tag][setname]
    return out


RES = {'reads': READS}
for setname in ('strict', 'orig178'):
    T = table('r16', 'x0', setname)
    ind_full = [1 if T[('full', s)]['acquired'] else 0 for s in range(6) if ('full', s) in T]
    ind_ko = [1 if T[('ko', s)]['acquired'] else 0 for s in range(6) if ('ko', s) in T]
    x1, n1, x2, n2 = sum(ind_full), len(ind_full), sum(ind_ko), len(ind_ko)
    pb = boschloo(x1, n1, x2, n2)
    try:
        import scipy.stats as ss
        pbs = ss.boschloo_exact([[x1, n1 - x1], [x2, n2 - x2]], alternative='greater').pvalue
    except Exception as e:
        pbs = str(e)
    print(f'\n[{setname}] r16 x0 primary indicator: full {ind_full} ({x1}/{n1}), knockout {ind_ko} ({x2}/{n2}); '
          f'Boschloo one-sided p = {pb:.5f} (scipy {pbs if isinstance(pbs, str) else round(pbs, 5)})')
    pf = {}
    for f in FAMS:
        a = sum(1 for s in range(6) if ('full', s) in T and f in T[('full', s)]['acquired'])
        b = sum(1 for s in range(6) if ('ko', s) in T and f in T[('ko', s)]['acquired'])
        pf[f] = (a, b, boschloo(a, 6, b, 6))
    order = sorted(FAMS, key=lambda f: pf[f][2])
    holm = {}
    run = 0
    for i, f in enumerate(order):
        adj = min(1.0, (len(FAMS) - i) * pf[f][2]); run = max(run, adj); holm[f] = run
    for f in FAMS:
        print(f'   {f:22s} full {pf[f][0]}/6 knockout {pf[f][1]}/6  Boschloo p {pf[f][2]:.4f}  Holm {holm[f]:.4f}')
    xs = [T[('full', s)]['solved'] for s in range(6)]; ys = [T[('ko', s)]['solved'] for s in range(6)]
    u, p = mw_exact_greater(xs, ys)
    print(f'   solved at r16 (of {T[("full", 0)]["of"]}): full {xs} (median {sorted(xs)[2]}/{sorted(xs)[3]}), knockout {ys} (median {sorted(ys)[2]}/{sorted(ys)[3]}); '
          f'U = {u}, exact one-sided p = {p:.5f}')
    if setname == 'strict':
        ds = [T[('dose1', s)]['solved'] for s in range(3) if ('dose1', s) in T]
        print(f'   dose1 r16 solved: {ds}; acquired: {[T[("dose1", s)]["acquired"] for s in range(3) if ("dose1", s) in T]}')
    RES[f'tests_{setname}'] = {'ind_full': ind_full, 'ind_ko': ind_ko, 'boschloo': pb, 'boschloo_scipy': pbs, 'per_family': pf, 'holm': holm,
                               'solved_full': xs, 'solved_ko': ys, 'U': u, 'mw_p': p}
json.dump(RES, open(f'{RV}/review_coe/out_acq.json', 'w'), indent=1, default=str)
