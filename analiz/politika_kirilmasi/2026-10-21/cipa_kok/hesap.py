import json,numpy as np,pandas as pd,statsmodels.api as sm
from statsmodels.tsa.filters.hp_filter import hpfilter
O=open("cikti.txt","w")
def P(*a): print(*a);print(*a,file=O)
def ev(c):
    d=json.load(open(f"ham/{c}.json"));k=c.replace(".","_")
    s=pd.Series({i["Tarih"]:float(i[k]) for i in d["items"] if i.get(k) not in (None,"")});s.index=pd.PeriodIndex(s.index,freq="M");return s
cpi=ev("TP.FG.J0");pi=(cpi/cpi.shift(12)-1)*100
b12=ev("TP.PKAUO.S01.E.U");b24=ev("TP.PKAUO.S01.F.U")
on=ev("TP.PY.P02.ON");fon=ev("TP.APIFON4");i=on.copy();i.loc[fon.index]=fon
ip=np.log(ev("TP.SANAYREV4.Y1"));ipsa=ip-ip.groupby(ip.index.month).transform("mean")  # kaba mevsim
cyc,_=hpfilter(ipsa.dropna(),lamb=129600);gap=cyc*100
fx=np.log(ev("TP.DK.USD.A.YTL"));dfx=(fx-fx.shift(12))*100
# K1
H={2006:5,2007:4,2008:4,2009:7.5,2010:6.5,2011:5.5,2012:5,2013:5,2014:5,2015:5,2016:5,2017:5,2018:5}
G={2006:9.7,2007:8.4,2008:10.1,2009:6.5,2010:6.4,2011:10.4,2012:6.2,2013:7.4,2014:8.2,2015:8.8,2016:8.5,2017:11.92,2018:20.30}
rows=[];n=0;C=0
for y in H:
    s=G[y]-H[y];n=n+1 if s>0 else 0;C+=s
    gy=(b24[str(y)].mean()-5) if str(y)>="2013" else np.nan
    rows.append((y,H[y],G[y],round(s,2),n,round(C,2),abs(s)>2,round(gy,2) if gy==gy else ""))
K1=pd.DataFrame(rows,columns=["yıl","hedef","gerç","sapma","ardışık_aşım","kümülatif","bant_dışı","g_b24"]);P(K1.to_string(index=False));K1.to_csv("k1.csv",index=False)
k=K1.dropna(subset=["g_b24"]);k=k[k.g_b24!=""];gg=k.g_b24.astype(float).values;Cl=K1.set_index("yıl").kümülatif.shift(1).loc[k.yıl].values
P("corr(g_t, C_{t-1}) 2013–18:",round(np.corrcoef(gg,Cl)[0,1],2),"; 2013–17:",round(np.corrcoef(gg[:-1],Cl[:-1])[0,1],2))
P("C eğimi 2012–2016:",round(np.polyfit(range(5),K1.set_index('yıl').kümülatif.loc[2012:2016].values,1)[0],2))
# öğrenme kazancı (2014+): Δ12 b12 = g·(pi_t - b12_{t-12})
D=pd.concat([b12.rename("b12"),pi.rename("pi")],axis=1);D["db"]=D.b12-D.b12.shift(12);D["sur"]=D.pi-D.b12.shift(12);D=D.dropna()
for a,b in [("2014-01","2016-10"),("2016-11","2018-12"),("2014-01","2018-12")]:
    x=D.loc[a:b];m=sm.OLS(x.db,sm.add_constant(x.sur)).fit(cov_type="HAC",cov_kwds={"maxlags":12});P("kazanç g",a,b,round(m.params.sur,2),"t",round(m.tvalues.sur,2),"n",len(x))
# K2 Taylor kayan 48 ay (π = gerçekleşen yıllık TÜFE [VEKİL, beklenti 2013 öncesi yok])
T=pd.concat([i.rename("i"),pi.rename("pi"),gap.rename("gap"),dfx.rename("dfx")],axis=1).dropna().loc["2006-01":"2019-12"]
ph={}
for e in T.index[47:]:
    x=T.loc[e-47:e];m=sm.OLS(x.i,sm.add_constant(x[["pi","gap","dfx"]])).fit();ph[e]=(m.params.pi,m.bse.pi)
ph=pd.DataFrame(ph,index=["phi","se"]).T
P("φπ pencere sonu (yıllık seçmeler):",ph.phi[ph.index.month==12].round(2).to_dict())
lt1=ph[ph.phi<1];P("φπ<1 olan pencere oranı: 2009-12..2012-12",round((ph.loc['2009-12':'2012-12'].phi<1).mean(),2),"; 2013-01..2016-10",round((ph.loc['2013-01':'2016-10'].phi<1).mean(),2),"; 2016-11..2019-12",round((ph.loc['2016-11':'2019-12'].phi<1).mean(),2))
P("φπ ilk <1 pencere:",lt1.index[0] if len(lt1) else None, "; 12 ay kesintisiz <1 ilk başlangıç:",next((str(t) for t in ph.index if (ph.loc[t:t+11].phi<1).all() and len(ph.loc[t:t+11])==12),None))
ph.to_csv("k2_phi.csv")
# 2011+ çoklu araç alt dönem ve 2016Q4 kalıntı
def fit(a,b,ex=[]):
    x=T.loc[a:b].join(EX[ex]) if ex else T.loc[a:b]
    x=x.dropna();return sm.OLS(x.i,sm.add_constant(x[["pi","gap","dfx"]+ex])).fit(cov_type="HAC",cov_kwds={"maxlags":6}),x
EX=pd.DataFrame(index=T.index)
X4=pd.read_csv("../cipa_sebep/aylik.csv",index_col=0).X4;X4.index=pd.PeriodIndex(X4.index,freq="M");EX["X4"]=X4
sec=["2011-06","2014-03","2014-08","2015-06","2015-11","2017-04","2018-06"];EX["secim"]=0
for s in sec:
    p=pd.Period(s,"M");EX.loc[p-5:p,"secim"]=1
for a,b in [("2006-01","2010-12"),("2011-01","2016-10"),("2011-01","2018-12")]:
    m,_=fit(a,b);P("Taylor",a,b,{k:(round(v,2),round(m.tvalues[k],2)) for k,v in m.params.items()})
m,x=fit("2011-01","2016-10");pr=m.predict(sm.add_constant(T.loc["2016-09":"2017-03",["pi","gap","dfx"]]))
P("2011–16/10 kuralına göre i tahmini vs gerçek:",{str(k):(round(pr[k],2),T.i[k]) for k in pr.index})
# K3
for a,b in [("2011-01","2016-10"),("2011-01","2018-12")]:
    m,x=fit(a,b,["X4","secim"]);P("K3",a,b,"X4",round(m.params.X4,3),"t",round(m.tvalues.X4,2),"secim",round(m.params.secim,2),"t",round(m.tvalues.secim,2),"n",len(x))
# K4
P("b24 2016-10:",b24.get(pd.Period("2016-10","M")),"b24 2018-01:",b24.get(pd.Period("2018-01","M")),"b12 2016-10:",b12.get(pd.Period("2016-10","M")))
# Emsal Brezilya
f=pd.DataFrame(json.load(open("ham/br_focus12c.json"))["value"]+json.load(open("ham/br_focus12.json"))["value"]);f["M"]=pd.to_datetime(f.Data).dt.to_period("M");fb=f.groupby("M").Mediana.mean()
ip_=pd.DataFrame(json.load(open("ham/br_ipca12.json")));ip_["M"]=pd.to_datetime(ip_.data,dayfirst=True).dt.to_period("M");ipb=ip_.set_index("M").valor.astype(float)
rows=[];n=0;C=0
for y in range(2006,2019):
    s=ipb[pd.Period(f"{y}-12","M")]-4.5;n=n+1 if s>0 else 0;C+=s;rows.append((y,round(ipb[pd.Period(f"{y}-12","M")],2),round(s,2),n,round(C,2),round(fb[str(y)].mean()-4.5,2)))
BR=pd.DataFrame(rows,columns=["yıl","IPCA_Ara","sapma(4,5)","ardışık","kümülatif","g_focus12"]);P("Brezilya:\n",BR.to_string(index=False))
P("BR corr(g_t,C_{t-1}) 2007–18:",round(np.corrcoef(BR.g_focus12[1:],BR.kümülatif.shift(1)[1:])[0,1],2))
tr12=pd.Series({y:b12[str(y)].mean()-5 for y in range(2013,2019)});P("TR g_b12:",tr12.round(2).to_dict())
