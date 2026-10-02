import re,json,sys,glob,os
rows=[]
sec=None
def cells(l): return [c.strip() for c in re.split(r'(?<!\\)\|',l.strip())[1:-1]]
for f in [os.path.expanduser('~/review/lit-review-2/lit_review_2/claims.md')]:
    for l in open(f):
        if l.startswith('## '): sec=l[3:].strip()
        if l.startswith('|') and not l.startswith('|---') and not l.startswith('| claim') and not l.startswith('| id '):
            c=cells(l)
            if sec.startswith('Q') and len(c)==5:
                rows.append(dict(sec=sec,claim=c[0],idv=c[1],loc=c[2],snip=c[3],v=c[4]))
json.dump(rows,open('claims.json','w'),indent=1)
print(len(rows)); from collections import Counter; print(Counter(r['sec'] for r in rows)); print(Counter(r['v'][:10] for r in rows))
ids=sorted({r['idv'] for r in rows if r['idv']!='—'}); print(len(ids),ids)
