#!/usr/bin/env python3
"""create-or-elicit: per-round read-outs of one 16-round ladder (runs where the ladder files are: on the pod, or on the VPS
after a pull).  Inputs: <ladder dir>/alloc_<r>.json (cumulative tried / accepted per target), the LAST found_<r>.jsonl and
found_transfer_<r>.jsonl (cumulative; every proof carries the round it was first found), round_<r>.json.

Per round r:
  * family training share: share of the family's trained key-step members with >= 1 accepted proof among round r's attempts
    (alloc differences; round 1 = the base's own k 32 sample), and cumulative share;
  * sigma-covered trained targets (families' key-step + generated classical-only, 291) with >= 1 success in round r;
  * held-out tracked members first solved by round r (cumulative), per family and for the 55 generated sigma-covered;
  * accepted target proofs first found in round r, classified on the ND string: sigma (DN cites a NEGI line, written or
    pruned), sigma+ (DN cites any derived line), lemma route, DN on a premise / hypothesis only, no DN;
  * first round with an accepted sigma+ proof on any target, and on a sigma-covered target.

  python3 coe/coe_rounds.py --dir artifacts/coe/ladder/la_ko_s0 --out artifacts/coe/rounds/la_ko_s0.json
"""
import argparse, collections, glob, json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from patterns import parse
from coe.coe_sigma import flags
from coe.coe_assemble import lemma_route


def classify(nd):
    fl = flags(nd)
    if fl is None:
        return 'unparsed'
    if any(fl[f]['sigma_strict'] or fl[f]['sigma_chain'] for f in ('w', 'p')):
        return 'sigma'
    if any(fl[f]['dn_derived'] for f in ('w', 'p')):
        return 'sigma_plus_only'
    lines = parse(nd)
    if lines is not None and lemma_route(lines):
        return 'lemma_route'
    if fl['w']['dn_any']:
        return 'dn_pr_as'
    return 'no_dn'


def last_file(d, stem):
    fs = glob.glob(os.path.join(d, f'{stem}_*.jsonl')) + glob.glob(os.path.join(d, f'{stem}_*.jsonl.gz'))
    best = None
    for f in fs:
        m = re.search(stem + r'_(\d+)\.jsonl', os.path.basename(f))
        if m and (best is None or int(m.group(1)) > best[0]):
            best = (int(m.group(1)), f)
    return best


def read_jsonl(fn):
    import gzip
    op = gzip.open(fn, 'rt') if fn.endswith('.gz') else open(fn)
    for l in op:
        if l.strip():
            yield json.loads(l)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--families', default='data/coe/families.json')
    a = ap.parse_args()
    fam = json.load(open(a.families))
    sets_tr = {f: d['keystep_trained'] for f, d in fam['families'].items() if d['classical']}
    sets_tr['generated'] = fam['generated_classical']['rl_targets']['sigma_covered']
    sets_ho = {f: d['keystep_heldout'] for f, d in fam['families'].items() if d['classical']}
    sets_ho['generated'] = fam['generated_classical']['transfer']['sigma_covered']
    sig_tr = set(n for v in sets_tr.values() for n in v)
    sig_ho = set(n for v in sets_ho.values() for n in v)
    rounds = sorted(int(re.search(r'round_(\d+)', f).group(1)) for f in glob.glob(os.path.join(a.dir, 'round_*.json')))
    al = {r: json.load(open(os.path.join(a.dir, f'alloc_{r}.json')))['accepted'] for r in rounds}
    out = {'dir': a.dir, 'rounds': rounds, 'per_round': {}}
    prev = {}
    cum = collections.defaultdict(set)
    for r in rounds:
        acc = al[r]
        succ = {t for t, v in acc.items() if v - prev.get(t, 0) > 0}
        row = {'share': {f: round(len(succ & set(m)) / len(m), 4) for f, m in sets_tr.items()},
               'sigma_targets_round': len(succ & sig_tr)}
        for f, m in sets_tr.items():
            cum[f] |= {t for t in m if acc.get(t, 0) > 0}
        row['cum_share'] = {f: round(len(cum[f]) / len(sets_tr[f]), 4) for f in sets_tr}
        row['sigma_targets_cum'] = len({t for t in sig_tr if acc.get(t, 0) > 0})
        rj = json.load(open(os.path.join(a.dir, f'round_{r}.json')))
        row['targets_cum_solved'] = rj.get('targets_cum', {}).get('solved')
        row['secs'] = rj.get('secs'); row['mix_rl_records'] = rj.get('mix_rl_records')
        row['heldout_greedy'] = (rj.get('heldout_greedy') or {}).get('rate')
        row['env'] = {k: rj.get('env', {}).get(k) for k in ('peak_alloc_gb', 'truncated_rate', 'step_cap_rate')} if rj.get('env') else None
        out['per_round'][r] = row
        prev = acc
    # proofs
    lf = last_file(a.dir, 'found')
    cls_round = collections.defaultdict(collections.Counter)
    cls_round_sig = collections.defaultdict(collections.Counter)
    first_sig_any, first_sig_cov = None, None
    examples = {}
    if lf:
        out['found_file'] = lf[1]
        for x in read_jsonl(lf[1]):
            c = classify(x['proof'])
            r = x['round']
            cls_round[r][c] += 1
            if x['name'] in sig_tr:
                cls_round_sig[r][c] += 1
            if c in ('sigma', 'sigma_plus_only', 'lemma_route'):
                if first_sig_any is None or r < first_sig_any:
                    first_sig_any = r
                if x['name'] in sig_tr and (first_sig_cov is None or r < first_sig_cov):
                    first_sig_cov = r
                    examples['first_sigma_covered'] = {'name': x['name'], 'round': r, 'proof': x['proof'], 'class': c}
    out['proof_classes_by_round'] = {r: dict(v) for r, v in sorted(cls_round.items())}
    out['proof_classes_by_round_sigma_targets'] = {r: dict(v) for r, v in sorted(cls_round_sig.items())}
    out['first_round_sigma_any_target'] = first_sig_any
    out['first_round_sigma_covered_target'] = first_sig_cov
    out['examples'] = examples
    lt = last_file(a.dir, 'found_transfer')
    first_ho = {}
    ho_cls = collections.Counter()
    if lt:
        out['found_transfer_file'] = lt[1]
        for x in read_jsonl(lt[1]):
            if x['name'] in sig_ho:
                first_ho[x['name']] = min(first_ho.get(x['name'], 99), x['round'])
                ho_cls[classify(x['proof'])] += 1
    out['heldout_first_solve_round'] = first_ho
    out['heldout_sigma_covered_proof_classes'] = dict(ho_cls)
    out['heldout_cum_by_round'] = {r: {f: sum(1 for n in m if first_ho.get(n, 99) <= r) for f, m in sets_ho.items()} for r in rounds}
    out['heldout_sizes'] = {f: len(m) for f, m in sets_ho.items()}
    out['trained_sizes'] = {f: len(m) for f, m in sets_tr.items()}
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    json.dump(out, open(a.out, 'w'), indent=1)
    fams = list(sets_tr)
    print(f"{a.dir}: rounds {rounds[0]}..{rounds[-1]}; first sigma+ proof: any target r{first_sig_any}, sigma-covered target r{first_sig_cov}")
    print('| r | ' + ' | '.join(f[:12] for f in fams) + ' | σ-cov targets (round / cum) | new proofs σ / σ+only / lemma / DN-PR-AS / noDN | held-out σ-cov first-solved (cum) |')
    for r in rounds:
        row = out['per_round'][r]; pc = out['proof_classes_by_round'].get(r, {})
        ho = sum(out['heldout_cum_by_round'][r].values())
        print(f"| {r} | " + ' | '.join(f"{row['share'][f]:.2f}" for f in fams) +
              f" | {row['sigma_targets_round']} / {row['sigma_targets_cum']} | {pc.get('sigma', 0)} / {pc.get('sigma_plus_only', 0)} / {pc.get('lemma_route', 0)} / {pc.get('dn_pr_as', 0)} / {pc.get('no_dn', 0)} | {ho} |")


if __name__ == '__main__':
    main()
