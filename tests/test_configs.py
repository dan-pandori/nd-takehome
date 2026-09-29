#!/usr/bin/env python3
"""Every script that writes outputs records its resolved configuration next to them (run repo-hygiene).

Static check: each top-level script that parses arguments and takes `--out` / `--outdir` calls `record.save_config`
(which writes `<out>.args.json` or `<outdir>/args.json` and names the file in every registry row).  Then a behavioural
check of `save_config` itself.     python3 tests/test_configs.py
"""
import glob, json, os, re, sys, tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
EXEMPT = {'artifact_inventory.py'}      # run repo-hygiene's one-off inventory tool (runs under the hf CLI's python)
missing = []
n = 0
for p in sorted(glob.glob(os.path.join(HERE, '*.py'))):
    s = open(p).read()
    if 'parse_args(' in s and re.search(r"add_argument\('--(out|outdir)'", s) and os.path.basename(p) not in EXEMPT:
        n += 1
        if 'save_config(' not in s:
            missing.append(os.path.basename(p))
print(f'{n} scripts take --out/--outdir; {len(missing)} do not call record.save_config: {missing}')
fails = list(missing)

os.environ['ND_OFFLINE'] = '1'; os.environ['ND_REGISTRY'] = '0'
import record
d = tempfile.mkdtemp()
for out, want in ((os.path.join(d, 'x.jsonl'), os.path.join(d, 'x.jsonl.args.json')), (d + '/sub/', os.path.join(d, 'sub', 'args.json')),
                  (d, os.path.join(d, 'args.json')), (None, None)):
    got = record.save_config({'steps': 5, 'out': out}, out)
    ok = got == want and (want is None or json.load(open(want))['steps'] == 5 and '_meta' in json.load(open(want)))
    print(('PASS' if ok else 'FAIL'), 'save_config', out, '->', got)
    if not ok:
        fails.append(f'save_config {out}')
print('ALL PASS' if not fails else f'{len(fails)} failed')
sys.exit(1 if fails else 0)
