import re,json,pandas as pd,numpy as np,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
def am(v):
    s=open(f'ham/{v}.html').read();vals=re.findall(r'<td formula="(?:=NA\(\)|[^"]*)">([^<]*)</td>',s)
    return pd.Series([float(x) if x else np.nan for x in vals],range(2000,2026))
def wb(i):
    d=json.load(open(f'ham/wb_{i}.json'))[1];return pd.Series({int(r['date']):r['value'] for r in d}).sort_index()
G,I,C,Gg,K=am('UVGD'),am('UIGT'),am('UKCT'),am('UIGG0'),am('OKND')
ni=(I-C)/G*100; pi=Gg/G*100
A=lambda s,a,b:s.loc[a:b].mean()
r={}
r['net_yat_0413']=A(ni,2004,2013);r['net_yat_1424']=A(ni,2014,2024)
r['eksik_net_yat_kum_1424']=((r['net_yat_0413']-ni.loc[2014:2024])).sum()
r['kamu_yat_0413']=A(pi,2004,2013);r['kamu_yat_1425']=A(pi,2014,2025)
r['kamu_yat_eksik_kum']=(r['kamu_yat_0413']-pi.loc[2014:2025]).sum()
pc=wb('NY.GDP.PCAP.KD');ed=wb('SE.XPD.TOTL.GD.ZS');he=wb('SH.XPD.GHED.GD.ZS')
r['egitim_reel_kb_2022_vs_2014_%']=(ed[2022]*pc[2022]/(ed[2014]*pc[2014])-1)*100
r['egitim_eksik_kum_vs2014pay']=(ed[2014]-ed.loc[2015:2022]).sum()
r['saglik_reel_kb_2023_vs_2014_%']=(he[2023]*pc[2023]/(he[2014]*pc[2014])-1)*100
r['saglik_eksik_kum_vs2014pay']=(he[2014]-he.loc[2015:2023]).sum()
r['ArGe_2014,2023']=(wb('GB.XPD.RSDV.GD.ZS')[2014],wb('GB.XPD.RSDV.GD.ZS')[2023])
n=wb('SL.UEM.NEET.ZS');r['NEET_2014,2025']=(n[2014],n[2025])
r['artik_fark']=3.1-(-0.75)
r['OKND_buyume_0913,1424']=((K[2013]/K[2009])**.25-1,(K[2024]/K[2014])**.1-1)
for k,v in r.items():print(k,np.round(v,2))
pd.DataFrame({'net_yatirim_gsyh':ni,'kamu_yatirim_gsyh':pi,'egitim_gsyh':ed,'saglik_kamu_gsyh':he,'NEET':n}).loc[2004:2025].round(2).to_csv('seriler_zarar.csv')
f,ax=plt.subplots(1,2,figsize=(12,4.5))
ax[0].plot(ni.loc[2004:2024],label='Net yatırım/GSYH (AMECO) [HESAP]');ax[0].plot(pi.loc[2004:2025],label='Kamu yatırımı/GSYH [HESAP]')
ax[0].plot(ed.dropna(),label='Eğitim/GSYH (WB) [VERİ]');ax[0].plot(he.dropna(),label='Kamu sağlık/GSYH (WB) [VERİ]')
ax[0].axvline(2013.5,c='k',ls=':');ax[0].legend(fontsize=7);ax[0].set_title('Seriler, % GSYH')
lab=['Net yatırım açığı','Kamu yatırımı açığı','Eğitim açığı','Sağlık açığı']
val=[r['eksik_net_yat_kum_1424'],r['kamu_yat_eksik_kum'],r['egitim_eksik_kum_vs2014pay'],r['saglik_eksik_kum_vs2014pay']]
ax[1].barh(lab,val,color='firebrick');ax[1].axvline(0,c='k');ax[1].set_title('Kümülatif açık, GSYH puanı (+ = eksik)')
for i,v in enumerate(val):ax[1].text(v,i,f' {v:.1f}',va='center')
plt.tight_layout();plt.savefig('zarar.png',dpi=110)
pd.Series({k:str(np.round(v,3)) for k,v in r.items()}).to_csv('ozet_zarar.csv')
