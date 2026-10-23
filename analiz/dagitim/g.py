import pandas as pd,numpy as np,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
T=pd.read_csv('aktor_kanal_yil.csv',index_col=0);S=pd.read_csv('stok_NFP_gsyh.csv',index_col=0)
act=['H_ust','H_alt','F','B','K','TCMB','D'];lab={'H_ust':'hane üst (≥1mn, VEKİL)','H_alt':'hane alt','F':'firma','B':'banka(+TCMB TL)','K':'Hazine','TCMB':'TCMB (döviz)','D':'yurt dışı+artık'}
col=dict(zip(act,['#1f77b4','#aec7e8','#d62728','#9467bd','#2ca02c','#17becf','#7f7f7f']))
f,ax=plt.subplots(2,2,figsize=(15,10))
def stack(a,M,x,w=.8):
  bp=np.zeros(len(x));bn=np.zeros(len(x))
  for c in act:
    v=np.nan_to_num(M[c].values);b=np.where(v>=0,bp,bn);a.bar(x,v,w,bottom=b,color=col[c],label=lab[c]);bp+=np.clip(v,0,None);bn+=np.clip(v,None,0)
  a.axhline(0,color='k',lw=.6)
for k,(a,ttl) in enumerate([(ax[0,0],'Kanal 1: TL erime, %GSYH reel [HESAP]'),(ax[0,1],'Kanal 2: kur, %GSYH reel [HESAP] (2017+)')]):
  M=pd.DataFrame({c:T.get(f'k{k+1}_{c}',0*T.index) for c in act},index=T.index);stack(a,M,T.index);a.set_title(ttl+'\nher yıl Σ=0 (D kapanış kalemi)')
ax[0,0].legend(fontsize=7,ncol=2)
a=ax[1,0];c=pd.read_csv('tablo_aktor_kanal.csv');c=c[c.donem=='2014-25'].set_index('aktor')
x=np.arange(len(act));a.bar(x-.2,c.loc[act,'k1_TL'],.4,label='TL erime');a.bar(x+.2,c.loc[act,'k2_kur'],.4,label='kur');a.plot(x,c.loc[act,'toplam_1+2'],'kD',label='toplam')
a.set_xticks(x);a.set_xticklabels([lab[i] for i in act],rotation=25,fontsize=8);a.axhline(0,color='k',lw=.6);a.legend();a.set_title('Kümülatif 2014–25 kim kazandı (%GSYH, reel) [HESAP]\nKKM, transfer, senyoraj EKSİK')
a=ax[1,1]
for s,l in [('H','hane'),('F','firma'),('K','kamu+?'),('B','banka+TCMB?'),('D','yurt dışı')]:a.plot(S.index,S[s],'o-',label=l)
a.plot(T.index,T.k6_H_hisse.cumsum(),'k--',label='hane hisse reel değ. kümülatif (gerçekleşmemiş, VEKİL)')
a.axhline(0,color='k',lw=.6);a.legend(fontsize=7,loc='upper right',bbox_to_anchor=(1,0.75));a.set_title('Birikim: net finansal varlık / GSYH %\n[VERİ: TCMB fin. hesap; EVDS3 anahtarsız çekim 7.10.2026]')
for b in [ax[0,0],ax[0,1],ax[1,1]]:
  for x0,x1 in [(2019.5,2020.5),(2021.5,2022.5)]:b.axvspan(x0,x1,color='orange',alpha=.12)
plt.tight_layout();plt.savefig('dagitim.png',dpi=105)
