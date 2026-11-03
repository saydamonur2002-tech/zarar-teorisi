import sys,json,itertools,csv,inspect,textwrap,os
os.chdir(os.path.dirname(os.path.abspath(__file__))+'/..')
sys.path.insert(0,'pr44_kopya');sys.path.insert(0,'pr44_kopya/cipali_uc_kural')
from cipali_uc_kural import kosu as K
from uc_kural_senaryo import load
cek=load();t=json.load(open('pr44_kopya/cipali_uc_kural/tahmin.json'))
R=62.12  # TP.KTF10 2026-10 [VEKİL: kod adı doğrulanmadı]
src=textwrap.dedent(inspect.getsource(K.calistir))
o1='pi_q = 3.0 * paket["alfa_pass"] + paket["lam"] * g'
o2='        st.kapsama = st.net_taban / st.yasam_maliyeti\n'
o3='"kapsama": st.kapsama,'
for o in (o1,o2,o3): assert o in src,o
src=src.replace(o1,o1+' + KREDI_PI(durum)').replace(o2,o2+'        KREDI_ADIM(st, durum, spec)\n').replace(o3,o3+' "etkin": durum.get("etkin"), "B": durum.get("B",0.0),').replace('def calistir(','def calistir5(')
ns=dict(vars(K));exec(src,ns);C=ns['calistir5']
def kur(kappa,mu,k2acik):
    def pi(d): return mu*100*d.get('kredi_q',0.0)/max(d.get('yas_q',1.0),1e-9)
    def adim(st,d,spec):
        B=d.get('B',0.0);servis=R/400*B+B/16
        acik=max(st.yasam_maliyeti-st.net_taban,0)*3
        kr=kappa*acik
        if spec['kilitli'] and k2acik:
            piy=d.get('pi',30.0);f=max(0.0,1+(-8)/max(piy,1.0))
            kr=0.0 if st.limit_dondur else kr*f
        d['B']=B*(1+R/400)-servis+kr+ (R/400*B)*0  # faiz servisle ödenir
        d['B']=max(B+kr-B/16,0.0)
        d['kredi_q']=kr;d['yas_q']=st.yasam_maliyeti*3
        d['etkin']=(st.net_taban-servis/3)/st.yasam_maliyeti
    return pi,adim
def k1e(yol):
    if not yol.get('kosuldu') or yol['patlama']: return 'kaldi'
    k0=yol['kap0'];e=[r['etkin'] for r in yol['satir']]
    if e[-1]<k0-0.02: return 'kaldi'
    return 'kaldi' if any(a<0.95*k0 and b<0.95*k0 for a,b in zip(e,e[1:])) else 'gecti'
rows=[]
for w,ap,lam,kap,mu,k2,faiz in itertools.product([0,.5,1],[1.951,0.0],[0.16,0.409],[0,.25,.5],[0,.05,.1],['acik','kapali'],['sabit','tepkili']):
    ns['KREDI_PI'],ns['KREDI_ADIM']=kur(kap,mu,k2=='acik');ns['H']=5.0
    t2=json.loads(json.dumps(t));t2['gecis']['R2426']['lam']=lam;t2['gecis']['R2426']['alfa']=ap
    o={k:C(cek,t2,{'mod':'a','faiz':faiz,'kilitli':k,'w':w}) for k in [True,False]}
    a,b,c=K.k1(o[True]),K.k2(o[True],o[False]),K.k3(o[True]);ae=k1e(o[True]);s=o[True]['satir']
    c2='sinanmadi' if o[True]['patlama'] else ('gecti' if any(r['pi_y']<=7 for r in s) else 'kaldi')
    rows.append(dict(w=w,alfa_pass=ap,lam=lam,kappa=kap,mu=mu,K2tavan=k2,faiz=faiz,K1=a,K1etkin=ae,K2=b,K3=c,K3alt=c2,birlikte=K.birlikte(a,b,c),birlikte_alt=K.birlikte(a,b,c2),birlikte_alt_etkin=K.birlikte(ae,b,c2),pi2031=round(s[-1]['pi_y'],1) if s else None,kap2031=round(s[-1]['kapsama'],3) if s else None,etkin2031=round(s[-1]['etkin'],3) if s else None,patlama=o[True]['patlama']))
with open('karsilama_kredi/izgara_v5.csv','w') as f:
    wr=csv.DictWriter(f,rows[0].keys());wr.writeheader();wr.writerows(rows)
print(len(rows))
