import json,numpy as np,pandas as pd,statsmodels.api as sm
O=open('cikti.txt','w');p=lambda *a:print(*a,file=O)
def ev(c):
    d=json.load(open(f'ham/{c}.json'))['items'];k=c.replace('.','_');s=pd.Series({i['Tarih']:float(i[k]) for i in d if i.get(k)});s.index=pd.PeriodIndex(s.index,freq='M');return s
P=ev('TP.TUKFIY2025.GENEL');P0=P['2026-09']
au=pd.read_csv('../../ucret_kopus/asgari_ucret.csv')
idx=pd.period_range('2016-01','2026-09',freq='M');net=pd.Series(np.nan,index=idx)
for r in au.itertuples():
    for m in pd.period_range(r.baslangic,r.bitis,freq='M'):
        if m in net.index: net[m]=r.net
net.loc['2026-01':]=28075.50
Y=48885*P.reindex(idx)/P0
kar=net/Y;acik=Y-net
df=pd.DataFrame({'net':net,'yasam_vekil':Y.round(0),'karsilama':kar.round(4),'acik_kisi':acik.round(0)})
kk=ev('TP.HPBITABLO6.2')+ev('TP.HPBITABLO6.16')   # bin TL
df['kredi_stok_binTL']=kk.reindex(idx);df['net_akim_binTL']=df.kredi_stok_binTL.diff()
df['net_akim_reel_2026_09']=df.net_akim_binTL*P0/P.reindex(idx)
df['Nstar']=(df.net_akim_binTL*1000/df.acik_kisi).round(0)   # kişi eşdeğeri
df.to_csv('aylik.csv')
per={'2016–17':('2016-01','2017-12'),'2018–20':('2018-01','2020-12'),'2021–23':('2021-01','2023-12'),'2024–26':('2024-01','2026-09')}
rows=[]
for k,(a,b) in per.items():
    x=df.loc[a:b];rows.append(dict(donem=k,karsilama_ort=round(100*x.karsilama.mean(),1),kars_min=round(100*x.karsilama.min(),1),kars_max=round(100*x.karsilama.max(),1),acik_kisi_ort=round(x.acik_kisi.mean()),net_akim_ort_milyarTL=round(x.net_akim_binTL.mean()/1e6,2) if x.net_akim_binTL.notna().any() else None,Nstar_ort_milyon=round(x.Nstar.mean()/1e6,2) if x.Nstar.notna().any() else None,n_kredi_ay=int(x.net_akim_binTL.notna().sum())))
T=pd.DataFrame(rows);T.to_csv('donem.csv',index=False);p(T.to_string())
p(df.loc['2024-06':].to_string())
# korelasyon (yalnız kredi olan aylar)
x=df.dropna(subset=['net_akim_reel_2026_09']);dk=x.karsilama.diff()
for L in range(0,7):
    d=pd.DataFrame({'y':x.net_akim_reel_2026_09,'x':dk.shift(L)}).dropna()
    if len(d)>8:
        r=sm.OLS(d.y,sm.add_constant(d.x)).fit(cov_type='HAC',cov_kwds={'maxlags':3});p(f'gecikme {L}: n={len(d)} corr={d.corr().iloc[0,1]:.2f} t={r.tvalues.x:.2f}')
import ruptures as rpt
s=x.Nstar.dropna();bk=rpt.Binseg(model='l2',min_size=6).fit(s.values).predict(pen=np.log(len(s))*s.var())
p('Binseg N*',[str(s.index[i-1]) for i in bk[:-1]],[round(x.karsilama.loc[s.index[i-1]],3) for i in bk[:-1]])
