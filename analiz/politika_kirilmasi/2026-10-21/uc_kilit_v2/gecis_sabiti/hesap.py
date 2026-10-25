import json,glob,numpy as np,pandas as pd,statsmodels.api as sm
from scipy.optimize import nnls
O=open('cikti.txt','w');p=lambda *a:print(*a,file=O)
def nw(y,X,names):
    r=sm.OLS(y,X).fit(cov_type='HAC',cov_kwds={'maxlags':4,'kernel':'bartlett'});ci=r.conf_int()
    return r,{n:(round(r.params.iloc[i],3),round(ci.iloc[i,0],3),round(ci.iloc[i,1],3)) for i,n in enumerate(names)}
pr=pd.DataFrame(json.load(open('pr_panel_2024.json')));pr.index=pd.PeriodIndex(pr.ay,freq='M')
r,c=nw(pr.pi1,sm.add_constant(pr.g1),['a','lam']);p('1) PR yeniden',c,'n',len(pr))
# usd full history for lags from PR ham
ham=json.load(open('../pr44_kopya/cipali_uc_kural/ham/aylik.json'))['seriler']
def ser(k):
    s=pd.Series({x['ay']:x['deger'] for x in ham[k]['satir'] if x['deger'] is not None});s.index=pd.PeriodIndex(s.index,freq='M');return s.sort_index()
p('PR seriler',list(ham))
def ev(c):
    d=json.load(open(f'ham/{c}.json'))['items'];k=c.replace('.','_');s=pd.Series({i['Tarih']:float(i[k]) for i in d if i.get(k)});s.index=pd.PeriodIndex(s.index,freq='M');return s
usd=ser([k for k in ham if 'usd' in k.lower()][0])
g1=100*np.log(usd/usd.shift(1))
G={c.split('/')[-1][:-5]:ev(c.split('/')[-1][:-5]) for c in glob.glob('ham/TP.TUKFIY2025.*.json')}
pi=pd.DataFrame({k.replace('TP.TUKFIY2025.',''):100*np.log(v/v.shift(1)) for k,v in G.items()})
W=slice('2024-01','2026-09')
d=pi.loc[W].join(g1.rename('g1'))
r,c=nw(d.GENEL,sm.add_constant(d.g1),['a','lam']);p('GENEL 2025 baz aynı pencere',c)
grp=[f'{i:02d}' for i in range(1,14)]
w,res=nnls(d[grp].values,d.GENEL.values);p('NNLS ağırlık toplam',round(w.sum(),3),'artık',round(res,3))
w=w/w.sum()
rows=[]
for j,gj in enumerate(grp+['041','0411','045','0451','072']):
    rr,cc=nw(d[gj],sm.add_constant(d.g1),['a','lam'])
    wj=w[j] if gj in grp else np.nan
    rows.append(dict(kalem=gj,a=cc['a'][0],a_lo=cc['a'][1],a_hi=cc['a'][2],lam=cc['lam'][0],agirlik_vekil=round(wj,3) if wj==wj else None,katki=round(wj*cc['a'][0],3) if wj==wj else None))
T=pd.DataFrame(rows);T.to_csv('ayristirma.csv',index=False);p(T.to_string())
p('Σkatkı',round(T.katki.sum(),3),'GENEL a',c['a'][0],'kapsama',round(T.katki.sum()/c['a'][0],3))
# model hatası: PR panel genel pi1
e=ser('e24') if 'e24' in ham else None
D=pd.DataFrame({'pi1':pr.pi1,'g1':g1}).join(pd.DataFrame({f'g1_l{k}':g1.shift(k) for k in range(1,7)}))
pg=pd.concat([pi['GENEL'].loc[:'2023-12'],pr.pi1]) ; D['pi1_l1']=pg.shift(1).reindex(D.index)
D['de']=(e-e.shift(1)).reindex(D.index);D['e12']=(e/12).reindex(D.index)
m=D.index.month;D['oca']=(m==1)*1.0;D['tem']=(m==7)*1.0
L=['g1']+[f'g1_l{k}' for k in range(1,7)]
specs={'M0':['g1'],'M1 +kur gecikme 1-6':L,'M2 +atalet':L+['pi1_l1'],'M3 +beklenti':L+['pi1_l1','de','e12'],'M4 +Ocak/Temmuz':L+['pi1_l1','de','e12','oca','tem']}
mh=[]
for nm,x in specs.items():
    dd=D[['pi1']+x].dropna();rr,cc=nw(dd.pi1,sm.add_constant(dd[x]),['a']+x)
    row=dict(model=nm,n=len(dd),a=cc['a'][0],a_lo=cc['a'][1],a_hi=cc['a'][2],lam_top=round(sum(rr.params[k] for k in L if k in x),3))
    if 'pi1_l1' in x: row['rho']=cc['pi1_l1'];row['uzun_a']=round(cc['a'][0]/(1-rr.params['pi1_l1']),3)
    for k in ['e12','oca','tem']:
        if k in x: row[k]=cc[k]
    mh.append(row)
# M5 mevsim: ay kuklaları, α = ay sabitlerinin ortalaması (g1 + gecikme + atalet)
dd=D[['pi1']+L+['pi1_l1']].dropna();Md=pd.get_dummies(dd.index.month,prefix='ay').astype(float);Md.index=dd.index
rr=sm.OLS(dd.pi1,pd.concat([Md,dd[L+['pi1_l1']]],axis=1)).fit(cov_type='HAC',cov_kwds={'maxlags':4})
a=rr.params[Md.columns].mean();V=rr.cov_params().loc[Md.columns,Md.columns].values.sum()/len(Md.columns)**2
mh.append(dict(model='M5 +12 ay kuklası (atalet+kur gecikme)',n=len(dd),a=round(a,3),a_lo=round(a-1.96*V**.5,3),a_hi=round(a+1.96*V**.5,3),rho=round(rr.params['pi1_l1'],3)))
MH=pd.DataFrame(mh);MH.to_csv('model_hatasi.csv',index=False);p(MH.to_string())
# 4) hizmet/kira ataleti: 041 kira, 0411; ücret ayları
for gj in ['041','0411','04','11','01','045']:
    y=pi[gj].loc[W];X=pd.DataFrame({'l1':pi[gj].shift(1).loc[W],'oca':(y.index.month==1)*1.0,'tem':(y.index.month==7)*1.0},index=y.index)
    rr,cc=nw(y,sm.add_constant(X),['a','l1','oca','tem']);p('A4',gj,cc)
# 5) Brezilya
b=pd.DataFrame(json.load(open('ham/br_ipca_m.json')));b.index=pd.to_datetime(b.data,dayfirst=True).dt.to_period('M');bp=b.valor.astype(float)
brl=pd.DataFrame(json.load(open('../../cipa_kur_hep/ham/brl.json')));brl.index=pd.to_datetime(brl.data,dayfirst=True).dt.to_period('M');bu=brl.valor.astype(float)
dd=pd.DataFrame({'pi1':100*np.log(1+bp/100),'g1':100*np.log(bu/bu.shift(1))}).loc['2024-01':].dropna()
r,c=nw(dd.pi1,sm.add_constant(dd.g1),['a','lam']);p('BR 2024+',c,'n',len(dd),'ort pi1',round(dd.pi1.mean(),3))
p('TR ort pi1 2024+',round(pr.pi1.mean(),3),'ort g1',round(pr.g1.mean(),3))
