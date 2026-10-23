#!/usr/bin/env python3
"""Tables for numbers.md § style-edl, generated from style_edl/results.csv, artifacts/style_edl/compute.csv and
style_edl/streams_manifest.json (run `style-edl`).

  python3 style_edl/numbers_section.py > artifacts/style_edl/numbers_tables.md
"""
import csv, json, math, os, statistics as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDER = ('S_own', 'S_own2', 'S_seed', 'S_RL', 'S_short', 'S_Kal')


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def fmt(v, d=2):
    if v is None:
        return '—'
    if abs(v) >= 100:
        return f'{v:.0f}'
    if abs(v) >= 10:
        return f'{v:.1f}'
    return f'{v:.{d}f}'


def trio(rows, S, k, d=2):
    vs = [f(r.get(k)) for r in rows if r['stream'] == S]
    if any(v is None for v in vs) or len(vs) != 3:
        return '—'
    return ' / '.join(fmt(v, d) for v in vs)


def mean(rows, S, k):
    vs = [f(r.get(k)) for r in rows if r['stream'] == S]
    vs = [v for v in vs if v is not None]
    return st.mean(vs) if vs else None


def main():
    rows = list(csv.DictReader(open(f'{ROOT}/style_edl/results.csv')))
    man = json.load(open(f'{ROOT}/style_edl/streams_manifest.json'))
    out = []
    P = out.append
    P('Per-seed values are s0 / s1 / s2; "mean" is the mean over the three seeds (n = 3: the IQM is the mean). Bits per '
      'proof unless stated; names the environment assigns are not coded. EDL and EDL_c include log₂ 3 bits for the lr choice.\n')
    P('**Table 1 — streams and the learner (before training).**\n')
    P('| stream | identical to the learner\'s greedy proof (of 256) | actions per proof | coded tokens per proof | '
      'TF agreement (per action) | learner bits per proof, test (L0) | starting loss (block [0, 8)) |')
    P('|---|---|---|---|---|---|---|')
    for S in ORDER:
        idn = ' / '.join(f"{man['stream_stats'][f's{s}/{S}']['identical_to_own_greedy']:.3f}" for s in (0, 1, 2))
        P(f"| {S} | {idn} | {trio(rows, S, 'acts_pp', 2)} | {trio(rows, S, 'tok_pp', 1)} | {trio(rows, S, 'tf_agree', 4)} | "
          f"{trio(rows, S, 'L0_test')} | {trio(rows, S, 'start_pp')} |")
    P('\n**Table 2 — EDL (A_ES, lr chosen per seed × stream by prequential code).**\n')
    P('| stream | lr (s0 / s1 / s2) | θ* test loss L_test | EDL per proof | EDL_c per proof | mean EDL_c | EDL_c per action | '
      'cross-fit EDL per proof (exploratory) | A_fixed (E = 4) EDL_c |')
    P('|---|---|---|---|---|---|---|---|---|')
    for S in ORDER:
        lrs = ' / '.join(f"{f(r['lr']):g}" for r in rows if r['stream'] == S)
        P(f"| {S} | {lrs} | {trio(rows, S, 'L_test')} | {trio(rows, S, 'EDL_pp')} | {trio(rows, S, 'EDL_c_pp')} | "
          f"{fmt(mean(rows, S, 'EDL_c_pp'))} | {trio(rows, S, 'EDL_c_pa', 3)} | {trio(rows, S, 'xfit_EDL_pp')} | "
          f"{trio(rows, S, 'fixed_EDL_c_pp')} |")
    P('\n**Table 3 — capability on the 128 test theorems (k 32, T 0.8, sample seed 2; θ* = A_ES at the chosen lr, '
      'order 0).** Learner before: plain pass@32 ' + ' / '.join(fmt(f(r.get('plain_pass32_before')), 3) for r in rows if r['stream'] == 'S_own')
      + ', pass@1 ' + ' / '.join(fmt(f(r.get('plain_pass1_before')), 3) for r in rows if r['stream'] == 'S_own')
      + '; guided pass@32 ' + ' / '.join(fmt(f(r.get('logical_pass32_before')), 3) for r in rows if r['stream'] == 'S_own')
      + ', pass@1 ' + ' / '.join(fmt(f(r.get('logical_pass1_before')), 3) for r in rows if r['stream'] == 'S_own') + '.\n')
    P('| stream | plain pass@32 after | plain pass@1 after | guided pass@32 after | guided pass@1 after | capability fixed? |')
    P('|---|---|---|---|---|---|')
    for S in ORDER:
        ok = []
        for r in rows:
            if r['stream'] != S:
                continue
            a, b = f(r.get('plain_pass32_after')), f(r.get('plain_pass32_before'))
            ok.append(a is not None and b is not None and a >= 0.9 and abs(a - b) <= 0.03)
        P(f"| {S} | {trio(rows, S, 'plain_pass32_after', 3)} | {trio(rows, S, 'plain_pass1_after', 3)} | "
          f"{trio(rows, S, 'logical_pass32_after', 3)} | {trio(rows, S, 'logical_pass1_after', 3)} | "
          f"{'yes (3 / 3)' if all(ok) and len(ok) == 3 else 'no (' + str(sum(ok)) + ' / ' + str(len(ok)) + ')'} |")
    if any(r.get('lv_EDL_c_pp') for r in rows):
        P('\n**Table 4 — the style-blind score ℓ_V (same fits, re-run at the chosen lr).**\n')
        P('| stream | ℓ_V of the learner, test (bits) | ℓ_V θ*, test | ℓ_V EDL per proof | ℓ_V EDL_c per proof | single-string EDL_c of the same re-fits |')
        P('|---|---|---|---|---|---|')
        for S in ORDER:
            P(f"| {S} | {trio(rows, S, 'lv_L0_test', 3)} | {trio(rows, S, 'lv_L_test', 3)} | {trio(rows, S, 'lv_EDL_pp', 3)} | "
              f"{trio(rows, S, 'lv_EDL_c_pp', 3)} | {trio(rows, S, 'lv_ss_EDL_c_pp', 3)} |")
    P('\n**Table 5 — A1, the per-proof attribution (Addendum 1): proofs identical to the learner\'s greedy proof (*same*) '
      'and the rest (*differ*).**\n')
    P('| stream | differing proofs, stream / test | learner bits per differing test proof | θ* bits per differing test proof | '
      'EDL_c per differing proof | EDL_c per same proof | cross-fit, both directions pooled: per differing / per same proof (exploratory) |')
    P('|---|---|---|---|---|---|---|')
    for S in ORDER[1:]:
        nd = ' / '.join(f"{r['n_differ_stream']}–{r['n_differ_test']}" for r in rows if r['stream'] == S)
        P(f"| {S} | {nd} | {trio(rows, S, 'differ_L0_test')} | {trio(rows, S, 'differ_Lth_test')} | "
          f"{trio(rows, S, 'differ_EDL_c_per_proof')} | {trio(rows, S, 'same_EDL_c_per_proof', 3)} | "
          f"{trio(rows, S, 'xfit_differ_EDL_c_per_proof')} / {trio(rows, S, 'xfit_same_EDL_c_per_proof', 3)} |")
    P('\n**Table 7 — the per-block curve (A_ES, chosen lr; seed means of the order means).** Block bits per proof for the '
      'blocks [0, 8) (the learner), [8, 16), [16, 32), [32, 64), [64, 128); then each fit\'s mean bits on the 128 test proofs '
      '(learner, after 8, 16, 32, 64, 128 proofs).\n')
    P('| stream | block bits per proof | test-set curve |')
    P('|---|---|---|')
    for S in ORDER:
        bl = [[float(x) for x in r['blocks_pp'].split()] for r in rows if r['stream'] == S]
        cu = [[float(x) for x in r['curve_test'].split()] for r in rows if r['stream'] == S]
        P(f"| {S} | {' → '.join(fmt(sum(v) / len(v)) for v in zip(*bl))} | {' → '.join(fmt(sum(v) / len(v)) for v in zip(*cu))} |")
    if os.path.exists(f'{ROOT}/artifacts/style_edl/compute.csv'):
        comp = list(csv.DictReader(open(f'{ROOT}/artifacts/style_edl/compute.csv')))
        P('\n**Table 6 — compute per arm (results registry; GPU = RTX A5000, except one guided read redone on an A40; GPU-seconds are process wall time on a GPU '
          'sometimes shared by 2–3 jobs).** Summed over the three seeds.\n')
        P('| arm | phases | GPU-s | train steps | train tokens (M) | gen tokens (M) | Lean checks |')
        P('|---|---|---|---|---|---|---|')
        arms = []
        for r in comp:
            if r['arm'] not in arms:
                arms.append(r['arm'])
        for A in arms:
            rs = [r for r in comp if r['arm'] == A]
            ph = sorted({r['phase'] for r in rs})
            sm = lambda k: sum(f(r[k]) or 0 for r in rs)
            P(f"| {A} | {', '.join(ph)} | {sm('gpu_seconds'):.0f} | {sm('train_steps'):.0f} | {sm('train_tokens') / 1e6:.1f} | "
              f"{sm('gen_tokens') / 1e6:.2f} | {sm('lean_checks'):.0f} |")
    print('\n'.join(out))


if __name__ == '__main__':
    main()
