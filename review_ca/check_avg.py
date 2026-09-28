import ptread, numpy as np, os
SD='/tmp/rv_ca/sd'; CA='../ckpts/ca'
L=lambda p: ptread.load(p)['state']
cache={}
def st(n):
    if n not in cache: cache[n]=L(f'{SD}/{n}.pt')
    return cache[n]
W=lambda t:f'w_s3.step{t:05d}'
F=lambda t:f'f_s1.step{t:05d}'
exp={'w_s3.A24_K2':[W(18000),W(19000)],'w_s3.A24_K4':[W(t) for t in range(16000,20000,1000)],
     'w_s3.A24_K8':[W(t) for t in range(12000,20000,1000)],'w_s3.T24_3':[W(22000),W(23000),'w_s3'],
     'w_s3.T24_5':[W(t) for t in range(20000,24000,1000)]+['w_s3'],'w_s0.CTRL_self19000':['w_s0.step19000']*2,
     'f_s1.A24_K8':[F(t) for t in range(4000,20000,2000)],'f_s1.A24_K4':[F(t) for t in range(12000,20000,2000)]}
for name,mem in exp.items():
    a=L(f'{CA}/{name}.pt'); ms=[st(m) for m in mem]
    md=0; mind=0
    for k,v in a.items():
        mean=np.mean([m[k].astype(np.float64) for m in ms],axis=0)
        md=max(md,float(np.abs(v-mean).max()))
        mind=max(mind, float(np.abs(v-ms[-1][k]).max()))
    print(f'{name:22s} max|avg-mean(members)|={md:.2e}  max|avg-last member|={mind:.2e}')
