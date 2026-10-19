"""Mean term size (executor per-record ts, shown equal to the reviewer's formula) and mean Lp per set; one file at a time."""
import gzip, json
E = '/home/dan/work/proof-strategies/artifacts/ps/labels'
out = {}
for s in ['k12', 'cap6', 'k12ko', 'k12dose1', 'rl_targets_gen', 'transfer_gen', 'holdout250_gen', 'k12_min990', 'tb_schema_search', 'charles_base', 'textbook72_search']:
    n = ts = lp = pf = 0
    for l in gzip.open(f'{E}/{s}.jsonl.gz', 'rt'):
        a = json.loads(l)
        if a.get('parse_fail'):
            pf += 1; continue
        n += 1; ts += a['ts']; lp += a['Lp']
    out[s] = {'n': n, 'parse_fail': pf, 'mean_ts': ts / n, 'mean_Lp': lp / n}
    print(s, out[s], flush=True)
json.dump(out, open('/home/dan/review/proof-strategies/phase2/scripts/tab_ts.out.json', 'w'), indent=1)
