# Reviewer's own fetcher: abs page (title, version check) + HTML full text, else PDF text (pdfminer from /tmp/lrvenv).
import json,re,sys,time,urllib.request,html,io,os
UA={"User-Agent":"Mozilla/5.0 (review; research)"}
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=90) as r: return r.read(), r.status
def strip(h):
    h=re.sub(r'(?is)<(script|style|nav|header|footer)\b.*?</\1>',' ',h)
    # keep math alttext so LaTeX-y quotes can match
    h=re.sub(r'(?is)<math[^>]*alttext="([^"]*)"[^>]*>.*?</math>',lambda m:' '+m.group(1)+' ',h)
    h=re.sub(r'(?s)<[^>]+>',' ',h); return html.unescape(h)
ids=json.load(open('ids.json'))
meta={}
for idv in ids:
    out=f'src/{idv}.txt'
    try:
        a,_=get(f'https://arxiv.org/abs/{idv}'); a=a.decode('utf8','replace')
        t=re.search(r'<meta name="citation_title" content="([^"]*)"',a)
        meta[idv]={'title':html.unescape(t.group(1)) if t else None}
    except Exception as e:
        meta[idv]={'title':None,'err':str(e)}; print(idv,'ABS FAIL',e,flush=True); continue
    if not os.path.exists(out):
        src=None
        try:
            h,_=get(f'https://arxiv.org/html/{idv}'); h=h.decode('utf8','replace')
            if len(h)>20000 and 'ltx_' in h: open(out,'w').write(strip(h)); src='html'
        except Exception: pass
        if not src:
            try:
                p,_=get(f'https://arxiv.org/pdf/{idv}')
                sys.path.insert(0,'/tmp/lrvenv/lib/python3.12/site-packages')
                from pdfminer.high_level import extract_text
                open(out,'w').write(extract_text(io.BytesIO(p))); src='pdf'
            except Exception as e: src='FAIL '+str(e)
        meta[idv]['src']=src
    print(idv,meta[idv],flush=True); time.sleep(2)
json.dump(meta,open('meta.json','w'),indent=1)
