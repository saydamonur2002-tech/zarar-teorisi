import pandas as pd,numpy as np
Y=list(range(2013,2026))
ws=pd.Series([43.32025,43.56054,43.97291,47.38013,44.74561,43.25307,44.62912,41.48331,37.91075,33.11055,40.0927,46.2386,46.32076],Y)  # AMECO ALCD0 [VERİ]
gdp=pd.Series([1831.74397,2062.35818,2354.05913,2629.98797,3151.52915,3806.47922,4402.05031,5141.7106,7433.79991,15325.85749,27091.46907,44587.22544,63020.90582],Y)*1e9  # AMECO UVGD
fa=pd.read_csv('/workspace/zt/finansal_hesaplar_uzun.csv');fa=fa[fa.Donem.str.endswith('Q4')];fa['zp']=fa.Seri.str.extract(r'ZP(\d+)$')[0].astype(int);fa['yil']=fa.Donem.str[:4].astype(int)
D=lambda h:fa[(fa.Hazne==h)&(fa.zp==34)].groupby('yil').Deger.sum().reindex(Y)
DH,DF=D('H')*1e3,D('F')*1e3  # bin TL
print((DH/gdp*100).round(2).to_dict());print((DF/gdp*100).round(2).to_dict())
yy=range(2015,2026)
gap=(ws-ws[2014]).loc[yy]
A_w_net=gap.sum();A_w_brut=gap[gap<0].sum()
def B(Ds):
  fl=(Ds.diff()/gdp*100).loc[yy];return fl.sum(),(Ds/gdp*100)[2025]-(Ds/gdp*100)[2014],fl
BH,BHs,flH=B(DH);BF,BFs,flF=B(DF)
# BDDK composition 2019-25
b=pd.read_csv('/workspace/gec_odeme_efektif_talep/reel_ucret/tamamla/bddk_tuketici.csv');b=b[b.period.str.endswith('-12')|(b.period=='2019-01')]
g=lambda s:b[b.BasitSira==s].set_index('period').Total
kon=g(2)+g(6);tuk=g(3)+g(4)+g(7)+g(8)+g(9)
dk=kon['2025-12']-kon['2019-01'];dt=tuk['2025-12']-tuk['2019-01'];pay_tuk=dt/(dk+dt)
# per-year consumption-credit real growth
yr=pd.Series({int(p[:4]):v for p,v in tuk.items() if p.endswith('-12')})
infl=pd.read_csv('/workspace/grafik5/mevduat/makro_yil.csv',index_col=0)['infl']
tg=(np.log(yr).diff()*100-np.log1p(infl/100)*100).dropna()
dws=ws.diff().reindex(tg.index);kor=np.corrcoef(dws,tg)[0,1]
# keys
Kg=np.array([.167,.357,.476]);Kt=np.array([.215,.411,.374])
yay=np.array([(27.5+32)/2,(34+32.1)/2,35.4]);Kb=yay*Kg;Kb=Kb/Kb.sum()   # İKİNCİL yaygınlık × gelir [VEKİL]
Afin=np.array([-0.077-0.845,-0.163-1.613,-0.882-1.467])  # hane3 ANA k1+k5
rows=[]
for nm,Kd in [('ANA_Kborc',Kb),('duy_Ktuketim',Kt),('duy_Kgelir',Kg)]:
  for i,gr in enumerate(['alt40','orta40','ust20']):
    Aw=A_w_net*Kg[i];Awb=A_w_brut*Kg[i];A=Aw+Afin[i];Bq=BH*Kd[i]
    rows.append(dict(set=nm,aktor='H_'+gr,A_ucret_net=Aw,A_ucret_brut=Awb,A_finans=Afin[i],A_top_net=A,A_top_brut=Awb+Afin[i],B_akim=Bq,kayis_net=Bq/abs(A),kayis_brut=Bq/abs(Awb+Afin[i])))
At=A_w_net+Afin.sum();Atb=A_w_brut+Afin.sum()
rows.append(dict(set='ANA',aktor='H_toplam',A_ucret_net=A_w_net,A_ucret_brut=A_w_brut,A_finans=Afin.sum(),A_top_net=At,A_top_brut=Atb,B_akim=BH,B_stok=BHs,kayis_net=BH/abs(At),kayis_brut=BH/abs(Atb)))
rows.append(dict(set='ANA',aktor='Firma',A_top_net=-10.58,A_finans=-10.58,B_akim=BF,B_stok=BFs,kayis_net=BF/10.58,A_ucret_net=-A_w_net,A_ucret_brut=-A_w_brut))
R=pd.DataFrame(rows);R.to_csv('tablo_borc.csv',index=False);print(R.round(2).to_string())
pd.DataFrame({'ws':ws,'gap':ws-ws[2014],'H_akim':flH,'F_akim':flF,'H_stok':DH/gdp*100,'F_stok':DF/gdp*100}).to_csv('yil_borc.csv')
print('Aw',A_w_net,A_w_brut,'BH',BH,BHs,'BF',BF,BFs,'pay_tuk',pay_tuk,dk,dt,'kor',kor,len(tg),'Kb',Kb)
print(tg.round(1).to_dict(),dws.round(1).to_dict())
pi=(infl/100).reindex(Y)
rf=lambda Ds:((Ds.diff()-pi*Ds.shift())/gdp*100).loc[yy]
rH,rF=rf(DH),rf(DF);print('reel akım H',rH.sum(),'F',rF.sum());print(rH.round(2).to_dict())
R['B_reel_akim']=np.nan
for i,gr in enumerate(['alt40','orta40','ust20']):
  for nm,Kd in [('ANA_Kborc',Kb),('duy_Ktuketim',Kt),('duy_Kgelir',Kg)]:
    R.loc[(R.set==nm)&(R.aktor=='H_'+gr),'B_reel_akim']=rH.sum()*Kd[i]
R.loc[R.aktor=='H_toplam','B_reel_akim']=rH.sum();R.loc[R.aktor=='Firma','B_reel_akim']=rF.sum()
R['kayis_reel']=R.B_reel_akim/R.A_top_net.abs();R.to_csv('tablo_borc.csv',index=False)
Yd=pd.read_csv('yil_borc.csv',index_col=0);Yd['H_reel']=rH;Yd['F_reel']=rF;Yd.to_csv('yil_borc.csv')
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
f,ax=plt.subplots(1,2,figsize=(13,5))
x=np.array(list(yy));ax[0].bar(x-.2,gap.values,.4,label='Ücret payı farkı (2014=0) [VERİ AMECO]');ax[0].bar(x+.2,rH.values,.4,label='Hane reel net yeni borç [HESAP]')
ax[0].plot(x,(DH/gdp*100).loc[yy].values,'k-o',label='Hane borcu/GSYH (stok)');ax[0].axhline(0,c='gray');ax[0].set_title('Haneler: ücret kaybı vs borç (% GSYH)');ax[0].legend(fontsize=8)
S=R[R.set=='ANA_Kborc'];g3=['alt40','orta40','ust20'];xx=np.arange(3)
ax[1].bar(xx-.25,-S.A_top_net,.25,label='|A| kayıp (ücret net + finans)');ax[1].bar(xx,S.B_akim,.25,label='B nominal net yeni borç');ax[1].bar(xx+.25,S.B_reel_akim,.25,label='B reel (enflasyon erimesi düşülmüş)')
ax[1].set_xticks(xx,g3);ax[1].axhline(0,c='gray');ax[1].set_title('2015-25 toplam, % GSYH; anahtarlar VEKİL');ax[1].legend(fontsize=8)
plt.tight_layout();plt.savefig('borc.png',dpi=110)
