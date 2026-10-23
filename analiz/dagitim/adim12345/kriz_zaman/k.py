import csv
Q=[(2026,4)]+[(y,q) for y in range(2027,2031) for q in (1,2,3,4)];lab=[f'{y}Q{q}' for y,q in Q];n=len(Q)
S={'düşük':dict(g=.25,tl=665,r=40,gap=0,npl=.10,kr=1,dep=.18,res=2,inf=20,pol=27.93),
   'orta':dict(g=.30,tl=844,r=48,gap=3,npl=.25,kr=2,dep=.25,res=0,inf=30,pol=31.5),
   'yüksek':dict(g=.38,tl=1042,r=58,gap=6,npl=.45,kr=3,dep=.35,res=-3,inf=45,pol=35)}
P={'düşük':(.25,669),'orta':(.30,756),'yüksek':(.38,841)}
rows=[];first={}
def mark(k,i,c):
  if c and k not in first:first[k]=lab[i]
for sc,p in S.items():
 for plan in (0,1):
  G=85346.;tc=-2187.;fg={'Genel':77.7,'KOBİ':66.8,'Büyük':84.8};eq=4771.2;rwa=eq/.166;npl=2.92;L=28678.
  d=16202.2;yp=8219.1;rev=16266.1;ir=2741.7/16202.2;res=39.34
  for i in range(n):
   t=i/5 if i<5 else 1;gq=(1+p['g'])**.25-1;G*=1+gq
   if not plan: tc-=p['tl']*(1+p['g'])**(i/4)/4
   rate=53.19+(p['r']-53.19)*t
   if plan: fv={'Genel':26.9,'KOBİ':26.9*66.8/77.7,'Büyük':31.6}
   else:
    fv={k:v*(rate/53.19)*(1+p['gap']/100)**((i+1)/4) for k,v in fg.items()}
   dn=0 if plan else p['npl'];npl+=dn;L*=1+gq;rwa*=1+gq
   eq+=1014.5*(1+p['g'])**(i/4)/4-.5*dn/100*L-(1591/4*(1+p['g'])**(i/4) if plan and i<8 else 0)
   syr=eq/rwa*100
   ir+=p['kr']/400;dpq=(1+p['dep'])**.25-1;yp*=1+dpq;d+=2712.7/4*(1+p['g'])**(i/4)+yp*dpq/(1+dpq);rev*=1+gq
   ki=(ir*d+(( (272 if sc=='düşük' else 349 if sc=='orta' else 426)+P[sc][1])*(1+p['g'])**(i/4) if plan else 0))/rev*100
   res+=p['res'];dis=243.3/res if res>0 else 99
   inf=29.73+(p['inf']-29.73)*t;dep=43.30+(p['pol']+7-43.30)*t;rm=(1+dep/100)/(1+inf/100)*100-100
   if plan: rm_s=(1+(.15 if sc!='düşük' else .25))/(1+inf/100)*100-100
   tcg=(tc if not plan else -2399)/G*100/((1+gq)**0)
   R=dict(senaryo=sc,plan='5 adım' if plan else 'S1 erteleme',ceyrek=lab[i],TCMB_acik_GSYH=round(tcg*4/4/(1) ,2),firma_Genel=round(fv['Genel'],1),firma_KOBI=round(fv['KOBİ'],1),firma_Buyuk=round(fv['Büyük'],1),NPL=round(npl,2),SYR=round(syr,2),kamu_faiz_gelir=round(ki,1),KVdis_netrez=round(dis,2),reel_mevduat=round(rm,2),reel_senet=round(rm_s,2) if plan else '')
   rows.append(R);pl=R['plan']
   # GSYH is quarterly-run; use annualized GSYH for ratios
   mark((sc,pl,'TCMB<-3%'),i,R['TCMB_acik_GSYH']<-3*1);mark((sc,pl,'TCMB<-5%'),i,R['TCMB_acik_GSYH']<-5)
   mark((sc,pl,'firma Büyük>100'),i,fv['Büyük']>100);mark((sc,pl,'firma Genel>100'),i,fv['Genel']>100);mark((sc,pl,'firma KOBİ>100'),i,fv['KOBİ']>100)
   mark((sc,pl,'SYR<12'),i,syr<12);mark((sc,pl,'SYR<8'),i,syr<8);mark((sc,pl,'kamu>20'),i,ki>20);mark((sc,pl,'kamu>25'),i,ki>25)
   mark((sc,pl,'KVdış/rezerv>1'),i,dis>1);mark((sc,pl,'reel mevduat<0'),i,rm<0)
   if plan: mark((sc,pl,'reel senet<0'),i,rm_s<0)
csv.writer(open('yollar.csv','w')).writerows([list(rows[0])]+[[r.get(k,'') for k in rows[0]] for r in rows])

E=[['senaryo','plan','esik','ilk_asim']]
keys=['TCMB<-3%','TCMB<-5%','firma Büyük>100','firma Genel>100','firma KOBİ>100','SYR<12','SYR<8','kamu>20','kamu>25','KVdış/rezerv>1','reel mevduat<0','reel senet<0']
for sc in S:
 for pl in ('S1 erteleme','5 adım'):
  for k in keys:
   if k=='reel senet<0' and pl!='5 adım':continue
   E.append([sc,pl,k,first.get((sc,pl,k),'2030Q4 sonrası/yok')])
csv.writer(open('esikler.csv','w')).writerows(E)
for e in E:print(e)
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
fig,axs=plt.subplots(1,2,figsize=(14,5.5),sharey=True);idx={l:i for i,l in enumerate(lab)}
for ax,pl in zip(axs,('S1 erteleme','5 adım')):
 ks=[k for k in keys if not(k=='reel senet<0' and pl!='5 adım')]
 for j,k in enumerate(ks):
  for sc,c,o in (('düşük','g',-.2),('orta','orange',0),('yüksek','r',.2)):
   v=first.get((sc,pl,k))
   if v: ax.plot(idx[v],j+o,'o',c=c,label=sc if j==0 or k==ks[0] else None)
 ax.set_yticks(range(len(ks)));ax.set_yticklabels(ks);ax.set_xticks(range(0,len(lab),2));ax.set_xticklabels(lab[::2],rotation=45);ax.set_title(pl+' — ilk eşik aşımı (muhasebe projeksiyonu, TAHMİN DEĞİL)');ax.grid(alpha=.3)
axs[0].legend(*[x[:3] for x in axs[0].get_legend_handles_labels()]);plt.tight_layout();plt.savefig('kriz_zaman.png',dpi=110)
