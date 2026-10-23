import pandas as pd,numpy as np
T=pd.read_csv('../eksik/tablo_aktor_kanal_tam.csv');T=T[T.donem=='2014-25'].set_index('aktor')
H=lambda c:T.loc[['H_ust','H_alt','H(ayrımsız)'],c].sum()
ch={'k1_TL':H('k1_TL'),'k2_kur':H('k2_kur'),'k3_KKM':H('k3_KKM'),'k5_senyoraj':H('k5_senyoraj'),'k7_bankaaltin':H('k7_bankaaltin')}
vh=H('k4_vergiharc');konut=T.loc['H(ayrımsız)','gercmemis_konut'];alt_lo,alt_hi=22.9,38.9446
inc=np.array([6.14,10.57,14.82,20.9,47.58])  # GYKA 2018 (gelir yılı 2017), SBB 2025 Tablo 2
rent=np.array([.7,1.2,1.8,2.6,4.9])*inc; sec=np.array([1.6,1.3,1.4,1.4,5.7])*inc  # dergipark 2020 Tablo2 (TÜİK 2020b)
cons=np.array([8.08,13.45,17.4,23.69,37.38])  # HBA 2022
g=lambda v:np.array([v[:2].sum(),v[2:4].sum(),v[4]])/v.sum()
K={'gelir':g(inc),'kira':g(rent),'faiz':g(sec),'tuketim':g(cons)}
m=pd.read_csv('/workspace/gec_odeme_efektif_talep/mevduat_tikaniklik/dogrulama/r/aylik_veri.csv');m=m[m.ay.str.endswith('12')&(m.ay>='2016')&(m.ay<'2025')]
dl=pd.read_csv('/workspace/gec_odeme_efektif_talep/dolarizasyon/aylik.csv',index_col=0);dl=dl[dl.index.str.endswith('12')]
s_tl=(m.gk_1m/m.gk_top).mean(); s_fx=(dl.dth_g_1m/dl.dth_g).mean()
band=lambda s:np.r_[(1-s)*g(inc[:4].copy()*1)[:2].sum()/(g(inc[:4])[:2].sum()) if False else 0,0,s]
def bk(s): r=inc[:4]/inc[:4].sum();return np.array([(1-s)*r[:2].sum(),(1-s)*r[2:].sum(),s])
kkm90=np.r_[0.1*K['faiz'][:2]/K['faiz'][:2].sum(),0.9]
sets={'ANA':{'k1_TL':K['faiz'],'k2_kur':K['faiz'],'k3_KKM':K['faiz'],'k5_senyoraj':K['tuketim'],'k7_bankaaltin':K['faiz'],'vh':K['gelir'],'konut':K['kira'],'altin':K['gelir']},
 'a_KKM90':None,'b_mevduat_dilim':None,'c_hepsi_gelir':None,'d_senyoraj_gelir_altin_tuketim':None}
import copy
sets['a_KKM90']=dict(sets['ANA'],k3_KKM=kkm90)
sets['b_mevduat_dilim']=dict(sets['ANA'],k1_TL=bk(s_tl),k2_kur=bk(s_fx),k3_KKM=bk(s_tl),k7_bankaaltin=bk(s_fx))
sets['c_hepsi_gelir']={k:K['gelir'] for k in sets['ANA']}
sets['d_senyoraj_gelir_altin_tuketim']=dict(sets['ANA'],k5_senyoraj=K['gelir'],altin=K['tuketim'])
rows=[];G=['alt','orta','ust']
for sn,S in sets.items():
  for c,v in ch.items(): rows.append([sn,c,v,*(v*S[c])])
  rows.append([sn,'k4_vergiharc',vh,*(vh*S['vh'])])
  rows.append([sn,'P_konut_kagit',konut,*(konut*S['konut'])])
  for nm,a in [('P_yastikalti_2200t',alt_lo),('P_yastikalti_3739t',alt_hi)]: rows.append([sn,nm,a,*(a*S['altin'])])
D=pd.DataFrame(rows,columns=['set','kanal','hane_toplam',*G])
out=[]
for sn,d in D.groupby('set',sort=False):
  r=d[d.kanal.str.startswith('k')&(d.kanal!='k4_vergiharc')][G].sum();rv=r+d[d.kanal=='k4_vergiharc'][G].sum().values
  rp=rv+d[d.kanal.isin(['P_konut_kagit','P_yastikalti_2200t'])][G].sum().values
  for nm,x in [('NET_vh_haric',r),('NET_vh_dahil',rv),('NET_vh_dahil+konut+altin2200',rp)]:out.append([sn,nm,x.sum(),*x.values])
D=pd.concat([D,pd.DataFrame(out,columns=D.columns)]);D.to_csv('hane3_kanal_grup.csv',index=False,float_format='%.3f')
pd.Series({**{f'K_{k}':str(np.round(v,3)) for k,v in K.items()},'s_tl_1m':s_tl,'s_fx_1m':s_fx}).to_csv('anahtarlar.csv')
print(pd.Series({**{k:np.round(v,3) for k,v in K.items()},'s_tl':s_tl,'s_fx':s_fx}))
pd.set_option('display.width',200);print(D.round(2).to_string())
n=D[D.kanal.str.startswith('NET')].copy();n['ust_pay']=n.ust/n.hane_toplam;print(n.round(3).to_string())
