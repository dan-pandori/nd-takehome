"""evidence-atlas re-score: eval_set.py (unchanged) with max_new set and sampler stop counts recorded.

Usage (from the repo root): MAXNEW=512 python3 atlas/scripts/rescore.py <eval_set.py args>
Writes <--out>.genstats.json: the sampler's stats (rows, stop_eos/exact/goal, peak memory) plus
`truncated` = rows that stopped for none of those reasons, i.e. hit max_new."""
import json, os, sys
sys.path.insert(0, os.getcwd())
import eval_set

MAXNEW = int(os.environ.get('MAXNEW', '512'))
STATS = {}
_gen = eval_set.generate


def generate(*a, **k):
    k.setdefault('max_new', MAXNEW)
    k['stats'] = STATS
    return _gen(*a, **k)


eval_set.generate = generate
eval_set.main()
out = sys.argv[sys.argv.index('--out') + 1]
STATS['max_new'] = MAXNEW
for key in ('declen', 'declen_by_prompt'):    # per-row lists: keep only a summary
    v = STATS.pop(key, None) or []
    if v:
        STATS[key + '_max'] = max(v); STATS[key + '_ge_max_new'] = sum(1 for x in v if x >= MAXNEW)
STATS['truncated'] = STATS.get('rows', 0) - sum(STATS.get(s, 0) for s in ('stop_eos', 'stop_exact', 'stop_goal'))
json.dump(STATS, open(out + '.genstats.json', 'w'), indent=1)
print('genstats', json.dumps(STATS), flush=True)
