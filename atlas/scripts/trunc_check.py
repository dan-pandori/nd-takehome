"""Truncation check for the whole-proof re-score: every read with > 0.1 % of samples at max_new 512 was re-read at
max_new 1,024 (same batch 2,048, sample seed 0; per-row seeding, so rows that end before 512 tokens decode the same).
Writes atlas/data/truncation_check.csv and prints solved / truncated share at both caps."""
import csv, glob, json, os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
E = os.path.join(ROOT, 'artifacts', 'atlas')
out = []
print(f'{"read":16s} {"solved@512":>10s} {"solved@1024":>11s} {"trunc@512":>9s} {"trunc@1024":>10s} {"same-solved-set":>15s}')
for f in sorted(glob.glob(os.path.join(E, 'eval_mn1024', '*__*.json'))):
    if f.endswith(('.args.json', '.genstats.json')):
        continue
    name = os.path.basename(f)[:-5]
    a, b = os.path.join(E, 'eval', name), os.path.join(E, 'eval_mn1024', name)
    if not os.path.exists(a + '.json'):
        continue
    sa, sb = json.load(open(a + '.json'))['solved'], json.load(open(b + '.json'))['solved']
    ga, gb = json.load(open(a + '.jsonl.genstats.json')), json.load(open(b + '.jsonl.genstats.json'))
    ta, tb = ga['truncated'] / ga['rows'], gb['truncated'] / gb['rows']
    seta = {json.loads(l)['thm'] for l in open(a + '.jsonl') if json.loads(l)['solved']}
    setb = {json.loads(l)['thm'] for l in open(b + '.jsonl') if json.loads(l)['solved']}
    out.append(dict(read=name, solved_512=sa, solved_1024=sb, trunc_512=round(ta, 6), trunc_1024=round(tb, 6),
                    only_512=len(seta - setb), only_1024=len(setb - seta)))
    print(f'{name:16s} {sa:10d} {sb:11d} {ta:9.4%} {tb:10.4%} {"yes" if seta == setb else f"-{len(seta-setb)}/+{len(setb-seta)}":>15s}')
with open(os.path.join(ROOT, 'atlas', 'data', 'truncation_check.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
