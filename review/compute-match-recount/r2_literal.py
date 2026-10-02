#!/usr/bin/env python3
"""Reviewer recount (compute-match), part 2: the literal sampled lean_seq text (LEAN_GATE_DUMP, bucket) re-checked by Lean.
Per dump: 150 random gate-accepted texts must be accepted; 40 random gate-rejected (prefilter) texts are run too (a Lean
accept there = the gate under-counts).  All accepted texts are scanned for tokens outside the strict grammar.
Cross-check: the prompts with an accepted text == the targets the eval file marks solved.  Output: recount_literal.json"""
import json, os, sys, gzip, random, re, collections
sys.path.insert(0, os.path.dirname(__file__)); import rlean
W = os.path.expanduser('~/review/compute-match'); D = '/tmp/cmr/dump'
BAD = re.compile(r'\b(sorry|admit|decide|tauto|simp|omega|aesop|native_decide|exact\?|apply\?|trivial|assumption|contradiction|cases|rcases|intro|by_cases|first|repeat|all_goals|sorryAx|Classical\.em|Decidable)\b')
def render(prompt, text, nm):
    prem, c = rlean.parse_prompt(prompt)
    hs = ''.join(f' (h{k + 1} : {rlean.lf(p)})' for k, p in enumerate(prem))
    return f'theorem {nm} (P Q R S : Prop){hs} : {rlean.lf(c)} := by {text}'
out = {}
for fn in sorted(os.listdir(D)):
    lab = fn[:-9]; rows = [json.loads(l) for l in gzip.open(f'{D}/{fn}', 'rt')]
    acc = [r for r in rows if r['lean_ok']]; rej = [r for r in rows if not r['lean_ok']]
    toks = collections.Counter(m.group(1) for r in acc for m in BAD.finditer(r['lean_text']))
    ev = [json.loads(l) for l in open(f'{W}/artifacts/cm/eval/{lab}.jsonl')]
    solved_p = {r['prompt'] for r in ev if r['solved']}; acc_p = {r['prompt'] for r in acc}
    rng = random.Random(0); sa = rng.sample(acc, min(150, len(acc))); sr = rng.sample(rej, min(40, len(rej)))
    ra = rlean.check([(r['prompt'], r['lean_text']) for r in sa], render)
    rr = rlean.check([(r['prompt'], r['lean_text']) for r in sr], render)
    d = {'dump_rows': len(rows), 'accepted_rows': len(acc), 'rejected_rows': len(rej),
         'rejected_reasons': dict(collections.Counter(str(r['filter'])[:30] for r in rej).most_common(6)),
         'sample_acc': len(sa), 'sample_acc_lean_ok': sum(a for a, _ in ra), 'sample_acc_fail': [w for a, w in ra if not a][:3],
         'sample_rej': len(sr), 'sample_rej_lean_ok': sum(a for a, _ in rr),
         'sample_rej_lean_ok_examples': [r['lean_text'][:300] for r, (a, _) in zip(sr, rr) if a][:2],
         'bad_tokens_in_accepted': dict(toks), 'solved_prompts_eval': len(solved_p), 'solved_prompts_dump': len(acc_p),
         'eval_minus_dump': len(solved_p - acc_p), 'dump_minus_eval': len(acc_p - solved_p)}
    out[lab] = d; print(lab, d, flush=True)
json.dump(out, open(os.path.join(os.path.dirname(__file__), 'recount_literal.json'), 'w'), indent=1)
