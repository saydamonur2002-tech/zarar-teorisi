import pandas as pd,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
b=pd.read_csv('/workspace/zt/butce_ham.csv'); b['yil']=b.Donem.str[:4].astype(int)
gdp=pd.read_csv('/workspace/gec_odeme_efektif_talep/mevduat_tikaniklik/dogrulama/r/aylik_veri.csv');gdp=gdp[gdp.ay.str.endswith('12')];gdp.index=gdp.ay.str[:4].astype(int);gdp=gdp.gsyh_4q
s=lambda c:(b[b.Seri==c].groupby('yil').Deger.sum()/1e3/gdp*100).loc[2014:2025]
print(b[b.Seri.isin(['TP.KB.GEL001','TP.KB.GID001'])][['Seri','Ad']].drop_duplicates())
gel=s('TP.KB.GEL001');gid=s('TP.KB.GID001');fz=s('TP.KB.GID152')
Y=pd.DataFrame({'gelir':gel,'gider':gid,'faiz':fz,'denge':gel-gid,'faizdisi':gel-gid+fz});print(Y.round(2));Y.round(3).to_csv('butce_yil_gsyh.csv')
print('Σ',Y.sum().round(2).to_dict())
S=pd.read_csv('tablo_paylas.csv',index_col=0).drop('TOPLAM')
fig,ax=plt.subplots(1,2,figsize=(14,6))
x=range(len(S));ax[0].bar([i-.2 for i in x],S.S1,.4,label='S1 erteleme (gerçek)');ax[0].bar([i+.2 for i in x],S.S2,.4,label='S2 dondur/tanı [VARSAYIM]')
ax[0].set_xticks(list(x));ax[0].set_xticklabels(S.index,rotation=45,ha='right');ax[0].axhline(0,c='k',lw=.5);ax[0].legend();ax[0].set_title('2014–25 kümülatif net, %GSYH reel')
d=S['S1_eksi_S2(ertelemenin_getirisi)'].sort_values();ax[1].barh(d.index,d,color=['C3' if v<0 else 'C2' for v in d]);ax[1].axvline(0,c='k',lw=.5);ax[1].set_title('Ertelemenin getirisi (S1−S2): + = ertelemeden kazanan')
plt.tight_layout();plt.savefig('paylas.png',dpi=110)
