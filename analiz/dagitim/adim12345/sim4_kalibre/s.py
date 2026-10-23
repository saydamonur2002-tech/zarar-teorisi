import sys,csv,numpy as np;sys.path.insert(0,'../model');sys.path.insert(0,'../sure/dinamik')
import model as M,model12 as m12,types
src=open('../sure/dinamik/d.py').read().split('rows=[]')[0].replace("sys.path.insert(0,'../../model');",'');Dm=types.SimpleNamespace();g={};exec(src,g);Dm.sim=g['sim']
F,E=m12.g('fin_gider_2025'),m12.g('efk_2025');s=M.mc();N=len(np.atleast_1d(s['A1_faiz']))
f=1-s['A1_stok']/M.S0;F1=F['G']-s['A1_faiz'];s['A3_faiz']=np.minimum(.5*f*(9905.7*.5319+9313.3*.0792),F1)
SEN=7869.8;fs=SEN/33108.4;kob=np.clip(np.random.default_rng(5).normal(.3264,.03,N),.15,.5)
P=lambda x:[round(float(v),1) for v in np.percentile(np.ones(N)*x,[10,50,90])]
rows=[];base={k:100*F[k]/E[k] for k in 'GKB'}
for k,sh in (('G',1),('K',kob),('B',1-kob)):
  rows.append(['oran','önce',k]+[round(base[k],1)]*3)
  c=0
  for a,v in (('A1',s['A1_faiz']),('A2',0*F1),('A3',s['A3_faiz']),('A4',0*F1)):
    c=c+v;rows.append(['oran',a,k]+P(100*np.maximum(F[k]-c*sh,0)/E[k]))
  rows.append(['nakit_A1+A3',  'faiz',k]+P((s['A1_faiz']+s['A3_faiz'])*sh))
  rows.append(['nakit_A2','serbest',k]+P(s['A2_nakit']*sh))
for pi in (.02,.05):
  rows.append(['nakit_A4_firma_mevduat_geliri',f'pi{pi}','G']+P(4400.1*fs*(pi-.4330)))
rows.append(['A4_kredi_daralma','stok','G']+[round(.08*SEN,1)]*3)
for c in (1,.5):
  r=Dm.sim(s,kob,.5,c,np.random.default_rng(3).uniform(.3,.7,N),'OVP','bek')
  for k in r: rows.append(['sure_yil',f'c{c}',k]+[round(float(np.nanpercentile(r[k]['T'],p)),2) for p in (10,50,90)])
NP=1014.5;RWA=4771.2/.166;G=85299
for pi in (.02,.05):
  rows+= [['tasiyan_banka_marj',f'pi{pi}','mlrTL/kar%/SYR',604.7,round(604.7/NP*100,1),round(604.7/RWA*100,2)],
          ['tasiyan_kamu_prim',f'pi{pi}','mlrTL/GSYH%',round(SEN*pi,1),round(SEN*pi/G*100,2),''],
          ['tasiyan_mevduat_sahibi',f'pi{pi}','mlrTL/GSYH%',round(1854.6-SEN*pi if pi==.02 else 4055.9*(.433-pi)-3814*(pi-.0258),1),'','']]
csv.writer(open('sim4.csv','w')).writerows([['kalem','adim','grup','P10','P50','P90']]+rows)
for x in rows: print(x)
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
g=[x for x in rows if x[0]=='oran' and x[2]=='G'];v=[x[4] for x in g];fig,a=plt.subplots(figsize=(7,4))
for i in range(1,len(v)): a.bar(i,v[i]-v[i-1],bottom=v[i-1],color='g' if v[i]<v[i-1] else 'grey')
a.bar(0,v[0],color='r');[a.text(i,v[i]+1,f'{v[i]:.1f}',ha='center') for i in range(len(v))]
a.axhline(33,ls='--',c='g');a.axhline(67,ls='--',c='r');a.set_xticks(range(len(v)),[x[1] for x in g]);a.set_ylabel('fin.gider/EFK % (P50)')
a.set_title('Kalibre 4 adım şelalesi (Genel, κ=0,5)');plt.tight_layout();plt.savefig('sim4.png',dpi=110)
