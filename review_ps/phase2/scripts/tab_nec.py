"""TABLES.md s5: necessity rows recomputed from data/ps/nec/*.checked.jsonl (reviewer copy). Prints counts only."""
import json, gzip, collections
D = '/home/dan/review/proof-strategies/data/ps'
O = '/home/dan/review/proof-strategies/review_ps/out'
res = {}
for fn in ('k12_nec594', 'charles_base', 'textbook72'):
    rows = [json.loads(l) for l in open(f'{D}/nec/{fn}.checked.jsonl')]
    n = len(rows)
    free_n_notnone = [r for r in rows if r['free']['n'] is not None]
    free_proof = [r for r in rows if r['free'].get('proof')]
    free_lean = [r for r in rows if r['free'].get('lean_ok')]
    free_to = sum(1 for r in rows if r['free']['timeout'])
    # anomalies: n not None but no proof / n > 12
    anom = [(i, r['free']['n'], r['free']['timeout'], bool(r['free'].get('proof')), r['free'].get('lean_ok')) for i, r in enumerate(rows)
            if (r['free']['n'] is not None) != bool(r['free'].get('proof')) or (r['free']['n'] is not None and r['free']['n'] > 12)]
    nmax = max((r['free']['n'] for r in free_n_notnone), default=None)
    dec = free_n_notnone
    req = {b: sum(bool(r['requires'][b]) for r in dec) for b in ('ORE', 'NEGI', 'BOTE', 'DN')}
    req_all = {b: sum(bool(r['requires'][b]) for r in rows) for b in ('ORE', 'NEGI', 'BOTE', 'DN')}
    to_dec = {b: sum(1 for r in dec if (r['ban'] or {}).get(b) and r['ban'][b]['timeout']) for b in req}
    to_all = {b: sum(1 for r in rows if (r['ban'].get(b) or {}).get('timeout')) for b in req}
    ban_none = sum(1 for r in rows if r['ban'] is None or any(r['ban'].get(b) is None for b in req))
    ban_found = sum(1 for r in rows for b in req if r['ban'] and r['ban'].get(b) and r['ban'][b].get('proof'))
    ban_lean = sum(1 for r in rows for b in req if r['ban'] and r['ban'].get(b) and r['ban'][b].get('proof') and r['ban'][b].get('lean_ok'))
    free_lean_ok = sum(1 for r in rows if r['free'].get('proof') and r['free'].get('lean_ok'))
    res[fn] = dict(n=n, free_n_notnone=len(free_n_notnone), free_proof=len(free_proof), free_lean=len(free_lean), free_timeout=free_to,
                   free_nmax=nmax, anomalies=anom, requires_decided=req, requires_all=req_all, ban_timeouts_decided=to_dec,
                   ban_timeouts_all=to_all, ban_none=ban_none, proofs_found=len(free_proof) + ban_found, proofs_lean_ok=free_lean_ok + ban_lean)
    print(fn, json.dumps(res[fn]))
json.dump(res, open('/home/dan/review/proof-strategies/phase2/scripts/tab_nec.out.json', 'w'), indent=1)
