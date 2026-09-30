"""long-pool-2 probe: per-bound timing of minlen's iterative deepening past 16 (same Search class, same memo).
Usage: probe.py <in.jsonl> <out.jsonl> <max_bound> <time_limit_s> [max_depth|none] [lemmas 1|0]
Writes one record per theorem: seconds at which each total was completed without a proof, and the proof if found."""
import json, sys, time, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import minlen
inp, out, B, T = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4])
md = None if len(sys.argv) < 6 or sys.argv[5] == 'none' else int(sys.argv[5])
lem = True if len(sys.argv) < 7 else sys.argv[6] == '1'
with open(out, 'a') as fo:
    for l in open(inp):
        r = json.loads(l); prem, concl = minlen.parse_thm(r['prompt']); t0 = time.time()
        s = minlen.Search(prem, concl, deadline=t0 + T, lemmas=lem, max_depth=md)
        done, found = {}, None
        try:
            for total in range(len(prem) + 1, B + 1):
                x = s.best(concl, frozenset(prem), total - len(prem))
                if x:
                    found = (len(prem) + x[0], s.to_text(x[1])); break
                done[total] = round(time.time() - t0, 1)
        except minlen.Timeout:
            pass
        fo.write(json.dumps({'name': r['name'], 'gen_lines': r.get('gen_lines'), 'done': done, 'found': found,
                             'secs': round(time.time() - t0, 1), 'max_depth': md, 'lemmas': lem}) + '\n'); fo.flush()
