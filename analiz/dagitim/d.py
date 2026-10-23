import pandas as pd,numpy as np,json
R=pd.read_csv('../kamu/sektor_aktarim.csv')
gdpm=pd.read_csv('/workspace/gec_odeme_efektif_talep/mevduat_tikaniklik/dogrulama/r/aylik_veri.csv');gdpm=gdpm[gdpm.ay.str.endswith('12')];gdpm['yil']=gdpm.ay.str[:4].astype(int);gm=gdpm.set_index('yil')
gdp=gm.gsyh_4q/1e3;kur=gm.usd;ust=(gm.gk_1m/gm.gk_top)   # mlr TL
m=pd.read_csv('../mevduat/makro_yil.csv',index_col=0);pi=m.infl/100;i=m.faiz/100
gdp_full=gdp.copy()
nom=R.pivot(index='yil',columns='s',values='nominal_gsyh').reindex(range(2013,2026))
# 2013 nominal yok kamu dosyasında -> yeniden hesapla
fa=pd.read_csv('/workspace/zarar_evds/finansal_hesaplar_uzun.csv');fa=fa[fa.Donem.str.endswith('Q4')&(fa.Hazne!='TOPLAM')];fa['zp']=fa.Seri.str.extract(r'ZP(\d+)$')[0].astype(int);fa['yil']=fa.Donem.str[:4].astype(int);fa['Hazne']=fa.Hazne.replace({'NPISH':'H'})
P=fa.groupby(['yil','Hazne','zp']).Deger.sum().unstack().fillna(0)/1e6
N=pd.DataFrame({'nom':(P[5]+P[9]+P[12])-(P[27]+P[31]+P[34]),'hisse':P[15]-P[37],'NFP':P[[2,5,9,12,15,20,21,22]].sum(axis=1)-P[[24,27,31,34,37,42,43,44]].sum(axis=1),'h_hisse_varlik':P[15]})
N.loc[(slice(None),'D'),:]*=-1
nomTL=N.nom.unstack()  # mlr TL
# döviz pozisyonları, mlr TL
fx=pd.DataFrame(index=range(2013,2026))
fd=json.load(open('ham/firma_net_doviz_mnusd.json'));fx['F']=pd.Series({int(k):v for k,v in fd.items()})/1e3*kur
dl=pd.read_csv('/workspace/gec_odeme_efektif_talep/dolarizasyon/aylik.csv',index_col=0);dl=dl[dl.index.str.endswith('12')];dl.index=dl.index.str[:4].astype(int)
fx['H']=dl.dth_g/1e3;fx['H_ust_pay']=dl.dth_g_1m/dl.dth_g
z=pd.read_csv('../zincir/ceyrek_zincir.csv',index_col=0);z=z[z.index.str.endswith('Q4')];z.index=z.index.str[:4].astype(int)
fx['TCMB']=z.NR*kur
dis=pd.Series(dict(zip(range(2014,2025),[10.0,10.5,11.6,11.4,13.3,13.7,15.6,20.4,14.8,13.9,10.3])));dis[2025]=dis[2024];dis[2013]=10.5
fx['K']=-dis/100*gdp;fx['B']=0.0
A=['H','F','B','K','TCMB']
fx['D']=-fx[A].sum(axis=1)
fx.to_csv('doviz_pozisyon_mlrTL.csv')
rows=[]
for t in range(2014,2026):
  g=gdp[t];r=dict(yil=t)
  # kanal 1 TL
  tl={}
  for s in ['H','F','B','K']:
    adj=fx.loc[t-1,s] if s!='B' else fx.loc[t-1,'TCMB']
    tl[s]=nomTL.loc[t-1,s]-(adj if pd.notna(adj) else 0)
  tl['D']=-sum(tl.values())
  for s,v in tl.items():r['k1_'+s]=(i[t]-pi[t])/(1+pi[t])*v/g*100
  # kanal 2 kur (2017+)
  f=(kur[t]/kur[t-1])/(1+pi[t])-1
  for s in A+['D']:
    p=fx.loc[t-1,s];r['k2_'+s]=p*f/g*100 if (t>=2017 and pd.notna(p)) else np.nan
  # hane üst/alt
  su=ust[t-1];sd=fx.loc[t-1,'H_ust_pay']
  r['k1_H_ust']=r['k1_H']*su;r['k1_H_alt']=r['k1_H']*(1-su)
  r['k2_H_ust']=r['k2_H']*sd if pd.notna(sd) else np.nan;r['k2_H_alt']=r['k2_H']-r['k2_H_ust'] if pd.notna(sd) else np.nan
  # kanal 6 hane hisse reel değişim
  h0,h1=N.h_hisse_varlik.loc[(t-1,'H')],N.h_hisse_varlik.loc[(t,'H')];r['k6_H_hisse']=(h1/(1+pi[t])-h0)/g*100
  r['pasta']=((gdp[t]/gdp[t-1])/(1+pi[t])-1)*100
  rows.append(r)
T=pd.DataFrame(rows).set_index('yil')
T['k1_toplam']=T[[f'k1_{s}' for s in ['H','F','B','K','D']]].sum(axis=1);T['k2_toplam']=T[[f'k2_{s}' for s in A+['D']]].sum(axis=1)
T.to_csv('aktor_kanal_yil.csv')
act=['H_ust','H_alt','F','B','K','TCMB','D']
def tab(sel):
  out=pd.DataFrame(index=act)
  out['k1_TL']=[T.loc[sel,'k1_'+a].sum() if 'k1_'+a in T else 0 for a in act]
  out['k2_kur']=[T.loc[sel,'k2_'+a].sum(min_count=1) if 'k2_'+a in T else np.nan for a in act]
  out['toplam_1+2']=out[['k1_TL','k2_kur']].sum(axis=1);return out
pd.set_option('display.width',200)
res={}
res['2014-25']=tab(slice(2014,2025));res['2017-25']=tab(slice(2017,2025))
for y_ in [2018,2019,2021,2022,2023,2024]:res[str(y_)]=tab([y_])
with open('tablo_aktor_kanal.txt','w') as fo:
  for k,v in res.items():
    s=f'== {k} (%GSYH, reel)\n'+v.round(2).to_string()+f'\nΣ: {v.sum().round(3).to_dict()}\n';print(s);fo.write(s)
print(T[['k1_toplam','k2_toplam','k6_H_hisse','pasta']].round(3).to_string())
pd.concat(res,names=['donem','aktor']).to_csv('tablo_aktor_kanal.csv')
# stok
S=(N.NFP.unstack().div(gdp,axis=0)*100).loc[2014:2025];S.to_csv('stok_NFP_gsyh.csv');print('NFP %GSYH\n',S.round(1).to_string())
V=N.hisse.unstack().div(gdp,axis=0).loc[2014:2025]*100;print('net hisse %GSYH\n',V.round(1).to_string())
