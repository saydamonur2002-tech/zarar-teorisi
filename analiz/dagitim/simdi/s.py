import pandas as pd,numpy as np,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
G_TL=63020.9;G_USD=1597.3
stok_TL=1836.567  # bn TL TCMB IFRS negatif öz sermaye 31.12.2025 [VERİ]
acc_TL=2494.058   # birikmiş zarar [VERİ]
kkm=0.0           # [İKİNCİL]
S=pd.read_csv('../paylas2/tablo_paylas2.csv');S=S[S.duzey.str.startswith('orta')].set_index('aktor')
pt=stok_TL/G_TL*100
act=['Hane_alt','Hane_orta','Hane_ust','Firma_KOBI','Firma_BUYUK','Banka','Hazine','TCMB']
A=S.S1.reindex(act).clip(lower=0);A=A/A.sum()
B=S.S1_eksi_S2.reindex(act).clip(lower=0);B=B/B.sum()
kt=np.array([.215,.411,.374]);C=pd.Series(0.0,index=act);C[['Hane_alt','Hane_orta','Hane_ust']]=kt
R=pd.DataFrame({'A_kazanc':A,'B_erteleme':B,'C_butce10y':C})*pt
out=R.copy()
for c in R: out[c+'_mlrTL']=R[c]/100*G_TL; out[c+'_mlrUSD']=R[c]/100*G_USD
out.round(3).to_csv('paylasim_simdi.csv')
ws={2018:43.25307,2019:44.62912,2020:41.48331,2021:37.91075,2022:33.11055,2023:40.0927,2024:46.2386,2025:46.32076}
d=ws[2025]-ws[2018]; acig=sum(max(ws[2018]-v,0) for v in ws.values())
pd.DataFrame({'ws':ws,'fark_2018':{k:v-ws[2018] for k,v in ws.items()}}).to_csv('ucret_payi.csv')
YH=60;inc=np.array([.167,.357,.476])*YH
rows=[]
for k in R: 
  yuk=R[k][['Hane_alt','Hane_orta','Hane_ust']].values/(10 if k=='C_butce10y' else 1)
  rows.append([k,*(-yuk/inc*100)])
# geriye dönük ücret açığı K_gelir ile, yıllık ortalama
ya=acig/5*np.array([.167,.357,.476]); rows.append(['2019-23 ucret acigi yillik ort.',*(ya/inc*100)])
H=pd.DataFrame(rows,columns=['senaryo','alt40_%gelir','orta40_%gelir','ust20_%gelir']);H.to_csv('hane_etki.csv',index=False)
print(pt,acc_TL/G_TL*100);print(out.round(2).to_string());print(d,acig);print(H.round(2))
fig,ax=plt.subplots(1,2,figsize=(13,5));R.plot.barh(ax=ax[0]);ax[0].set_title(f'Şimdi dondurma: {pt:.2f} GSYH puanı paylaşımı [HESAP]');ax[0].set_xlabel('GSYH %')
ax[1].plot(list(ws),list(ws.values()),'o-');ax[1].axhline(ws[2018],ls='--',c='r',label='2018');ax[1].set_title('Ücret payı AMECO [VERİ]');ax[1].legend()
plt.tight_layout();plt.savefig('simdi.png',dpi=90)
