import sys,json,os
os.chdir(os.path.dirname(os.path.abspath(__file__))+'/..')
sys.path.insert(0,'pr44_kopya');sys.path.insert(0,'pr44_kopya/cipali_uc_kural')
from cipali_uc_kural import kosu as K
from uc_kural_senaryo import load
cek=load();t=json.load(open('pr44_kopya/cipali_uc_kural/tahmin.json'))
def run(tag):
    out=[]
    for w in [0,.5,1]:
        for faiz in ['sabit','tepkili']:
            o={k:K.calistir(cek,t,{'mod':'a','faiz':faiz,'kilitli':k,'w':w}) for k in [True,False]}
            s=o[True]['satir'];out.append((tag,w,faiz,K.k1(o[True]),K.k2(o[True],o[False]),round(s[-1]['kapsama'],4),round(s[-1]['pi_y'],2)))
    return out
a=run('PR (K2 açık)')
orig=K._kilitli_buyume_yillik;orig_lim=K.State if hasattr(K,'State') else None
K._kilitli_buyume_yillik=lambda k,tufe,st: K._mevcut_buyume_yillik(k) if k in ('H_kart','H_teminatsiz') else orig(k,tufe,st)
import cipali_uc_kural.kosu as KK
src_stok=KK._stok_adim
def stok2(st,y,kil,params):
    st.limit_dondur=False;return src_stok(st,y,kil,params)
KK._stok_adim=stok2
b=run('K2 kapalı (tüketici kredisi mevcut büyümede, dondurma yok)')
for r in a+b: print(r)
