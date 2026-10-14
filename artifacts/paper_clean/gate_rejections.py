#!/usr/bin/env python3
"""paper-clean item 5: were all Lean-gate rejections the pre-filter's?  Every `[lean_gate]` summary line in the
create-or-elicit and create-or-elicit-paper logs reads "... rej N (filter M, prefilter=on) ..."; count lines with N == M.
  python3 artifacts/paper_clean/gate_rejections.py > artifacts/paper_clean/gate_rejections.json"""
import glob, json, os, re
pat = re.compile(r'rej (\d+) \(filter (\d+), prefilter=(\w+)\)')
n = eq = tot = 0; pf = {}; files = set()
for f in sorted(glob.glob('artifacts/coe/logs/**/*', recursive=True) + glob.glob('artifacts/coe_paper/logs/**/*', recursive=True)):
    if not os.path.isfile(f):
        continue
    for line in open(f, errors='replace'):
        for a, b, p in pat.findall(line):
            n += 1; eq += a == b; tot += int(a); pf[p] = pf.get(p, 0) + 1; files.add(f)
print(json.dumps({'gate_lines': n, 'rej_equals_filter': eq, 'total_rejections': tot, 'prefilter': pf, 'files': len(files)}, indent=1))
