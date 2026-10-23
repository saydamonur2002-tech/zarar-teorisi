import pandas as pd,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt,numpy as np
X=pd.read_csv('tablo_aktor_kanal_tam.csv',index_col=[0,1]).loc['2014-25']
X.index=X.index.str.replace('KDV/ÖTV/diğer(ayrılamadı)','KDV/ÖTV/diğer*')
H=X.loc[['H_ust','H_alt','H(ayrımsız)']].sum();Hrow=H.copy()
A=pd.concat([X.loc[['F','B','K','TCMB','D']],Hrow.to_frame('Hane (toplam)').T])
cols=[('k1_TL','TL erime'),('k2_kur','Kur'),('k3_KKM','KKM'),('k5_senyoraj','Senyoraj'),('k7_bankaaltin','Banka altın'),('k8_swap','Swap düzeltme')]
fig,ax=plt.subplots(1,3,figsize=(17,6.5),gridspec_kw={'width_ratios':[2.2,1.3,1.3]})
y=np.arange(len(A));pos=np.zeros(len(A));neg=np.zeros(len(A))
for c,l in cols:
  v=A[c].fillna(0).values;b=np.where(v>=0,pos,neg);ax[0].barh(y,v,left=b,label=l);pos+=np.clip(v,0,None);neg+=np.clip(v,None,0)
ax[0].scatter(A.NET_vh_haric,y,color='k',zorder=5,marker='D',label='NET (vergi harc. hariç)')
for j,v in enumerate(A.NET_vh_haric):ax[0].text(v,j+0.3,f'{v:+.1f}',ha='center',fontsize=9)
ax[0].set_yticks(y);ax[0].set_yticklabels(A.index);ax[0].axvline(0,color='k',lw=.8);ax[0].legend(fontsize=8,loc='lower right')
ax[0].set_title('Gerçekleşen aktarım 2014–25, kümülatif %GSYH reel\n(Σ=0; D = yurt dışı+artık)',fontsize=10)
vh=X.loc[['F','K','H(ayrımsız)','KDV/ÖTV/diğer*'],'k4_vergiharc']
ax[1].barh(vh.index,vh.values,color=['tab:orange','tab:red','tab:green','grey']);ax[1].axvline(0,color='k',lw=.8)
for j,v in enumerate(vh.values):ax[1].text(v,j,f'{v:+.1f}',va='center',fontsize=9)
ax[1].set_title('Vergi harcaması (ayrı; 2017 yöntem kırılması)\nNET dahil: F %+.1f, Hazine %+.1f'%(X.loc['F','NET_vh_dahil'],X.loc['K','NET_vh_dahil']),fontsize=10)
R=pd.read_csv('yeni_kanallar_yil.csv',index_col=0)
ax[2].plot(R.index,R.k6_H_konut.cumsum(),label='Kiradaki konut [VEKİL]');ax[2].plot(R.index,R.k7_H_yastik.cumsum(),label='Yastık altı altın, 3.739 t sabit [VARSAYIM]')
ax[2].plot(R.index,R.k7_H_yastik.cumsum()*2200/3739,'--',label='altın, 2.200 t')
ax[2].axhline(0,color='k',lw=.8);ax[2].legend(fontsize=8);ax[2].set_title('Hane gerçekleşmemiş değerleme\nkümülatif %GSYH reel (karşı tarafı yok)',fontsize=10)
fig.text(0.01,0.01,'Kaynak: TCMB (yıllık rapor 2022–25 KKM gideri, FİR 2024-I, ER 2025-I Kutu 2.5, UYP, analitik bilanço), HMB/GİB vergi harcamaları [İKİNCİL], BIS reel KFE. *KDV/ÖTV/diğer: aktöre ayrılamadı.',fontsize=8)
plt.tight_layout(rect=[0,0.03,1,1]);plt.savefig('eksik.png',dpi=110)
