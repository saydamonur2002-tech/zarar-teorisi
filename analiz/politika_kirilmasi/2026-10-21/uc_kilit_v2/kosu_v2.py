import sys,json,itertools,csv
sys.path.insert(0,'pr44_kopya');sys.path.insert(0,'pr44_kopya/cipali_uc_kural')
from cipali_uc_kural import kosu as K
from uc_kural_senaryo import load
cek=load()
t=json.load(open('pr44_kopya/cipali_uc_kural/tahmin.json'))
bas=t['baslangic']['gozlem'];print('baslangic',bas)
R=t['beklenti']['R2426']['serbest']['b']
orig_calistir=K.calistir
def run(spec,H,alfa_g,lam,ap,i_sabit,sabitli):
    K.H=H
    t2=json.loads(json.dumps(t));k=t2['kur']['R2426'];k['alfa_g']=alfa_g
    g=t2['gecis']['R2426'];g['lam']=lam;g['alfa']=ap
    if i_sabit is not None: t2['baslangic']['gozlem']['i']=i_sabit
    if sabitli: # e24 = a + b pi + c g12 : w=0 ve phi ile taklit edilemez -> H'yi a/(w) ile değil; w=1 ve H=a+b*pi... dinamik: özel yol
        pass
    return orig_calistir(cek,t2,spec)
pi0=bas['pi']; i0=bas['i']
KUR={'pr_R2426':2.751470054226085,'kst_taban':13.405/3,'kst_kalan':3.591/3,'sifir':0.0}
rows=[]
for w,dl,kn,lam,ap,faiz,ir in itertools.product([0,.25,.5,.75,1],[0,0.9,bas['e']-5],KUR,[0.160,0.409],[1.951,0.0],['sabit','tepkili'],['i0','pi+5','pi-5']):
    if faiz=='tepkili' and ir!='i0': continue
    isb={'i0':None,'pi+5':pi0+5,'pi-5':pi0-5}[ir]
    out={}
    for kil in [True,False]:
        out[kil]=run({'mod':'a','faiz':faiz,'kilitli':kil,'w':w},5+dl,KUR[kn],lam,ap,isb,False)
    a,b,c=K.k1(out[True]),K.k2(out[True],out[False]),K.k3(out[True])
    s=out[True]['satir'];rows.append(dict(w=w,delta=round(dl,2),kur=kn,lam=lam,alfa_pass=ap,faiz=faiz,i=ir,K1=a,K2=b,K3=c,birlikte=K.birlikte(a,b,c),pi2031=round(s[-1]['pi_y'],1) if s else None,kap2031=round(s[-1]['kapsama'],3) if s else None,patlama=out[True]['patlama'],dondur=sum(r['limit_dondur'] for r in s)))
with open('izgara_gecici.csv','w') as f:
    wr=csv.DictWriter(f,rows[0].keys());wr.writeheader();wr.writerows(rows)
print(len(rows))
