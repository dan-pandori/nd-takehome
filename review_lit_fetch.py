# Reviewer (lit-review): independent arXiv/Nature text fetcher. Usage: python3 review_lit_fetch.py 2502.03438v3 ... -> ~/rv_lit/src/<id>.txt
import sys,re,html,urllib.request,io,os
UA={'User-Agent':'Mozilla/5.0 (reviewer)'}
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60).read()
def html_text(b):
    s=b.decode('utf8','ignore')
    s=re.sub(r'(?s)<(script|style|math)[^>]*>.*?</\1>',lambda m: ' '+(re.search(r'alttext="([^"]*)"',m.group(0)).group(1) if m.group(1)=='math' and 'alttext' in m.group(0) else '')+' ',s)
    s=re.sub(r'<(br|p|div|tr|h\d|li|table|figcaption|section)[^>]*>','\n',s)
    s=re.sub(r'</t[dh]>',' | ',s)
    s=re.sub(r'<[^>]+>','',s)
    return re.sub(r'[ \t]+',' ',html.unescape(s))
for idv in sys.argv[1:]:
    out=os.path.expanduser(f'~/rv_lit/src/{idv}.txt')
    if os.path.exists(out): continue
    t=None
    try:
        b=get(f'https://arxiv.org/html/{idv}'); t=html_text(b)
        if 'No HTML for' in t or len(t)<20000: t=None
    except Exception as e: pass
    if t is None:
        import glob; sys.path.insert(0,glob.glob('/tmp/lrvenv/lib/python3*/site-packages')[0])
        import pypdf
        b=get(f'https://arxiv.org/pdf/{idv}')
        t='\n'.join(p.extract_text() or '' for p in pypdf.PdfReader(io.BytesIO(b)).pages); t='[PDF]\n'+t
    open(out,'w').write(t); print(idv,len(t),t[:6])
