import json,pandas as pd,numpy as np,statsmodels.api as sm
H='ham/'
def ev(c):
    d=json.load(open(H+c+'.json'))['items'];k=c.replace('.','_')
    s=pd.Series({i['Tarih']:float(i[k]) for i in d if i[k]});s.index=pd.PeriodIndex(s.index,freq='M');return s
b24,b12,usd,cpi=ev('TP.PKAUO.S01.F.U'),ev('TP.PKAUO.S01.E.U'),ev('TP.DK.USD.A.YTL'),ev('TP.FG.J0')
tr=pd.DataFrame({'b24':b24,'b12':b12,'usd':usd,'pi':(cpi/cpi.shift(12)-1)*100})
tr['dk']=np.log(tr.usd/tr.usd.shift(3))*100; tr['H']=5.0
def bcb(f):
    s=pd.DataFrame(json.load(open(H+f)));s.index=pd.to_datetime(s.data,dayfirst=True).dt.to_period('M');return s.valor.astype(float)
v=pd.DataFrame(json.load(open(H+'br_focus12.json'))['value']);v.index=pd.to_datetime(v.Data).dt.to_period('M')
br=pd.DataFrame({'b12':v.groupby(level=0).Mediana.mean(),'usd':bcb('brl.json'),'pi':bcb('ipca12.json')})
br['dk']=np.log(br.usd/br.usd.shift(3))*100
Hb={**{y:4.5 for y in range(2005,2019)},2019:4.25,2020:4.0,2021:3.75,2022:3.5,2023:3.25}
br['H']=[Hb.get(p.year,3.0 if p.year>=2024 else np.nan) for p in br.index]
def fit(d,bcol,const):
    d=d.dropna(subset=[bcol,'pi','dk','H']);y=d[bcol]-d.pi;X=pd.DataFrame({'w':d.H-d.pi,'lam':d.dk})
    if const: X=sm.add_constant(X)
    r=sm.OLS(y,X).fit(cov_type='HAC',cov_kwds={'maxlags':6});ci=r.conf_int()
    return {**{f'{k}':r.params[k] for k in ['w','lam']},**{f'{k}_lo':ci.loc[k,0] for k in ['w','lam']},**{f'{k}_hi':ci.loc[k,1] for k in ['w','lam']},'n':len(d)}
def roll(d,bcol,const,W=36):
    d=d.dropna(subset=[bcol,'pi','dk','H']);out={}
    for i in range(W,len(d)+1): out[d.index[i-1]]=fit(d.iloc[i-W:i],bcol,const)
    return pd.DataFrame(out).T
def per(d,bcol,const,pers):
    return pd.DataFrame({f'{a}..{b}':fit(d.loc[a:b],bcol,const) for a,b in pers}).T
res={}
TP=[('2013-01','2015-12'),('2013-01','2016-10'),('2017-01','2019-12'),('2020-01','2023-06'),('2023-07','2026-09'),('2017-01','2026-09')]
BP=[('2005-01','2010-12'),('2011-01','2015-12'),('2016-01','2019-12'),('2020-01','2023-06'),('2023-07','2026-09')]
with open('donem_tablo.txt','w') as f:
  for nm,d,bc,P in [('TR b24',tr,'b24',TP),('TR b12',tr,'b12',TP),('BR b12',br,'b12',BP)]:
    for c in [1,0]:
        t=per(d,bc,c,P).round(3); f.write(f'\n## {nm} sabit={c}\n{t.to_string()}\n')
        r=roll(d,bc,c); r.to_csv(f'kayan_{nm.replace(" ","_")}_c{c}.csv'); res[(nm,c)]=r
# pass-through: b on dk only
for nm,d,bc in [('TR b24',tr,'b24'),('TR b12',tr,'b12'),('BR b12',br,'b12')]:
    dd=d.dropna(subset=[bc,'dk']); g=(dd[bc]-dd[bc].shift(1)).dropna()
    rows={}
    for i in range(36,len(g)+1):
        s=g.iloc[i-36:i]; x=dd.dk.loc[s.index]; r=sm.OLS(s,sm.add_constant(x)).fit(cov_type='HAC',cov_kwds={'maxlags':6}); rows[s.index[-1]]=[r.params.iloc[1],*r.conf_int().iloc[1]]
    pd.DataFrame(rows,index=['gecis','lo','hi']).T.to_csv(f'gecis_{nm.replace(" ","_")}.csv')
import ruptures as rpt
with open('kirilma.txt','w') as f:
  for (nm,c),r in res.items():
    for k in ['w','lam']:
        x=r[k].astype(float).values; a=rpt.Binseg(model='l2',min_size=12).fit(x)
        sig=np.var(x); bk=a.predict(pen=np.log(len(x))*sig*2)
        f.write(f'{nm} c{c} {k}: {[str(r.index[i-1]) for i in bk[:-1]]}\n')
tr.to_csv('tr_aylik.csv');br.to_csv('br_aylik.csv')
# sup-Chow on full equation (sabitli), %15 trimming
with open('kirilma.txt','a') as f:
  for nm,d,bc in [('TR b24',tr,'b24'),('TR b12',tr,'b12'),('BR b12',br,'b12')]:
    d=d.dropna(subset=[bc,'pi','dk','H']);y=(d[bc]-d.pi).values;X=sm.add_constant(np.c_[d.H-d.pi,d.dk]);n=len(y);k=3
    s0=sm.OLS(y,X).fit().ssr;best=(0,None)
    for t in range(int(.15*n),int(.85*n)):
        s=sm.OLS(y[:t],X[:t]).fit().ssr+sm.OLS(y[t:],X[t:]).fit().ssr;F=((s0-s)/k)/(s/(n-2*k))
        if F>best[0]: best=(F,str(d.index[t]))
    f.write(f'supChow {nm}: F={best[0]:.1f} tarih={best[1]} (Andrews %5 kritik ~ 15-16, k=3)\n')
