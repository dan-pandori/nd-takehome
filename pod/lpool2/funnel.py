import json,collections,sys
out={}  # name -> (gen_lines, outcome, secs, thm)
for c in ['g1','g2','g3','g4']:
    for b in [10,12,14,16]:
        for l in open(f'/tmp/lp/{c}_ml{b}.jsonl'):
            r=json.loads(l); n=r['name']
            gl,_,s,thm=out.get(n,(r.get('gen_lines'),None,0.0,r['thm']))
            s+=r['secs']
            if r['timeout'] or r.get('error'): o='TO'
            elif r['min_lines_ub'] is not None: o=r['min_lines_ub']
            else: o='>%d'%b
            out[n]=(gl,o,s,thm)
json.dump(out,open('/tmp/lp/funnel.json','w'))
