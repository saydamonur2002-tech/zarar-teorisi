import os
import pandas as pd, numpy as np, statsmodels.api as sm
_BURASI = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.normpath(os.path.join(_BURASI, "..", "..", "..", ".."))
# Eski kutu kökü bu deponun iki üstüydü; bu depo orada ucret_fiyat/repo idi.
_KUTU = os.path.normpath(os.path.join(_REPO, "..", ".."))
f=pd.read_csv(os.path.join(_REPO, "faiz_kur_ham.csv")); f.index=pd.PeriodIndex(f.donem,freq='M')
us=pd.read_csv(os.path.join(_KUTU, "tfv_marj", "ham", "fred_cpiaucsl.csv")); us.index=pd.PeriodIndex(us.observation_date,freq='M'); f['us']=us.CPIAUCSL
b=pd.read_csv(os.path.join(_REPO, "etki_cephesi", "git-harm", "data", "evds_odeme_dengesi_aylik.csv")); b.index=pd.PeriodIndex(b.Donem,freq='M')
f=f.join(b.drop(columns='Donem'))
g=pd.read_csv(os.path.join(_BURASI, "..", "cipa_kur_hep", "gecis_TR_b24.csv"), index_col=0); g.index=pd.PeriodIndex(g.index,freq='M'); f['gam']=g.gecis
# tufe: missing tail -> keep NaN
q=f.drop(columns='donem').groupby(f.index.asfreq('Q')).mean(numeric_only=True)
cnt=f.groupby(f.index.asfreq('Q')).size(); q=q[cnt==3]
d=pd.DataFrame(index=q.index)
d['g']=100*np.log(q.usd).diff()
d['aofm_l']=q.aofm.shift(1)
d['D1']=100*(np.log(q.tufe).diff()-np.log(q.us).diff())
d['D1_l']=d.D1.shift(1)
d['D2']=100*(q.X_mal_ihracati-q.M_mal_ithalati+q.YG_yatirim_geliri_geliri-q.YG_yatirim_geliri_gideri)/q.M_mal_ithalati
d['D2_l']=d.D2.shift(1)
d['D5_l']=q.gam.shift(1)
# t-1 düzeltmesi: günlük seriyi bir iş günü geri kaydır (EVDS t günü = t-1 bülteni)
gd=pd.read_csv(os.path.join(_KUTU, "politika_kirilmasi", "tcmb_gunluk.csv"), index_col=0, parse_dates=True).USDTRY
gs=gd.shift(-1).dropna(); qa=gd.groupby(gd.index.to_period('Q')).mean(); qs=gs.groupby(gs.index.to_period('Q')).mean()
d['g_kay']=100*np.log(qs).diff()
d['g_ham_gunluk']=100*np.log(qa).diff()
d.to_csv('ceyrek.csv')
out=[]
def run(name,y,X,a,bq):
    s=d.loc[a:bq,[y]+X].dropna()
    m=sm.OLS(s[y],sm.add_constant(s[X])).fit()
    r=dict(model=name,pencere=f'{a}-{bq}',n=int(m.nobs),alpha=m.params['const'],alpha_se=m.bse['const'],R2=m.rsquared,R2adj=m.rsquared_adj)
    for x in X: r[x]=m.params[x]; r[x+'_se']=m.bse[x]
    out.append(r); return r
for a,bq in [('2021Q1','2024Q4'),('2018Q1','2024Q4'),('2018Q1','2026Q3'),('2011Q1','2017Q4')]:
    base=run('taban','g',['aofm_l'],a,bq)
    for X,n in [(['aofm_l','D1'],'+D1'),(['aofm_l','D1_l'],'+D1_l'),(['aofm_l','D2_l'],'+D2_l'),(['aofm_l','D5_l'],'+D5_l'),(['aofm_l','D1','D2_l','D5_l'],'+D1+D2_l+D5_l'),(['aofm_l','D1_l','D2_l','D5_l'],'+D1_l+D2_l+D5_l')]:
        run(n,'g',X,a,bq)
# taban aynı örneklem sorunu: kalan pay için taban ile karşılaştır
for a,bq in [('2019Q2','2023Q2')]:
    run('taban_gunluk_ham','g_ham_gunluk',['aofm_l'],a,bq); run('taban_gunluk_kaydirilmis','g_kay',['aofm_l'],a,bq)
o=pd.DataFrame(out); o.to_csv('ayristirma.csv',index=False)
pd.set_option('display.width',250); print(o.round(3).to_string())
# reel kur: D1 ile düzeltilmiş kur değişimi ortalaması
d['reel']=d.g-d.D1
for a,bq in [('2011Q1','2017Q4'),('2018Q1','2020Q4'),('2021Q1','2024Q4'),('2025Q1','2026Q3')]:
    s=d.loc[a:bq]; print(a,bq,'ort g',round(s.g.mean(),2),'ort D1',round(s.D1.mean(),2),'ort reel',round(s.reel.mean(),2),'n',s.reel.notna().sum())
# emsal
P={'BR':('EXBZUS','BRACPIALLMINMEI'),'MX':('EXMXUS','MEXCPIALLMINMEI'),'ZA':('EXSFUS','ZAFCPIALLMINMEI')}
for k,(fx,cp) in P.items():
    a=pd.read_csv('ham/'+fx+'.csv'); a.index=pd.PeriodIndex(a.iloc[:,0],freq='M')
    c=pd.read_csv('ham/'+cp+'.csv'); c.index=pd.PeriodIndex(c.iloc[:,0],freq='M')
    m=pd.DataFrame({'fx':pd.to_numeric(a.iloc[:,1],errors='coerce'),'cp':pd.to_numeric(c.iloc[:,1],errors='coerce'),'us':f.us}).dropna()
    qq=m.groupby(m.index.asfreq('Q')).mean(); qq=qq[m.groupby(m.index.asfreq('Q')).size()==3]
    e=pd.DataFrame({'g':100*np.log(qq.fx).diff(),'D1':100*(np.log(qq.cp).diff()-np.log(qq.us).diff())}).loc['2018Q1':'2024Q2'].dropna()
    r0=sm.OLS(e.g,np.ones(len(e))).fit(); r1=sm.OLS(e.g,sm.add_constant(e.D1)).fit()
    print(k,'n',len(e),'ort g',round(e.g.mean(),2),'alpha|D1',round(r1.params['const'],2),'se',round(r1.bse['const'],2),'dD1',round(r1.params['D1'],2),'se',round(r1.bse['D1'],2),'R2',round(r1.rsquared,3))
