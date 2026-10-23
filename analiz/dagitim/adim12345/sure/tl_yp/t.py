import sys,numpy as np,csv;sys.path.insert(0,'../../model');sys.path.insert(0,'../dinamik')
import model as M,model12 as m12
F,E=m12.g('fin_gider_2025'),m12.g('efk_2025');AN=19219.0;KB=6998.3/AN;YP={'G':.485,'K':.184,'B':.657}
OVPpi=[.21,.135,.09];OVPg=[.042,.046,.05];PKApi=[.2333,.1794,.1217]
SC={'dusuk':(OVPpi,[.029]*3),'OVP':(OVPpi,OVPg),'yuksek':(PKApi,OVPg)}
def path(sc,n=40):
  pi,g=SC[sc];return np.array([.2963]+pi+[pi[-1]]*n),np.array([.029]+g+[g[-1]]*n)
def sim(o,kobi,kappa,c,phi,sc,kur,rule):
  pi,g=path(sc);Eg=np.prod((1+pi[:3])*(1+g[:3]));res={}
  for k,s in (('G',1),('K',kobi),('B',1-kobi)):
    I3=o['A3_faiz']*s;D0=kappa*AN*(1-o['A1_stok']/M.S0)*s;Fk=F[k]-(o['A1_faiz']+o['A3_faiz'])*s
    tl=D0*(1-YP[k]);yp=D0*YP[k];Et=E[k]*Eg
    for y in range(3): yp=yp*(1.19 if (kur=='bek' and y==0) else (1+pi[y])/1.025)
    Ttl=np.full(np.shape(D0),np.nan);Typ=Ttl.copy()
    for t in range(40):
      y=3+t
      if t>0: Et=Et*(1+pi[y])*(1+g[y]);yp=yp*(1+pi[y])/1.025
      pay=c*I3+np.maximum(Et-Fk,0)*.75*(1-phi);tot=tl+yp
      if rule=='a': ptl=pay*tl/np.maximum(tot,1e-9);pyp=pay-ptl
      elif rule=='b': pyp=np.minimum(pay,yp);ptl=pay-pyp
      else: ptl=np.minimum(pay,tl);pyp=pay-ptl
      P=np.maximum(pay,1e-9)
      if rule=='a': ftl=fyp=np.clip(tot/P,0,1)
      elif rule=='b': fyp=np.clip(yp/P,0,1);ftl=np.clip(tot/P,0,1)
      else: ftl=np.clip(tl/P,0,1);fyp=np.clip(tot/P,0,1)
      for T,b,p,f in ((Ttl,tl,ptl,ftl),(Typ,yp,pyp,fyp)):
        done=np.isnan(T)&(b<=p+1e-9);T[done]=t+f[done]
      tl=np.maximum(tl-ptl,0);yp=np.maximum(yp-pyp,0)
    res[k]=(Ttl,Typ)
  return res
N=m12.P['mc']['n'];s=M.mc();phi=np.random.default_rng(3).uniform(.3,.7,N)
kap=np.random.default_rng(7).triangular(.25,.5,1,N);kobi=np.clip(np.random.default_rng(5).normal(KB,.03,N),.15,.5)
rows=[];K={}
for sc in SC:
 for kur in ('bek','reel'):
  for c in (1,.5):
   for rule in 'abc':
    r=sim(s,kobi,kap,c,phi,sc,kur,rule);K[(sc,kur,c,rule)]=r
    for k,(a,b) in r.items():
      rows.append([sc,kur,c,rule,k]+[round(float(np.nanpercentile(a,p)),2) for p in (10,50,90)]+[round(float(np.nanpercentile(b,p)),2) for p in (10,50,90)])
w=csv.writer(open('tl_yp.csv','w'));w.writerow(['senaryo','kur','c','kural','grup','TL_P10','TL_P50','TL_P90','YP_P10','YP_P50','YP_P90']);w.writerows(rows)
for x in rows:
  if x[0]=='OVP' and x[1]=='bek': print(x)
import itertools
for k in 'GKB':
  v=[float(np.nanmedian(K[(sc,kur,1,'a')][k][1])) for sc in SC for kur in ('bek','reel')];print('YP P50 aralık c=1 a',k,min(v),max(v))
  v=[float(np.nanmedian(K[(sc,kur,1,'a')][k][0])) for sc in SC for kur in ('bek','reel')];print('TL',k,min(v),max(v))
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
fig,ax=plt.subplots(1,2,figsize=(11,4))
for i,c in enumerate((1,.5)):
  d=[];l=[]
  for rule in 'abc':
    for k in 'KB':
      a,b=K[('OVP','bek',c,rule)][k];d+= [a,b];l+=[f'{rule}-{k}-TL',f'{rule}-{k}-YP']
  ax[i].boxplot(d,showfliers=False);ax[i].set_xticklabels(l,rotation=70,fontsize=7);ax[i].set_title(f'OVP, kur beklentisi, nakdin %{int(c*100)}ü');ax[i].set_ylabel('yıl')
plt.tight_layout();plt.savefig('tl_yp.png',dpi=110)
