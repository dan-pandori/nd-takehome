#!/usr/bin/env python3
"""Reviewer recount of the dose sets: K12^1% (data/coe/train_k12dose1.jsonl.gz, trained) and K12^0.1% (built, not trained).
Expected: K12- with N refill records replaced by N of the records the knockout removed (sigma records), per-length counts
unchanged, the sigma length mix proportional to K12's."""
import collections, hashlib, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

RV = C.RV


def ident(r):
    return hashlib.blake2b((r['prompt'] + ' || ' + r['proof'].strip()).encode(), digest_size=12).digest()


K12 = {ident(r): r for r in C.rows(f'{RV}/data/coe/src/train_k12.jsonl.gz')}
KO = {ident(r): r for r in C.rows(f'{RV}/data/coe/train_k12ko.jsonl.gz')}
refill = {x for x in KO if x not in K12}
removed = {x for x in K12 if x not in KO}
out = {}
for nm in ('train_k12dose1', 'train_k12dose01'):
    D = [r for r in C.rows(f'{RV}/data/coe/{nm}.jsonl.gz')]
    ids = [ident(r) for r in D]
    s = set(ids)
    added = [x for x in ids if x not in KO]
    dropped = [x for x in KO if x not in s]
    o = {'records': len(D), 'distinct': len(s), 'added_not_in_ko': len(added), 'added_in_removed': sum(1 for x in added if x in removed),
         'added_sigma_plus': sum(1 for x in added if C.sigma_flags(K12[x]['proof'])['sigma_plus']),
         'added_sigma_negi': sum(1 for x in added if C.sigma_flags(K12[x]['proof'])['sigma']),
         'dropped_from_ko': len(dropped), 'dropped_are_refill': sum(1 for x in dropped if x in refill),
         'added_per_len': dict(sorted(collections.Counter(int(K12[x]['n_lines']) for x in added if x in K12).items())),
         'dropped_per_len': dict(sorted(collections.Counter(int(KO[x]['n_lines']) for x in dropped).items())),
         'per_len_equal_k12': dict(sorted(collections.Counter(int(r['n_lines']) for r in D).items())) ==
                              dict(sorted(collections.Counter(int(r['n_lines']) for r in K12.values()).items())),
         'sigma_plus_records': sum(1 for r in D if C.sigma_flags(r['proof'])['sigma_plus'])}
    o['sigma_share'] = o['sigma_plus_records'] / len(D)
    out[nm] = o
    print(nm, o)
# K12's sigma length mix (for proportionality)
mix = collections.Counter(int(K12[x]['n_lines']) for x in removed if C.sigma_flags(K12[x]['proof'])['sigma'])
tot = sum(mix.values())
print('K12 sigma (NEGI) records per length:', dict(sorted(mix.items())), 'total', tot)
print('expected 1,550 at that mix:', {L: round(1550 * v / tot, 1) for L, v in sorted(mix.items())})
json.dump(out, open(f'{RV}/review_coe/out_dose.json', 'w'), indent=1)
