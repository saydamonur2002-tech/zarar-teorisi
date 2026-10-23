import pandas as pd,numpy as np
B='/workspace/grafik5/dagitim/'
gm=pd.read_csv('/workspace/gec_odeme_efektif_talep/mevduat_tikaniklik/dogrulama/r/aylik_veri.csv').set_index('ay')
dec=gm[gm.index.str.endswith('12')].copy();dec.index=dec.index.str[:4].astype(int)
gdp=dec.gsyh_4q/1e3;kur=dec.usd
m=pd.read_csv('/workspace/grafik5/mevduat/makro_yil.csv',index_col=0);pi=m.infl/100;i=m.faiz/100
fx=pd.read_csv(B+'doviz_pozisyon_mlrTL.csv',index_col=0)
Y=range(2014,2026);R=pd.DataFrame(index=Y,dtype=float)
# K3 KKM (mlr TL nominal, yıl içi) -> /GSYH_t
haz={2022:92.5,2023:59.87};tcmb={2022:72.843,2023:833.420,2024:240.167,2025:166.476}
hp=0.74  # hane payı FİR 2024-I (03.23: 1250.6/(1250.6+451); 09.23: 2495.5/(2495.5+809))
for t in Y:
  g=gdp[t];k=haz.get(t,0);c=tcmb.get(t,0)
  R.loc[t,'k3_K']=-k/g*100;R.loc[t,'k3_TCMB']=-c/g*100
  R.loc[t,'k3_H']=hp*(k+c)/g*100;R.loc[t,'k3_F']=(1-hp)*(k+c)/g*100
# K4 vergi harcaması (mn TL; dergipark tablo 2 <- GİB raporları); 2025 GİB 2024 raporu tahmini
vh=pd.DataFrame({'gv':[16314.8,18097.2,20493.7,37714.1,54249.8,68267.4,76917.3,91172.6,127902.7,443471.5,1006274.1,1417924],
 'kv':[4313.2,4131.0,4448.2,15110.2,17654.3,28031.0,40164.9,49423.3,86107.8,280839.6,657044.4,701028],
 'top':[23888.4,26112.6,29962.6,102216.0,132141.9,178695.9,195590.8,230770.1,335968.5,994380.3,2210375.5,3005167]},index=Y)/1e3
for t in Y:
  g=gdp[t];R.loc[t,'k4_H']=vh.gv[t]/g*100;R.loc[t,'k4_F']=vh.kv[t]/g*100;R.loc[t,'k4_diger']=(vh.top[t]-vh.gv[t]-vh.kv[t])/g*100;R.loc[t,'k4_K']=-vh.top[t]/g*100
# K5 senyoraj: emisyon (TCMB analitik bilanço, bin TL)
ab=pd.read_csv('/workspace/zt/veri/aktarim_matrisi/evds/evds_a_analitik_bilanco_aylik.csv');ab=ab[ab.Donem.str.endswith('-12')]
E=ab[ab.Seri=='TP.AB.A17'].set_index(ab[ab.Seri=='TP.AB.A17'].Donem.str[:4].astype(int)).Deger/1e6
RP=ab[ab.Seri=='TP.AB.A16'].set_index(ab[ab.Seri=='TP.AB.A16'].Donem.str[:4].astype(int)).Deger/1e6
for t in Y:
  g=gdp[t];e=E[t-1]
  R.loc[t,'k5_H']=-i[t]/(1+pi[t])*e/g*100;R.loc[t,'k5_TCMB']=pi[t]/(1+pi[t])*e/g*100;R.loc[t,'k5_D']=-(R.loc[t,'k5_H']+R.loc[t,'k5_TCMB'])
  R.loc[t,'bag_enfvergi_emisyon']=pi[t]/(1+pi[t])*e/g*100
  R.loc[t,'bag_RP_reel_artis']=(RP[t]/(1+pi[t])-RP[t-1])/g*100
# K6 konut (kiradaki konut, TCMB ER2025-I Kutu2.5: 701 mlr$ 2024Ç3), BIS reel KFE
ms=pd.read_csv('/workspace/grafik5/zincir/konut_reel_bis.csv',index_col=0);ms.index=pd.to_datetime(ms.index);h=ms.iloc[:,0]
hq4=h[h.index.month==10];hq4.index=hq4.index.year;h_anchor=h['2024-07-01']
cpi=gm.cpi;cpi_dec=dec.cpi;V0=701*gm.loc['2024-09','usd']  # mlr TL 2024-09
for t in Y:
  Vprev=V0*(hq4[t-1]/h_anchor)*(cpi_dec[t-1]/gm.loc['2024-09','cpi'])  # sabit adet [VARSAYIM]
  R.loc[t,'k6_H_konut']=Vprev*(hq4[t]/hq4[t-1]-1)/gdp[t]*100
# K7 altın: yastık altı 311 mlr$ 2024Ç3 -> ton sabit; banka altın (km_g gerçek kişi)
dl=pd.read_csv('/workspace/gec_odeme_efektif_talep/dolarizasyon/aylik.csv',index_col=0)
P=dl['TP.MK.LON.YTL'];oz=311e9/P['2024-09'];ton=oz*31.1035/1e6
Pd=P[P.index.str.endswith('12')];Pd.index=Pd.index.str[:4].astype(int)
kmg=dl.km_g[dl.index.str.endswith('12')];kmg.index=kmg.index.str[:4].astype(int)
for t in Y:
  if t-1 in Pd.index:
    f=(Pd[t]*kur[t])/(Pd[t-1]*kur[t-1])/(1+pi[t])-1
    R.loc[t,'k7_H_yastik']=oz*Pd[t-1]*kur[t-1]/1e9*f/gdp[t]*100
    R.loc[t,'k7_H_bankaaltin']=kmg[t-1]/1e3*f/gdp[t]*100;R.loc[t,'k7_D']=-R.loc[t,'k7_H_bankaaltin']
# K8 TCMB swap düşülmüş
z=pd.read_csv('/workspace/grafik5/zincir/ceyrek_zincir.csv',index_col=0);z=z[z.index.str.endswith('Q4')];z.index=z.index.str[:4].astype(int)
for t in Y:
  f=(kur[t]/kur[t-1])/(1+pi[t])-1
  if t>=2017 and (t-1) in z.index: R.loc[t,'k8_TCMB']=-z.swap[t-1]*kur[t-1]*f/gdp[t]*100;R.loc[t,'k8_D']=-R.loc[t,'k8_TCMB']
# K9 D doğrudan UYP
niip=pd.Series([-392.130,-441.009,-371.594,-335.934,-444.127,-327.070,-308.823,-383.338,-236.672,-341.471,-308.387,-353.256,-349.966],index=range(2013,2026))
fa=pd.Series([-36.515,-20.933,-18.467,-49.127,-915/1e3,7.134,-38.391,-5.606,-23.410,-37.399,-20.894,-36.319],index=Y)
for t in Y:
  N1=niip[t]*kur[t];N0=niip[t-1]*kur[t-1];FA=fa[t]*(kur[t]+kur[t-1])/2
  R.loc[t,'D_UYP_dogrudan']=-(N1/(1+pi[t])-N0-FA/(1+pi[t])**0.5)/gdp[t]*100  # mlr$*TL = mlr TL... birim: mlr$→ *1e3 mn$; see below
R['D_UYP_dogrudan']*=1  # niip mlr $ * kur = mlr TL, gdp mlr TL: ok
R.to_csv('yeni_kanallar_yil.csv')
print(R.round(2).to_string());print('ton',round(ton))
# --- birleşik tablo
T=pd.read_csv(B+'aktor_kanal_yil.csv',index_col=0).loc[2014:2025]
act=['H_ust','H_alt','F','B','K','TCMB','D']
def S(c,sel): return R.loc[sel,c].sum(min_count=1) if c in R else np.nan
out={}
for nm,sel in [('2014-25',slice(2014,2025)),('2017-25',slice(2017,2025)),('2018',[2018]),('2021',[2021]),('2022',[2022]),('2023',[2023])]:
  o=pd.DataFrame(index=act)
  o['k1_TL']=[T.loc[sel,'k1_'+a].sum() if 'k1_'+a in T else 0 for a in act]
  o['k2_kur']=[T.loc[sel,'k2_'+a].sum() if 'k2_'+a in T else 0 for a in act]
  o['eski_toplam']=o.k1_TL+o.k2_kur
  hs={'H_ust':None,'H_alt':None}
  o['k3_KKM']=[0,0,S('k3_F',sel),0,S('k3_K',sel),S('k3_TCMB',sel),0]
  o['k4_vergiharc']=[0,0,S('k4_F',sel),0,S('k4_K',sel),0,0]
  o['k5_senyoraj']=[0,0,0,0,0,S('k5_TCMB',sel),S('k5_D',sel)]
  o['k7_bankaaltin']=[0,0,0,0,0,0,S('k7_D',sel)]
  o['k8_swap']=[0,0,0,0,0,S('k8_TCMB',sel),S('k8_D',sel)]
  # hane kalemleri: KKM, gelir vergisi harcaması, senyoraj, banka altın -> üst/alt ayrımı yok: H_ust satırına değil ayrı 'H_toplam_ek' sütununa
  o['H_ek_gerceklesen']=0.0
  hk=S('k3_H',sel)+S('k4_H',sel)+S('k5_H',sel)+np.nan_to_num(S('k7_H_bankaaltin',sel))
  o.loc['H_ust','H_ek_gerceklesen']=np.nan;o.loc['H_alt','H_ek_gerceklesen']=np.nan
  o.loc['H(ayrımsız)']=0.0;o.loc['H(ayrımsız)','H_ek_gerceklesen']=hk
  o.loc['H(ayrımsız)',['k3_KKM','k4_vergiharc','k5_senyoraj','k7_bankaaltin']]=[S('k3_H',sel),S('k4_H',sel),S('k5_H',sel),np.nan_to_num(S('k7_H_bankaaltin',sel))]
  o.loc['H(ayrımsız)','H_ek_gerceklesen']=0
  o.loc['KDV/ÖTV/diğer(ayrılamadı)']=0.0;o.loc['KDV/ÖTV/diğer(ayrılamadı)','k4_vergiharc']=S('k4_diger',sel)
  newc=['k3_KKM','k4_vergiharc','k5_senyoraj','k7_bankaaltin','k8_swap']
  o['yeni_toplam_vh_haric']=o[[c for c in newc if c!='k4_vergiharc']].sum(axis=1);o['NET_vh_haric']=o.eski_toplam+o.yeni_toplam_vh_haric;o['NET_vh_dahil']=o.NET_vh_haric+o.k4_vergiharc
  o=o.drop(columns='H_ek_gerceklesen')
  # gerçekleşmemiş
  o['gercmemis_konut']=0.0;o['gercmemis_yastikaltin']=0.0
  o.loc['H(ayrımsız)','gercmemis_konut']=S('k6_H_konut',sel);o.loc['H(ayrımsız)','gercmemis_yastikaltin']=S('k7_H_yastik',sel)
  o['D_UYP_dogrudan']=np.nan;o.loc['D','D_UYP_dogrudan']=S('D_UYP_dogrudan',sel)
  out[nm]=o
X=pd.concat(out,names=['donem','aktor']);X.to_csv('tablo_aktor_kanal_tam.csv')
pd.set_option('display.width',250)
for k,v in out.items():print('==',k);print(v.round(2).to_string());print('Σ',v.drop(columns=['D_UYP_dogrudan']).sum().round(2).to_dict())
