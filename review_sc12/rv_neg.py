"""negative controls: (a) prefilter-rejected literal texts from the dumps, (b) an accepted text under a different
prompt's header, (c) an accepted text with its last step removed."""
import json, os, sys, random, glob
sys.path.insert(0, os.path.dirname(__file__))
from rv_common import rd
B = os.path.expanduser(os.environ.get('RV_BASE', '~/review/state-cap12'))
rng = random.Random(7)
pos = list(rd(f'{B}/rv/lean_sample_pos.jsonl'))
neg = []
for fn in sorted(glob.glob(f'{B}/dl/dump/rr_*rr600.jsonl.gz'))[:6]:
    rej = [r for r in rd(fn) if r['lean_ok'] is not True]
    for r in rng.sample(rej, 25):
        neg.append({'tag': os.path.basename(fn), 'kind': 'prefilter_rej:' + str(r.get('filter')), 'prompt': r['prompt'], 'text': r['lean_text'], 'expect': False})
sh = rng.sample(pos, 150)
for a, b in zip(sh[:75], sh[75:]):
    if a['prompt'] != b['prompt']:
        neg.append({'tag': a['tag'], 'kind': 'swapped_header', 'prompt': b['prompt'], 'text': a['text'], 'expect': False})
for a in rng.sample(pos, 75):
    t = a['text'].rsplit(' ; ', 1)[0]
    neg.append({'tag': a['tag'], 'kind': 'last_step_dropped', 'prompt': a['prompt'], 'text': t, 'expect': False})
with open(f'{B}/rv/lean_sample_all.jsonl', 'w') as f:
    for r in pos + neg:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(len(pos), len(neg))
