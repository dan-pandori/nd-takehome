import sys, os, json, glob, re, collections
sys.path.insert(0, os.path.dirname(__file__))

tgt = [json.loads(l) for l in open('data/p2/targets_depth3.jsonl')]
names = {t['name'] for t in tgt}

res = {}
for d in sorted(glob.glob('artifacts/dsr/*/ei_d3_*_s?') + glob.glob('artifacts/dsr/*/frz_d3_*_s?')):
    m = re.match(r'(ei|frz)_d3_(\w+?)_s(\d)$', os.path.basename(d))
    kind, arm, seed = m.groups()
    f = os.path.join(d, 'found_4.jsonl')
    if not os.path.exists(f):
        print('MISSING', f); continue
    got = {json.loads(l)['name'] for l in open(f) if l.strip()}
    assert got <= names, (d, len(got - names))
    res[(arm, int(seed), kind)] = len(got)

print('dial on data/p2/targets_depth3.jsonl (1000), 4 rounds, k=32, T0.8, batch 2048')
print('arm seed   EI cum solved   frozen cum solved   EI - frozen')
for arm in ['c0', 'r1', 'r2', 'r3', 'r4']:
    for s in (0, 1):
        if (arm, s, 'ei') not in res:
            continue
        e = res[(arm, s, 'ei')]; f = res[(arm, s, 'frz')]
        print('%-3s  %d     %5d (%.3f)    %5d (%.3f)       %+.3f' % (arm, s, e, e / 1000, f, f / 1000, (e - f) / 1000))

# cross-check against the run's own round_4.json
print('\nround_4.json targets_cum.solved for comparison')
for d in sorted(glob.glob('artifacts/dsr/*/ei_d3_*_s?') + glob.glob('artifacts/dsr/*/frz_d3_*_s?')):
    j = os.path.join(d, 'round_4.json')
    if os.path.exists(j):
        print('%-40s %d' % (os.path.basename(d), json.load(open(j))['targets_cum']['solved']))
