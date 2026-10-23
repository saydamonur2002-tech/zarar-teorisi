import csv
oib=[('1986-2003 toplam',8.2,'İKİNCİL'),(2005,3.04,'İKİNCİL'),(2008,1.341,'İKİNCİL'),(2013,12.4,'İKİNCİL'),(2017,.751,'İKİNCİL'),(2018,1.3,'İKİNCİL'),(2019,.116,'İKİNCİL'),(2020,.022,'İKİNCİL'),(2021,.413,'İKİNCİL'),(2022,.504,'İKİNCİL'),(2023,.181,'İKİNCİL'),(2024,.122,'İKİNCİL'),(2025,round(73.5-71.6,1),'HESAP: 73,5−71,6')]
sek=[('enerji üretim+dağıtım (2008–2025)',28.3,'mlr$ İKİNCİL'),('limanlar (1997–2025)',3.5,'mlr$ İKİNCİL'),('KÖİ yatırım: karayolu',41.85,'mlr$ VERİ SBB'),('KÖİ yatırım: havalimanı',25.78,'mlr$ VERİ SBB'),('KÖİ yatırım: enerji',22.93,'mlr$ VERİ SBB'),('KÖİ yatırım: sağlık (YKD, şehir hastanesi)',13.80,'mlr$ VERİ SBB')]
koi=[(2025,85.1,111.1,'gerçekleşme İKİNCİL'),(2026,103.2,150.0,'KGM beklenti; hastane 150 TAHMİN (basın)'),(2027,134.1+2.0,82.2+78.3,'bütçe teklifi İKİNCİL'),(2028,165.2+2.2,97.4+89.7,'bütçe tahmini'),(2029,167.9+2.5,113.1+98.2,'bütçe tahmini')]
# kriz_zaman orta: (oran-20)%*gelir
Y=list(csv.DictReader(open('../kriz_zaman/yollar.csv')))
gap=[]
for r in Y:
  if r['senaryo']=='orta' and r['plan']=='S1 erteleme' and r['ceyrek'].endswith('Q4'):
    y=int(r['ceyrek'][:4]);rev=16266.1*1.30**(y-2026);g=max(0,float(r['kamu_faiz_gelir'])-20)/100*rev
    gap.append((y,float(r['kamu_faiz_gelir']),round(rev),round(g)))
cap={'2025 gerçekleşme 74,4':74.4,'OVP 2026 hedefi 185':185}
w=csv.writer(open('ozellestirme.csv','w'))
w.writerow(['blok','kalem','deger','etiket']);[w.writerow(['ÖİB yıllık mlr$',a,b,c]) for a,b,c in oib];[w.writerow(['kırılım/KÖİ',a,b,c]) for a,b,c in sek]
[w.writerow(['KÖİ ödemesi mlrTL',y,round(a+b,1),f'KGM+ulaştırma {a:.1f}, hastane {b:.1f}; {c}']) for y,a,b,c in koi]
for y,k,rv,g in gap:
  w.writerow(['kamu açığı (oran−20)×gelir',y,g,f'oran {k}, gelir {rv} [HESAP]'])
  for n,c in cap.items(): w.writerow(['kapsama oranı',f'{y} {n}',round(c/g,2) if g else 'açık yok','HESAP'])
print(gap)
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
fig,ax=plt.subplots(1,3,figsize=(15,4.3))
yy=[o for o in oib if o[0]!='1986-2003 toplam'];ax[0].bar([str(o[0]) for o in yy],[o[1] for o in yy]);ax[0].set_title('ÖİB uygulama, mlr $ (eksik yıllar boş)');ax[0].tick_params(axis='x',rotation=60)
ax[1].bar([k[0] for k in koi],[k[1] for k in koi],label='karayolu/ulaştırma garanti');ax[1].bar([k[0] for k in koi],[k[2] for k in koi],bottom=[k[1] for k in koi],label='şehir hastanesi');ax[1].set_title('KÖİ bütçe ödemesi, mlr TL nominal');ax[1].legend()
ax[2].plot([g[0] for g in gap],[g[3] for g in gap],'o-',c='r',label='kapatılacak kamu açığı (orta)');ax[2].axhline(185,ls='--',label='OVP 2026 özelleştirme 185');ax[2].axhline(74.4,ls=':',label='2025 özelleştirme 74,4');ax[2].set_title('mlr TL/yıl');ax[2].legend(fontsize=8)
plt.tight_layout();plt.savefig('ozellestirme.png',dpi=110)
