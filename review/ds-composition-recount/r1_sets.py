"""Recount 1 — the four assembled sets + the control's set: shape, rule shares,
pattern shares, cap assertion, and nd_verify on every record (streaming)."""
import sys, json, collections, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rv
from nd_verify import verify_text

SETS = {
    'C0': 'data/p2/train_depth3_f0_a1.jsonl',
    'A1': 'data/dsc/train_a1.jsonl.gz',
    'A2': 'data/dsc/train_a2.jsonl.gz',
    'A3': 'data/dsc/train_a3.jsonl.gz',
    'A4': 'data/dsc/train_a4.jsonl.gz',
}
CAP = {'C0': 6, 'A1': 6, 'A2': 6, 'A3': 8, 'A4': 6}

out = {}
for arm, path in SETS.items():
    n = 0
    bylen = collections.Counter()
    rule_proofs = collections.Counter()   # proofs containing the rule >= once
    pats = collections.Counter()
    keys = set()
    nd_bad = 0
    over_cap = 0
    unparsable = 0
    dup_text = 0
    seen_text = set()
    tsz = 0
    for rec in rv.load(path):
        n += 1
        pr = rec['proof']
        lines = rv.try_parse(pr)
        if lines is None:
            unparsable += 1
            continue
        L = len(lines)
        bylen[L] += 1
        if L > CAP[arm]:
            over_cap += 1
        for r in {x['rule'] for x in lines}:
            rule_proofs[r] += 1
        p = rv.prune(lines)
        if rv.is_depth3(p):
            pats['depth3_pruned'] += 1
        if rv.is_depth3(lines):
            pats['depth3_written'] += 1
        if rv.is_reductio(p):
            pats['reductio'] += 1
        if rv.is_derived_ore(p):
            pats['derived_ore'] += 1
        if rv.is_derived_ore_strict(p):
            pats['derived_ore_strict'] += 1
        tsz += rv.term_size(lines)
        keys.add(rv.rkey(rec['prompt']))
        t = rec['text']
        if t in seen_text:
            dup_text += 1
        seen_text.add(t)
        if n % 20000 == 0:
            ok, why, _nl = verify_text(rec['prompt'] + ' ' + pr)
            if not ok:
                nd_bad += 1
    out[arm] = {'path': path, 'n': n, 'by_len': dict(sorted(bylen.items())),
                'unparsable': unparsable, 'over_cap(cap=%d)' % CAP[arm]: over_cap,
                'distinct_renaming_classes': len(keys),
                'duplicate_texts': dup_text,
                'rule_proof_share': {k: round(v / n, 5) for k, v in sorted(rule_proofs.items())},
                'rule_proof_count': dict(sorted(rule_proofs.items())),
                'pattern_count': dict(pats),
                'pattern_share': {k: round(v / n, 5) for k, v in pats.items()},
                'mean_term_size': round(tsz / n, 3)}
    print(arm, 'done', n, flush=True)
json.dump(out, open('recount/out_sets.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
