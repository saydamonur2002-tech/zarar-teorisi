import sys,numpy as np,csv;sys.path.insert(0,'../../model');sys.path.insert(0,'..')
import model as M,model12 as m12
F,E=m12.g('fin_gider_2025'),m12.g('efk_2025');AN,KB=19219.0,6998.3/19219.0
def calc(o,kobi,kappa,c,phi,tau=.25):
  out={}
  for k,s in (('G',1),('K',kobi),('B',1-kobi)):
    I3=o['A3_faiz']*s;D=kappa*AN*(1-o['A1_stok']/M.S0)*s
    Fk=F[k]-(o['A1_faiz']+o['A3_faiz'])*s;ex=np.maximum(E[k]-Fk,0)*(1-tau)*(1-phi)
    T=D/(c*I3+ex);L=np.where(Fk/E[k]>=.33,np.nan,np.clip(T*(1-(0.33*E[k]-Fk)/I3),0,None))
    out[k]=dict(D=D,T=T,L=L,o=100*Fk/E[k])
  return out
rows=[]
for kap in (.25,.5,1):
  for c in (.5,1):
    p=dict(M.MER,kappa=kap);r=calc(M.run(**p),KB,kap,c,.5)
    for k in r: rows.append(['nokta',kap,c,k]+[round(float(np.asarray(r[k][x])),2) for x in 'DTLo'])
N=m12.P['mc']['n'];s=M.mc();phi=np.random.default_rng(3).uniform(.3,.7,N)
kap=np.random.default_rng(7).triangular(.25,.5,1,N);kobi=np.clip(np.random.default_rng(5).normal(KB,.03,N),.15,.5)
R={}
for c in (.5,1):
  R[c]=r=calc(s,kobi,kap,c,phi)
  for k in r:
    for q in (10,50,90): rows.append([f'P{q}','κ~',c,k]+[round(float(np.nanpercentile(r[k][x],q)),2) for x in 'DTLo'])
    rows.append(['imkansiz_pay','κ~',c,k,'','',round(float(np.isnan(r[k]['L']).mean()),3),''])
w=csv.writer(open('anapara.csv','w'));w.writerow(['tip','kappa','c','grup','anapara_mlrTL','T_yil','Lmin_yil','oran_durma%']);w.writerows(rows)
[print(x) for x in rows]
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
fig,a=plt.subplots(figsize=(7,4))
for i,c in enumerate((.5,1)):a.boxplot([R[c][k]['T'] for k in 'GKB'],positions=np.arange(3)+.35*i,widths=.3,showfliers=False)
a.set_xticks([.17,1.17,2.17],['Genel','KOBİ','Büyük']);a.set_ylabel('yıl');a.set_title('Anapara (BDDK, tahakkuk hariç) kaç yılda biter\nsol: nakdin %50si, sağ: %100ü')
plt.tight_layout();plt.savefig('anapara.png',dpi=110)
