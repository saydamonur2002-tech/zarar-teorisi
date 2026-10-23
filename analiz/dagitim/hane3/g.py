import pandas as pd,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt,numpy as np
D=pd.read_csv('hane3_kanal_grup.csv');G=['alt','orta','ust'];L=['alt %40','orta %40','üst %20']
f,ax=plt.subplots(1,2,figsize=(14,5.5))
a=D[(D.set=='ANA')&D.kanal.str.match('k[12357]')].set_index('kanal')[G]
lab={'k1_TL':'TL erimesi','k2_kur':'kur (DTH)','k3_KKM':'KKM','k5_senyoraj':'senyoraj (nakit)','k7_bankaaltin':'banka altını'}
x=np.arange(3);b=np.zeros(3);bn=np.zeros(3)
for k,r in a.iterrows():
  v=r.values;base=np.where(v>=0,b,bn);ax[0].bar(x,v,bottom=base,label=lab[k]);b+=np.where(v>=0,v,0);bn+=np.where(v<0,v,0)
n=D[(D.set=='ANA')&(D.kanal=='NET_vh_haric')][G].values[0];ax[0].plot(x,n,'kD',ms=9,label='NET (VH hariç)')
for i,v in enumerate(n):ax[0].annotate(f'{v:+.2f}',(i,v),xytext=(12,0),textcoords='offset points',fontweight='bold')
ax[0].axhline(0,c='k',lw=.6);ax[0].set_xticks(x,L);ax[0].set_ylabel('2014-25 kümülatif, %GSYH reel');ax[0].set_title('ANA anahtar: gerçekleşen aktarım kanalları [HESAP/VEKİL]');ax[0].legend(fontsize=8)
s=D[D.kanal=='NET_vh_haric'].set_index('set')[G];s=s.div(s.sum(axis=1),axis=0)*100
s.plot.barh(stacked=True,ax=ax[1],color=['tab:red','tab:orange','tab:blue'],legend=False);ax[1].legend(ax[1].containers,L,fontsize=8,loc='lower right');ax[1].axvline(47.6,c='k',ls='--');ax[1].text(48,-.6,'üst gelir payı %47,6',fontsize=8)
ax[1].set_xlabel('hane net kazancındaki pay (%) — VH hariç');ax[1].set_title('Duyarlılık: anahtar setleri')
plt.tight_layout();plt.savefig('hane3.png',dpi=110)
