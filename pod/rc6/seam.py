# Seamlessness check 3: every target / transfer theorem solved in found_8 is still solved in found_9; proof counts.
import json, sys
d = f'artifacts/rc6/la_T1_best6_s{sys.argv[1]}'
def names(f): return {json.loads(l)['name'] for l in open(f'{d}/{f}')}
for k in ('found', 'found_transfer'):
    a, b = names(f'{k}_8.jsonl'), names(f'{k}_9.jsonl')
    print(sys.argv[1], k, 'r8', len(a), 'r9', len(b), 'r8 not in r9', len(a - b), 'new', len(b - a))
