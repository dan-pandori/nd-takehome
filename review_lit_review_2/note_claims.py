import re,json,glob,os
rows=[]
for f in sorted(glob.glob(os.path.expanduser('~/review/lit-review-2/lit_review_2/notes/*.md'))):
    t=open(f).read(); m=re.search(r'arxiv\.org/abs/([0-9.]+v\d+)',t)
    idv=m.group(1) if m else '—'
    for l in t.splitlines():
        for q in re.findall(r'"([^"]{12,})"',l):
            rows.append(dict(sec='note:'+os.path.basename(f)[:-3],claim=l.strip()[:200],idv=idv,loc='',snip='"'+q+'"',v=''))
json.dump(rows,open('note_claims.json','w'),indent=1); print(len(rows),{r['idv'] for r in rows})
