import sys; sys.path.insert(0,'.')
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import sfc_model as m
sc=m.ts_scenarios(); [v.update(no_jump=True,psi=3.4,cap_band=1e6) for v in sc.values()]; res={k:m.simulate(v) for k,v in sc.items() if k.startswith('Baz')}
lab=['2026Q3','2026Q4','2027Q1','2027Q2','2027Q3','2027Q4','2028Q1','2028Q2','2028Q3','2028Q4','2029Q1','2029Q2','2029Q3','2029Q4']
C={'paketsiz':('Paketsiz','gray'),'Kötümser':('Kötümser','red'),'Olası':('Olası','blue'),'İyimser':('İyimser','green')}
fig,ax=plt.subplots(2,2,figsize=(13,9));ax=ax.ravel()
T=['Yıllık enflasyon (%)','Reel GSYH endeksi (2026Q3=100)','Net rezerv (mlr $)','Kamu borcu / GSYH (%)']
for k,o in res.items():
    n,c=C[k.split(' · ')[1]]; x=range(len(o['pi']))
    rg=m.real_gdp(o); s=[np.array(o['pi'])*100, rg/rg[0]*100, np.array(o['NR']), np.array(o['debt'])*100]
    for a,y in zip(ax,s): a.plot(x,y,color=c,label=n,lw=2,marker='o',ms=3)
    print(n, 'n=',len(o['pi']), '2029Q4: pi=%.1f gdp=%.1f NR=%.1f debt=%.1f'%tuple(v[-1] for v in s))
for a,t in zip(ax,T):
    a.set_title(t);a.grid(alpha=.3);a.set_xticks(range(0,14));a.set_xticklabels(lab,rotation=45,fontsize=8)
ax[0].legend()
fig.suptitle('Tek Sistem 5 adım: senaryolar (baz arka plan, kalibre)',fontsize=15)
fig.text(.5,.01,'Kur-rezerv kuralı 2016–2025 veriyle kalibre; model çıktısı [aday] · karşı-olgu yok · kaynak: zarar-teorisi @ b051b9b, zararin_muhasebesi/sfc_model.py',ha='center',fontsize=9)
fig.tight_layout(rect=[0,.03,1,.96]); fig.savefig('../senaryo_kalibre.png',dpi=150)
