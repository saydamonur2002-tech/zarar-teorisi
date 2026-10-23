import pandas as pd,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt,numpy as np
R=pd.read_csv('tablo_paylas2.csv');W=R.pivot(index='aktor',columns='duzey',values='S1_eksi_S2')
o=['Hane_alt','Hane_orta','Hane_ust','Firma_KOBI','Firma_BUYUK','Banka','Hazine','TCMB','Yurtdisi+artik'];W=W.loc[o]
m=W['orta(asimetrik,k=.5)'];lo=W.min(axis=1);hi=W.max(axis=1)
f,ax=plt.subplots(figsize=(10,6));y=np.arange(len(o))
ax.barh(y,m,color=['g' if v>0 else 'r' for v in m],alpha=.6,label='orta')
ax.errorbar(m,y,xerr=[m-lo,hi-m],fmt='none',ecolor='k',capsize=4,label='düşük–yüksek aralığı')
ax.scatter(W['dusuk(simetrik,k=1)'],y,marker='x',c='k',label='düşük (statik eşdeğeri)')
ax.set_yticks(y);ax.set_yticklabels(o);ax.axvline(0,c='k',lw=.8)
ax.set_xlabel('Ertelemenin getirisi S1−S2 (2014–25, GSYH puanı) [HESAP; S2 VARSAYIM]');ax.set_title('paylas2: dinamik S2 (kur kuralı psi=3,4) + TCMB→Hazine kâr aktarımı + banka YP pozisyonu')
ax.legend(fontsize=8);plt.tight_layout();plt.savefig('paylas2.png',dpi=120)
