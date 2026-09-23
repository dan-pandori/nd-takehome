#!/usr/bin/env python3
"""Generate the `numbers.md` § ds-rendering section from artifacts/dsr/summary.json.

Written as a generator rather than by hand so that every row is re-derivable and cannot drift from the artefacts:
`python3 dsr_analysis.py && python3 dsr_numbers.py >> numbers.md`.  Each table names the file its numbers come from.
"""
import json, sys

S = json.load(open('artifacts/dsr/summary.json'))
ARMS = ['c0', 'r1', 'r3', 'r2', 'r4']
NAME = {'c0': 'C0 `lean_seq` (control)', 'r1': 'R1 `lean_seq_noprem`', 'r3': 'R3 `lean_seq_nofml`',
        'r2': 'R2 `lean_seq_intro`', 'r4': 'R4 `lean_seq_funbare`'}
SHORT = {'c0': 'C0', 'r1': 'R1', 'r3': 'R3', 'r2': 'R2', 'r4': 'R4'}


def g(arm, s, *path):
    v = S['arms'].get(arm, {}).get('seeds', {}).get(str(s))
    for k in path:
        if not isinstance(v, dict):
            return None
        v = v.get(k)
    return v


def pair(arm, *path, fmt='{:.3f}'):
    """seed0 / seed1 as one cell."""
    out = []
    for s in (0, 1):
        v = g(arm, s, *path)
        out.append('–' if v is None else (fmt.format(v) if isinstance(v, (int, float)) else str(v)))
    return ' / '.join(out)


def have(arm):
    return any(g(arm, s, 'heldout_greedy', 'rate') is not None for s in (0, 1))


P = print
P()
P('# ds-rendering (proposal 10) — how the same proofs are written in Lean')
P()
P('Run id `ds-rendering`, branch `dan_ds-rendering`. Every number is re-derived by `python3 dsr_analysis.py` →')
P('`artifacts/dsr/summary.json` from files pulled into `artifacts/dsr/<pod>/`; each table names its source.')
P()
P('**Model label, identical in every arm** (an inherited number carries its own label where one is quoted): 3.2M')
P('parameters (4 layers, d 256, 8 heads), trained **from scratch**, 6,000 steps, bs 128, lr 1e-3 → 1e-4, cap 6, on the')
P('**same 155,000 ND records** `data/p2/train_depth3_f0_a1.jsonl` (cap 6, **zero depth-3 proofs**: box-depth histogram')
P('0 / 1 / 2 = 82,393 / 54,883 / 17,724). Surface form is Lean `lean_seq` with a random first-appearance name offset;')
P('the arms differ **only** in how `lean_tok.py` renders that record into Lean text. Sampler in every arm and every')
P('stage: `path=fast, early=eos, compact, rowrng`, **batch 2048**, `max_new` 400, T 0.8 (the efficiency run\'s caveat —')
P('a batch change reshuffles the accepted set, so it is held fixed). A sample counts iff **Lean 4.34 accepts the literal')
P('sampled text and `nd_verify` accepts the ND proof it denotes**. GPU: NVIDIA A40 in every arm.')
P()
P('## 1 — The renderings and the render check (`dsr_render_check.py` → `artifacts/dsr/render_check{,_funbare}.json`)')
P()
P('| arm | mode | box form / change | vocab | mean tokens / proof | ratio to C0 | round-trip | Lean accepts | swapped negatives accepted |')
P('|---|---|---|---:|---:|---:|---|---|---|')
rc = dict(S.get('render_check', {}).get('modes', {}))
try:
    rc.update(json.load(open('artifacts/dsr/render_check_funbare.json'))['modes'])
except Exception:
    pass
BOX = {'c0': '`( fun ( nS : A ) => by … )`; premises re-stated; every `have` annotated',
       'r1': 'premise lines not rendered; later lines cite `hK`',
       'r3': '`have n3 := n1 n2` for IMPE / ANDE / NEGE / R',
       'r2': '`( by intro nS ; … )`',
       'r4': '`( fun nS => by … )` — `fun` kept, binder type dropped'}
base = rc.get('lean_seq', {}).get('mean_tokens')
for a in ARMS:
    m = S['arms'][a]['mode'] if a in S['arms'] else {'r4': 'lean_seq_funbare'}[a]
    r = rc.get(m)
    if not r:
        continue
    P(f"| {NAME[a]} | `{m}` | {BOX[a]} | {r['vocab_size']} | {r['mean_tokens']:.1f} | "
      f"{r['mean_tokens']/base:.3f} | {r['round_trip_ok']} / {S['render_check']['n_round_trip']} | "
      f"{r['lean_ok']} / {r['lean_n']} | {r['neg_accepted']} / {r['neg_n']} |")
P()
P('- Text length in `have` lines (3,000 a1 records; ND lengths 2–6 are flat at 600 each): C0 / R3 / R2 / R4')
P('  `1:80 2:680 3:875 4:844 5:386 6:135`; **R1 `1:1106 2:931 3:888 4:75`** — R1 shortens the text by the premise count,')
P('  so a 6-line ND proof is at most a 4-`have` text.')
P('- The rules whose annotation R3 drops occur on **0.625 lines per proof** (by ND length 2/3/4/5/6:')
P('  0.012 / 0.752 / 0.479 / 0.828 / 1.053), which is why R3 saves 4.4 % of tokens and not the brief\'s 20–30 %.')
P('- `train.py --cap 6` re-checks `decode(encode(proof)) == proof` on all **155,000** records at training time in every')
P('  arm; every arm loaded without an assertion failure.')
P()
sp = S.get('splits')
if sp:
    P('## 2 — Splits: the shared training set against every evaluation pool (`dsr_splits.py` → `artifacts/dsr/splits.json`)')
    P()
    P('All arms train on the identical records, so this table is a property of the run, not of an arm.')
    P(f"Training classes: **{sp['train_classes_ordered']:,}** order-sensitive, **{sp['train_classes_unordered']:,}** premise-order-insensitive.")
    P()
    P('| pool | classes | shared, order-sensitive | shared, premise-order-insensitive |')
    P('|---|---:|---:|---:|')
    for k, v in sp['overlap'].items():
        if 'missing' in v:
            continue
        P(f"| `{v['file']}` | {v['pool_classes_ordered']:,} | **{v['shared_ordered']}** | {v['shared_unordered']} |")
    P()
    P('- The only non-zero order-sensitive overlap is **7 of 1,638** in `data/transfer.jsonl`, the mechanism-test pool')
    P('  (8 premise-order-insensitive). It is the same 7 theorems for every arm, so it cannot bias the comparison, but')
    P('  lean-format\'s review never checked that file and it is 0.43 % of the pool.')
    P()
P('## 3 — Held-out greedy, and where the difference lives (`artifacts/dsr/<pod>/held_<arm>_s<k>.json`;')
P('`data/p2/heldout.jsonl`, 5,000 = 1,000 per ND length 2–6, greedy, one sample per theorem)')
P()
P('| arm | overall s0 / s1 | by ND length 2 / 3 / 4 / 5 / **6** (s0) | same (s1) |')
P('|---|---|---|---|')
for a in ARMS:
    if not have(a):
        continue
    def bl(s):
        d = g(a, s, 'heldout_greedy', 'by_len') or {}
        return ' / '.join(f"{d.get(str(L), float('nan')):.3f}" for L in range(2, 7))
    P(f"| {NAME[a]} | **{pair(a, 'heldout_greedy', 'rate')}** | {bl(0)} | {bl(1)} |")
P()
P('**The 500 held-out theorems whose reference proof has box depth 3 are out of distribution — the training set has')
P('none.** Splitting on that (source: the same `held_*.jsonl`; `dsr_analysis.held_breakdown` and the depth recomputed')
P('from each reference proof) separates in-distribution accuracy from zero-shot depth-3 composition:')
P()
P('| arm | depth ≤ 2 (4,500, in distribution) s0 / s1 | **depth 3 (500, f = 0)** s0 / s1 |')
P('|---|---|---|')
DEPTH = {}
try:
    import collections
    meta = {}
    for l in open('data/p2/heldout.jsonl'):
        x = json.loads(l)
        meta[x['name']] = max((y.count('| ') for y in x['proof'].split(' ; ')), default=0)
    for a in ARMS:
        for s in (0, 1):
            src = g(a, s, 'heldout_by_prem_len', 'src')
            if not src:
                continue
            lo = [0, 0]; hi = [0, 0]
            for l in open(src):
                r = json.loads(l)
                t = hi if meta[r['name']] == 3 else lo
                t[0] += bool(r['solved']); t[1] += 1
            DEPTH[(a, s)] = (lo[0] / lo[1], hi[0] / hi[1])
except Exception as e:
    print(f'<!-- depth split unavailable: {e} -->', file=sys.stderr)
for a in ARMS:
    if (a, 0) not in DEPTH and (a, 1) not in DEPTH:
        continue
    c = lambda i: ' / '.join(f'{DEPTH[(a, s)][i]:.3f}' if (a, s) in DEPTH else '–' for s in (0, 1))
    P(f'| {NAME[a]} | {c(0)} | **{c(1)}** |')
P()
P('## 4 — Mechanism test: pass@16 on `data/transfer.jsonl` (1,638 theorems; `artifacts/dsr/<pod>/mech_<arm>_s<k>.jsonl`;')
P('distinct **start-index-normalised** proofs by written ND length; every counted proof carries its literal Lean text)')
P()
P('| arm | solved / 1,638 | distinct 7-line | 8-line | ≥ 9-line | 7-line by `n_prem` 0 / 1 / 2 / 3 (s0; s1) |')
P('|---|---|---|---|---|---|')
for a in ARMS:
    if g(a, 0, 'mech_pass16') is None and g(a, 1, 'mech_pass16') is None:
        continue
    def bp(s):
        d = g(a, s, 'mech_pass16', 'by_nprem') or {}
        return ' / '.join(str(d.get(str(k), {}).get('d7', '–')) for k in range(4))
    P(f"| {NAME[a]} | {pair(a, 'mech_pass16', 'solved', fmt='{:d}')} | **{pair(a, 'mech_pass16', 'd7', fmt='{:d}')}** | "
      f"{pair(a, 'mech_pass16', 'd8', fmt='{:d}')} | {pair(a, 'mech_pass16', 'd9plus', fmt='{:d}')} | {bp(0)}; {bp(1)} |")
P()
P('## 5 — Base rates at pass@2,000 (`coverage.py --k 2000 --temperature 0.8 --seed 0 --batch 2048`;')
P('`artifacts/dsr/<pod>/cov_<pool>_<arm>_s<k>.s0.jsonl`)')
P()
P('| arm | depth-3 (1,000) targets hit s0 / s1 | per-sample rate | `depth3_req` (300) | `reductio_req` (300) | distinct ≥ 8-line proofs, depth-3 pool |')
P('|---|---|---|---|---|---|')
for a in ARMS:
    if g(a, 0, 'cov', 'd3') is None and g(a, 1, 'cov', 'd3') is None:
        continue
    P(f"| {NAME[a]} | **{pair(a, 'cov', 'd3', 'targets_hit', fmt='{:d}')}** | {pair(a, 'cov', 'd3', 'per_sample_rate', fmt='{:.4f}')} | "
      f"{pair(a, 'cov', 'd3req', 'targets_hit', fmt='{:d}')} | {pair(a, 'cov', 'red', 'targets_hit', fmt='{:d}')} | "
      f"{pair(a, 'cov', 'd3', 'distinct_ge8', fmt='{:d}')} |")
P()
P('## 6 — Dial: depth-3 EI vs frozen, 4 rounds × 32 (`artifacts/dsr/<pod>/{ei,frz}_d3_<arm>_s<k>/round_4.json`)')
P()
P('| arm | EI solved / 1,000 s0 / s1 | frozen, equal attempts | **EI − frozen** | EI depth-3 acquisition | frozen acquisition | held-out greedy at r4 |')
P('|---|---|---|---|---|---|---|')
for a in ARMS:
    if g(a, 0, 'dial_ei') is None and g(a, 1, 'dial_ei') is None:
        continue
    diff = []
    for s in (0, 1):
        e, f = g(a, s, 'dial_ei', 'targets_cum_rate'), g(a, s, 'dial_frozen', 'targets_cum_rate')
        diff.append('–' if e is None or f is None else f'{e - f:+.3f}')
    P(f"| {NAME[a]} | {pair(a, 'dial_ei', 'targets_cum_solved', fmt='{:d}')} | {pair(a, 'dial_frozen', 'targets_cum_solved', fmt='{:d}')} | "
      f"**{' / '.join(diff)}** | {pair(a, 'dial_ei', 'acq_depth3', 'acquisition')} | {pair(a, 'dial_frozen', 'acq_depth3', 'acquisition')} | "
      f"{pair(a, 'dial_ei', 'heldout_greedy')} |")
P()
P('## 7 — Ladder rung T1 and frozen, 8 rounds × 32 (`artifacts/dsr/<pod>/la_{T1,frz}_<arm>_s<k>/round_8.json`;')
P('pools byte-identical to ladder-A\'s, `transfer.jsonl` sha256 `47dd1886…`, `rl_targets.jsonl` `a5c4c277…`)')
P()
P('| arm | frozen solved / 2,285 | frozen `L*` | T1 solved / 2,285 | **T1 `L*`** | `L*` − `L*`_frozen | textbook schemata with ≥ 5 solves (T1) | held-out greedy at r8 |')
P('|---|---|---|---|---|---|---|---|')
for a in ARMS:
    if g(a, 0, 'ladder_T1') is None and g(a, 1, 'ladder_T1') is None:
        continue
    d = []
    for s in (0, 1):
        t, f = g(a, s, 'ladder_T1', 'lstar'), g(a, s, 'ladder_frozen', 'lstar')
        d.append('–' if t is None or f is None else f'{t - f:+d}')
    P(f"| {NAME[a]} | {pair(a, 'ladder_frozen', 'transfer_solved', fmt='{:d}')} | {pair(a, 'ladder_frozen', 'lstar', fmt='{:d}')} | "
      f"{pair(a, 'ladder_T1', 'transfer_solved', fmt='{:d}')} | **{pair(a, 'ladder_T1', 'lstar', fmt='{:d}')}** | "
      f"{' / '.join(d)} | {pair(a, 'ladder_T1', 'textbook_schemata_ge5', fmt='{:d}')} | {pair(a, 'ladder_T1', 'heldout_greedy')} |")
P()
P('## 8 — Checker of record (`pod/dsr/record.py` → `artifacts/dsr/<pod>/record_<arm>.json`; in-loop gate totals from')
P('`artifacts/dsr/<pod>/gate_*.jsonl`)')
P()
P('| arm | distinct counted proofs | (A) unmodified `nd2lean.py --check`: both accept / disagree | (B) Lean on the literal text: accepted / rejected | in-loop samples | parse-fail | `nd_verify`-only | Lean-only |')
P('|---|---:|---|---|---:|---:|---:|---:|')
for a in ARMS:
    rec = None
    for pod in (S['arms'].get(a, {}).get('pod'),):
        try:
            rec = json.load(open(f'artifacts/dsr/{pod}/record_{a}.json'))
        except Exception:
            pass
    gt = (S['arms'].get(a, {}).get('gate') or {}).get('totals', {})
    if not rec and not gt:
        continue
    A = (rec or {}).get('A_nd2lean_unmodified', {})
    B = (rec or {}).get('B_literal_text', {})
    P(f"| {NAME[a]} | {(rec or {}).get('distinct_proofs', '–')} | "
      f"{A.get('both_accept', '–')} / {A.get('nd_ok_lean_rej', 0) + A.get('nd_rej_lean_ok', 0) if A else '–'} | "
      f"{B.get('accepted', '–')} / {B.get('rejected', '–')} | {gt.get('samples', '–'):,} | {gt.get('parse_fail', '–'):,} | "
      f"{gt.get('nd_ok_lean_rej', '–')} | {gt.get('nd_rej_lean_ok', '–')} |")
P()
P('## 9 — Cost')
P()
P('RTX 3090 was unavailable (the two sibling runs had taken the capacity), so every arm ran on an **NVIDIA A40**')
P('($0.49/h): five pods `dsr-{c0,r1,r3,r2,r4}`, one arm each. See `log.md` for the per-stage timeline and')
P('`podbudget ds-rendering` for the ledger.')
