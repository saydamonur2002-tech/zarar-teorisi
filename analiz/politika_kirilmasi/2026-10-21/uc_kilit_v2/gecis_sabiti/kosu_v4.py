import sys,json,itertools,csv,inspect,textwrap,os
os.chdir(os.path.dirname(os.path.abspath(__file__))+'/..')
sys.path.insert(0,'pr44_kopya');sys.path.insert(0,'pr44_kopya/cipali_uc_kural')
from cipali_uc_kural import kosu as K
from uc_kural_senaryo import load
cek=load();t=json.load(open('pr44_kopya/cipali_uc_kural/tahmin.json'))
src=textwrap.dedent(inspect.getsource(K.calistir))
o1='g_ham = 3.0 * (paket["alfa_g"] + paket["beta_i"] * durum["i_giren"])';o2='pi_q = 3.0 * paket["alfa_pass"] + paket["lam"] * g'
assert o1 in src and o2 in src
src=src.replace(o1,o1+' + KURX(durum)').replace(o2,'pi_q = PIQ(paket, g, durum, e24)').replace('def calistir(','def calistir4(')
ns=dict(vars(K));exec(src,ns);C=ns['calistir4']
b0=t['baslangic']['gozlem'];pi0,e0=b0['pi'],b0['e']
KUR={'pr_R2426':(2.751470054226085,None,0,0),'kst_kalan':(3.591/3,None,0,0),'a_cursor_dogru':(13.41/3,-0.187/3,0,0),'b_cursor_parca':(13.41/3,-0.187/3,0.018,0.137)}
GEC={'pr_1951':lambda p,g,d,e:3*1.951+p['lam']*g,
 'kalan_M5_1302':lambda p,g,d,e:3*1.302+p['lam']*g,
 'atalet_M5':lambda p,g,d,e:3*1.302+0.481*d['p'][-1]+p['lam']*g,
 'beklenti_M3':lambda p,g,d,e:3*(-0.841+2.156*e/12)+p['lam']*g}
rows=[]
for w,kn,lam,gn,faiz in itertools.product([0,.25,.5,.75,1],KUR,[0.160,0.409],GEC,['sabit','tepkili']):
    ag,bi,bp,be=KUR[kn];ns['KURX']=lambda d,bp=bp,be=be:bp*(d['pi']-pi0)+be*(d['e']-e0);ns['PIQ']=GEC[gn];ns['H']=5.0
    t2=json.loads(json.dumps(t));t2['kur']['R2426']['alfa_g']=ag
    if bi is not None: t2['kur']['R2426']['beta_i']=bi
    t2['gecis']['R2426']['lam']=lam
    o={k:C(cek,t2,{'mod':'a','faiz':faiz,'kilitli':k,'w':w}) for k in [True,False]}
    a,b,c=K.k1(o[True]),K.k2(o[True],o[False]),K.k3(o[True]);s=o[True]['satir']
    c2='sinanmadi' if o[True]['patlama'] else ('gecti' if any(r['pi_y']<=7 for r in s) else 'kaldi')
    rows.append(dict(w=w,kur=kn,lam=lam,gecis=gn,faiz=faiz,K1=a,K2=b,K3=c,birlikte=K.birlikte(a,b,c),K3alt=c2,birlikte_alt=K.birlikte(a,b,c2),pi2031=round(s[-1]['pi_y'],1) if s else None,patlama=o[True]['patlama']))
with open('gecis_sabiti/izgara_v4.csv','w') as f:
    wr=csv.DictWriter(f,rows[0].keys());wr.writeheader();wr.writerows(rows)
