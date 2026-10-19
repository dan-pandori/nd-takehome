#!/usr/bin/env python3
"""ctx.py <regex> <file>... [-w N] [-m M]: print each match with N chars of context (default 160), max M per file."""
import sys, re, os
args = sys.argv[1:]; w = 160; m = 8
if '-w' in args: i = args.index('-w'); w = int(args[i+1]); del args[i:i+2]
if '-m' in args: i = args.index('-m'); m = int(args[i+1]); del args[i:i+2]
pat = re.compile(args[0], re.I)
for f in args[1:]:
    p = f if os.path.isabs(f) or os.path.exists(f) else os.path.expanduser('~/rcs_sources/' + f)
    t = open(p, errors='replace').read()
    print(f'=== {os.path.basename(p)} | {t.splitlines()[0][:100]}')
    for k, mt in enumerate(pat.finditer(t)):
        if k >= m: print('   ...'); break
        s = t[max(0, mt.start()-w):mt.end()+w].replace('\n', ' ')
        print(f'  @{t.count(chr(10), 0, mt.start())+1}: {s}')
