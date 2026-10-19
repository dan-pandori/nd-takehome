"""Reductio-kinds figure check: each proof with #10 counted once by its best instance (working > non-vacuous template > vacuous).
Note: per-record labels give kinds present and the working flag; a non-working record with a scaffolded kind has only
immediate-route scaffolded instances (else it would be working)."""
import gzip, json, collections as C
O = '/home/dan/review/proof-strategies/review_ps/out/'
for s in ['k12', 'k12dose1', 'tb_schema_search', 'charles_base', 'textbook72_search']:
    c = C.Counter()
    for l in gzip.open(O + f'labels_{s}.jsonl.gz', 'rt'):
        r = json.loads(l)
        if 'contradiction' not in r.get('uses', []): continue
        sub = set(r['sub'])
        c['n'] += 1
        if 'contradiction' in r['work']: c['working'] += 1
        elif {'contradiction.pointless', 'contradiction.scaffolded'} & sub: c['template_nonvac'] += 1
        elif 'contradiction.vacuous' in sub: c['vacuous_only'] += 1
        else: c['other'] += 1
    n = c['n']
    print(s, dict(c), {k: f"{100*v/n:.1f} %" for k, v in c.items() if k != 'n'})
