import sys,json,itertools,csv,inspect,textwrap
sys.path.insert(0,'pr44_kopya');sys.path.insert(0,'pr44_kopya/cipali_uc_kural')
from cipali_uc_kural import kosu as K
from uc_kural_senaryo import load
cek=load();t=json.load(open('pr44_kopya/cipali_uc_kural/tahmin.json'))
src=textwrap.dedent(inspect.getsource(K.calistir))
old='g_ham = 3.0 * (paket["alfa_g"] + paket["beta_i"] * durum["i_giren"])'
assert old in src
src=src.replace(old,old+' + KURX(durum)').replace('def calistir(','def calistir3(')
ns=dict(vars(K));exec(src,ns);calistir3=ns['calistir3']
b0=t['baslangic']['gozlem'];pi0,e0=b0['pi'],b0['e']
def setx(bp,be): ns['KURX']=lambda d:bp*(d['pi']-pi0)+be*(d['e']-e0)
KUR={'pr_R2426':(2.751470054226085,None,0,0),'kst_kalan':(3.591/3,None,0,0),
 'a_cursor_dogru':(13.41/3,-0.187/3,0,0),'b_cursor_parca':(13.41/3,-0.187/3,0.018,0.137),
 'c_ust':(13.41/3,-0.187/3,0.355,1.544),'c_alt':(13.41/3,-0.187/3,-0.319,-1.270)}
rows=[]
for w,dl,kn,lam,ap,faiz in itertools.product([0,.25,.5,.75,1],[0,0.9],KUR,[0.160,0.409],[1.951,0.0],['sabit','tepkili']):
    ag,bi,bp,be=KUR[kn];setx(bp,be);ns['H']=5+dl
    t2=json.loads(json.dumps(t));t2['kur']['R2426']['alfa_g']=ag
    if bi is not None: t2['kur']['R2426']['beta_i']=bi
    t2['gecis']['R2426']['lam']=lam;t2['gecis']['R2426']['alfa']=ap
    o={kil:calistir3(cek,t2,{'mod':'a','faiz':faiz,'kilitli':kil,'w':w}) for kil in [True,False]}
    a,b,c=K.k1(o[True]),K.k2(o[True],o[False]),K.k3(o[True]);s=o[True]['satir']
    c2='sinanmadi' if o[True]['patlama'] else ('gecti' if any(r['pi_y']<=7 for r in s) else 'kaldi')
    rows.append(dict(w=w,delta=dl,kur=kn,lam=lam,alfa_pass=ap,faiz=faiz,K1=a,K2=b,K3=c,birlikte=K.birlikte(a,b,c),K3alt=c2,birlikte_alt=K.birlikte(a,b,c2),pi2031=round(s[-1]['pi_y'],1) if s else None,pimin=round(min(r['pi_y'] for r in s),1) if s else None,kap2031=round(s[-1]['kapsama'],3) if s else None,patlama=o[True]['patlama']))
with open('izgara_v3.csv','w') as f:
    wr=csv.DictWriter(f,rows[0].keys());wr.writeheader();wr.writerows(rows)
print(len(rows), 'kap0', o[True]['kap0'])
