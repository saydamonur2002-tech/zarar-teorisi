import sys,numpy as np,csv;sys.path.insert(0,'../model');import model as M,model12 as m12
F,E=m12.g('fin_gider_2025'),m12.g('efk_2025');rng=np.random.default_rng(3)
def calc(o,kobi,kappa,c,phi,tau=.25):
    out={}
    for k,s in (('G',1),('K',kobi),('B',1-kobi)):
        I3=o['A3_faiz']*s;D=kappa*M.PSI*(M.S0-o['A1_stok'])*s
        Fk=F[k]-(o['A1_faiz']+o['A3_faiz'])*s;ex=np.maximum(E[k]-Fk,0)*(1-tau)*(1-phi)
        T=D/(c*I3+ex);L=np.clip(T*(1-(0.33*E[k]-Fk)/I3),0,None);L=np.where(Fk/E[k]>=.33,np.nan,L)
        out[k]=dict(D=D,T=T,Lmin=L,oran_durma=100*Fk/E[k],oran_kalkinca_0yil=100*(Fk+I3)/E[k],oran_kalkinca_sonra=100*Fk/E[k])
    return out
rows=[]
for kap in (.25,.5,1):
  for c in (.5,1):
    p=dict(M.MER,kappa=kap);o=M.run(**p);r=calc(o,p['kobi_payi'],kap,c,.5)
    for k in r: rows.append(['nokta',kap,c,k]+[round(float(np.asarray(r[k][x])),2) for x in ('D','T','Lmin','oran_durma','oran_kalkinca_0yil')])
N=m12.P['mc']['n'];x={}
s=M.mc();phi=rng.uniform(.3,.7,N)
# kappa ve kobi'yi yeniden üretmek için mc girdileri: model.mc aynı seed
r0=np.random.default_rng(7);kap=r0.triangular(.25,.5,1,N)
rr=np.random.default_rng(1);mm=m12.P['mc'];z=rr.multivariate_normal([0,0],[[1,.5],[.5,1]],N);rr.random(N);rr.random(N);kobi=np.clip(rr.normal(.3264,.03,N),.15,.5)
for c in (.5,1):
  r=calc(s,kobi,kap,c,phi)
  for k in r:
    for q in (10,50,90): rows.append([f'MC_P{q}','κ~',c,k]+[round(float(np.nanpercentile(r[k][x],q)),2) for x in ('D','T','Lmin','oran_durma','oran_kalkinca_0yil')])
    rows.append(['MC_imkansiz_pay','κ~',c,k,'','',round(float(np.isnan(r[k]['Lmin']).mean()),3),'',''])
with open('sure.csv','w') as f:
  w=csv.writer(f);w.writerow(['tip','kappa','c','grup','D_mlrTL','T_yil','Lmin_yil','oran_durma%','oran_hemen_kalk%']);w.writerows(rows)
for r_ in rows: print(r_)
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
fig,a=plt.subplots(1,2,figsize=(10,4))
for c in (.5,1):
  r=calc(s,kobi,kap,c,phi)
  a[0].boxplot([r[k]['T'] for k in 'GKB'],positions=np.arange(3)+(0 if c==.5 else .35),widths=.3,showfliers=False)
a[0].set_xticks([.17,1.17,2.17],['Genel','KOBİ','Büyük']);a[0].set_title('Anapara kaç yılda biter (sol c=0.5, sağ c=1)')
r=calc(s,kobi,kap,1,phi);a[1].boxplot([r['G']['oran_durma'],r['G']['oran_kalkinca_0yil']],showfliers=False);a[1].axhline(33,ls='--',c='r')
a[1].set_xticks([1,2],['durma sırasında','anapara bitmeden kalkarsa']);a[1].set_title('Fin. gid./EFK % (Genel)')
plt.tight_layout();plt.savefig('sure.png',dpi=110)
