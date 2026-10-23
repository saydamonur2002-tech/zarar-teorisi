import sys,csv,numpy as np;sys.path.insert(0,'../model');import model as M,model12 as m12
F,E=m12.g('fin_gider_2025'),m12.g('efk_2025');s=M.mc();N=len(s['A1_faiz'])
f=1-s['A1_stok']/M.S0;F1=F['G']-s['A1_faiz'];s['A3_faiz']=np.minimum(.5*f*(9905.7*.5319+9313.3*.0792),F1)
kob=np.clip(np.random.default_rng(5).normal(.3264,.03,N),.15,.5);phi=np.random.default_rng(3).uniform(.3,.7,N)
DAR=.08*7869.8;EKF=DAR*.5319
pi=np.array([.2963,.21,.135,.09]+[.09]*40);g=np.array([.029,.042,.046,.05]+[.05]*40);Eg=np.prod((1+pi[:3])*(1+g[:3]))
PC=lambda x:[round(float(v),2) for v in np.nanpercentile(np.ones(N)*x,[10,50,90])]
def sure(k,sh,c,mode):
  TL0={'G':9905.7,'K':5712.8,'B':4192.9}[k];YP0={'G':9313.3,'K':1285.5,'B':8027.8}[k]
  w=sh if k=='G' else 1
  tl=.5*f*TL0*w if k!='G' else .5*f*TL0;yp=.5*f*YP0 if k!='G' else .5*f*YP0
  sc={'G':1,'K':TL0/9905.7*0+ (TL0+YP0)/19219,'B':(TL0+YP0)/19219}[k]
  I3=s['A3_faiz']*sc;Fk=F[k]-(s['A1_faiz']+s['A3_faiz'])*sc;Et=E[k]*Eg
  for y in range(3): yp=yp*(1.19 if y==0 else (1+pi[y])/1.025)
  ek=EKF*sc if mode!='yok' else 0;kay=DAR*sc if mode=='erisim' else 0
  Tt=np.full(N,np.nan);Ty=Tt.copy()
  for t in range(40):
    if t>0: Et=Et*(1+pi[3+t])*(1+g[3+t]);yp=yp*(1+pi[3+t])/1.025
    pay=np.maximum(c*I3+np.maximum(Et-Fk-ek,0)*.75*(1-phi)-kay,1e-9);tot=tl+yp;fr=np.clip(tot/pay,0,1)
    ptl=pay*tl/np.maximum(tot,1e-9);pyp=pay-ptl
    for T,b,p in ((Tt,tl,ptl),(Ty,yp,pyp)): d=np.isnan(T)&(b<=p+1e-9)&(b>0);T[d]=t+fr[d]
    tl=np.maximum(tl-ptl,0);yp=np.maximum(yp-pyp,0)
  return Tt,Ty
rows=[]
for k in 'GKB':
  sc={'G':1,'K':(5712.8+1285.5)/19219,'B':(4192.9+8027.8)/19219}[k];c=0;rows.append(['oran','önce',k,'']+[round(100*F[k]/E[k],1)]*3)
  for a,v in (('A1',s['A1_faiz']),('A2',0*F1),('A3',s['A3_faiz'])):
    c=c+v;rows.append(['oran',a,k,'']+PC(100*np.maximum(F[k]-c*sc,0)/E[k]))
  rows.append(['oran','A4(eski: etkisiz)',k,'']+PC(100*np.maximum(F[k]-c*sc,0)/E[k]))
  rows.append(['oran','A4(yeni: daralma yeniden finansman)',k,'']+PC(100*np.maximum(F[k]-c*sc+EKF*sc,0)/E[k]))
  for mode in ('yok','refi','erisim'):
    for cc in (1,.5):
      a,b=sure(k,None,cc,mode);rows.append(['sure_TL',mode,k,cc]+PC(a));rows.append(['sure_YP',mode,k,cc]+PC(b))
fx=12560/256.2;yps=82.7*fx/11454;ft,fy=4400.1*(1-yps)*.198,4400.1*yps*.302
for p in (.02,.05): rows.append(['firma_mevduat_kaybi',f'pi{p}','TL/YP/toplam','',round(ft*(p-.433),1),round(fy*(p-.0258),1),round(ft*(p-.433)+fy*(p-.0258),1)])
NP=1014.5;RWA=4771.2/.166;G=85299
A1=PC(s['A1_faiz']);KF=PC(s['kopru_faiz'])
T=[['banka','A1 net faiz kaybı']+A1+[round(A1[1]/NP*100,1),round(A1[1]/RWA*100,2)],
   ['banka','A2 doğrudan yük']+[0,0,0,0,0],
   ['banka','A2 köprü kredi fırsat geliri']+KF+[round(KF[1]/NP*100,1),''],
   ['banka','A3 marj']+[604.7]*3+[59.6,2.1],
   ['banka','A4 kredi daralması faiz geliri']+[round(EKF,1)]*3+[round(EKF/NP*100,1),''],
   ['kamu','A1/A2']+[0]*3+['',''],['kamu','A4 prim π2/π5',157.4,'',393.5,round(157.4/G*100,2),round(393.5/G*100,2)],
   ['mevduat sahibi','A4 net kayıp π2/π5',1697.2,'',1461.1,'',''],
   ['banka','TOPLAM doğrudan (A1+A3) P50',round(A1[1]+604.7,1),'','',round((A1[1]+604.7)/NP*100,1),round((A1[1]+604.7)/RWA*100,2)]]
for t in T: rows.append(['tasiyan']+t)
csv.writer(open('sim4_v2.csv','w')).writerows([['kalem','adim','grup','c','P10','P50','P90']]+rows)
for r in rows: print(r)
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
fig,ax=plt.subplots(1,2,figsize=(12,4.5));gg=[r for r in rows if r[0]=='oran' and r[2]=='G'];v=[r[5] for r in gg];lab=['önce','A1','A2','A3','A4 eski','A4 yeni']
for i in range(len(v)):
  b=v[i-1] if 0<i<4 else (v[3] if i>=4 else 0);ax[0].bar(i,v[i]-b,bottom=b,color='r' if i==0 else ('g' if v[i]<b else 'orange'));ax[0].text(i,v[i]+1,f'{v[i]:.1f}',ha='center')
ax[0].axhline(33,ls='--',c='g');ax[0].set_xticks(range(len(v)),lab);ax[0].set_title('Fin.gider/EFK % P50 (Genel)')
d=[r for r in rows if r[0].startswith('sure') and r[2]=='G' and r[3]==1]
ax[1].bar([f"{r[0][5:]}\n{r[1]}" for r in d],[r[5] for r in d],yerr=[[r[5]-r[4] for r in d],[r[6]-r[5] for r in d]],color=['tab:blue','tab:orange']*3)
ax[1].set_ylabel('yıl');ax[1].set_title('Anapara süresi TL/YP, daralma modu (c=1, P10-P90)');plt.tight_layout();plt.savefig('sim4_v2.png',dpi=110)
