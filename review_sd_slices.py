#!/usr/bin/env python3
# (reviewer of run stage1-dynamics; independent of the executor.  Phase 1 was run in ~/review/stage1-dynamics.)
"""Reviewer's independent re-derivation of the stage1-dynamics held-out slices.

Nothing here imports the run's code.  My own ND-proof line counter and my own
depth counter, my own Wilson interval, my own term-size measure.
"""
import json, gzip, math, os, sys, glob, collections

HELD = 'data/p2/heldout.jsonl'


def nd_lines(proof):
    """ND body 'N1 ... ; N2 ... ; QED' -> list of (idx, depth, rule).  My own parser:
    a line is 'N<k> [| ...] <formula> : <RULE> [refs] ;'."""
    out = []
    for chunk in proof.split(';'):
        t = chunk.split()
        if not t or t[0] == 'QED':
            continue
        assert t[0][0] == 'N', chunk
        idx = int(t[0][1:])
        d = 0
        j = 1
        while j < len(t) and t[j] == '|':
            d += 1; j += 1
        # rule token is the one after the ':' that separates formula from rule
        ci = len(t) - 1
        while t[ci][0] == 'N' and t[ci][1:].isdigit():
            ci -= 1
        rule = t[ci]
        out.append((idx, d, rule))
    return out


def my_depth3(proof):
    """True iff the proof has a line nested three boxes deep."""
    return max(d for _, d, _ in nd_lines(proof)) >= 3


def my_nlines(proof):
    return len(nd_lines(proof))


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1 + z*z/n
    mid = (p + z*z/(2*n)) / den
    hw = z/den * math.sqrt(p*(1-p)/n + z*z/(4*n*n))
    return (max(0.0, mid-hw), min(1.0, mid+hw))


def load_held():
    recs = [json.loads(l) for l in open(HELD) if l.strip()]
    for r in recs:
        r['my_nlines'] = my_nlines(r['proof'])
        r['my_depth3'] = my_depth3(r['proof'])
    return recs


def read_ev(path):
    op = gzip.open if path.endswith('.gz') else open
    with op(path, 'rt') as f:
        return [json.loads(l) for l in f if l.strip()]


def main():
    held = load_held()
    # --- premise 1: do my line counts and depth flags match the pool's own labels? ---
    bad_l = sum(1 for r in held if r['my_nlines'] != r['n_lines'])
    bad_d = sum(1 for r in held if r['my_depth3'] != bool(r['pat']['depth3']))
    print(f'heldout n={len(held)}  my n_lines disagreements={bad_l}  my depth3 disagreements={bad_d}')
    print('  my bins:', dict(sorted(collections.Counter(r['my_nlines'] for r in held).items())))
    print('  my depth3 count:', sum(1 for r in held if r['my_depth3']),
          ' of which 6-line:', sum(1 for r in held if r['my_depth3'] and r['my_nlines'] == 6))
    names = [r['name'] for r in held]
    assert len(set(names)) == len(names)
    my = {r['name']: r for r in held}

    # --- per-checkpoint recount ---
    rows = {}
    for jf in sorted(glob.glob('artifacts/sd/ev/*.json')):
        stem = os.path.basename(jf)[:-5]
        lf = jf[:-5] + '.jsonl'
        if not os.path.exists(lf):
            lf += '.gz'
        if not os.path.exists(lf):
            print('MISSING raw for', stem); continue
        recs = read_ev(lf)
        ex = json.load(open(jf))
        assert len(recs) == len(held), (stem, len(recs))
        # align by name; verify the eval's own labels against mine
        mis_l = mis_d = 0
        for r in recs:
            h = my[r['name']]
            if r['n_lines'] != h['my_nlines']: mis_l += 1
            if bool(r['depth3']) != h['my_depth3']: mis_d += 1
        # my slices, keyed off MY labels
        sl = collections.defaultdict(list)
        for r in recs:
            h = my[r['name']]
            ok = bool(r['lean_ok'])
            sl['all'].append((ok, r))
            sl[f'len{h["my_nlines"]}'].append((ok, r))
            if h['my_depth3']:
                sl['depth3'].append((ok, r))
            elif h['my_nlines'] == 6:
                sl['nodepth3_len6'].append((ok, r))
        out = {}
        for k, v in sl.items():
            n = len(v); s = sum(1 for ok, _ in v if ok)
            tk = [r['n_tok'] for ok, r in v if ok]
            hv = [r['n_have'] for ok, r in v if ok]
            out[k] = {'solved': s, 'n': n, 'rate': s/n if n else None,
                      'ci': wilson(s, n),
                      'mean_term_size': (sum(tk)/len(tk)) if tk else None,
                      'mean_written_lines': (sum(hv)/len(hv)+1) if hv else None}
        # parse/lean bookkeeping
        pf = sum(1 for r in recs if not r['parsed'])
        lr = sum(1 for r in recs if r['parsed'] and not r['lean_ok'])
        okbutnotparsed = sum(1 for r in recs if r['lean_ok'] and not r['parsed'])
        rows[stem] = {'mine': out, 'theirs': ex['slices'], 'parse_fail': pf,
                      'lean_rej_of_parsed': lr, 'lean_ok_unparsed': okbutnotparsed,
                      'their_parse_fail': ex['parse_fail'],
                      'their_lean_rej': ex['lean_rej_of_parsed'],
                      'step': ex['model']['step'], 'n_params': ex['model']['n_params'],
                      'mode': ex['model']['mode'], 'judge': ex['judge'],
                      'args': ex['model']['train_args'], 'label_mismatch': (mis_l, mis_d),
                      'raw': lf}
    json.dump(rows, open('review_sd_slices.json', 'w'), indent=1)

    # --- report disagreements with the executor's own .json ---
    ndis = 0
    for stem, d in sorted(rows.items()):
        for k, v in d['mine'].items():
            t = d['theirs'].get(k)
            if t is None:
                print(f'{stem}: slice {k} absent from theirs'); ndis += 1; continue
            if v['solved'] != t['solved'] or v['n'] != t['n']:
                print(f"{stem}: {k} mine {v['solved']}/{v['n']} theirs {t['solved']}/{t['n']}"); ndis += 1
            for f in ('mean_term_size', 'mean_written_lines'):
                a, b = v[f], t.get(f)
                if a is None or b is None:
                    if a != b: print(f'{stem}: {k} {f} mine {a} theirs {b}'); ndis += 1
                elif abs(a-b) > 1e-6:
                    print(f'{stem}: {k} {f} mine {a:.4f} theirs {b:.4f}'); ndis += 1
        for f, g in (('parse_fail', 'their_parse_fail'), ('lean_rej_of_parsed', 'their_lean_rej')):
            if d[f] != d[g]:
                print(f'{stem}: {f} mine {d[f]} theirs {d[g]}'); ndis += 1
        if d['label_mismatch'] != (0, 0):
            print(f"{stem}: label mismatch vs my own labels {d['label_mismatch']}"); ndis += 1
        if d['lean_ok_unparsed']:
            print(f"{stem}: {d['lean_ok_unparsed']} records lean_ok but not parsed"); ndis += 1
        if d['judge'] != 'lean_alone':
            print(f"{stem}: judge is {d['judge']}"); ndis += 1
    print(f'\n{len(rows)} checkpoints recounted, {ndis} disagreements with the run\'s own .json')
    # slice sizes I measure
    any_stem = sorted(rows)[0]
    print('slice sizes (mine):', {k: v['n'] for k, v in sorted(rows[any_stem]['mine'].items())})


main()
