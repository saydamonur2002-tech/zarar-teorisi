import pandas as pd,json,numpy as np,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
P=10.321+1.477+3.102
c=pd.Series({int(x['date']):x['value'] for x in json.load(open('cons.json'))[1]}).sort_index()
gi=pd.read_csv('wb_tur_dagilim.csv',index_col=0); s40=gi['SI.DST.FRST.20']+gi['SI.DST.02ND.20']
gap=sum((s40[2013]-s40[y])/100*c[y] for y in range(2014,2024) if not np.isnan(s40[y]))
gap25=gap+ (s40[2013]-s40[2023])/100*c[2024]*2  # 2024-25 son değerle [VARSAYIM]
alt_comp=0.845+0.077+6.904*0.215
S2=[('a nötr: gelir payı %16,7',0.167*P,'P×0,167 [VERİ TÜİK 2018 İKİNCİL]'),
('b nüfus payı %40',0.40*P,'P×0,40'),
('c telafi: senyoraj+TL erimesi+Hazine zararının tüketim payı',alt_comp,'0,845+0,077+6,904×0,215 [HESAP/VEKİL]'),
('d alt-40 gelir payını 2013 düzeyinde tutmak',gap25,'Σ(s40_2013−s40_t)×özel tüketim/GSYH [VERİ WB, 2024-25 VARSAYIM]'),
('e WB paylaşılan refah (alt40 büyümesi ≥ ort.)',max(gap25,0.167*P),'≥ max(a,d)'),
('fiili (ANA anahtar)',0.129,'hane3 [HESAP]')]
S3=[('a makine stoku/GSYH 2014 düzeyine (22,6→19,4, 2021)',22.62-19.43,'panel net defter değeri [VEKİL, 2023 kırılması öncesi]'),
('a2 toplam yatırımı emsal ortalamasına',0.0,'TR GSCF/GSYH 29,8 > emsal 22,6 [VERİ WB] → açık yok'),
('b firmaların net kaybını kapatmak',6.822,'eksik tablosu [HESAP]'),
('c 2004-13 büyümesine dönmek: ICOR×Δg×12',6.24*(6.01-4.78)*12,'ICOR 6,24, Δg 1,23 puan [HESAP]'),
('d fiili teşvik: kurumlar vergi harcaması',7.757,'[İKİNCİL]')]
rows=[]
for k,L in (('alt40',S2),('uretim',S3)):
    for n,v,f in L: rows.append((k,n,round(v,2),round(v/P*100,1),f))
t=pd.DataFrame(rows,columns=['soru','olcut','pct_gsyh_kumulatif','havuz_payi_pct','formul']);t.to_csv('menu_alt40_uretim.csv',index=False);print(t.to_string());print('P',P,'gap',gap,gap25)
sp=pd.read_csv('sentetik_placebo.csv',index_col=0)
f,ax=plt.subplots(1,3,figsize=(17,5.5))
yol={2013:0,2014:.5,2015:1.8,2016:.9,2017:5.3,2018:4.2,2019:3.6,2020:11.6,2021:12.2,2022:13.2,2023:15.4,2024:14.9,2025:14.4}
ax[0].plot(list(yol),list(yol.values()),'r-o',label='Türkiye − sentetik (log puan)');ax[0].axhline(0,c='k')
ax[0].set_title('1) Kişi başı reel GSYH: TR − sentetik\nTR üstte (+14), placebo: ayırt edilemez',fontsize=10);ax[0].set_xticks(range(2013,2026,3));ax[0].legend()
q=sp['oran'].sort_values();ax[0].text(2013.2,-3,f"placebo: TR oranı 3,8; |oran|>3,8 olan {int((q.abs()>3.84).sum())}/10 emsal\n→ ayırt edilemez",fontsize=8)
for i,(k,L,col) in enumerate((('alt40',S2,'tab:blue'),('uretim',S3,'tab:green'))):
    s=t[t.soru==k];ax[i+1].barh(s.olcut.str.slice(0,42),s.havuz_payi_pct,color=col);ax[i+1].invert_yaxis()
    for j,(v,g) in enumerate(zip(s.havuz_payi_pct,s.pct_gsyh_kumulatif)):ax[i+1].text(min(v,150)+1,j,f"%{v} havuz | {g} GSYH",va='center',fontsize=8)
    ax[i+1].set_xlim(0,180)
ax[1].set_title(f'2) Alt %40 payı menüsü (havuz P={P:.1f} %GSYH)');ax[2].set_title('3) Üretime pay menüsü (c ölçeği aşar: %%%.0f)'%(t.havuz_payi_pct.iloc[-2]))
plt.tight_layout();plt.savefig('pasta.png',dpi=110)
