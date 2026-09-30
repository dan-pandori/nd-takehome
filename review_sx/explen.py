import json, os, statistics as S, collections
A = os.path.expanduser('~/review/search-expert/artifacts/sx')
def shortest(tag):
    d = {}
    for l in open(f'{A}/{tag}/found_8.jsonl'):
        r = json.loads(l); n = r['proof'].count(';')
        k = (n, len(r['proof'].split()))
        if r['name'] not in d or k < d[r['name']]: d[r['name']] = k
    return d
for ex, base, seeds in (('B', 'A', range(6)), ('C', 'A2', range(2))):
    for s in seeds:
        e = shortest(f'{ex}_s{s}'); b = shortest(f'{base}_s{s}')
        both = set(e) & set(b)
        dl = [e[t][0] - b[t][0] for t in both]
        c = collections.Counter((x > 0) - (x < 0) for x in dl)
        print(f'{ex} vs {base} s{s}: both {len(both)} median dLines {S.median(dl)} mean {S.mean(dl):.3f} longer {c[1]} same {c[0]} shorter {c[-1]}')
