import json,numpy as np,pandas as pd,statsmodels.api as sm,ruptures as rpt
O=open('cikti_v2.txt','w');p=lambda *a:print(*a,file=O)
v1=pd.read_csv('aylik.csv',index_col=0);v1.index=pd.PeriodIndex(v1.index,freq='M')
b=pd.read_csv('ham/bddk_tablo4.csv',index_col=0);b.index=pd.PeriodIndex(b.index,freq='M')
d=json.load(open('ham/TP.TUKFIY2025.GENEL.json'))['items'];P=pd.Series({i['Tarih']:float(i['TP_TUKFIY2025_GENEL']) for i in d if i.get('TP_TUKFIY2025_GENEL')});P.index=pd.PeriodIndex(P.index,freq='M')
df=v1[['net','yasam_vekil','karsilama','acik_kisi']].copy()
df['stok_mnTL']=b.r12.reindex(df.index);df['akim_mnTL']=b.r12.diff().reindex(df.index)
df['akim_reel']=df.akim_mnTL*P['2026-09']/P.reindex(df.index)
df['Nstar']=df.akim_mnTL*1e6/df.acik_kisi
df['akim_stok']=df.akim_mnTL/b.r12.shift(1).reindex(df.index)*100
df.to_csv('aylik_v2.csv')
per={'2016–17':('2016-01','2017-12'),'2018–20':('2018-01','2020-12'),'2021–23':('2021-01','2023-12'),'2024–26':('2024-01','2026-08')}
T=pd.DataFrame([dict(donem=k,karsilama=round(100*x.karsilama.mean(),1),acik_kisi=round(x.acik_kisi.mean()),net_akim_mlyTL=round(x.akim_mnTL.mean()/1e3,1),akim_stok_yuzde=round(x.akim_stok.mean(),2),Nstar_mn=round(x.Nstar.mean()/1e6,2),Nstar_medyan=round(x.Nstar.median()/1e6,2)) for k,(a,c) in per.items() for x in [df.loc[a:c]]])
T.to_csv('donem_v2.csv',index=False);p(T.to_string())
x=df.dropna(subset=['akim_reel']).copy();x['dk']=x.karsilama.diff()*100;m=x.index.month
for L in range(0,13):
    dd=pd.DataFrame({'y':x.akim_stok,'x':x.dk.shift(L),'oca':(m==1)*1.,'mar':(m==3)*1.},index=x.index).dropna()
    r0=sm.OLS(dd.y,sm.add_constant(dd.x)).fit(cov_type='HAC',cov_kwds={'maxlags':6})
    r1=sm.OLS(dd.y,sm.add_constant(dd[['x','oca','mar']])).fit(cov_type='HAC',cov_kwds={'maxlags':6})
    p(f'gecikme {L:2d}: n={len(dd)} corr={dd[["y","x"]].corr().iloc[0,1]:+.2f} t={r0.tvalues.x:+.2f} | takvim kontrollü b={r1.params.x:+.3f} t={r1.tvalues.x:+.2f}')
# düzey ilişkisi: karşılama düzeyi vs akım/stok
r=sm.OLS(x.akim_stok,sm.add_constant(x.karsilama*100)).fit(cov_type='HAC',cov_kwds={'maxlags':6});p('düzey: akım/stok ~ karşılama',round(r.params.iloc[1],4),'t',round(r.tvalues.iloc[1],2))
for col in ['akim_stok','Nstar']:
    s=x[col].rolling(3).mean().dropna();bk=rpt.Binseg(model='l2',min_size=6).fit(s.values).predict(pen=np.log(len(s))*s.var()*2)
    p('Binseg',col,[(str(s.index[i-1]),round(100*x.karsilama.rolling(3).mean().loc[s.index[i-1]],1)) for i in bk[:-1]])
# κ tahmini: reel akım ~ reel kişi başı açık (oran)
r=sm.OLS(x.akim_stok,sm.add_constant(x.acik_kisi/x.yasam_vekil*100)).fit(cov_type='HAC',cov_kwds={'maxlags':6});p('akım/stok ~ açık payı(%):',round(r.params.iloc[1],4),'t',round(r.tvalues.iloc[1],2))
