#!/usr/bin/env python3
"""Assemble numbers.md § kalmar-complexity from numbers_section.tmpl.md and the generated tables (run kalmar-complexity).
  .venv-tok/bin/python kalmar_complexity/assemble_numbers.py
Placeholders {{t_*}} are filled from numbers_tables.py; {{b2_text}} from kalmar_complexity/b2_text.md;
{{t_prereg}} from kalmar_complexity/prereg_outcomes.md; {{t_compute}} from artifacts/kc/compute_table.md;
{{spend}} from artifacts/kc/spend.txt.  Replaces an existing '## kalmar-complexity' section in numbers.md."""
import contextlib, io, os, re, sys
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(H)
sys.path.insert(0, H)
import numbers_tables as NT
T = open(os.path.join(H, 'numbers_section.tmpl.md')).read()
for name in ('t_programs', 't_calibration', 't_b1', 't_b2', 't_q4', 't_types'):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        getattr(NT, name)()
    T = T.replace('{{%s}}' % name, buf.getvalue().strip())
for key, f in (('b2_text', 'kalmar_complexity/b2_text.md'), ('t_prereg', 'kalmar_complexity/prereg_outcomes.md'),
               ('t_compute', 'artifacts/kc/compute_table.md'), ('spend', 'artifacts/kc/spend.txt')):
    p = os.path.join(ROOT, f)
    T = T.replace('{{%s}}' % key, open(p).read().strip() if os.path.exists(p) else f'(pending: {f})')
N = open(os.path.join(ROOT, 'numbers.md')).read()
m = re.search(r'^## kalmar-complexity .*?(?=^## |\Z)', N, flags=re.S | re.M)
N = (N[:m.start()] + T.rstrip() + '\n\n' + N[m.end():]) if m else (N.rstrip() + '\n\n' + T.rstrip() + '\n')
open(os.path.join(ROOT, 'numbers.md'), 'w').write(N)
print('numbers.md § kalmar-complexity:', len(T.split()), 'words')
