"""Own summary of the executor's bounded necessity labels + comparison with exact sequent-calculus labels."""
import json, sys, collections
from seq_provers import labels
R = [json.loads(l) for l in open(sys.argv[1])]
def lab(r, t):
    if r['full'] is None: return 'unknown_full_fail' + ('_timeout' if r['full_timeout'] else '')
    if r[t] is None and r[t + '_timeout']: return 'unknown_timeout'
    if r[t] is None: return 'requires'
    return 'costlier' if r[t] > r['full'] else 'not_needed'
errs = sum(bool(r.get(k + '_err')) for r in R for k in ('full', 'no_ore', 'no_dn'))
print(f"n={len(R)} full_found={sum(r['full'] is not None for r in R)} full_timeout={sum(bool(r['full_timeout']) for r in R)} minlen_errors(nd_verify self-check fails)={errs}")
X = collections.Counter(); rows = []
for r in R:
    L = labels(r['prompt']); ex_ore = L['classical'] and not L['classical_no_lor']; ex_dn = L['classical'] and not L['intuitionistic']
    lo, ld = lab(r, 'no_ore'), lab(r, 'no_dn')
    X[('ORE', lo, 'exact_needs' if ex_ore else 'exact_not')] += 1; X[('DN', ld, 'exact_needs' if ex_dn else 'exact_not')] += 1
    X['classical_valid'] += L['classical']; X['exact_needs_ORE'] += ex_ore; X['exact_needs_DN'] += ex_dn; X['exact_needs_both'] += ex_ore and ex_dn
    X[('bounded_both')] += lo == 'requires' and ld == 'requires'
    rows.append(dict(name=r['name'], prompt=r['prompt'], ref=r['reference_lines'], full=r['full'], no_ore=r['no_ore'], no_dn=r['no_dn'], lab_ore=lo, lab_dn=ld, exact_ore=ex_ore, exact_dn=ex_dn, intuit=L['intuitionistic']))
for k in sorted(X, key=str): print(k, X[k])
json.dump(rows, open(sys.argv[2], 'w'), indent=0)
