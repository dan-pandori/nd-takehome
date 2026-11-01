#!/usr/bin/env python3
"""Reviewer (coe-dose01): positive control of tb72strict.py -- the 72 statements rendered as ND prompts, Lean headers and
'A, B ⊢ C' prose, written to /tmp (never into the repository), scanned, deleted.  Prints counts only."""
import os, subprocess, sys
sys.path.insert(0, '/home/dan/work/coe-dose01/review_cd01')
from common import REPO, jl, seq_of_prompt, pf, lean_f
tb = [x['prompt'] for x in jl(f'{REPO}/data/coe/read1054.jsonl') if x['name'].startswith('textbook_')]
for tag in ('nd', 'lean', 'uni'):
    fn = f'/tmp/tb72ctl_{tag}.md'
    with open(fn, 'w') as f:
        for p in tb:
            pr, c = seq_of_prompt(p)
            if tag == 'nd': f.write(f'Example: `{p}` here.\n')
            if tag == 'lean': f.write('theorem t (P Q R S : Prop) ' + ' '.join(f'(h{i + 1} : {lean_f(pf(x))})' for i, x in enumerate(pr)) + f' : {lean_f(pf(c))} := by exact foo\n')
            if tag == 'uni': f.write('The sequent ' + ', '.join(lean_f(pf(x)) for x in pr) + f' ⊢ {lean_f(pf(c))} is classical.\n')
    r = subprocess.run([sys.executable, '/home/dan/work/coe-dose01/review_cd01/tb72strict.py', fn], capture_output=True, text=True).stdout.splitlines()
    print(tag, 'notation:', r[-1].split(': ', 1)[1] if r else 'no output', 'of', len(tb))
    os.remove(fn)
