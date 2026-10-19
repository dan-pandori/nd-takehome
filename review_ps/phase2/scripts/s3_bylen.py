import json
S = json.load(open('/home/dan/review/proof-strategies/review_ps/out/summary_all.json'))
for s in ['k12', 'k12ko', 'k12dose1']:
    bl = S[s]['by_len']
    print(s, {int(k): v['n'] for k, v in sorted(bl.items(), key=lambda kv: int(kv[0]))}, 'min', min(v['n'] for v in bl.values()), 'max', max(v['n'] for v in bl.values()))
print('k12 depth', {k: v.get('n') for k, v in S['k12']['by_depth'].items()})
