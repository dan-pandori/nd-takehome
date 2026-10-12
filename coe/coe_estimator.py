#!/usr/bin/env python3
"""create-or-elicit Phase 0.1: the known-proof estimator at small p (no pod; capability-defs J1 / J2 / J9 artefacts).

  python3 coe/coe_estimator.py [--cd ~/work/capability-defs] [--out artifacts/coe/estimator]
  python3 coe/coe_estimator.py --selftest      (bound arithmetic + positive / negative controls of the proof matching)
  -> per_theorem.json, summary.json, estimator.txt (the printed tables)

Model behind every number: best-cap12 pend s0 / s1 / s2 = `trajectory/ckpts/tj/stage1_best12_s{S}_b1200.pt`
(9.56 M-parameter ALiBiGPT, lean_staten, from scratch on K12; Lean alone decides every success).

Inputs (read-only, from the capability-defs worktree; each J1 / J2 / J9 file is byte-for-byte the size of its copy in
hf://buckets/dan-pandori/nd-rl/capability-defs/artifacts/cd/, checked 2026-10-12):
  capability_defs/analysis/out/bracket.json  {seed: {theorem: {grp H|CAL, c, n, phat, LB08, ...}}} (cd_bracket.py)
  artifacts/cd/j1/targets_s{S}.jsonl          J1 known set F_known(t): every distinct accepted ND proof of t in any read
                                              of any model (cap 12 / cap 6, every checkpoint, draws x0-x10) + reference
  artifacts/cd/j1/s2targets_s{S}.jsonl        stage-2 targets: top-20 known proofs + pend's own J2 finds (tid j2:...)
  artifacts/cd/j1/b1_s{S}_p*/compact.jsonl.gz stage-1 scores (name base 0 only; term = b0 - ln 33, a lower bound)
  artifacts/cd/j1/b33_s{S}/compact.jsonl.gz   stage-2 exact scores (all 33 name bases)
  artifacts/cd/j2/s{S}_{cNN,cal,dNN,bNN}.jsonl large-k plain sampling of pend (t00, the doubled-cap check, excluded as in
                                              cd_bracket); artifacts/cd/j9/s{S}_k{N}.jsonl certification chunks
Definitions:
  p-hat = c / n of bracket.json (pend x0 + x1 + x2 + x4 reads + J2 + J9); CP = exact two-sided 95 % Clopper-Pearson.
  E_all   = exp(LB08) of bracket.json: sum over F(t) = F_known + pend's own J2 c/cal finds of pi_pend(F) at T 0.8 (exact
            33-base terms where stage 2 scored the proof, the stage-1 lower bound b0 - ln 33 elsewhere).  Recomputed here
            and asserted equal to bracket.json.
  E_known = the same sum over F_known only (tid k:...): the estimate without any of the base's own large-k proofs.
  Large-k sample of (S, t): every J2 (not t00) and J9 chunk; N = sum n_ok, n_L = sum n_tried.  A chunk row keeps only
  its DISTINCT accepted proofs, so a chunk with n_ok > d (d distinct) has e = n_ok - d duplicate successes of unknown
  identity; every count below that depends on multiplicities is given as exact [min, max] bounds over all allocations.
  Coverage C = K / N, K = base large-k successes whose proof is in F_known (exact ND string; `normalize.norm`, the repo's
  start-index renumbering, is the identity on every state-env proof and is applied anyway).  Since F_known was built
  from reads independent of J2 / J9, K ~ Bin(N, C_t) with C_t = sum_{F in F_known} pi(F) / p: the share of p carried by
  the known set, the out-of-sample completeness of the estimator.  1 - C is the unseen share.
  Calibration of teacher forcing: expected known-proof successes mu = n_L * E_known vs observed K; per theorem
  E_known / p-hat_L = (mu / K) * (K / N) exactly (p-hat_L = N / n_L): estimate / truth = calibration x coverage.
  Good-Turing on the base's own successes: f1 = proofs seen exactly once among the N; M0 = f1 / N is the missing mass of
  the base's own seen set; f1u = singletons outside F_known, M0u = f1u / N the missing mass of F_known + seen (the set
  E_all sums over, when every seen proof was scored); GT-corrected estimate E_all / (1 - M0u) where M0u < 1.
"""
import argparse, collections, glob, gzip, hashlib, json, math, os, sys
import numpy as np
from scipy.stats import beta, chi2, poisson

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, ROOT)
from normalize import norm          # noqa: E402  (start-index renumbering; identity on state-env proofs)

LN33 = math.log(33)
SEEDS = (0, 1, 2)
BINS = (('ge1e-3', 1e-3, 2.0), ('1e-4..1e-3', 1e-4, 1e-3), ('1e-5..1e-4', 1e-5, 1e-4), ('lt1e-5', 0.0, 1e-5))
EBINS = (('ge1e-3', 1e-3, 2.0), ('1e-4..1e-3', 1e-4, 1e-3), ('1e-5..1e-4', 1e-5, 1e-4), ('1e-6..1e-5', 1e-6, 1e-5),
         ('lt1e-6', -1.0, 1e-6))     # bins of the estimate itself (E_known; 0 when no known proof scores)
MODEL = ('best-cap12 pend s{S} = trajectory/ckpts/tj/stage1_best12_s{S}_b1200.pt (9.56M ALiBiGPT, lean_staten, from '
         'scratch on K12, Lean alone)')


def lse(xs):
    if not xs:
        return -math.inf
    m = max(xs)
    return m + math.log(sum(math.exp(x - m) for x in xs))


def cp2(c, n, a=0.05):
    """exact two-sided (1 - a) Clopper-Pearson interval."""
    lo = 0.0 if c == 0 else float(beta.ppf(a / 2, c, n - c + 1))
    hi = 1.0 if c >= n else float(beta.ppf(1 - a / 2, c + 1, n - c))
    return lo, hi


def pois_ci(k, a=0.05):
    """exact 95 % interval for a Poisson mean given an observed count k."""
    return (0.0 if k == 0 else float(chi2.ppf(a / 2, 2 * k)) / 2, float(chi2.ppf(1 - a / 2, 2 * k + 2)) / 2)


def bin_of(p, bins=BINS):
    for name, lo, hi in bins:
        if lo <= p < hi:
            return name
    raise ValueError(p)


def pct(xs, q):
    return float(np.percentile(xs, q)) if len(xs) else None


def chunk_tag(path):
    return os.path.basename(path)[:-len('.jsonl')]


def load_large_k(cd, s):
    """{theorem: [ {chunk, n_ok, n_tried, proofs} ]} over J2 (no t*) and J9 chunk files of seed s."""
    out = collections.defaultdict(list)
    paths = sorted(glob.glob(f'{cd}/artifacts/cd/j2/s{s}_*.jsonl')) + sorted(glob.glob(f'{cd}/artifacts/cd/j9/s{s}_k*.jsonl'))
    for p in paths:
        if p.endswith('.full.jsonl'):
            continue
        tag = chunk_tag(p)
        if '/j2/' in p and tag.split('_')[1].startswith('t'):
            continue            # doubled-cap truncation check: a different sampler, excluded as in cd_bracket
        for l in open(p):
            r = json.loads(l)
            ps = [norm(x) for x in (r.get('proofs') or [])]
            assert len(set(ps)) == len(ps) and r['n_ok'] >= len(ps), (p, r['name'])
            out[r['name']].append({'chunk': tag, 'n_ok': r['n_ok'], 'n_tried': r['n_tried'], 'proofs': ps})
    return out


def load_scores(cd, s):
    """cd_bracket.load_j1 + lb(): per theorem [(tid, T 0.8 pend term, exact?)] and tid -> term."""
    rows = collections.defaultdict(list)
    have = set()
    for p in sorted(glob.glob(f'{cd}/artifacts/cd/j1/b1_s{s}_p*/compact.jsonl.gz')):
        with gzip.open(p, 'rt') as f:
            for l in f:
                r = json.loads(l)
                if r['replay_ok']:
                    rows[r['name']].append(r); have.add(r['tid'])
    exact = {}
    for p in sorted(glob.glob(f'{cd}/artifacts/cd/j1/b33_s{s}*/compact.jsonl.gz')):
        with gzip.open(p, 'rt') as f:
            for l in f:
                r = json.loads(l)
                if r['replay_ok']:
                    exact[r['tid']] = r['sc']
                    if r['tid'] not in have:
                        rows[r['name']].append(r); have.add(r['tid'])
    lab = f's{s}_pend'
    terms, term_of = {}, {}
    for n, rs in rows.items():
        tt = []
        for r in rs:
            if r['tid'] in exact and lab in exact[r['tid']]:
                v, ex = exact[r['tid']][lab][2], True
            elif lab in r['sc']:
                v, ex = r['sc'][lab][2] - LN33, False
            else:
                continue
            tt.append((r['tid'], v, ex)); term_of[r['tid']] = (v, ex)
        terms[n] = tt
    return terms, term_of


def proof_index(cd, s, want):
    """(theorem, proof) -> (tid, src) for the proofs in `want` ({theorem: set(proofs)}), from targets + s2targets."""
    idx = {}
    for l in open(f'{cd}/artifacts/cd/j1/targets_s{s}.jsonl'):
        r = json.loads(l)
        w = want.get(r['name'])
        if w and norm(r['proof']) in w:
            idx[(r['name'], norm(r['proof']))] = (r['tid'], tuple(r['src']))
    for l in open(f'{cd}/artifacts/cd/j1/s2targets_s{s}.jsonl'):
        r = json.loads(l)
        w = want.get(r['name'])
        k = (r['name'], norm(r['proof']))
        if w and k[1] in w and k not in idx:
            idx[k] = (r['tid'], tuple(r['src']))
    return idx


def multiplicity(chunks, known):
    """exact [min, max] bounds over every allocation of each chunk's e = n_ok - d duplicate successes to its proofs.
    known: set of proofs in F_known.  Returns dict with K, f1, f1u bounds and recoverability flags."""
    cnt = collections.Counter(p for c in chunks for p in c['proofs'])
    K = [0, 0]; f1 = [0, 0]; f1u = [0, 0]
    for c in chunks:
        P = c['proofs']
        if not P:
            continue
        e = c['n_ok'] - len(P)
        kn = sum(1 for p in P if p in known)
        K[0] += kn + (e if kn == len(P) else 0)
        K[1] += kn + (e if kn > 0 else 0)
        U = [p for p in P if cnt[p] == 1]
        Uu = [p for p in U if p not in known]
        f1[0] += len(U) - min(e, len(U))
        f1[1] += len(U) - (1 if e > 0 and len(U) == len(P) else 0)
        f1u[0] += len(Uu) - min(e, len(Uu))
        f1u[1] += len(Uu) - (1 if e > 0 and len(Uu) == len(P) else 0)
    succ = [c for c in chunks if c['n_ok'] > 0]
    return {'K': K, 'f1': f1, 'f1u': f1u,
            'prereg_recoverable': all(c['n_ok'] <= len(c['proofs']) + 1 for c in succ),
            'all_singletons': all(c['n_ok'] == len(c['proofs']) for c in succ),
            'f1_exact': f1[0] == f1[1], 'K_exact': K[0] == K[1]}


def model_K(chunks, known, w):
    """model-based point estimate of K: each chunk's duplicates allocated in proportion to pi (unscored proofs get the
    chunk's smallest scored pi; equal weights if none scored).  Uses pi, so it is not a test of pi."""
    k = 0.0
    for c in chunks:
        P = c['proofs']
        if not P:
            continue
        e = c['n_ok'] - len(P)
        ws = [w.get(p) for p in P]
        floor = min([x for x in ws if x is not None], default=1.0)
        ws = [floor if x is None else x for x in ws]
        tot = sum(ws)
        k += sum(1 + e * x / tot for p, x in zip(P, ws) if p in known)
    return k


def theorem_rows(cd, s, B, L, terms, term_of):
    want = {n: {p for c in L.get(n, []) for p in c['proofs']} for n in B}
    idx = proof_index(cd, s, want)
    out = {}
    for n, b in B.items():
        tt = terms.get(n, [])
        lb_all = lse([v for _, v, _ in tt])
        assert abs(lb_all - b['LB08']) < 1e-9 or lb_all == b['LB08'], (s, n, lb_all, b['LB08'])   # = cd_bracket
        tk = [(v, ex) for tid, v, ex in tt if tid.startswith('k:')]
        lb_known = lse([v for v, _ in tk])
        ex_share = sum(math.exp(v - lb_known) for v, ex in tk if ex) if tk else None
        lo, hi = cp2(b['c'], b['n'])
        E_all, E_known = math.exp(lb_all), math.exp(lb_known)
        chunks = L.get(n, [])
        task1 = b['grp'] == 'CAL' or b['c'] >= 1          # theorems with a measured p-hat (Tasks 1-3)
        nL = sum(c['n_tried'] for c in chunks); N = sum(c['n_ok'] for c in chunks)
        seen = sorted({p for c in chunks for p in c['proofs']})
        info = {p: idx.get((n, p)) for p in seen}
        known = {p for p in seen if info[p] and info[p][0].startswith('k:')}
        nonbase = {p for p in known if any(x != f'pend{s}' for x in info[p][1])}
        w = {}
        unscored = 0
        for p in seen:
            if info[p] and info[p][0] in term_of:
                w[p] = math.exp(term_of[info[p][0]][0])
            else:
                unscored += 1
        m = multiplicity(chunks, known)
        mn = multiplicity(chunks, nonbase)
        row = {'seed': s, 'theorem': n, 'grp': b['grp'], 'rl_solved_J2set': None, 'task1': task1, 'c': b['c'],
               'n': b['n'], 'phat': b['phat'], 'cp_lo': lo, 'cp_hi': hi, 'ub95_one_sided': b['ub'],
               'bin': bin_of(b['phat']) if task1 else None, 'ebin': bin_of(E_known, EBINS),
               'E_all': E_all, 'E_known': E_known, 'ratio_all': E_all / b['phat'] if task1 else None,
               'ratio_known': E_known / b['phat'] if task1 else None,
               'n_F_all': len(tt), 'n_F_known': len(tk), 'exact_share_known': ex_share,
               'bound_share_known': None if ex_share is None else 1 - ex_share,
               'large_k': {'n_L': nL, 'N': N, 'chunks_with_success': [
                   {'chunk': c['chunk'], 'n_ok': c['n_ok'], 'n_tried': c['n_tried'], 'distinct': len(c['proofs']),
                    'known': sum(p in known for p in c['proofs'])} for c in chunks if c['n_ok'] > 0],
                   'distinct': len(seen), 'distinct_known': len(known), 'distinct_known_nonbase': len(nonbase),
                   'own_unscored': unscored,
                   'src_of_known': dict(sorted(collections.Counter('+'.join(info[p][1]) for p in known).items()))},
               'K': m['K'], 'K_nonbase': mn['K'], 'f1': m['f1'], 'f1u': m['f1u'],
               'prereg_recoverable': m['prereg_recoverable'], 'all_singletons': m['all_singletons'],
               'f1_exact': m['f1_exact'], 'K_exact': m['K_exact'],
               'K_model': model_K(chunks, known, w) if N else 0.0,
               'K_model_nonbase': model_K(chunks, nonbase, w) if N else 0.0}
        # selection-free check: predicted successes in the large-k sample from the known-set estimate alone
        mu = nL * E_known
        row['mu_known'] = mu                          # expected large-k successes if p = E_known
        row['p_over'] = float(poisson.cdf(N, mu)) if mu > 0 else 1.0       # small: E_known too high for the N seen
        row['p_under'] = float(poisson.sf(N - 1, mu)) if N > 0 else 1.0    # small: E_known too low for the N seen
        if N and b['grp'] == 'H':     # every distinct base large-k proof of a hard theorem (md5 of the ND string)
            row['large_k']['proofs'] = [
                {'md5': hashlib.md5(p.encode()).hexdigest()[:12],
                 'chunks': [c['chunk'] for c in chunks if p in c['proofs']],
                 'known': p in known, 'src': '+'.join(info[p][1]) if info[p] else None,
                 'ln_pi_T08': (round(term_of[info[p][0]][0], 4) if info[p] and info[p][0] in term_of else None),
                 'pi_exact': (term_of[info[p][0]][1] if info[p] and info[p][0] in term_of else None)} for p in seen]
        if N:
            row['coverage'] = [m['K'][0] / N, m['K'][1] / N]
            row['coverage_nonbase'] = [mn['K'][0] / N, mn['K'][1] / N]
            row['coverage_cp'] = [cp2(m['K'][0], N)[0], cp2(m['K'][1], N)[1]]
            row['coverage_model'] = row['K_model'] / N
            row['GT_M0'] = [m['f1'][0] / N, m['f1'][1] / N]
            row['GT_M0u'] = [m['f1u'][0] / N, m['f1u'][1] / N]
            row['phat_L'] = N / nL
            ok = unscored == 0 and m['f1u'][1] < N
            row['E_GT'] = [E_all / (1 - m['f1u'][0] / N), E_all / (1 - m['f1u'][1] / N)] if ok else None
            row['ratio_GT'] = [x / b['phat'] for x in row['E_GT']] if ok else None
        out[n] = row
    return out


def summarize(rows):
    """one bin x seed cell (or a pooled cell)."""
    if not rows:
        return {'n': 0}
    ra = [r['ratio_all'] for r in rows]; rk = [r['ratio_known'] for r in rows]
    bs = [r['bound_share_known'] for r in rows if r['bound_share_known'] is not None]
    d = {'n': len(rows),
         'phat_range': [min(r['phat'] for r in rows), max(r['phat'] for r in rows)],
         'stage1_bound_share_of_E_known': {'median': pct(bs, 50), 'max': max(bs) if bs else None},
         'ratio_all': {'median': pct(ra, 50), 'p10': pct(ra, 10), 'p90': pct(ra, 90),
                       'inside_cp': sum(r['cp_lo'] <= r['E_all'] <= r['cp_hi'] for r in rows) / len(rows),
                       'above_cp_hi': sum(r['E_all'] > r['cp_hi'] for r in rows) / len(rows),
                       'below_cp_lo': sum(r['E_all'] < r['cp_lo'] for r in rows) / len(rows)},
         'ratio_known': {'median': pct(rk, 50), 'p10': pct(rk, 10), 'p90': pct(rk, 90),
                         'inside_cp': sum(r['cp_lo'] <= r['E_known'] <= r['cp_hi'] for r in rows) / len(rows),
                         'above_cp_hi': sum(r['E_known'] > r['cp_hi'] for r in rows) / len(rows),
                         'below_cp_lo': sum(r['E_known'] < r['cp_lo'] for r in rows) / len(rows)}}
    S = [r for r in rows if r['large_k']['N'] > 0]
    if S:
        N = sum(r['large_k']['N'] for r in S)
        K0 = sum(r['K'][0] for r in S); K1 = sum(r['K'][1] for r in S)
        Kn0 = sum(r['K_nonbase'][0] for r in S); Kn1 = sum(r['K_nonbase'][1] for r in S)
        f10 = sum(r['f1'][0] for r in S); f11 = sum(r['f1'][1] for r in S)
        fu0 = sum(r['f1u'][0] for r in S); fu1 = sum(r['f1u'][1] for r in S)
        mu = sum(r['mu_known'] for r in S)
        cov_mid = [(r['coverage'][0] + r['coverage'][1]) / 2 for r in S]
        rec = [r for r in S if r['prereg_recoverable']]
        d['coverage'] = {
            'theorems_with_base_successes': len(S), 'N': N,
            'distinct': sum(r['large_k']['distinct'] for r in S),
            'distinct_known': sum(r['large_k']['distinct_known'] for r in S),
            'K': [K0, K1], 'pooled': [K0 / N, K1 / N],
            'pooled_cp95': [cp2(K0, N)[0], cp2(K1, N)[1]],
            'unseen_share': [1 - K1 / N, 1 - K0 / N],
            'unseen_cp95': [1 - cp2(K1, N)[1], 1 - cp2(K0, N)[0]],
            'pooled_nonbase': [Kn0 / N, Kn1 / N],
            'pooled_model_pi_alloc': sum(r['K_model'] for r in S) / N,
            'pooled_nonbase_model_pi_alloc': sum(r['K_model_nonbase'] for r in S) / N,
            'theorem_median_lo_hi': [pct([r['coverage'][0] for r in S], 50), pct([r['coverage'][1] for r in S], 50)],
            'theorem_p10_p90_mid': [pct(cov_mid, 10), pct(cov_mid, 90)],
            'theorems_K_exact': sum(r['K_exact'] for r in S),
            'theorems_le3_successes': sum(r['large_k']['N'] <= 3 for r in S),
            'median_N': pct([r['large_k']['N'] for r in S], 50)}
        d['multiplicity'] = {
            'theorems': len(S), 'prereg_recoverable': len(rec),
            'all_singletons': sum(r['all_singletons'] for r in S), 'f1_exact': sum(r['f1_exact'] for r in S)}
        d['good_turing'] = {
            'all_theorems_M0_bounds': [f10 / N, f11 / N], 'all_theorems_M0u_bounds': [fu0 / N, fu1 / N],
            'recoverable_N': sum(r['large_k']['N'] for r in rec),
            'recoverable_M0': ([sum(r['f1'][0] for r in rec) / sum(r['large_k']['N'] for r in rec),
                                sum(r['f1'][1] for r in rec) / sum(r['large_k']['N'] for r in rec)] if rec else None),
            'recoverable_M0u': ([sum(r['f1u'][0] for r in rec) / sum(r['large_k']['N'] for r in rec),
                                 sum(r['f1u'][1] for r in rec) / sum(r['large_k']['N'] for r in rec)] if rec else None),
            'GT_corrected_defined': sum(r['E_GT'] is not None for r in S),
            'GT_corrected_ratio_median': ([pct([r['ratio_GT'][0] for r in S if r['E_GT']], 50),
                                           pct([r['ratio_GT'][1] for r in S if r['E_GT']], 50)]
                                          if any(r['E_GT'] for r in S) else None)}
        d['calibration'] = {
            'mu_known': mu, 'K': [K0, K1],
            'factor_mu_over_K': [mu / K1 if K1 else None, mu / K0 if K0 else None],
            'theorem_median_E_known_over_phatL': pct([r['E_known'] / r['phat_L'] for r in S], 50)}
        c_pi = d['coverage']['pooled_model_pi_alloc']     # = K / N exactly wherever K is exact
        d['coverage_corrected'] = {'C_bin_pi_alloc': c_pi,
                                   'median_ratio_known_over_C': d['ratio_known']['median'] / c_pi if c_pi else None}
    return d


def ecal(rows):
    """selection-free calibration in a bin of E_known (the estimate does not depend on the large-k outcomes):
    observed large-k successes vs predicted sum n_L * E_known, exact Poisson interval on the observed count."""
    if not rows:
        return {'n': 0}
    N = sum(r['large_k']['N'] for r in rows); mu = sum(r['mu_known'] for r in rows)
    lo, hi = pois_ci(N)
    S = [r for r in rows if r['large_k']['N'] > 0]
    K0 = sum(r['K'][0] for r in S); K1 = sum(r['K'][1] for r in S)
    return {'n': len(rows), 'n_H': sum(r['grp'] == 'H' for r in rows), 'n_CAL': sum(r['grp'] == 'CAL' for r in rows),
            'with_success': len(S), 'n_L': sum(r['large_k']['n_L'] for r in rows), 'predicted': mu, 'observed': N,
            'obs_over_pred': N / mu if mu else None,
            'obs_over_pred_ci95': [lo / mu, hi / mu] if mu else None,
            'pred_over_obs': mu / N if N else None,
            'over_estimates_p025': sum(r['p_over'] < 0.025 for r in rows),
            'under_estimates_p025': sum(r['p_under'] < 0.025 for r in rows),
            'K': [K0, K1], 'coverage': [K0 / N, K1 / N] if N else None,
            'coverage_cp95': [cp2(K0, N)[0], cp2(K1, N)[1]] if N else None,
            'mu_over_K': [mu / K1 if K1 else None, mu / K0 if K0 else None],   # TF calibration on the known set
            'coverage_pi_alloc': sum(r['K_model'] for r in S) / N if N else None,
            'median_E_known': pct([r['E_known'] for r in rows], 50)}


PBINS = ((-2, -1), (-3, -2), (-4, -3), (-5, -4), (-6, -5), (-7, -6), (-9, -7), (-40, -9))   # log10 pi


def proof_calibration(cd, s, B, L, terms):
    """per-proof check of teacher forcing: every known proof with an exact 33-base score (stage-2 top-20 targets,
    chosen by stage-1 score, i.e. independently of J2 / J9) -> expected large-k count n_L * pi vs observed count
    (exact bounds: the proof's chunks x [1, 1 + that chunk's duplicates]).  {grp: {log10 bin: [exp, lo, hi, proofs]}}"""
    ex = {tid: (n, v) for n, tt in terms.items() for tid, v, e in tt if e and tid.startswith('k:')}
    out = {g: {f'{a}..{b}': [0.0, 0, 0, 0] for a, b in PBINS} for g in ('H', 'CAL')}
    for l in open(f'{cd}/artifacts/cd/j1/s2targets_s{s}.jsonl'):
        r = json.loads(l)
        if r['tid'] not in ex:
            continue
        n, v = ex.pop(r['tid'])
        chunks = L.get(n, [])
        nL = sum(c['n_tried'] for c in chunks)
        if not nL or n not in B:
            continue
        p = norm(r['proof'])
        lo = sum(1 for c in chunks if p in c['proofs'])
        hi = sum(1 + c['n_ok'] - len(c['proofs']) for c in chunks if p in c['proofs'])
        lv = v / math.log(10)
        for a, b in PBINS:
            if a <= lv < b:
                x = out[B[n]['grp']][f'{a}..{b}']
                x[0] += nL * math.exp(v); x[1] += lo; x[2] += hi; x[3] += 1
    return out


def gap_stats(cd, s):
    """exact (33-base) minus stage-1 b0 score, T 0.8 pend, over known proofs scored both ways."""
    b1 = {}
    for p in sorted(glob.glob(f'{cd}/artifacts/cd/j1/b1_s{s}_p*/compact.jsonl.gz')):
        with gzip.open(p, 'rt') as f:
            for l in f:
                r = json.loads(l)
                if r['replay_ok']:
                    b1[r['tid']] = r['sc'][f's{s}_pend'][2]
    g = []
    with gzip.open(f'{cd}/artifacts/cd/j1/b33_s{s}/compact.jsonl.gz', 'rt') as f:
        for l in f:
            r = json.loads(l)
            if r['replay_ok'] and r['tid'] in b1:
                g.append(r['sc'][f's{s}_pend'][2] - b1[r['tid']])
    q = np.percentile(g, [5, 50, 95])
    return {'n': len(g), 'exact_minus_b0_p5_p50_p95': [float(x) for x in q],
            'exact_minus_stage1_bound_median': float(q[1]) + LN33}


def fmt(x, nd=2):
    if x is None:
        return '-'
    if isinstance(x, float) and (abs(x) >= 1000 or (0 < abs(x) < 0.01)):
        return f'{x:.1e}'
    return f'{x:.{nd}f}' if isinstance(x, float) else str(x)


def selftest(cd):
    """(1) multiplicity bounds on hand-made chunks; (2) positive control: every proof of seed 0's J2 c / cal chunks
    that capability-defs' stage 2 saw must be found by proof_index (coverage 1 against targets + s2targets);
    (3) negative control: no theorem's large-k proofs match another theorem's known set."""
    ch = [{'n_ok': 3, 'proofs': ['a', 'b']}, {'n_ok': 1, 'proofs': ['a']}, {'n_ok': 2, 'proofs': ['c', 'd']}]
    m = multiplicity(ch, known={'a'})
    # chunk 1: e=1 over {a,b}; a is in 2 chunks -> U={b}; f1 in [0,1]. chunk 3: e=0, U={c,d}: +2.  K: a known ->
    # chunk1 [1, 2], chunk2 1 -> K [2, 3].  f1u: U' = {b} (+{c,d}) -> [0+2, 1+2]
    assert m['K'] == [2, 3] and m['f1'] == [2, 3] and m['f1u'] == [2, 3], m
    m = multiplicity([{'n_ok': 4, 'proofs': ['x']}], known=set())
    assert m['K'] == [0, 0] and m['f1'] == [0, 0] and m['all_singletons'] is False, m
    L = load_large_k(cd, 0)
    s2 = collections.defaultdict(set)
    for l in open(f'{cd}/artifacts/cd/j1/s2targets_s0.jsonl'):
        r = json.loads(l)
        s2[r['name']].add(norm(r['proof']))
    want = {n: {p for c in cs if c['chunk'].split('_')[1][0] == 'c' for p in c['proofs']} for n, cs in L.items()}
    want = {n: ps for n, ps in want.items() if ps and n in s2}
    idx = proof_index(cd, 0, want)
    tot = sum(len(ps) for ps in want.values())
    hit = sum(1 for n, ps in want.items() for p in ps if (n, p) in idx)
    assert tot > 500 and hit == tot, (hit, tot)
    names = sorted(want)
    shifted = {names[i]: want[names[(i + 1) % len(names)]] for i in range(len(names))}   # wrong theorem's proofs
    idx2 = proof_index(cd, 0, shifted)
    assert len(idx2) == 0, len(idx2)
    print(f'selftest ok: multiplicity bounds; positive control {hit} / {tot} c/cal-chunk proofs found; '
          f'negative control (proofs shifted to another theorem) 0 matches')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cd', default=os.path.expanduser('~/work/capability-defs'))
    ap.add_argument('--out', default=os.path.join(ROOT, 'artifacts', 'coe', 'estimator'))
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return selftest(a.cd)
    os.makedirs(a.out, exist_ok=True)
    BR = json.load(open(f'{a.cd}/capability_defs/analysis/out/bracket.json'))
    sets = json.load(open(f'{a.cd}/artifacts/cd/j1/sets.json'))
    per, loaded = {}, {}
    for s in SEEDS:
        L = load_large_k(a.cd, s)
        terms, term_of = load_scores(a.cd, s)
        loaded[s] = (L, terms)
        rows = theorem_rows(a.cd, s, BR[str(s)], L, terms, term_of)
        for n, r in rows.items():
            r['rl_solved_J2set'] = n in set(sets[str(s)]['J2'])
        per[str(s)] = rows
    allrows = [r for s in per for r in per[s].values()]
    t1 = [r for r in allrows if r['task1']]                 # measured p-hat: H with c >= 1, and CAL
    summ = {'model': MODEL, 'bins': [b[0] for b in BINS], 'cells': {}, 'pooled_bins': {}, 'by_group': {}}
    for bname, _, _ in BINS:
        for s in SEEDS:
            summ['cells'][f's{s}|{bname}'] = summarize([r for r in t1 if r['seed'] == s and r['bin'] == bname])
        summ['pooled_bins'][bname] = summarize([r for r in t1 if r['bin'] == bname])
    for g in ('H', 'CAL'):
        summ['by_group'][g] = summarize([r for r in t1 if r['grp'] == g])
    summ['pooled_ge1e-4'] = summarize([r for r in t1 if r['phat'] >= 1e-4])
    summ['pooled_lt1e-4'] = summarize([r for r in t1 if r['phat'] < 1e-4])
    summ['pooled_H_lt1e-3'] = summarize([r for r in t1 if r['phat'] < 1e-3 and r['grp'] == 'H'])
    summ['hard_large_k_counts'] = {f's{s}': {
        'H': sum(1 for r in per[str(s)].values() if r['grp'] == 'H'),
        'H_with_base_success': sum(1 for r in per[str(s)].values() if r['grp'] == 'H' and r['task1']),
        'H_with_base_success_in_J2_set_rl_solved': sum(1 for r in per[str(s)].values()
                                                       if r['grp'] == 'H' and r['task1'] and r['rl_solved_J2set']),
        'min_phat': min(r['phat'] for r in per[str(s)].values() if r['grp'] == 'H' and r['task1'])} for s in SEEDS}
    # selection-free calibration, binned by the estimate E_known over every H and CAL theorem (0-success ones too)
    summ['ebins'] = {'all': {}, 'H': {}, 'CAL': {}, 'per_seed': {}}
    for bname, _, _ in EBINS:
        summ['ebins']['all'][bname] = ecal([r for r in allrows if r['ebin'] == bname])
        for g in ('H', 'CAL'):
            summ['ebins'][g][bname] = ecal([r for r in allrows if r['ebin'] == bname and r['grp'] == g])
        for s in SEEDS:
            summ['ebins']['per_seed'][f's{s}|{bname}'] = ecal([r for r in allrows if r['ebin'] == bname and r['seed'] == s])
    summ['ebins']['H_E_lt1e-3'] = ecal([r for r in allrows if r['grp'] == 'H' and r['E_known'] < 1e-3])
    summ['stage1_gap'] = {f's{s}': gap_stats(a.cd, s) for s in SEEDS}
    pc = {g: {f'{x}..{y}': [0.0, 0, 0, 0] for x, y in PBINS} for g in ('H', 'CAL')}
    for s in SEEDS:
        for g, d in proof_calibration(a.cd, s, BR[str(s)], *loaded[s]).items():
            for k, v in d.items():
                pc[g][k] = [u + w for u, w in zip(pc[g][k], v)]
    summ['proof_calibration'] = {g: {k: {'proofs': v[3], 'expected': v[0], 'observed': [v[1], v[2]],
                                         'obs_over_exp': [v[1] / v[0], v[2] / v[0]] if v[0] else None,
                                         'poisson95': ([pois_ci(v[1])[0] / v[0], pois_ci(v[2])[1] / v[0]]
                                                       if v[0] else None)}
                                     for k, v in d.items() if v[3]} for g, d in pc.items()}
    # which sources the known proofs among the base's large-k successes come from (distinct proofs)
    src = {}
    for g in ('H', 'CAL'):
        cnt = collections.Counter()
        for r in t1:
            if r['grp'] != g:
                continue
            for k, v in r['large_k']['src_of_known'].items():
                tags = set(k.split('+'))
                s = r['seed']
                cls = ('rl' if f'rl{s}' in tags else 'pt' if f'pt{s}' in tags else 'ref' if 'ref' in tags
                       else 'other_seed_or_cap6' if 'other' in tags else 'pend_only')
                cnt[cls] += v; cnt['total_known'] += v
        cnt['total_distinct'] = sum(r['large_k']['distinct'] for r in t1 if r['grp'] == g)
        src[g] = dict(sorted(cnt.items()))
    summ['known_source_of_base_proofs_distinct'] = src
    # ---- pre-registered expectations (preregistration/create-or-elicit.md, Phase 0.1); rules fixed before the run
    pre = {}
    meds = {s: summ['cells'][f's{s}|ge1e-3']['ratio_all']['median'] for s in SEEDS}
    pre['E1_median_ratio_ge1e-3_in_[0.7,1.2]'] = {
        'rule': 'per-seed median of exp(LB08) / p-hat over theorems with p-hat >= 1e-3: hit if all three in [0.7, 1.2]',
        'values': meds, 'pooled': summ['pooled_bins']['ge1e-3']['ratio_all']['median'],
        'known_only_values': {s: summ['cells'][f's{s}|ge1e-3']['ratio_known']['median'] for s in SEEDS},
        'score': 'hit' if all(0.7 <= v <= 1.2 for v in meds.values()) else 'miss'}
    lt = summ['pooled_lt1e-4']['ratio_all']; ltk = summ['pooled_lt1e-4']['ratio_known']
    pre['E2_ratio_10-90_wider_than_[0.3,3]_below_1e-4'] = {
        'rule': 'pooled over seeds, theorems with p-hat < 1e-4: hit if P90 / P10 > 10 (the width of [0.3, 3]); '
                'containment of [0.3, 3] reported too',
        'n': summ['pooled_lt1e-4']['n'], 'p10': lt['p10'], 'p90': lt['p90'], 'width': lt['p90'] / lt['p10'],
        'contains_[0.3,3]': lt['p10'] <= 0.3 and lt['p90'] >= 3,
        'known_only': {'p10': ltk['p10'], 'p90': ltk['p90'], 'width': ltk['p90'] / ltk['p10']},
        'score': 'hit' if lt['p90'] / lt['p10'] > 10 else 'miss'}
    cv = summ['pooled_ge1e-4']['coverage']
    pre['E3a_coverage_ge0.6_for_phat_ge1e-4'] = {
        'rule': 'success-weighted coverage pooled over seeds and theorems with p-hat >= 1e-4, exact multiplicity bounds: '
                'hit if both bounds >= 0.6, miss if both < 0.6, else not measurable (bounds straddle 0.6)',
        'pooled_bounds': cv['pooled'], 'cp95': cv['pooled_cp95'], 'model_pi_alloc': cv['pooled_model_pi_alloc'],
        'score': ('hit' if cv['pooled'][0] >= 0.6 else 'miss' if cv['pooled'][1] < 0.6 else 'not measurable')}
    low = [r for r in t1 if r['phat'] < 1e-5]
    pre['E3b_coverage_undetermined_below_1e-5'] = {
        'rule': 'hit if every theorem with p-hat < 1e-5 has <= 3 base large-k successes',
        'theorems': [{'seed': r['seed'], 'theorem': r['theorem'], 'N': r['large_k']['N'], 'c': r['c'], 'n': r['n'],
                      'known': r['K']} for r in low],
        'score': ('not measurable' if not low else 'hit' if all(r['large_k']['N'] <= 3 for r in low) else 'miss')}
    pre['E4_GT_on_this_runs_large_k_reads'] = {'score': 'not measurable',
                                               'why': 'no large-k read of this run exists yet (Phase 0.1 precedes every pod)'}
    summ['preregistered'] = pre
    json.dump(per, open(f'{a.out}/per_theorem.json', 'w'), indent=1)
    json.dump(summ, open(f'{a.out}/summary.json', 'w'), indent=1)
    # ---- printed tables
    L = []
    P = L.append
    P(f'# coe_estimator: known-proof estimate vs sampled p-hat. Model: {MODEL}')
    P('## Task 1: estimate / p-hat by p-hat bin (E_all = exp(LB08) as published; E_known = known set only)')
    P('| bin | seed | n | median E_all/p | P10-P90 | in CP95 | > CP hi | < CP lo | median E_known/p | P10-P90 | in CP95 | > CP hi |')
    P('|---|---|---:|---:|---|---:|---:|---:|---:|---|---:|---:|')
    for bname, _, _ in BINS:
        for key, lab in [(f's{s}|{bname}', f's{s}') for s in SEEDS] + [(None, 'all')]:
            c = summ['cells'][key] if key else summ['pooled_bins'][bname]
            if not c['n']:
                P(f'| {bname} | {lab} | 0 | | | | | | | | | |'); continue
            ra, rk = c['ratio_all'], c['ratio_known']
            P(f"| {bname} | {lab} | {c['n']} | {fmt(ra['median'])} | {fmt(ra['p10'])}-{fmt(ra['p90'])} | "
              f"{ra['inside_cp']:.2f} | {ra['above_cp_hi']:.2f} | {ra['below_cp_lo']:.2f} | {fmt(rk['median'])} | "
              f"{fmt(rk['p10'])}-{fmt(rk['p90'])} | {rk['inside_cp']:.2f} | {rk['above_cp_hi']:.2f} |")
    P('\n## Task 2: coverage of the base large-k successes by F_known (exact bounds over duplicate allocations)')
    P('| bin | seed | thms | N succ | distinct (known) | K [min,max] | C pooled | CP95 | C theorem median [lo,hi] | non-base C | pi-alloc C | thms <=3 succ | recoverable (prereg / all-singleton / f1 exact) |')
    P('|---|---|---:|---:|---|---|---|---|---|---|---:|---:|---|')
    for bname, _, _ in BINS:
        for key, lab in [(f's{s}|{bname}', f's{s}') for s in SEEDS] + [(None, 'all')]:
            c = summ['cells'][key] if key else summ['pooled_bins'][bname]
            if 'coverage' not in c:
                continue
            v, m = c['coverage'], c['multiplicity']
            P(f"| {bname} | {lab} | {v['theorems_with_base_successes']} | {v['N']} | {v['distinct']} ({v['distinct_known']}) | "
              f"[{v['K'][0]}, {v['K'][1]}] | [{v['pooled'][0]:.2f}, {v['pooled'][1]:.2f}] | "
              f"[{v['pooled_cp95'][0]:.2f}, {v['pooled_cp95'][1]:.2f}] | [{v['theorem_median_lo_hi'][0]:.2f}, "
              f"{v['theorem_median_lo_hi'][1]:.2f}] | [{v['pooled_nonbase'][0]:.2f}, {v['pooled_nonbase'][1]:.2f}] | "
              f"{v['pooled_model_pi_alloc']:.2f} | {v['theorems_le3_successes']} | {m['prereg_recoverable']} / "
              f"{m['all_singletons']} / {m['f1_exact']} |")
    P('\n## Task 3: unseen share, Good-Turing, calibration of teacher forcing (pooled over seeds per bin)')
    P('| bin | unseen 1-C [bounds] | CP95 | GT M0 all thms | GT M0u all thms | GT M0 recoverable (N) | mu/K calibration | GT-corr. ratio median (defined) | median E_known/p / C_bin |')
    P('|---|---|---|---|---|---|---|---|---|')
    for bname, _, _ in BINS:
        c = summ['pooled_bins'][bname]
        if 'coverage' not in c:
            continue
        v, g, k, cc = c['coverage'], c['good_turing'], c['calibration'], c['coverage_corrected']
        rec = (f"[{g['recoverable_M0'][0]:.2f}, {g['recoverable_M0'][1]:.2f}] ({g['recoverable_N']})"
               if g['recoverable_M0'] else '-')
        gtc = (f"[{fmt(g['GT_corrected_ratio_median'][0])}, {fmt(g['GT_corrected_ratio_median'][1])}] "
               f"({g['GT_corrected_defined']})" if g['GT_corrected_ratio_median'] else '-')
        P(f"| {bname} | [{v['unseen_share'][0]:.2f}, {v['unseen_share'][1]:.2f}] | [{v['unseen_cp95'][0]:.2f}, "
          f"{v['unseen_cp95'][1]:.2f}] | [{g['all_theorems_M0_bounds'][0]:.2f}, {g['all_theorems_M0_bounds'][1]:.2f}] | "
          f"[{g['all_theorems_M0u_bounds'][0]:.2f}, {g['all_theorems_M0u_bounds'][1]:.2f}] | {rec} | "
          f"[{fmt(k['factor_mu_over_K'][0])}, {fmt(k['factor_mu_over_K'][1])}] | {gtc} | {fmt(cc['median_ratio_known_over_C'])} |")
    P('\n## Task 1b: selection-free calibration in bins of the estimate E_known (all H and CAL theorems, 0-success ones too)')
    P('| E_known bin | group | thms (H/CAL) | with success | sum n_L | predicted sum n_L*E | observed N | obs/pred [Poisson 95 %] | E too high (p<.025) | E too low (p<.025) | coverage K/N [bounds] | pi-alloc C | mu/K [bounds] |')
    P('|---|---|---|---:|---:|---:|---:|---|---:|---:|---|---:|---|')
    for bname, _, _ in EBINS:
        for g in ('all', 'H', 'CAL'):
            c = summ['ebins'][g][bname]
            if not c['n']:
                continue
            op = (f"{fmt(c['obs_over_pred'])} [{fmt(c['obs_over_pred_ci95'][0])}, {fmt(c['obs_over_pred_ci95'][1])}]"
                  if c['obs_over_pred'] is not None else '-')
            cv = f"[{c['coverage'][0]:.2f}, {c['coverage'][1]:.2f}]" if c['coverage'] else '-'
            P(f"| {bname} | {g} | {c['n']} ({c['n_H']}/{c['n_CAL']}) | {c['with_success']} | {c['n_L']:,} | "
              f"{c['predicted']:.1f} | {c['observed']} | {op} | {c['over_estimates_p025']} | {c['under_estimates_p025']} | "
              f"{cv} | {fmt(c['coverage_pi_alloc'])} | [{fmt(c['mu_over_K'][0])}, {fmt(c['mu_over_K'][1])}] |")
    c = summ['ebins']['H_E_lt1e-3']
    P(f"- hard theorems with E_known < 1e-3: {c['n']} theorems, predicted {c['predicted']:.1f}, observed {c['observed']}, "
      f"obs/pred {fmt(c['obs_over_pred'])} [{fmt(c['obs_over_pred_ci95'][0])}, {fmt(c['obs_over_pred_ci95'][1])}]")
    P('- stage-1 bound looseness (exact 33-base minus b0, nats, p5/p50/p95): ' + '; '.join(
        f"s{s}: " + '/'.join(f'{x:.2f}' for x in summ['stage1_gap'][f's{s}']['exact_minus_b0_p5_p50_p95']) for s in SEEDS))
    P('- source of the known proofs among the base large-k proofs (distinct): ' + json.dumps(src))
    for g in ('H', 'CAL'):
        c = summ['by_group'][g]
        v, m = c['coverage'], c['multiplicity']
        P(f"- {g} (all task-1 theorems): n {c['n']}, base large-k successes {v['N']}, coverage [{v['pooled'][0]:.2f}, "
          f"{v['pooled'][1]:.2f}] (pi-alloc {v['pooled_model_pi_alloc']:.2f}); multiplicities recoverable by the prereg "
          f"rule (n_ok <= d + 1 in every chunk) on {m['prereg_recoverable']} / {m['theorems']}, all-singleton "
          f"{m['all_singletons']}, f1 exact {m['f1_exact']}, K exact {v['theorems_K_exact']}")
    P('\n## Task 3b: per-proof teacher-forcing calibration (exactly scored known proofs; n_L * pi vs observed count)')
    P('| group | log10 pi | proofs | expected | observed [bounds] | obs/exp [bounds] | Poisson 95 % |')
    P('|---|---|---:|---:|---|---|---|')
    for g in ('H', 'CAL'):
        for k, v in summ['proof_calibration'][g].items():
            if v['obs_over_exp'] is None:
                continue
            P(f"| {g} | {k} | {v['proofs']} | {v['expected']:.2f} | [{v['observed'][0]}, {v['observed'][1]}] | "
              f"[{fmt(v['obs_over_exp'][0])}, {fmt(v['obs_over_exp'][1])}] | [{fmt(v['poisson95'][0])}, {fmt(v['poisson95'][1])}] |")

    P('\n## Pre-registered expectations')
    for k, v in pre.items():
        P(f"- {k}: **{v['score']}** -- " + json.dumps({x: y for x, y in v.items() if x not in ('score', 'rule')}, default=str))
    txt = '\n'.join(L)
    print(txt)
    open(f'{a.out}/estimator.txt', 'w').write(txt + '\n')


if __name__ == '__main__':
    main()
