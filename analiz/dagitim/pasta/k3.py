import pandas as pd,numpy as np
d=pd.read_csv('../../toprak/panel_sektor.csv',dtype={'nace':str})
d=d[~d.nace.isin(['41','42','43','68'])]
a=d.groupby('yil')[['makine','aktif','arazi','bina','satis']].sum()
a['makine_aktif']=a.makine/a.aktif*100; a['bina_arazi_aktif']=(a.bina+a.arazi)/a.aktif*100
print(a[['makine_aktif','bina_arazi_aktif']].round(2))
a[['makine_aktif','bina_arazi_aktif']].to_csv('panel_makine_payi.csv')
p=d.pivot(index='nace',columns='yil',values='finS'); m=d.pivot(index='nace',columns='yil',values='makine')/d.pivot(index='nace',columns='yil',values='aktif')
def test(sy,o0,o1):
    x=(p[sy]-p[sy-1]); y=np.log(m[o1]/m[o0]); k=x.notna()&y.notna()&np.isfinite(y); x,y=x[k],y[k]
    x=x.clip(x.quantile(.05),x.quantile(.95))
    b=np.polyfit(x,y,1)[0]; rng=np.random.default_rng(0)
    pm=np.array([np.polyfit(rng.permutation(x.values),y.values,1)[0] for _ in range(2000)])
    return b,(np.abs(pm)>=abs(b)).mean(),len(x)
r=[('ana_2018->2018-20',*test(2018,2018,2020)),('placebo_2016->2016-17',*test(2016,2016,2017)),('ters/öncül_2018->2016-17',*test(2018,2016,2017)),('2021->2021-23',*test(2021,2021,2023))]
r=pd.DataFrame(r,columns=['test','egim','perm_p','n']);print(r);r.to_csv('k3_sektor_test.csv',index=False)
