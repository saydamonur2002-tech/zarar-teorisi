import pandas as pd,statsmodels.api as sm,numpy as np
d=pd.read_csv('yillik_2005_2025.csv'  # yerel veri, repoda yok (ham/KAYNAKLAR.md),index_col=0)
d['infl_l']=d.infl.shift(1);X=['infl','infl_l','ip_g','kredi_reel_g'];s=d[['npl_wb']+X].dropna()
m=sm.OLS(s.npl_wb,sm.add_constant(s[X])).fit(cov_type='HAC',cov_kwds={'maxlags':2})
b=(m.params.infl+m.params.infl_l)/100;V=m.cov_params();se=np.sqrt(V.loc['infl','infl']+V.loc['infl_l','infl_l']+2*V.loc['infl','infl_l'])/100
o=[f'NPL: 1 puan enflasyon ↑ → NPL {b:+.3f} puan [%95 {b-1.96*se:+.3f}; {b+1.96*se:+.3f}], n={len(s)}']
# alt dönem (2022-24 hariç) sağlamlık
s2=s[s.index<2022];m2=sm.OLS(s2.npl_wb,sm.add_constant(s2[X])).fit(cov_type='HAC',cov_kwds={'maxlags':2})
o.append(f'  2006-2021: {(m2.params.infl+m2.params.infl_l)/100:+.3f} puan/puan')
kredi=28636.8;kars=.743;ic_tl=7748.0;tic_tl=11260.7
rep=[.66,1,1,1,1];fak=np.mean(rep)  # HMB: 12 ayda yenilenecek pay %66 (Ağu-2026), kalan ort. vade 2,5 yıl → ~2. yıldan tam [VARSAYIM]
o.append(f'Hazine yeniden fiyatlama faktörü 5 yıl ort. {fak:.2f}')
S={'1/3':(1/3,1/3,1/3),'20-40-40':(.2,.4,.4),'50-25-25':(.5,.25,.25),'40-30-30':(.4,.3,.3)}
for dp in (1.2,3.5):
  dnpl=b*(-dp);bank=-dnpl*kredi*kars/100   # NPL artarsa banka gelir eksi
  lo,hi=[-(x*(-dp))*kredi*kars/100 for x in (b-1.96*se,b+1.96*se)]
  o.append(f'\nYol −{dp} puan: NPL {dnpl:+.2f} puan → banka gelir {bank:.0f} mlr [{min(lo,hi):.0f};{max(lo,hi):.0f}]')
  for r in (0,.2,.5):
    hz=ic_tl*r/100*fak;fr=tic_tl*r/100
    for k,sh in S.items():
      n=[hz-sh[0]*38.7,fr-sh[1]*38.7,bank-sh[2]*38.7]
      o.append(f'  r={r} {k}: devlet {n[0]:.1f} / firma {n[1]:.1f} / banka {n[2]:.1f}')
  o.append(f'  bankayı başabaşa getiren devlet transferi (40-30-30): {-(bank-.3*38.7):.0f} mlr TL/yıl')
open('cikti.txt','w').write('\n'.join(o));print('\n'.join(o))
