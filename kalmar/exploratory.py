#!/usr/bin/env python3
"""Exploratory tables (pre-registration Addendum 3, NOT pre-registered): is the EI jump RL or annealing?

  python3 kalmar/exploratory.py > artifacts/kalmar/exploratory_stdout.txt

Models:
- KAL-D s0–s2: data-matched Kalmár pretraining.
- KAL-D+A s0–s2: KAL-D + the ladder's fine-tune command (600 steps, lr 3e-4 → 3e-5, 128 proofs per step) on 20,000
  replayed K12-Kalmár records, without EI proofs (`ckpts/kalmar/anneal/kalDA_s<S>.pt`).
- EI r1 / r2: the EI ladder's checkpoints after 1 / 2 rounds from KAL-D s0 (`ckpts/kalmar/ladder/la_kal_ei_s0_r<R>.pt`).
- control s0–s2: K12-trained.

Reads (greedy, batch 1,024, RTX 3090 or A40; Lean on the literal text):
- teacher-forced agreement and greedy free generation on tf1200;
- greedy on val300 (the ladder's held-out greedy);
- the greedy suite on the standard and generalisation sets;
- for s0, one k 16 sampling of the 1,000 EI targets (T 0.8, seed 2, batch 1,024);
- plain k 32 (T 0.8, seed 1, batch 1,024; the control's at 2,048) on the standard and generalisation sets.
MDD = 3.04 × the pooled per-seed sd (n = 3 per arm), as in `kalmar/gen_verdicts.py`.
"""
import gzip, json, os, statistics as st
from analysis import SETS, passk, read_counts

A = 'artifacts/kalmar'


def jl(fn):
    return json.load(open(fn)) if os.path.exists(fn) else None


def tf(t):
    d = jl(f'{A}/tf/{t}__tf1200.json')
    return None if not d else d['agreement']['all']['rate']


def fg(t, s='tf1200'):
    d = jl(f'{A}/free/{t}__{s}_greedy.json')
    if not d:
        return None
    b = d['by']['all']
    return b['valid'] / b['n'], b['follow'] / b['n'], d['by']


def pct(x):
    return '—' if x is None else f'{100 * x:.1f}'


def targets(t):
    fn = f'{A}/eval/{t}_targets_k16.rows.jsonl.gz'
    if not os.path.exists(fn):
        return None
    rows = [json.loads(l) for l in gzip.open(fn, 'rt')]
    return sum(r['n_ok'] > 0 for r in rows), len(rows)


def main():
    P = print
    P('**Exploratory (Addendum 3): annealing vs EI — teacher-forced agreement and greedy free generation**\n')
    P('| model | TF agreement % | tf1200 greedy valid % | exact Kalmár % | 4-atom valid % | val300 greedy valid % |')
    P('|---|---|---|---|---|---|')
    for t, lab in [('kalD_s0', 'KAL-D s0'), ('kalD_s1', 'KAL-D s1'), ('kalD_s2', 'KAL-D s2'),
                   ('kalDA_s0', 'KAL-D+A s0'), ('kalDA_s1', 'KAL-D+A s1'), ('kalDA_s2', 'KAL-D+A s2'),
                   ('la_kal_ei_s0_r1', 'EI r1 (from KAL-D s0)'), ('la_kal_ei_s0_r2', 'EI r2 (from KAL-D s0)')]:
        g = fg(t); v = fg(t, 'val300')
        a4 = None if not g else g[2]['atoms=4']['valid'] / g[2]['atoms=4']['n']
        P(f"| {lab} | {pct(tf(t))} | {pct(g[0] if g else None)} | {pct(g[1] if g else None)} | {pct(a4)} | {pct(v[0] if v else None)} |")
    # pre-registered "learned" criteria on the annealed models
    P('\n**"Learned" criteria** (≥ 99 % TF and ≥ 95 % per step type; exact-follow ≥ 90 % at 1–2 atoms, ≥ 60 % at 4):\n')
    for t in ('kalDA_s0', 'kalDA_s1', 'kalDA_s2', 'la_kal_ei_s0_r2'):
        d = jl(f'{A}/tf/{t}__tf1200.json'); g = fg(t)
        if not d or not g:
            continue
        worst = min((v['rate'], k) for k, v in d['agreement'].items() if k.startswith('tagg=') and v['n'] >= 500)
        ex = [g[2][f'atoms={k}']['follow'] / g[2][f'atoms={k}']['n'] for k in (1, 2, 4)]
        ok = d['agreement']['all']['rate'] >= 0.99 and worst[0] >= 0.95 and min(ex[:2]) >= 0.90 and ex[2] >= 0.60
        P(f"- {t}: TF {pct(d['agreement']['all']['rate'])}, worst step type {worst[1][5:]} {pct(worst[0])}, exact-follow 1/2/4 atoms "
          f"{' / '.join(pct(x) for x in ex)} -> {'learned' if ok else 'not learned'}")
    P('\n**Targets (the ladder\'s 1,000 EI targets), solved at k 16**\n')
    for t, lab in [('kalD_s0', 'KAL-D s0 (seed-2 re-draw of round 1)'), ('kalDA_s0', 'KAL-D+A s0')]:
        x = targets(t)
        P(f"- {lab}: {'—' if not x else f'{x[0]} / {x[1]}'}")
    P('- EI ladder, targets solved in the round (round_<r>.json; round 3 from the log, its json was not written):')
    P('  - EI: round 1 (KAL-D s0) 135, round 2 (EI r1) 572, round 3 (EI r2) 668 of 1,000;')
    P('  - frozen (KAL-D s0, re-drawn each round): 135 / 138 / 146 / 119; held-out greedy (val300) 87 / 300 every round;')
    P('  - EI held-out greedy 87 → 215 → 223 / 300.')
    # greedy suite on the standard / generalisation sets
    P('\n**Greedy suite, % of theorems Lean-valid (KAL-D vs KAL-D+A vs control)**\n')
    sets = ['holdout250', 'rr600', 'ge17', 'long2', 'candidate_v0', 'candidate_v1', 'batch3', 'hand_proved_14',
            'g1_premises', 'g2_large', 'g3_classical']
    P('| set | KAL-D | KAL-D+A | control |')
    P('|---|---|---|---|')
    for s in sets:
        row = []
        for arm in ('kalD', 'kalDA', 'ctl'):
            vs = [fg(f'{arm}_s{i}', s) for i in range(3)]
            vs = [100 * v[0] for v in vs if v]
            row.append(' / '.join(f'{x:.1f}' for x in vs) + (f' ({st.mean(vs):.1f})' if len(vs) > 1 else '') if vs else '—')
        P(f'| {s} | ' + ' | '.join(row) + ' |')
    g1 = {}
    for arm in ('kalD', 'kalDA', 'ctl'):
        vs = []
        for i in range(3):
            d = jl(f'{A}/free/{arm}_s{i}__g1_supplied_greedy.json')
            if d:
                vs.append(d['solved_theorems'])
        g1[arm] = vs
    P(f"\nG1 with premise lines supplied, greedy, theorems solved of 200: KAL-D {g1['kalD']}, KAL-D+A {g1['kalDA']}, control {g1['ctl']}")
    # plain k 32 (T 0.8, sample seed 1): KAL-D and KAL-D+A at batch 1,024, the control at 2,048 (Addendum 2's check)
    P('\n**Plain k 32 (T 0.8, seed 1), theorems solved (unbiased pass@32; per seed, then mean)**\n')
    P('| set | n | KAL-D | KAL-D+A | control | KAL-D+A − control (MDD) |')
    P('|---|---|---|---|---|---|')
    cnt = {(arm, i): read_counts(f'{A}/eval/{arm}_s{i}_plain_k32.rows.jsonl.gz') for arm in ('kalD', 'kalDA', 'ctl') for i in range(3)}
    for lab, fl in SETS:
        row, means = [], {}
        n = None
        for arm in ('kalD', 'kalDA', 'ctl'):
            vs = []
            for i in range(3):
                c = cnt[(arm, i)]
                if c:
                    ks = [k for k in c if k[0] == fl]
                    if ks:
                        vs.append(sum(passk(*c[k], 32) for k in ks)); n = len(ks)
            means[arm] = vs
            row.append(' / '.join(f'{x:.0f}' for x in vs) + (f' ({st.mean(vs):.1f})' if len(vs) > 1 else '') if vs else '—')
        a_, c_ = means['kalDA'], means['ctl']
        d = f'{st.mean(a_) - st.mean(c_):+.1f} ({3.04 * ((st.variance(a_) + st.variance(c_)) / 2) ** 0.5:.1f})' \
            if len(a_) == 3 and len(c_) == 3 else '—'
        P(f'| {lab} | {n or "—"} | ' + ' | '.join(row) + f' | {d} |')


if __name__ == '__main__':
    main()
