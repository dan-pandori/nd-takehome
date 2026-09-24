"""Reviewer recount 6: pattern shares in the assembled training sets, with the reviewer's own
reductio / derived-ORE predicates on the dependency-pruned proof."""
import sys, os, json, gzip, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rvlib

ROOT = '/home/dan/review/cap-horizon'


def kept_lines(body):
    lines = rvlib.parse_proof(body)
    if lines is None:
        return None
    keep = rvlib.pruned_lines(body)
    return [l for l in lines if l['idx'] in keep]


def is_reductio(lines):
    """a DN of a NEGI whose discharged assumption is the negation of the DN's own conclusion."""
    by = {l['idx']: l for l in lines}
    for l in lines:
        if l['rule'] != 'DN' or not l['refs']:
            continue
        neg = by.get(l['refs'][0])
        if not neg or neg['rule'] != 'NEGI' or len(neg['refs']) != 2:
            continue
        hyp = by.get(neg['refs'][0])
        if hyp and hyp['rule'] == 'AS' and hyp['ftoks'] == ['(', '~'] + l['ftoks'] + [')']:
            return True
    return False


def is_derived_ore(lines):
    """an ORE whose disjunction line is not a premise."""
    by = {l['idx']: l for l in lines}
    return any(l['rule'] == 'ORE' and l['refs'] and (by[l['refs'][0]]['rule'] if l['refs'][0] in by else None) != 'PR'
               for l in lines)


out = {}
for arm in ('k8add', 'k10', 'k12', 'k14'):
    tot = collections.Counter()
    byl = collections.defaultdict(collections.Counter)
    n = 0
    with gzip.open(f'{ROOT}/data/kh/train_{arm}.jsonl.gz', 'rt') as f:
        for line in f:
            r = json.loads(line)
            ls = kept_lines(r['proof'])
            L = len(ls)
            red, ore = is_reductio(ls), is_derived_ore(ls)
            n += 1
            tot['reductio'] += red; tot['derived_ore'] += ore
            byl[L]['n'] += 1; byl[L]['reductio'] += red; byl[L]['derived_ore'] += ore
    out[arm] = {'records': n,
                'reductio_pct': round(100 * tot['reductio'] / n, 2),
                'derived_ore_pct': round(100 * tot['derived_ore'] / n, 2),
                'by_len': {L: [round(100 * byl[L]['reductio'] / byl[L]['n'], 2),
                               round(100 * byl[L]['derived_ore'] / byl[L]['n'], 2)] for L in sorted(byl)}}
    print(arm, json.dumps(out[arm]))
    sys.stdout.flush()
json.dump(out, open(f'{ROOT}/rv/out_patterns.json', 'w'), indent=1)
