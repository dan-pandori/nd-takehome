#!/usr/bin/env python3
"""Collect every ds-rendering number from the pulled raw files into artifacts/dsr/summary.json.

Reads artifacts/dsr/<pod>/... (one directory per pod, never a shared flat dir) and writes one record per
(arm, seed, stage).  Every number here names its source file so a reviewer can re-derive it.

Model label carried on every row: 3.2M params (4 layers, d 256, 8 heads), from-scratch, Lean `lean_seq` surface
form in the arm's rendering variant, trained 6,000 steps / bs 128 / cap 6 on data/p2/train_depth3_f0_a1.jsonl
(155,000 ND records, cap 6, depth-3 removed).  Sampler: path=fast, early=eos, compact, rowrng, batch 2048,
max_new 400, temperature 0.8.  Acceptance: Lean 4.34 on the literal text AND nd_verify on the denoted ND proof.

  python3 dsr_analysis.py [--out artifacts/dsr/summary.json]
"""
import argparse, json, os, sys, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from normalize import norm
from patterns import classify

ARMS = ['c0', 'r1', 'r3', 'r2']
POD = {'c0': 'dsr-c0', 'r1': 'dsr-r1', 'r3': 'dsr-r3', 'r2': 'dsr-r2'}
MODE = {'c0': 'lean_seq', 'r1': 'lean_seq_noprem', 'r3': 'lean_seq_nofml', 'r2': 'lean_seq_intro'}
SEEDS = [0, 1]
A = 'artifacts/dsr'


def find(arm, rel):
    """the pulled path of one artefact, preferring this arm's own pod directory."""
    for d in (f'{A}/{POD[arm]}', A):
        p = f'{d}/{rel}'
        if os.path.exists(p):
            return p
    return None


def jload(p):
    return json.load(open(p)) if p and os.path.exists(p) else None


def jlines(p):
    if not p or not os.path.exists(p):
        return None
    return [json.loads(l) for l in open(p) if l.strip()]


def box_depth(proof):
    return max((x.count('| ') for x in proof.split(' ; ')), default=0)


def mech(arm, s):
    """pass@16 on data/transfer.jsonl: distinct START-INDEX-NORMALISED proofs by written ND length."""
    p = find(arm, f'mech_{arm}_s{s}.jsonl')
    rows = jlines(p)
    if rows is None:
        return None
    nprem = {}
    for l in open('data/transfer.jsonl'):
        x = json.loads(l)
        pre = x['thm'].split('|-')[0].strip()
        nprem[x['name']] = int(x.get('n_prem') if x.get('n_prem') is not None else (0 if not pre else pre.count(',') + 1))
    wh = collections.Counter(); solved = 0; n = 0; ntext = 0; ndist = 0
    # by premise count: R1 removes exactly n_prem `have` lines from the text, so if the horizon is text length the
    # gain must grow with n_prem.  Added 2026-09-23 21:40 UTC, before any arm's mech result existed (log.md).
    byp = collections.defaultdict(lambda: collections.Counter())
    for r in rows:
        n += 1
        seen = {}
        for pr, wl in zip(r['proofs'], r['written_lens']):
            seen.setdefault(norm(pr), wl)
        if seen:
            solved += 1
        ndist += len(seen)
        ntext += sum(1 for t in (r.get('lean_texts') or []) if t)
        k = nprem.get(r['name'], -1)
        for wl in seen.values():
            wh[wl] += 1
            byp[k][wl] += 1
    return {'src': p, 'n': n, 'solved': solved, 'rate': solved / max(n, 1),
            'by_nprem': {str(k): {'d7': v[7], 'd8': v[8], 'd9plus': sum(c for L, c in v.items() if L >= 9),
                                  'total': sum(v.values())} for k, v in sorted(byp.items())},
            'distinct_norm_by_written_len': dict(sorted(wh.items())),
            'd7': wh[7], 'd8': wh[8], 'd9plus': sum(v for k, v in wh.items() if k >= 9),
            'distinct_total': ndist, 'with_lean_text': ntext,
            'frontier_written': max([L for L, c in wh.items() if c >= 5], default=0)}


def held_breakdown(arm, s):
    """held-out greedy split by (premise count, ND length).  The 6-line deficit every Lean rendering shows turns out
    to live almost entirely in the 0-premise 6-line cell (511 of the 1,000 6-line held-out theorems), so the split is
    what separates the renderings; added 2026-09-23 21:45 UTC, log.md."""
    p = find(arm, f'held_{arm}_s{s}.jsonl')
    rows = jlines(p)
    if rows is None:
        return None
    prem = {}
    for l in open('data/p2/heldout.jsonl'):
        x = json.loads(l)
        pre = x['thm'].split('|-')[0].strip()
        prem[x.get('name') or x['thm']] = int(x.get('n_prem') if x.get('n_prem') is not None else (0 if not pre else pre.count(',') + 1))
    d = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        k = f"p{prem.get(r['name'], -1)}_L{r['n_lines']}"
        d[k][0] += bool(r['solved']); d[k][1] += 1
    return {'src': p, 'cells': {k: {'solved': v[0], 'n': v[1], 'rate': v[0] / v[1]} for k, v in sorted(d.items())}}


def cov(arm, s, tag):
    """coverage.py pass@2,000 on one pool."""
    p = find(arm, f'cov_{tag}_{arm}_s{s}.s0.jsonl')
    rows = jlines(p)
    if rows is None:
        return None
    n = len(rows)
    hit = sum(1 for r in rows if r['first_hit'] is not None)
    n_ok = sum(r['n_ok'] for r in rows); n_tried = sum(r['n_tried'] for r in rows)
    by_str = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        k = str(r.get('gen_lines'))
        by_str[k][0] += (r['first_hit'] is not None); by_str[k][1] += 1
    wh = collections.Counter(); d3 = 0; red = 0; texts = 0; nproofs = 0
    for r in rows:
        for x in r['proofs']:
            wh[x['written']] += 1; nproofs += 1
            texts += bool(x.get('text'))
            if x['pat'].get('depth3'):
                d3 += 1
            if x['pat'].get('reductio'):
                red += 1
    return {'src': p, 'n': n, 'targets_hit': hit, 'rate': hit / max(n, 1),
            'per_sample_rate': n_ok / max(n_tried, 1), 'n_tried': n_tried, 'n_ok': n_ok,
            'by_min_lines_ub': {k: {'hit': v[0], 'n': v[1]} for k, v in sorted(by_str.items())},
            'distinct_by_written_len': dict(sorted(wh.items())),
            'distinct_ge8': sum(v for k, v in wh.items() if k >= 8),
            'distinct_depth3': d3, 'distinct_reductio': red,
            'distinct_proofs': nproofs, 'with_lean_text': texts,
            'solved_within': {b: sum(1 for r in rows if r['solved_within'].get(b)) for b in ('32', '128', '512', '1000')}}


def acquisition(dirpath, pat='depth3'):
    """fraction of targets with at least one accepted proof carrying the pattern (the lean-format 'acquisition')."""
    fs = sorted(glob.glob(f'{dirpath}/found_*.jsonl'), key=lambda x: -len(x))
    best = None
    for r in range(8, 0, -1):
        f = f'{dirpath}/found_{r}.jsonl'
        if os.path.exists(f):
            best = (r, f); break
    if not best:
        return None
    names = set()
    total = set()
    for l in open(best[1]):
        x = json.loads(l)
        total.add(x['name'])
        if classify(x['proof']).get(pat):
            names.add(x['name'])
    return {'src': best[1], 'round': best[0], 'targets_with_pattern': len(names), 'targets_with_any_proof': len(total)}


def dial(arm, s, kind):
    d = find(arm, f'{kind}_d3_{arm}_s{s}')
    if d is None:
        return None
    r4 = jload(f'{d}/round_4.json')
    if r4 is None:
        return None
    acq = acquisition(d, 'depth3')
    if acq:
        acq['acquisition'] = acq['targets_with_pattern'] / 1000.0
    return {'src': f'{d}/round_4.json', 'round': r4['round'],
            'targets_cum_solved': r4['targets_cum']['solved'], 'targets_cum_rate': r4['targets_cum']['rate'],
            'heldout_greedy': r4['heldout_greedy']['rate'],
            'transfer_cum_solved': r4.get('transfer_cum', {}).get('solved'),
            'acq_depth3': acq}


def ladder(arm, s, kind):
    d = find(arm, f'la_{kind}_{arm}_s{s}')
    if d is None:
        return None
    last = None
    for r in range(8, 0, -1):
        if os.path.exists(f'{d}/round_{r}.json'):
            last = (r, jload(f'{d}/round_{r}.json')); break
    if not last:
        return None
    r8 = last[1]
    tc = r8.get('transfer_cum', {})
    out = {'src': f'{d}/round_{last[0]}.json', 'round': last[0],
           'transfer_solved': tc.get('solved'), 'transfer_n': tc.get('n'), 'lstar': tc.get('lstar'),
           'ge': tc.get('ge'), 'by_bin': tc.get('by_bin'),
           'heldout_greedy': r8.get('heldout_greedy', {}).get('rate'),
           'targets_solved': r8.get('targets_cum', {}).get('solved')}
    # textbook solves per schema: the round file has no per-schema view, so derive it from found_transfer_<R>.jsonl
    ft = f'{d}/found_transfer_{last[0]}.jsonl'
    if os.path.exists(ft):
        solved = collections.defaultdict(set)
        for l in open(ft):
            x = json.loads(l)
            if x.get('source') == 'textbook' and x.get('schema'):
                solved[x['schema']].add(x['name'])
        tot = collections.Counter()
        for l in open('data/ladder/transfer.jsonl'):
            x = json.loads(l)
            if x.get('source') == 'textbook' and x.get('schema'):
                tot[x['schema']] += 1
        out['textbook_by_schema'] = {k: {'solved': len(solved.get(k, ())), 'n': v} for k, v in sorted(tot.items())}
        out['textbook_schemata_ge5'] = sum(1 for k, v in out['textbook_by_schema'].items() if v['solved'] >= 5)
        out['textbook_src'] = ft
    return out


def gate_totals(arm):
    """the in-loop Lean-vs-nd_verify 2x2 over every gate log of this arm's pod."""
    t = collections.Counter(); reasons = collections.Counter()
    for p in glob.glob(f'{A}/{POD[arm]}/gate_*.jsonl'):
        if p.endswith('.disagree.jsonl'):
            continue
        for l in open(p):
            try:
                r = json.loads(l)
            except Exception:
                continue
            for k in ('samples', 'parse_fail', 'distinct_checked', 'both_ok', 'nd_ok_lean_rej', 'nd_rej_lean_ok', 'both_rej'):
                t[k] += r.get(k, 0)
            for k, v in (r.get('parse_reasons') or {}).items():
                reasons[k] += v
    ndis = sum(1 for p in glob.glob(f'{A}/{POD[arm]}/gate_*.disagree.jsonl') for _ in open(p))
    return {'totals': dict(t), 'parse_reasons': dict(reasons.most_common(10)), 'disagree_lines': ndis}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=f'{A}/summary.json')
    a = ap.parse_args()
    out = {'run': 'ds-rendering',
           'model': '3.2M params (4 layers, d 256, 8 heads), from-scratch, Lean lean_seq surface form, '
                    '6,000 steps, bs 128, cap 6, data/p2/train_depth3_f0_a1.jsonl (155,000 ND records)',
           'sampler': 'path=fast early=eos compact rowrng, batch 2048, max_new 400, T 0.8',
           'acceptance': 'Lean 4.34 on the literal sampled text AND nd_verify on the denoted ND proof',
           'render_check': jload(f'{A}/render_check.json'),
           'splits': jload(f'{A}/splits.json'),
           'arms': {}}
    if out['render_check']:
        for m, r in out['render_check']['modes'].items():
            r.pop('round_trip_fail', None); r.pop('lean_rejected_examples', None)
    for arm in ARMS:
        rec = {'mode': MODE[arm], 'pod': POD[arm], 'seeds': {}}
        for s in SEEDS:
            h = jload(find(arm, f'held_{arm}_s{s}.json'))
            rec['seeds'][s] = {
                'ckpt': f'ckpts/dsr/stage1_a1_seq_s{s}.pt' if arm == 'c0' else f'ckpts/dsr/stage1_{arm}_s{s}.pt',
                'heldout_greedy': None if h is None else {
                    'src': find(arm, f'held_{arm}_s{s}.json'), 'n': h['n'], 'solved': h['solved'], 'rate': h['rate'],
                    'by_len': {k: v['rate'] for k, v in h['by_len'].items()},
                    'written_hist': h.get('written_hist')},
                'heldout_by_prem_len': held_breakdown(arm, s),
                'mech_pass16': mech(arm, s),
                'cov': {tag: cov(arm, s, tag) for tag in ('d3', 'd3req', 'red')},
                'dial_ei': dial(arm, s, 'ei'), 'dial_frozen': dial(arm, s, 'frz'),
                'ladder_T1': ladder(arm, s, 'T1'), 'ladder_frozen': ladder(arm, s, 'frz'),
            }
        rec['gate'] = gate_totals(arm)
        out['arms'][arm] = rec
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    json.dump(out, open(a.out, 'w'), indent=1)
    # compact console table
    print(f'{"arm":4s} {"seed":4s} {"held":7s} {"6bin":6s} {"m7":5s} {"m8":5s} {"m9+":5s} {"d3":6s} {"d3req":6s} {"red":5s} '
          f'{"EI4":6s} {"FRZ4":6s} {"laT1":10s} {"laFRZ":10s}')
    for arm in ARMS:
        for s in SEEDS:
            r = out['arms'][arm]['seeds'][s]
            g = lambda x, *k: ('-' if x is None else x) if not k else (x.get(k[0], '-') if isinstance(x, dict) else '-')
            h = r['heldout_greedy']; m = r['mech_pass16']
            c1, c2, c3 = r['cov']['d3'], r['cov']['d3req'], r['cov']['red']
            e, f = r['dial_ei'], r['dial_frozen']
            l1, l2 = r['ladder_T1'], r['ladder_frozen']
            fmt = lambda v, w=6, p=3: (f'{v:.{p}f}'.ljust(w) if isinstance(v, float) else str(v if v is not None else '-').ljust(w))
            print(f'{arm:4s} {s:<4d} '
                  f'{fmt(h and h["rate"], 7)} {fmt(h and float(h["by_len"].get("6", 0)), 6)} '
                  f'{fmt(m and m["d7"], 5)} {fmt(m and m["d8"], 5)} {fmt(m and m["d9plus"], 5)} '
                  f'{fmt(c1 and c1["rate"], 6)} {fmt(c2 and c2["rate"], 6)} {fmt(c3 and c3["targets_hit"], 5)} '
                  f'{fmt(e and e["targets_cum_rate"], 6)} {fmt(f and f["targets_cum_rate"], 6)} '
                  f'{fmt(l1 and f"{l1["transfer_solved"]}/L*{l1["lstar"]}", 10)} '
                  f'{fmt(l2 and f"{l2["transfer_solved"]}/L*{l2["lstar"]}", 10)}')
    print('wrote', a.out)


if __name__ == '__main__':
    main()
