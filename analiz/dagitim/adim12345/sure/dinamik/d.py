import sys,numpy as np,csv;sys.path.insert(0,'../../model');import model as M,model12 as m12
F,E=m12.g('fin_gider_2025'),m12.g('efk_2025');AN=19219.0;KB=6998.3/AN;YP={'G':.485,'K':.184,'B':.657}
OVPpi=[.21,.135,.09];OVPg=[.042,.046,.05];PKApi=[.2333,.1794,.1217]
SC={'dusuk':(OVPpi,[.029]*3),'OVP':(OVPpi,OVPg),'yuksek':(PKApi,OVPg)}
def path(sc,n=40):
  pi,g=SC[sc];pi=[.2963]+pi+[pi[-1]]*n;g=[.029]+g+[g[-1]]*n;return np.array(pi),np.array(g)
def sim(o,kobi,kappa,c,phi,sc,kur):
  pi,g=path(sc);Eg=np.prod((1+pi[:3])*(1+g[:3]))  # 2026-28
  res={}
  for k,s in (('G',1),('K',kobi),('B',1-kobi)):
    I3=o['A3_faiz']*s;D0=kappa*AN*(1-o['A1_stok']/M.S0)*s;Fk=F[k]-(o['A1_faiz']+o['A3_faiz'])*s
    tl=D0*(1-YP[k]);yp=D0*YP[k];Et=E[k]*Eg
    # kur 2026-28 de YP'yi büyütür
    for y in range(3): yp=yp*((1.19 if (kur=='bek' and y==0) else (1+pi[y])/1.025))
    D_start=tl+yp;T=np.full(np.shape(D0),np.nan);L=np.full(np.shape(D0),np.nan)
    for t in range(40):
      y=3+t;Et=Et*(1+pi[y])*(1+g[y]) if t>0 else Et
      pay=c*I3+np.maximum(Et-Fk,0)*.75*(1-phi);rem=tl+yp
      fr=np.clip(rem/pay,0,1);done=(rem<=pay)&np.isnan(T);T=np.where(done,t+fr,T)
      if t>0: yp=yp*(1+pi[y])/1.025
      sh=np.minimum(pay,rem);tot=tl+yp;tl=np.maximum(tl-sh*tl/np.maximum(tot,1e-9),0);yp=np.maximum(yp-sh*(yp/np.maximum(tot,1e-9)),0)
      ok=((Fk+I3*(tl+yp)/D_start)/Et<.33)&np.isnan(L);L=np.where(ok,t+1,L)
    res[k]=dict(T=T,L=L)
  return res
rows=[];N=m12.P['mc']['n'];s=M.mc();phi=np.random.default_rng(3).uniform(.3,.7,N)
kap=np.random.default_rng(7).triangular(.25,.5,1,N);kobi=np.clip(np.random.default_rng(5).normal(KB,.03,N),.15,.5)
ST={1:2.40,.5:3.43};keep={}
for sc in SC:
 for kur in ('bek','reel'):
  for c in (1,.5):
   r=sim(s,kobi,kap,c,phi,sc,kur);keep[(sc,kur,c)]=r
   for k in r:
    q=[round(float(np.nanpercentile(r[k]['T'],p)),2) for p in (10,50,90)];l=[round(float(np.nanpercentile(r[k]['L'],p)),1) for p in (10,50,90)]
    rows.append([sc,kur,c,k]+q+[round(ST[c]-q[1],2) if k=='G' else '']+l+[round(float(np.isnan(r[k]['L']).mean()),3)])
w=csv.writer(open('dinamik.csv','w'));w.writerow(['senaryo','kur','c','grup','T_P10','T_P50','T_P90','statige_gore_kisalma_P50','Lmin_P10','Lmin_P50','Lmin_P90','40yilda_33alti_olmayan_pay']);w.writerows(rows)
[print(x) for x in rows]
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
fig,a=plt.subplots(figsize=(8,4));lab=[];dat=[]
for sc in SC:
  for c in (1,.5): dat.append(keep[(sc,'bek',c)]['G']['T']);lab.append(f'{sc}\n%{int(c*100)}')
a.boxplot(dat,showfliers=False);a.set_xticklabels(lab);a.axhline(2.40,ls='--',c='g',label='statik %100');a.axhline(3.43,ls='--',c='r',label='statik %50')
a.set_ylabel('yıl');a.set_title('Anapara bitiş süresi, dinamik (Genel, kur beklentisi)');a.legend();plt.tight_layout();plt.savefig('dinamik.png',dpi=110)
