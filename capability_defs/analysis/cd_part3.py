#!/usr/bin/env python3
"""capability-defs Part 3: final created sets per definition, noise floors, agreement matrix, elicitation curves.

  python3 capability_defs/analysis/cd_part3.py   -> out/part3.json, out/part3.txt (stdout)

Model labels (every number): cap-12 best-cap12 (`best_model.ALiBiGPT`, 9,560,832 params, `lean_staten`, from scratch on
K12 = `data/kh/train_k12.jsonl`), seeds s0-s2; base = pend (end of pretraining, trajectory); RL = r8 (trajectory T1
ladder) and r16 (rl-continue).  Lean alone.  Plain T 0.8 reads (k 256) unless a definition says guided.
Comparisons: (s, R, draw x) for R = r8 (x0 defines, x1 = redraw) and r16 (x1 defines, x0 = redraw, J5).

Definitions (card slug -> key):
  passk-equal-k   eqk      R solves t on draw x (>= 1 / 256), pend 0 / 256 on the same draw
  passk-budget    cm       R solves t on draw x; pend 0 / 256 on x; pend NOT within reach at K = K_eval-set: over all its
                           standard-cap attempts (x0, x1, x2, x4, J2 stage A / A' / B; n >= K required) p-hat = c / n < 1 / K
                           (the card's capability statement p >= 1 / K).  cm0 = the subset with c = 0 ("not reached").
                           Theorems with n < K stay undetermined.  J2's doubled-cap truncation chunks (t) are excluded.
  reliability     rel      p-hat_R >= 1/2 on draw x and t in cm
  tf-proof-prob   tfmax    R solves t on x, pend 0 / 256 on x, and max over known proofs of pi_pend(y) < 1 / K_eval-set
                           (T 0.8; exact 33-base score where stage 2 scored it, else the stage-1 bound b0 - ln 33)
  marginal-bracket brk_ne  R solves t on x, t in H (pend 0 / 512), and NOT certified elicited at K_eval-set
                           (sum over F of pi_pend < 1 / K and the sampling lower bound < 1 / K)
  irt-ability     irt      DIF+ items pend fails (descriptive; the matched-placebo verdict is set level: no excess)
  schema-acq.     schema   holdout250 members of families created at family level (pend <= 0.05, R >= 0.5)
  cap-vs-prop.    guided   R solves t on x; pend 0 in all plain attempts AND 0 in its guided read (J3, k 256)
  sharpen-expand  sharp    R solves t; t in H; rho >= 1/2 (R's success mass on known proofs with pi_pend < 1 / K)
  new-proof/thm   npnt     cm AND NP across theorems: every one of R's accepted proofs of t uses a rule set that occurs in
                           no pend-accepted proof of any theorem (all pend reads + J2)  [revised after the card's critic]
  chain           chain    holdout250 t first solved by the ladder's sampler at round >= 2, and cm
  out-of-data     ood      R solves t and none of R's proofs of t uses a K12 rule set (coarsest skeleton level)
Each also "_net": minus theorems the replay-only control (rl-from-ckpt c<s>_pend_r8) solves on the same draw.
"""
import collections, glob, gzip, itertools, json, math, os, re, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cd_reads as R
from cd_defs import budgets, jac, READ_S, LADDER_S
from cd_bracket import cp_upper, cp_lower, lse, LN33
from cd_skeleton import skeleton

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
DEFS = ['eqk', 'cm', 'rel', 'tfmax', 'brk_ne', 'irt', 'schema', 'guided', 'sharp', 'npnt', 'chain', 'ood']
EXTRA = ['cm0', 'cm_undet', 'cm_recipe', 'cm_j7', 'eqk_j7']
J2_COST = 3.6e-3          # A40 seconds per pend attempt on hard theorems (J2 chunk s0_c00: 470 s / 131,072)


def k_evalset(s, rl):
    return LADDER_S[rl][s] / (322 * J2_COST)


def j2_counts(s, trunc=False):
    """pend's J2 attempts per theorem: standard caps (stage A c*, calibration cal, A' d*, B b*), or with trunc=True only
    the doubled-cap truncation chunks t*."""
    out = collections.defaultdict(lambda: [0, 0, set()])
    paths = glob.glob(f'{ROOT}/artifacts/cd/j2/s{s}_*.jsonl')
    if not trunc:                 # J9 certification chunks: the same standard-cap protocol (compacted rows)
        paths += [p for p in glob.glob(f'{ROOT}/artifacts/cd/j9/s{s}_k*.jsonl') if not p.endswith('.full.jsonl')]
    for p in paths:
        if '/j2/' in p and os.path.basename(p).split('_')[1].startswith('t') != trunc:
            continue
        for l in open(p):
            r = json.loads(l)
            c = out[r['name']]; c[0] += r['n_ok']; c[1] += r['n_tried']; c[2].update(r.get('proofs') or [])
    return out


def guided_counts(s, ck):
    p = f'{ROOT}/artifacts/cd/j3/s{s}_{ck}_logical.rows.jsonl.gz'
    if not os.path.exists(p):
        return None
    out = {}
    for l in gzip.open(p, 'rt'):
        r = json.loads(l); out[r['name']] = (r['n_ok'], r['k'])
    return out


def detour(proof):
    """True if some ORE's disjunction (first citation) was built by ORI in the same proof (a self-built Or-detour)."""
    rules = {}
    for part in proof.split(';'):
        m = re.match(r'\s*N(\d+)\s+(?:\|\s*)*.*?:\s*([A-Z]+)\d*\s*((?:N\d+\s*)*)$', part.strip())
        if not m:
            continue
        n, rule, refs = int(m.group(1)), m.group(2), [int(x[1:]) for x in m.group(3).split()]
        rules[n] = rule
        if rule == 'ORE' and refs and rules.get(refs[0]) == 'ORI':
            return True
    return False


def load_scores(s):
    """{name: [(proof, {label: (T08 total exact-or-bound)})]} combining stage-1 bounds and stage-2 exact scores."""
    tgt = {}
    for p in sorted(glob.glob(f'{ROOT}/artifacts/cd/j1/targets_s{s}_p*.jsonl')) + [f'{ROOT}/artifacts/cd/j1/s2targets_s{s}.jsonl']:
        if os.path.exists(p):
            for l in open(p):
                r = json.loads(l); tgt[r['tid']] = r['proof']
    by = collections.defaultdict(dict)
    for p in sorted(glob.glob(f'{ROOT}/artifacts/cd/j1/b1_s{s}_p*/compact.jsonl.gz')):
        for l in gzip.open(p, 'rt'):
            r = json.loads(l)
            if r['replay_ok']:
                by[r['name']][r['tid']] = {k: (v[2] - LN33, v[2], False) for k, v in r['sc'].items()}   # (bound, b0 point, exact?)
    p = f'{ROOT}/artifacts/cd/j1/b33_s{s}/compact.jsonl.gz'
    if os.path.exists(p):
        for l in gzip.open(p, 'rt'):
            r = json.loads(l)
            if r['replay_ok']:
                d = by[r['name']].setdefault(r['tid'], {})
                for k, v in r['sc'].items():
                    d[k] = (v[2], v[2], True)
    return by, tgt


def main():
    T = json.load(open(f'{OUT}/table_c12.json'))
    sets_j1 = json.load(open(f'{ROOT}/artifacts/cd/j1/sets.json'))
    irt = json.load(open(f'{OUT}/irt_c12.json'))
    sch = json.load(open(f'{OUT}/schema_c12.json'))
    names = T['names']; meta = T['meta']
    # schema family membership (transfer schema labels) and family verdict on holdout250 members (as cd_defs)
    fam_of = {}
    for l in open(f'{ROOT}/data/ladder/transfer.jsonl'):
        r = json.loads(l)
        if r.get('schema'):
            fam_of[r['name']] = r['schema']
    # K12 rule sets (coarsest skeleton level)
    k12_rulesets = set()
    for l in open(os.path.expanduser('~/work/best-state/data/kh/train_k12.jsonl')):
        sk = skeleton(json.loads(l)['proof'])
        k12_rulesets.add(tuple(sorted(set(r for _, r, _ in sk))))
    # chain depth: first round each transfer theorem was solved by the ladder (cumulative found_transfer_16)
    first_round = {}
    for s in R.SEEDS:
        fr = {}
        p = os.path.expanduser(f'~/review/rc_data/s{s}/found_transfer_16.jsonl')
        if os.path.exists(p):
            for l in open(p):
                r = json.loads(l)
                if r['name'] in meta:
                    fr[r['name']] = min(fr.get(r['name'], 99), r.get('round') or 99)
        first_round[s] = fr
    res = {'sets': {}, 'curves': {}, 'cov': {}, 'sens': {}, 'meta': {'J2_COST': J2_COST}}
    J2ALL = {s: j2_counts(s) for s in R.SEEDS}

    def pend_any_seed(n):
        """successes of ANY seed's pend over all its attempts on t (x0 / x1 / x2 / x4 + J2)."""
        tot = 0
        for s2 in R.SEEDS:
            for x, v in T['seeds'][str(s2)][n]['counts'].get('pend', {}).items():
                tot += v[0]
            if n in J2ALL[s2]:
                tot += J2ALL[s2][n][0]
        return tot

    def j7_solves(s, x):
        out = set()
        for pool in R.POOLS:
            p7 = f'{ROOT}/artifacts/cd/j7/s{s}_cont__{pool}_x{x}.jsonl'
            if os.path.exists(p7):
                for l in open(p7):
                    r = json.loads(l)
                    if r['n_ok'] > 0:
                        out.add(r['name'])
        return out

    for s in R.SEEDS:
        S = T['seeds'][str(s)]
        J2 = j2_counts(s)
        by, tgt = load_scores(s)
        H = set(sets_j1[str(s)]['H'])
        g_pend = guided_counts(s, 'pend')
        pend_rulesets = set()                       # rule sets of every proof pend ever had accepted (any theorem)
        for n0 in names:
            for x0 in ('0', '1'):
                d0 = R.read(12, s, 'pend', meta[n0]['pool'], int(x0))
                if d0 and n0 in d0:
                    for p0 in d0[n0][2]:
                        pend_rulesets.add(tuple(sorted(set(r for _, r, _ in skeleton(p0)))))
        for v in J2.values():
            for p0 in v[2]:
                pend_rulesets.add(tuple(sorted(set(r for _, r, _ in skeleton(p0)))))

        def pend_all(n):
            c = n_ = 0
            for x, v in S[n]['counts'].get('pend', {}).items():
                c += v[0]; n_ += v[1]
            if n in J2:
                c += J2[n][0]; n_ += J2[n][1]
            return c, n_

        for rl, xs in (('r8', (0, 1)), ('r16', (1, 0))):
            K = k_evalset(s, rl)
            lnK = math.log(K)
            for x in xs:
                key = f's{s}_{rl}_x{x}'
                if not any(S[n]['counts'].get(rl, {}).get(str(x)) for n in names):
                    continue          # this draw was not read (yet): no sets, not empty sets
                D = collections.defaultdict(list)
                rho_all = {}
                for n in names:
                    rec = S[n]
                    cr = rec['counts'].get(rl, {}).get(str(x)); cb = rec['counts'].get('pend', {}).get(str(x))
                    if not cr or not cb:
                        continue
                    solves = cr[0] > 0
                    if not solves:
                        continue
                    pR = cr[0] / cr[1]
                    cB, nB = pend_all(n)
                    base_zero_big = cb[0] == 0 and nB >= K and cB / nB < 1 / K     # not within reach at K_eval-set
                    if cb[0] == 0:
                        D['eqk'].append(n)
                        if nB < K and cB == 0:          # c >= 1 with n < K already means p-hat > 1 / K (reached)
                            D['cm_undet'].append(n)
                    if base_zero_big:
                        D['cm'].append(n)
                        if cB == 0:
                            D['cm0'].append(n)
                        if pR >= 0.5:
                            D['rel'].append(n)
                    terms = by.get(n, {})
                    lab_b, lab_r = f's{s}_pend', f's{s}_{rl}'
                    if cb[0] == 0 and terms:
                        mx = max((v[lab_b][0] for v in terms.values() if lab_b in v), default=-math.inf)
                        if mx < -lnK:
                            D['tfmax'].append(n)
                    if n in H:
                        LB = lse([v[lab_b][0] for v in terms.values() if lab_b in v]) if terms else -math.inf
                        lo = cp_lower(cB, nB)
                        if not (LB >= math.log(2) - lnK or lo >= 1 / K):     # factor-2 margin on the known-proof estimate
                            D['brk_ne'].append(n)
                        # rho: R's mass on known proofs with pi_pend < 1/K (point scores: exact where available else b0)
                        if terms:
                            def rho(sel):
                                num = den = 0.0
                                for tid, v in terms.items():
                                    if lab_b not in v or lab_r not in v or not sel(tid):
                                        continue
                                    w = math.exp(v[lab_r][1])
                                    den += w
                                    if v[lab_b][1] < -lnK:
                                        num += w
                                return num / den if den > 0 else float('nan')
                            r_all = rho(lambda tid: True)
                            r_nod = rho(lambda tid: tid in tgt and not detour(tgt[tid]))
                            rho_all[n] = (r_all, r_nod)
                            if r_all >= 0.5:
                                D['sharp'].append(n)
                            pass
                    if base_zero_big and g_pend is not None and n in g_pend and g_pend[n][0] == 0:
                        D['guided'].append(n)
                    if base_zero_big and meta[n]['pool'] == 'h250' and first_round[s].get(n, 99) >= 2:
                        D['chain'].append(n)
                    # ood: R's accepted proofs of t on this draw all use a rule set absent from K12
                    pr = R.read(12, s, rl, meta[n]['pool'], x)
                    proofs = pr[n][2] if pr and n in pr else []
                    rs = [tuple(sorted(set(r for _, r, _ in skeleton(p)))) for p in proofs]
                    if rs and not any(r in k12_rulesets for r in rs):
                        D['ood'].append(n)
                    if base_zero_big and rs and not any(r in pend_rulesets for r in rs):
                        D['npnt'].append(n)
                D['irt'] = list(irt['dif'].get(f's{s}_{rl}', {}).get('created', []))
                # schema: family-level verdict on holdout250 members, this draw
                fam = collections.defaultdict(list)
                for n in names:
                    if n in fam_of and meta[n]['pool'] == 'h250':
                        fam[fam_of[n]].append(n)
                for f, mem in fam.items():
                    def rate(ck):
                        v = [S[m]['counts'].get(ck, {}).get(str(x)) for m in mem]
                        v = [c for c in v if c]
                        return np.mean([c[0] > 0 for c in v]) if v else float('nan')
                    if rate('pend') <= 0.05 and rate(rl) >= 0.5:
                        D['schema'].extend(mem)
                # relative to the recipe: no seed's base solves t in any attempt
                D['cm_recipe'] = [n for n in D['cm'] if pend_any_seed(n) == 0]
                # net of the compute-matched pretraining continuation (J7), when its reads exist
                c7 = j7_solves(s, x if x in (0, 1) else 1)
                if c7:
                    D['cm_j7'] = [n for n in D['cm'] if n not in c7]
                    D['eqk_j7'] = [n for n in D['eqk'] if n not in c7]
                # net of replay
                for d in list(D):
                    D[d + '_net'] = [n for n in D[d] if not ((S[n]['counts'].get('ctrl8', {}).get(str(x if x in (0, 1) else 1)) or [0])[0] > 0)]
                res['sets'][key] = {k: sorted(set(v)) for k, v in D.items()}
                res['sets'][key + '_rho'] = rho_all
            # set-level compute-matched coverage (draw xs[0])
            x = xs[0]
            r_cov = sum(1 for n in names if (S[n]['counts'].get(rl, {}).get(str(x)) or [0])[0] > 0)
            b_cov = sum(1 for n in names if pend_all(n)[0] > 0)
            b_reach = sum(1 for n in names if pend_all(n)[0] / max(pend_all(n)[1], 1) >= 1 / K)
            c_cov = sum(1 for n in names if (S[n]['counts'].get('ctrl8', {}).get(str(x)) or [0])[0] > 0)
            j7 = j7_solves(s, x)
            res['cov'][f's{s}_{rl}'] = {'rl_solved_256': r_cov, 'base_solved_all': b_cov, 'base_within_K': b_reach,
                                        'ctrl8_solved_256': c_cov, 'j7_solved_256': len(j7) if j7 else None,
                                        'K_evalset': K,
                                        'base_attempts_median_H': float(np.median([pend_all(n)[1] for n in H])) if H else 0,
                                        'base_attempts_min_H': float(min(pend_all(n)[1] for n in H)) if H else 0}
            # elicitation curve over budgets for RL-solved hard theorems
            Ks = np.logspace(np.log10(256), 7, 25)
            cur = []
            Hs = [n for n in H if (S[n]['counts'].get(rl, {}).get(str(x)) or [0])[0] > 0]
            for Kc in Ks:
                el = cr_ = 0
                for n in Hs:
                    terms = by.get(n, {})
                    LB = lse([v[f's{s}_pend'][0] for v in terms.values() if f's{s}_pend' in v]) if terms else -math.inf
                    cB, nB = pend_all(n)
                    if LB >= math.log(2) - math.log(Kc) or cp_lower(cB, nB) >= 1 / Kc:
                        el += 1
                    elif cp_upper(cB, nB) < 0.05 / Kc:
                        cr_ += 1
                cur.append((float(Kc), el, cr_, len(Hs) - el - cr_))
            res['curves'][f's{s}_{rl}'] = cur
        # ---- threshold sensitivity (r8, draw x0): created-set sizes as each definition's threshold moves
        rl, x = 'r8', 0
        K0 = k_evalset(s, rl)
        lab_b = f's{s}_pend'
        cand = [n for n in names if (S[n]['counts'].get(rl, {}).get(str(x)) or [0])[0] > 0
                and (S[n]['counts'].get('pend', {}).get(str(x)) or [1])[0] == 0]          # = eqk on the defining draw
        sens = {'n_eqk': len(cand)}
        for mul in (0.1, 0.3, 1, 3):
            K = K0 * mul
            row = {'K': K, 'cm': 0, 'cm_undet': 0, 'tfmax': 0, 'brk_ne': 0}
            for n in cand:
                cB, nB = pend_all(n)
                terms = by.get(n, {})
                row['cm'] += nB >= K and cB / nB < 1 / K
                row['cm_undet'] += nB < K and cB == 0
                mx = max((v[lab_b][0] for v in terms.values() if lab_b in v), default=-math.inf)
                row['tfmax'] += bool(terms) and mx < -math.log(K)
                if n in H:
                    LB = lse([v[lab_b][0] for v in terms.values() if lab_b in v]) if terms else -math.inf
                    row['brk_ne'] += not (LB >= math.log(2) - math.log(K) or cp_lower(cB, nB) >= 1 / K)
            sens[f'K x{mul}'] = row
        e = {}
        for lab, keys in (('256 (x0)', ('0',)), ('512 (x0+x1)', ('0', '1')), ('all reads', None)):
            def z(n, keys=keys):
                pc = S[n]['counts'].get('pend', {})
                return all((pc.get(k) or [0])[0] == 0 for k in (keys or list(pc)))
            e[lab] = sum(1 for n in cand if z(n))
        sens['eqk base sample'] = e
        cmK0 = [n for n in cand if pend_all(n)[1] >= K0 and pend_all(n)[0] / pend_all(n)[1] < 1 / K0]
        sens['rel q'] = {str(q): sum(1 for n in cmK0 if S[n]['counts'][rl][str(x)][0] / S[n]['counts'][rl][str(x)][1] >= q)
                         for q in (0.1, 0.25, 0.5, 0.75)}
        rh = res['sets'].get(f's{s}_r8_x0_rho', {})
        sens['sharp rho'] = {str(q): sum(1 for n, (ra, rn) in rh.items() if ra >= q) for q in (0.25, 0.5, 0.75, 0.9)}
        fam = collections.defaultdict(list)
        for n in names:
            if n in fam_of and meta[n]['pool'] == 'h250':
                fam[fam_of[n]].append(n)
        def frate(mem, ck):
            v = [S[m]['counts'].get(ck, {}).get(str(x)) for m in mem]
            v = [c for c in v if c]
            return np.mean([c[0] > 0 for c in v]) if v else float('nan')
        sens['schema (pend<=lo, RL>=hi)'] = {f'{lo}/{hi}': sum(len(m) for m in fam.values()
                                             if frate(m, 'pend') <= lo and frate(m, rl) >= hi)
                                             for lo in (0.0, 0.05, 0.1) for hi in (0.3, 0.5, 0.7)}
        res['sens'][f's{s}'] = sens
    # ---- print summary
    print('created-set sizes (of 322) per comparison; _net = minus replay-only-control solves')
    keys = [k for k in res['sets'] if not k.endswith('_rho')]
    print(f'{"def":10s} ' + ' '.join(f'{k:>11s}' for k in keys))
    for d in DEFS + EXTRA:
        print(f'{d:10s} ' + ' '.join(f'{len(res["sets"][k].get(d, [])):11d}' for k in keys))
        print(f'{d + "_net":10s} ' + ' '.join(f'{len(res["sets"][k].get(d + "_net", [])):11d}' for k in keys))
    print('\nset-level compute-matched coverage (r8: draw x0; r16: x1): RL solved@256 vs base within reach at K_eval-set')
    for k, v in res['cov'].items():
        print(f'  {k}: RL {v["rl_solved_256"]} at 256 (replay-only {v["ctrl8_solved_256"]}, J7 {v["j7_solved_256"]}) vs base {v["base_within_K"]} within reach at K_eval-set {v["K_evalset"]:,.0f} '
              f'(p-hat >= 1/K; base ever solved {v["base_solved_all"]}); base attempts on H: median {v["base_attempts_median_H"]:,.0f}, '
              f'min {v["base_attempts_min_H"]:,.0f}')
    print('\nredraw floor (Jaccard, defining draw vs redraw) and seed floor (mean pairwise Jaccard across seeds, defining draw):')
    for d in DEFS:
        rd = [jac(res['sets'][f's{s}_{rl}_x{a}'].get(d, []), res['sets'][f's{s}_{rl}_x{b}'].get(d, []))
              if f's{s}_{rl}_x{a}' in res['sets'] and f's{s}_{rl}_x{b}' in res['sets'] else float('nan')
              for rl, a, b in (('r8', 0, 1), ('r16', 1, 0)) for s in R.SEEDS]
        sd = [jac(res['sets'][f's{i}_r8_x0'].get(d, []), res['sets'][f's{j}_r8_x0'].get(d, [])) for i, j in ((0, 1), (0, 2), (1, 2))]
        print(f'  {d:8s} redraw r8 {" ".join(f"{v:.2f}" for v in rd[:3])} | r16 {" ".join(f"{v:.2f}" for v in rd[3:])} | seeds r8 {" ".join(f"{v:.2f}" for v in sd)}')
    for rl, x in (('r8', 0), ('r16', 1)):
        print(f'\nagreement matrix ({rl}, draw x{x}): mean Jaccard over seeds')
        print(' ' * 9 + ' '.join(f'{d[:7]:>7s}' for d in DEFS))
        mat = {}
        for d1 in DEFS:
            row = []
            for d2 in DEFS:
                js = [jac(res['sets'][f's{s}_{rl}_x{x}'].get(d1, []), res['sets'][f's{s}_{rl}_x{x}'].get(d2, [])) for s in R.SEEDS]
                js = [j for j in js if not math.isnan(j)]
                row.append(float(np.mean(js)) if js else float('nan'))
                mat[f'{d1}|{d2}'] = row[-1]
            print(f'{d1:9s}' + ' '.join(f'{v:7.2f}' for v in row))
        res[f'agree_{rl}'] = mat
        off = [v for k, v in mat.items() if k.split('|')[0] < k.split('|')[1] and not math.isnan(v)]
        print(f'  mean off-diagonal Jaccard {np.mean(off):.3f} over {len(off)} pairs')
    print('\nelicitation curve (r8, RL-solved hard theorems): K -> certified elicited / certified created / undetermined')
    for s in R.SEEDS:
        cur = res['curves'][f's{s}_r8']
        print(f'  s{s}: ' + ' '.join(f'{K:.0e}:{e}/{c}/{u}' for K, e, c, u in cur[::4]))
    print('\nthreshold sensitivity (cap 12, r8, draw x0; K in multiples of K_eval-set): created-set sizes per seed')
    for sk, v in res['sens'].items():
        print(f'  {sk}: eqk (pend 0 / 256 on x0, r8 solves) {v["n_eqk"]}')
        for mul in (0.1, 0.3, 1, 3):
            r = v[f'K x{mul}']
            print(f'    K x{mul:<4} ({r["K"]:9,.0f}): cm {r["cm"]:3d} (undetermined, n < K: {r["cm_undet"]:3d})  tfmax {r["tfmax"]:3d}  brk_ne {r["brk_ne"]:3d}')
        for lab in ('eqk base sample', 'rel q', 'sharp rho', 'schema (pend<=lo, RL>=hi)'):
            print(f'    {lab}: ' + ', '.join(f'{k} -> {c}' for k, c in v[lab].items()))
    json.dump(res, open(f'{OUT}/part3.json', 'w'))


if __name__ == '__main__':
    main()
