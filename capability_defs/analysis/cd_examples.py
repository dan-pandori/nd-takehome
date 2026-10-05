#!/usr/bin/env python3
"""capability-defs: worked examples for REPORT.md (Lean renderings of proofs + every number the definitions use).

  python3 capability_defs/analysis/cd_examples.py SEED NAME [NAME ...] [--ev] > capability_defs/analysis/out/examples_<...>.md
  (--ev: also r8's eventual proof, i.e. the ladder's own proof of t, rebuilt from trajectory's score targets)

For each theorem: the statement; pend's attempts and successes (x0 / x1 / x2 / J2) and its k-to-solve interval
[1 / UB95, 1 / LB] (LB = known-proof sum at T 0.8, exact 33-base terms where scored); r8 / r16 p-hat; the replay-only
control; the other seeds' pend; RL's shortest accepted proof rendered in Lean (nd2lean), and pend's best known proof if
different, with their log p under pend.
"""
import gzip, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
import cd_reads as R
import nd2lean
from lean_check import check as lean_check


def lean_meta(src):
    """(Lean accepts?, term size = inference nodes of the elaborated value, lines) for one rendered theorem."""
    res, _, _ = lean_check([src], workers=1)
    r = res[0]
    return r['ok'], r.get('size'), sum(1 for l in src.splitlines() if l.strip().startswith('have'))
from cd_bracket import cp_upper, lse, LN33
from cd_part3 import load_scores, j2_counts

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')


def ev_proof(s, n, prompt):
    """r8's eventual proof of n (trajectory's score targets, kind 'ev'), rebuilt as an ND proof by replaying its
    base-0 actions through the proof-state environment."""
    from state_env import Env
    p = os.path.expanduser(f'~/work/trajectory/artifacts/tj/score/s{s}/targets.jsonl')
    for l in open(p):
        m = json.loads(l)
        if m['tid'] == f'ev:{n}':
            env = Env(prompt, canon=True)
            for a in m['actions_b0']:
                ok, why = env.apply(a.split())
                if not ok:
                    return None
            y = env.nd()
            return None if y.startswith('LEANPARSE') else y
    return None


EV = '--ev' in sys.argv


def main():
    s = int(sys.argv[1]); names = [a for a in sys.argv[2:] if a != '--ev']
    T = json.load(open(f'{OUT}/table_c12.json'))
    S = T['seeds'][str(s)]; meta = T['meta']
    by, tgt = load_scores(s)
    J2 = j2_counts(s)
    for n in names:
        rec = S[n]; c = rec['counts']
        cB = sum(v[0] for v in c.get('pend', {}).values()) + (J2[n][0] if n in J2 else 0)
        nB = sum(v[1] for v in c.get('pend', {}).values()) + (J2[n][1] if n in J2 else 0)
        terms = by.get(n, {})
        lab = f's{s}_pend'
        vals = [(v[lab][0], tid) for tid, v in terms.items() if lab in v]
        LB = lse([v for v, _ in vals]) if vals else -math.inf
        ub = cp_upper(cB, nB)
        print(f'### {n} (seed {s}; {meta[n]["pool"]})\n')
        print(f'`{meta[n]["prompt"]}`\n')
        est = math.exp(LB) if LB > -math.inf else 0.0
        kt = f'{1 / est:,.3g}' if est > 0 else 'no known proof scored'
        pt = f'; point estimate 1 / p-hat = {nB / cB:,.0f}' if cB else ''
        print(f'- pend: {cB} successes in {nB:,} attempts. k-to-solve: sampling >= {1 / ub:,.0f} (UB95 {ub:.2e}){pt}; '
              f'known-proof estimate {kt} (sum over {len(vals)} known proofs = e^{LB:.1f})'
              + (' — the estimate exceeds the sampling UB95 here' if est > ub else ''))
        for ck, xs in (('r8', ('0', '1', '2')), ('r16', ('0', '1')), ('ctrl8', ('0', '1'))):
            v = [c.get(ck, {}).get(x) for x in xs]; v = [u for u in v if u]
            if v:
                print(f'- {ck}: {sum(u[0] for u in v)} / {sum(u[1] for u in v)}')
        other = []
        for s2 in (0, 1, 2):
            if s2 != s:
                v = [T['seeds'][str(s2)][n]['counts'].get('pend', {}).get(x) for x in ('0', '1', '2')]
                v = [u for u in v if u]
                other.append(f's{s2} pend {sum(u[0] for u in v)} / {sum(u[1] for u in v)}')
        print('- other seeds: ' + '; '.join(other))
        # RL's shortest accepted proof (r8 x0 read) and pend's best known proof
        d = R.read(12, s, 'r8', meta[n]['pool'], 0)
        prs = sorted(d[n][2], key=lambda p: (p.count(';'), p)) if d and n in d else []
        if prs:
            y = prs[0]
            lp = next((v for v, tid in vals if tgt.get(tid) == y), None)
            src = nd2lean.translate(meta[n]['prompt'], y, require_all_pr=False)
            ok, size, nl = lean_meta(src)
            print(f'\nr8\'s shortest accepted proof (log p under pend at T 0.8: {lp if lp is None else round(lp, 1)}; Lean {"accepts" if ok else "REJECTS"}; '
                  f'{nl} `have` lines; term size {size}):\n')
            print('```lean\n' + src + '\n```')
        if EV:
            evp = ev_proof(s, n, meta[n]['prompt'])
            if evp:
                lp = rec['tf']['ev'].get('pend', {}).get('T0.8', {}).get('total')
                src = nd2lean.translate(meta[n]['prompt'], evp, require_all_pr=False)
                ok, size, nl = lean_meta(src)
                print(f'\nr8\'s eventual proof (the ladder\'s proof of t; log p under pend at T 0.8: '
                      f'{lp if lp is None else round(lp, 1)}; Lean {"accepts" if ok else "REJECTS"}; {nl} `have` lines; term size {size}):\n')
                print('```lean\n' + src + '\n```')
        if vals:
            best = max(vals)
            yb = tgt.get(best[1])
            if yb and (not prs or yb != prs[0]):
                src = nd2lean.translate(meta[n]['prompt'], yb, require_all_pr=False)
                ok, size, nl = lean_meta(src)
                print(f'\npend\'s most probable known proof (log p {best[0]:.1f}; Lean {"accepts" if ok else "REJECTS"}; {nl} `have` lines; term size {size}):\n')
                print('```lean\n' + src + '\n```')
        print()


if __name__ == '__main__':
    main()
