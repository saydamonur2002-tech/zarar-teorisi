import pandas as pd,numpy as np,statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller,kpss
import warnings;warnings.filterwarnings('ignore')
tr=pd.read_csv('../tr_aylik.csv',index_col=0);tr.index=pd.PeriodIndex(tr.index,freq='M')
br=pd.read_csv('../br_aylik.csv',index_col=0);br.index=pd.PeriodIndex(br.index,freq='M')
O=open('cikti.txt','w');p=lambda *a:print(*a,file=O)
def mci(s):
    r=sm.OLS(s.values,np.ones(len(s))).fit(cov_type='HAC',cov_kwds={'maxlags':6});return r.params[0],*r.conf_int()[0]
def a1(s,nm):
    s=s.dropna();m,lo,hi=mci(s);ad=adfuller(s,autolag='AIC')[1];kp=kpss(s,regression='c',nlags='auto')[1]
    p(f'A1 {nm}: n={len(s)} ort={m:.2f} GA[{lo:.2f},{hi:.2f}] std={s.std():.2f} min={s.min():.2f} max={s.max():.2f} ADF p={ad:.3f} KPSS p={kp:.3f}')
def a3(d,b,nm):
    d=d.dropna(subset=[b,'pi']);x=d[b]-d.pi;m,lo,hi=mci(x)
    r=sm.OLS(d[b],sm.add_constant(d.pi)).fit(cov_type='HAC',cov_kwds={'maxlags':6});ci=r.conf_int().loc['pi']
    p(f'A3 {nm}: b-pi ort={m:.2f} GA[{lo:.2f},{hi:.2f}] eğim={r.params.pi:.3f} GA[{ci[0]:.3f},{ci[1]:.3f}] std(pi)={d.pi.std():.2f}')
def a4(s,up,nm):
    s=s.dropna();m,lo,hi=mci(s);p(f'A4 {nm}: üst band {up}: GA içeriyor={lo<=up<=hi}; pay[{up-.5},{up+.5}]={((s>=up-.5)&(s<=up+.5)).mean():.2f}')
P=slice('2013-01','2016-10')
for b in ['b24','b12']:
    a1(tr.loc[P,b],f'TR {b}');a3(tr.loc[P],b,f'TR {b}');a4(tr.loc[P,b],7,f'TR {b}')
p('pi 2013-01..2016-10 std',round(tr.loc[P,'pi'].std(),2))
for nm,sl in [('2005-01..2010-12',slice('2005-01','2010-12')),('2013-01..2016-10',P)]:
    a1(br.loc[sl,'b12'],f'BR b12 {nm}');a3(br.loc[sl],'b12',f'BR b12 {nm}');a4(br.loc[sl,'b12'],6.5,f'BR b12 {nm}')
    p(f'  BR hedef ort {br.loc[sl,"H"].mean():.2f}, pi std {br.loc[sl,"pi"].std():.2f}')
# A2
e=pd.read_csv('er_tahmin.csv');e['ay']=pd.PeriodIndex(e.ay,freq='M')
rows=[]
for _,r in e.iterrows():
    m=r.ay.month;F12=r.F_cari+(r.F_sonraki-r.F_cari)*m/12
    b12=tr.b12.get(r.ay);b24=tr.b24.get(r.ay);b12p=tr.b12.get(r.ay-1);b12n=tr.b12.get(r.ay+1)
    rows.append(dict(rapor=r.rapor,F12=round(F12,2),F_sonraki=r.F_sonraki,b12=b12,b24=b24,d_F12=abs(b12-F12),d5_12=abs(b12-5),d_F24=abs(b24-r.F_sonraki),d5_24=abs(b24-5),db12=(b12n-b12p) if b12n==b12n else np.nan))
A=pd.DataFrame(rows);A['dF12']=A.F12.diff();A['uyum']=np.sign(A.dF12)==np.sign(A.db12)
A.round(2).to_csv('a2_olay.csv',index=False);p(A.round(2).to_string())
p(f'A2 ort |b12-F12|={A.d_F12.mean():.2f} vs |b12-5|={A.d5_12.mean():.2f}; |b24-Fsonraki|={A.d_F24.mean():.2f} vs |b24-5|={A.d5_24.mean():.2f}')
nz=A.dropna(subset=['dF12','db12']);nz=nz[nz.dF12!=0];p(f'A2 işaret uyumu {nz.uyum.mean():.2f} (n={len(nz)}, revizyonsuz raporlar hariç)')
# kayma
for nm,sl in [('2013-01..2016-10',P),('2016-11..2018-07',slice('2016-11','2018-07')),('2018-08..2021-08',slice('2018-08','2021-08')),('2021-09..2023-06',slice('2021-09','2023-06')),('2023-07..',slice('2023-07',None))]:
    for b in ['b24','b12']:
        m,lo,hi=mci(tr.loc[sl,b].dropna());p(f'KAYMA {nm} {b}: ort={m:.2f} GA[{lo:.2f},{hi:.2f}] std={tr.loc[sl,b].std():.2f} pi_ort={tr.loc[sl,"pi"].mean():.2f}')
import ruptures as rpt
x=tr.b24.dropna();bk=rpt.Binseg(model='l2',min_size=6).fit(x.values).predict(pen=np.log(len(x))*x.var()*0.5)
p('b24 düzey kırılmaları',[str(x.index[i-1]) for i in bk[:-1]])
x.rolling(12).mean().to_csv('b24_12ay_ort.csv')
