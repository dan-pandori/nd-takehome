#!/usr/bin/env python3
"""Phase-2 sub-audit (TAXONOMY §5/§6): σ / σ strict / σ⁺ / #10 ∪ #11-on_derived, σ-covered under both dneg readings,
coverage (empty uses, unlabelled primary, dead lines, curried trivial), and the v0 'no label' records.  Reviewer labels,
streamed.  Counts only."""
import collections, gzip, json
RV = "/home/dan/review/proof-strategies/review_ps/out"
R = "/home/dan/review/proof-strategies"
C = collections.Counter()
fl = gzip.open(f"{RV}/labels_k12.jsonl.gz", "rt"); ft = gzip.open(f"{RV}/thm_k12.jsonl.gz", "rt")
fs = gzip.open(f"{R}/data/ps/in/train_k12.jsonl.gz", "rt")
for ll, lt, ls in zip(fl, ft, fs):
    a, t, s = json.loads(ll), json.loads(lt), json.loads(ls)
    assert a['i'] == t['i']
    C['n'] += 1
    sub = set(a['sub'])
    C['sigma'] += a['sigma']; C['sigma_strict'] += a['sigma_strict']; C['sigma_plus'] += a['sigma_plus']
    c10sig = 'contradiction.sigma' in sub
    C['#10 via NEGI (contradiction.sigma)'] += c10sig
    C['sigma != #10-via-NEGI'] += a['sigma'] != c10sig
    u10_11d = ('contradiction' in a['uses']) or ('dne.on_derived' in sub)
    C['#10 or #11 on_derived'] += u10_11d
    C['sigma_plus != (#10 or #11 on_derived)'] += a['sigma_plus'] != u10_11d
    C['uses #10'] += 'contradiction' in a['uses']
    C['co'] += t['co']; C['sc_sem'] += t['sc_sem']; C['sc_syn'] += t['sc_syn']; C['inc'] += t['inc']
    C['empty uses'] += not a['uses']
    C['primary missing/unlabelled'] += a['primary'] in (None, '', 'unlabelled')
    C['primary trivial'] += a['primary'] == 'trivial'
    C['curried trivial'] += a['curried'] == 'trivial'
    C['dead lines (n_lines != n_kept)'] += a['n_lines'] != a['n_kept']
    if set(a['uses']) == {'direct'} and 'direct.neg_elim_root' in sub and not ({'direct.mp', 'direct.ande'} & sub):
        C['v0-unlabelled candidates (only root NEGE)'] += 1
        concl = s['prompt'][4:-4].split(' SEQ ')[1].strip()
        last = [x for x in s['proof'].split(';') if x.strip() and x.strip() != 'QED'][-1].split()
        C['  of which goal F'] += concl == 'F'
        C['  of which root rule NEGE'] += last[last.index(':') + 1] == 'NEGE'
        C['  of which pruned length = premises + 1'] += a['n_kept'] == s['n_prem'] + 1
        C['  of which inconsistent premises'] += t['inc']
for k, v in C.items():
    print(f"{k}: {v}" + (f"  ({100 * v / C['n']:.2f} %)" if k in ('curried trivial', 'co', 'sc_syn', 'uses #10', 'sigma_plus') else ''))
for name in ('labels_tb_schema_search', 'labels_charles_base'):
    dl = sum(1 for l in gzip.open(f"{RV}/{name}.jsonl.gz", "rt") if (lambda r: r['n_lines'] != r['n_kept'])(json.loads(l)))
    print(name, 'dead-line records:', dl)
