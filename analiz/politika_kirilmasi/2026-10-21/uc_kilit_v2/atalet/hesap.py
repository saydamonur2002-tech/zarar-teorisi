import json,numpy as np,pandas as pd,statsmodels.api as sm
from scipy.optimize import nnls
O=open('cikti.txt','w');p=lambda *a:print(*a,file=O)
def ev(c):
    d=json.load(open(f'ham/{c}.json'))['items'];k=c.replace('.','_');s=pd.Series({i['Tarih']:float(i[k]) for i in d if i.get(k)});s.index=pd.PeriodIndex(s.index,freq='M');return s
AD={'01':'TÜFE','03':'B','04':'C','05':'D','07':'Enerji','08':'Gıda','09':'İşlenmemiş gıda','12':'İşlenmiş gıda','16':'Temel mal','20':'Alkol-tütün-altın','21':'Hizmet','22':'Kira','23':'Lokanta-otel','24':'Ulaştırma hiz.','25':'Haberleşme','26':'Diğer hizmet','28':'F (yönetilen hariç)'}
P=pd.DataFrame({AD[k]:100*np.log(ev('TP.FE.OKTG'+k)).diff() for k in AD})
usd=ev('TP.DK.USD.A.YTL');g1=100*np.log(usd).diff();e12=ev('TP.PKAUO.S01.E.U');e24=ev('TP.PKAUO.S01.F.U')
W=slice('2024-01','2025-12')
def fit(y,X):
    d=pd.concat([y.rename('y'),X],axis=1).loc[W].dropna();r=sm.OLS(d.y,sm.add_constant(d.drop(columns='y'))).fit(cov_type='HAC',cov_kwds={'maxlags':4});return r,len(d)
def ci(r,k): return f"{r.params[k]:.3f} [{r.conf_int().loc[k,0]:.2f}; {r.conf_int().loc[k,1]:.2f}]"
mo=lambda s:pd.Series(s.index.month,index=s.index)
base=pd.DataFrame({'g1':g1},index=P.index)
for k in range(1,7): base[f'g1_l{k}']=g1.shift(k)
base['oca']=(mo(base)==1)*1.;base['tem']=(mo(base)==7)*1.;base['e12']=e12/12
# weights: partition
part=['Enerji','Gıda','Temel mal','Alkol-tütün-altın','Hizmet']
d=P.loc[W,part+['TÜFE']].dropna();w,res=nnls(d[part].values,d['TÜFE'].values);p('NNLS ağırlık',dict(zip(part,w.round(3))),'toplam',round(w.sum(),3),'artık',round(res,3))
w=w/w.sum();WG=dict(zip(part,w))
rows=[]
for nm in P.columns:
    y=P[nm];X0=pd.DataFrame({'l1':y.shift(1),'g1':g1})
    r0,_=fit(y,pd.DataFrame({'g1':g1}))
    r1,n=fit(y,X0)
    Xf=base.copy();Xf['l1']=y.shift(1);rf,_=fit(y,Xf)
    rows.append(dict(kapsam=nm,n=n,ort=round(y.loc[W].mean(),3),alfa_PR=round(r0.params['const'],3),alfa_PR_GA=ci(r0,'const'),alfa_ar=round(r1.params['const'],3),rho=round(r1.params['l1'],3),rho_GA=ci(r1,'l1'),rho_tam=ci(rf,'l1'),alfa_tam=ci(rf,'const'),lam_top=round(sum(rf.params[c] for c in rf.params.index if c.startswith('g1')),3),oca=ci(rf,'oca'),tem=ci(rf,'tem'),e12=ci(rf,'e12'),agirlik=round(WG.get(nm,np.nan),3)))
T=pd.DataFrame(rows);T.to_csv('kapsam.csv',index=False);p(T.to_string())
g=T.set_index('kapsam')
aG=g.loc['TÜFE','alfa_PR'];rG=g.loc['TÜFE','rho']*g.loc['TÜFE','ort']
for nm in part:
    p(f"KATKI {nm}: α katkı={WG[nm]*g.loc[nm,'alfa_PR']:.3f} (%{100*WG[nm]*g.loc[nm,'alfa_PR']/aG:.0f}); atalet katkı ρ·ort·w={WG[nm]*g.loc[nm,'rho']*g.loc[nm,'ort']:.3f} (%{100*WG[nm]*g.loc[nm,'rho']*g.loc[nm,'ort']/rG:.0f})")
p('Σα katkı',round(sum(WG[n]*g.loc[n,'alfa_PR'] for n in part),3),'TÜFE α',aG,'| Σ atalet',round(sum(WG[n]*g.loc[n,'rho']*g.loc[n,'ort'] for n in part),3),'TÜFE ρ·ort',round(rG,3))
# sebepler
au=pd.read_csv('../../ucret_kopus/asgari_ucret.csv');p('AU kolonlar',list(au.columns))
aum=pd.Series(dtype=float)
br={pd.Period(r.baslangic,freq='M'):r.brut for r in au.itertuples()}
idx=pd.period_range('2018-01','2026-09',freq='M');lvl=pd.Series(np.nan,index=idx)
for k,v in br.items():
    if k in lvl.index: lvl[k]=v
lvl=lvl.ffill();dau=100*np.log(lvl).diff().reindex(P.index).fillna(0)
tufe12=(P['TÜFE'].rolling(12).sum()/12)
tavan=pd.Series(((P.index>=pd.Period('2024-01','M'))&(P.index<=pd.Period('2024-06','M')))*1.,index=P.index)
def seq(nm):
    y=P[nm];X=pd.DataFrame({'l1':y.shift(1),'l12':y.shift(12),'g1':g1});out=[]
    steps=[('S0 taban (ρ1, ρ12, λ0)',{}),('S1 +AÜ artışı, 12ay TÜFE ort, tavan kuklası',{'dau':dau,'tufe12':tufe12,'tavan':tavan}),
           ('S2 +enerji ve alkol-tütün-altın aylık',{'enj':P['Enerji'],'ata':P['Alkol-tütün-altın']}),('S3 +e12/12, e24/12',{'e12':e12/12,'e24':e24/12}),
           ('S5 +Ocak, Temmuz kukla',{'oca':base.oca,'tem':base.tem})]
    for s,add in steps:
        if nm in ('Enerji','Alkol-tütün-altın') and 'enj' in add: add={}
        for k,v in add.items(): X[k]=v
        r,n=fit(y,X);row=dict(kapsam=nm,adim=s,n=n,alfa=ci(r,'const'),rho1=ci(r,'l1'),rho12=ci(r,'l12'),rho_top=round(r.params['l1']+r.params['l12'],3))
        for k in ['dau','tufe12','tavan','e12','e24','enj','ata','oca']:
            if k in r.params: row[k]=ci(r,k)
        out.append(row)
    return out
S=pd.DataFrame(sum([seq(n) for n in ['TÜFE','Hizmet','Kira','Gıda','Temel mal']],[]));S.to_csv('sebep.csv',index=False)
pd.set_option('display.width',400);pd.set_option('display.max_colwidth',30);p(S.to_string())
# Brezilya
B={}
for s,nm in [(10844,'serviços'),(11428,'livres'),(4449,'monitorados'),(433,'IPCA')]:
    b=pd.DataFrame(json.load(open(f'ham/br_{s}.json')));b.index=pd.to_datetime(b.data,dayfirst=True).dt.to_period('M');B[nm]=b.valor.astype(float)
B=pd.DataFrame(B)
for nm in B:
    y=B[nm];d=pd.DataFrame({'y':y,'l1':y.shift(1),'l12':y.shift(12)}).loc['2024-01':'2025-12'].dropna()
    r=sm.OLS(d.y,sm.add_constant(d[['l1','l12']])).fit(cov_type='HAC',cov_kwds={'maxlags':4})
    d2=d.assign(oca=(d.index.month==1)*1.);r2=sm.OLS(d2.y,sm.add_constant(d2[['l1','oca']])).fit(cov_type='HAC',cov_kwds={'maxlags':4})
    p(f'BR {nm}: n={len(d)} ort={d.y.mean():.3f} α={ci(r,"const")} ρ1={ci(r,"l1")} ρ12={ci(r,"l12")} | Ocak={ci(r2,"oca")}')
for nm in ['TÜFE','Hizmet','Kira','Gıda','Temel mal','F (yönetilen hariç)']:
    y=P[nm];d=pd.DataFrame({'y':y,'l1':y.shift(1),'l12':y.shift(12)}).loc[W].dropna();r=sm.OLS(d.y,sm.add_constant(d[['l1','l12']])).fit(cov_type='HAC',cov_kwds={'maxlags':4})
    p(f'TR {nm}: α={ci(r,"const")} ρ1={ci(r,"l1")} ρ12={ci(r,"l12")}')
