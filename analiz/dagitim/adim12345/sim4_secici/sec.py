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
  ek=mode if not isinstance(mode,str) else (EKF*sc if mode!='yok' else 0);kay=DAR*sc if mode=='erisim' else 0
  Tt=np.full(N,np.nan);Ty=Tt.copy()
  for t in range(40):
    if t>0: Et=Et*(1+pi[3+t])*(1+g[3+t]);yp=yp*(1+pi[3+t])/1.025
    pay=np.maximum(c*I3+np.maximum(Et-Fk-ek,0)*.75*(1-phi)-kay,1e-9);tot=tl+yp;fr=np.clip(tot/pay,0,1)
    ptl=pay*tl/np.maximum(tot,1e-9);pyp=pay-ptl
    for T,b,p in ((Tt,tl,ptl),(Ty,yp,pyp)): d=np.isnan(T)&(b<=p+1e-9)&(b>0);T[d]=t+fr[d]
    tl=np.maximum(tl-ptl,0);yp=np.maximum(yp-pyp,0)
  return Tt,Ty

sh={'K':.364,'B':.636}
def ekgrup(q,rs):
  sec=q*DAR;kn=DAR*sh['K'];sk=min(sec,kn);sb=sec-sk
  ek={'K':sk*rs['K']+(kn-sk)*.5319,'B':sb*rs['B']+(DAR*sh['B']-sb)*.5319}
  ek['G']=ek['K']+ek['B'];tes=sk*(.5319-rs['K'])+sb*(.5319-rs['B']);return ek,tes,sk,sb
rows=[];Ssc={'G':1,'K':(5712.8+1285.5)/19219,'B':(4192.9+8027.8)/19219}
RS={'reeskont':{'K':.38,'B':.37},'derin25':{'K':.25,'B':.25}}
for k in 'GKB':
  c3=s['A1_faiz']+s['A3_faiz'];sc=Ssc[k]
  for nm,ekk in (('v2_yok',0),('v2_refi',EKF*sc)):
    rows.append([nm,'',k,'oran']+PC(100*np.maximum(F[k]-c3*sc+ekk,0)/E[k]));rows.append([nm,'',k,'sure_c1']+PC(sure(k,None,1,ekk if ekk else 'yok')[0]))
  for rn,rs in RS.items():
    for q in (.5,.75,1):
      ek,tes,sk,sb=ekgrup(q,rs)
      rows.append([f'secici_{rn}',q,k,'oran']+PC(100*np.maximum(F[k]-c3*sc+ek[k],0)/E[k]))
      rows.append([f'secici_{rn}',q,k,'sure_c1']+PC(sure(k,None,1,ek[k])[0]))
      if k=='G': rows.append([f'secici_{rn}',q,'G','kamu_tesvik_mlr/GSYH%/KOBİ_sec/Büyük_sec',round(tes,1),round(tes/85299*100,3),f'{sk:.1f}/{sb:.1f}'])
import csv;csv.writer(open('secici.csv','w')).writerows([['mod','kota','grup','olcu','P10','P50','P90']]+rows)
for r in rows: print(r)
NP=1014.5;A1=PC(s['A1_faiz'])[1]
open('tasiyan.csv','w').write(f"""taraf,kalem,mlrTL,not
banka,A1 net faiz,{A1},P50 kâr %{A1/NP*100:.1f}
banka,A3 marj,604.7,kâr %59.6 SYR -2.1
banka,seçici kredi,0,teşvik farkı kamuda [VARSAYIM]
kamu,A4 prim,157.4-393.5,GSYH %0.18-0.46
kamu,seçici teşvik (reeskont q=1),{ekgrup(1,RS['reeskont'])[1]:.1f},GSYH %{ekgrup(1,RS['reeskont'])[1]/85299*100:.2f}
kamu,seçici teşvik (derin25 q=1),{ekgrup(1,RS['derin25'])[1]:.1f},GSYH %{ekgrup(1,RS['derin25'])[1]/85299*100:.2f}
mevduat sahibi,A4 net kayıp,1461.1-1697.2,
""")
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
fig,ax=plt.subplots(1,3,figsize=(14,4.3))
for a,k in zip(ax,'GKB'):
  d=[r for r in rows if r[2]==k and r[3]=='oran'];lab=[f"{r[0].replace('secici_','')}\n{r[1]}" for r in d]
  a.bar(range(len(d)),[r[5] for r in d],yerr=[[r[5]-r[4] for r in d],[r[6]-r[5] for r in d]]);a.axhline(33,ls='--',c='g')
  a.set_xticks(range(len(d)),lab,fontsize=7,rotation=60);a.set_title({'G':'Genel','K':'KOBİ','B':'Büyük'}[k]+' A4 sonrası fin.gider/EFK %')
plt.tight_layout();plt.savefig('secici.png',dpi=110)
