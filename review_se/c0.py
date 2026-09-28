#!/usr/bin/env python3
"""Reviewer: C0 (ds-generator whole-proof control) re-derived from git HEAD, plus what Lean alone adds (from the gate's
Lean-vs-nd_verify disagreement logs).  Run from the run worktree (git show)."""
import json, subprocess, collections, sys
def gl(p):
    return [json.loads(l) for l in subprocess.check_output(['git', 'show', f'HEAD:{p}']).decode().splitlines() if l.strip()]
T = [json.loads(l) for l in open(sys.argv[1] + '/data/ladder/transfer.jsonl')]
Lt = {r['name']: r['n_lines'] for r in T}; byp = {r['prompt']: r['name'] for r in T}; src = {r['name']: r['source'] for r in T}
def lstar(sl): return max([L for L in range(2, 30) if sum(1 for x in sl if x >= L) >= 5], default=0)
out = {}
for run in ['la_T1_c0_s0', 'la_T1_c0_s1', 'la_frozen_c0_s0', 'la_frozen_c0_s1']:
    F = gl(f'artifacts/dsg/{run}/found_transfer_8.jsonl')
    sol = {x['name'] for x in F}
    D = gl(f'artifacts/dsg/gate_{run}.disagree.jsonl')
    extra = {byp[d['prompt']] for d in D if d['prompt'] in byp and d['lean_ok'] and not d['nd_ok']} - sol
    wrong = {byp[d['prompt']] for d in D if d['prompt'] in byp and d['nd_ok'] and not d['lean_ok']}
    s2 = sol | extra
    out[run] = {'solved': len(sol), 'lstar': lstar([Lt[n] for n in sol]), 'ge12': sum(Lt[n] >= 12 for n in sol), 'ge13': sum(Lt[n] >= 13 for n in sol),
                'textbook': sum(src[n] == 'textbook' for n in sol),
                'lean_only_extra_theorems': len(extra), 'extra_ge13': sorted((n, Lt[n]) for n in extra if Lt[n] >= 13),
                'lean_alone_solved_upper': len(s2), 'lean_alone_lstar': lstar([Lt[n] for n in s2]), 'nd_ok_lean_rej_transfer': len(wrong),
                'n_disagree': len(D)}
for s in (0, 1):
    for f in (f'artifacts/dsg/heldout_c0_s{s}.json',):
        j = json.loads(subprocess.check_output(['git', 'show', f'HEAD:{f}']))
        out[f] = {'rate': j.get('rate'), 'bin6': j.get('by_len', {}).get('6', {}).get('rate'), 'n': j.get('n')}
print(json.dumps(out, indent=1))
