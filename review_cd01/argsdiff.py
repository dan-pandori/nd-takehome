#!/usr/bin/env python3
"""Reviewer (coe-dose01): diff each new ladder's args.json against the 1 % arm's (same seed), and knockout s1's r25-32
args against its r17-24 args; _meta (git sha, host, utc) reported separately."""
import json, subprocess
W = '/home/dan/work'
def load(path):
    return json.load(open(path))
def diff(a, b):
    ks = sorted(set(a) | set(b))
    return {k: (a.get(k), b.get(k)) for k in ks if k != '_meta' and a.get(k) != b.get(k)}
out = {}
for S in (0, 1, 2):
    a = load(f'{W}/coe-dose01/artifacts/coe/ladder/la_dose01_s{S}/args.json')
    b = load(f'{W}/create-or-elicit/artifacts/coe/ladder/la_dose1_s{S}/args.json')
    d = diff(a, b)
    out[f'dose01_s{S} vs dose1_s{S}'] = {k: v for k, v in d.items()}
    print(f'dose01_s{S} vs dose1_s{S}:', d)
    print('   argv new:', ' '.join(a['_meta']['argv'][1:]))
    print('   argv 1 %:', ' '.join(b['_meta']['argv'][1:]))
    print('   sha new', a['_meta']['git_sha'][:8], 'sha 1 %', b['_meta']['git_sha'][:8])
a = load(f'{W}/coe-dose01/artifacts/coe/ladder/la_ko_s1/args_r25-32.json')
b = load(f'{W}/create-or-elicit/artifacts/coe/ladder/la_ko_s1/args_r17-24.json') if __import__('os').path.exists(f'{W}/create-or-elicit/artifacts/coe/ladder/la_ko_s1/args_r17-24.json') else load(f'{W}/create-or-elicit/artifacts/coe/ladder/la_ko_s1/args.json')
d = diff(a, b)
out['ko_s1 r25-32 vs r17-24'] = d
print('ko_s1 r25-32 vs create-or-elicit r17-24:', d)
print('   argv r25-32:', ' '.join(a['_meta']['argv'][1:]), '| sha', a['_meta']['git_sha'][:8])
print('   argv r17-24:', ' '.join(b['_meta']['argv'][1:]), '| sha', b['_meta']['git_sha'][:8])
# code differences between the 1 % arm's launch sha and this run's sha, limited to files a ladder / read imports
shas = sorted({load(f'{W}/create-or-elicit/artifacts/coe/ladder/la_dose1_s{S}/args.json')['_meta']['git_sha'] for S in (0, 1, 2)})
new = load(f'{W}/coe-dose01/artifacts/coe/ladder/la_dose01_s0/args.json')['_meta']['git_sha']
for s in shas:
    r = subprocess.run(['git', '-C', f'{W}/coe-dose01', 'diff', '--stat', s, new, '--', '*.py', ':!coe/', ':!review_*', ':!rl_needed/'], capture_output=True, text=True)
    print(f'code diff {s[:8]}..{new[:8]} (*.py outside coe/, review_*/, rl_needed/):', r.stdout.strip().splitlines()[-1] if r.stdout.strip() else 'none', r.stderr.strip()[:200])
    out[f'code_diff_{s[:8]}'] = r.stdout
json.dump(out, open(f'{W}/coe-dose01/review_cd01/out/argsdiff.json', 'w'), indent=1)
