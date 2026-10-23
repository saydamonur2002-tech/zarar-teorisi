import csv
R=[
('şehir hastaneleri','(a) bütçe','2025 kira+hizmet ödemesi',111.1,'mlr TL','İKİNCİL (Sağlık Bak. bütçe aktarımı)'),
('şehir hastaneleri','(a) bütçe','2027 teklif: kira 82,2 + hizmet 78,3',160.5,'mlr TL','İKİNCİL (bütçe teklifi aktarımı)'),
('şehir hastaneleri','(a) bütçe','KÖİ sağlık yatırım tutarı',13.80,'mlr $','VERİ SBB'),
('şehir hastaneleri','(a) bütçe','18 hastane 25 yıl kira toplamı (Kalkınma Bak. 2016)',30.2,'mlr $','İKİNCİL'),
('şehir hastaneleri','(b) kullanıcı','katkı payı/fark ücreti','', '','ÖLÇÜLMEDİ'),
('şehir hastaneleri','(c) çalışan','hizmet alımı personeli ücret/istihdam','', '','ÖLÇÜLMEDİ'),
('şehir hastaneleri','(d) şirket','kullanım bedeli talepten bağımsız → talep riski kamuda','', '','VERİ (Sayıştay: kullanım bedeli; eksik iş indirimi yapılmadı)'),
('şehir hastaneleri','(e) döviz','kullanım bedeli enflasyon+döviz bileşenli formül; bazı sözleşmelerde döviz taban/tavan → yabancı para borcu niteliği','', '','VERİ Sayıştay Sağlık Bak.'),
('otoyol/köprü','(a) bütçe','2025 KGM geçiş garantisi ödemesi',85.1,'mlr TL','İKİNCİL (KGM mali durum raporu aktarımı)'),
('otoyol/köprü','(a) bütçe','2026 KGM beklenti',103.2,'mlr TL','İKİNCİL'),
('otoyol/köprü','(a) bütçe','2027 teklif KGM 134,1 + UAB 2,0',136.1,'mlr TL','İKİNCİL'),
('otoyol/köprü','(a) bütçe','KGM garanti ödemeleri 2018–2024 toplam',186.6,'mlr TL','İKİNCİL (TBMM önergesi, Sayıştay atfı)'),
('otoyol/köprü','(a) bütçe','KÖİ karayolu yatırım tutarı',41.85,'mlr $','VERİ SBB'),
('otoyol/köprü','(b) kullanıcı','geçiş ücreti tahsilatı (şirkete)','', '','ÖLÇÜLMEDİ (Bakanlık rakam vermiyor)'),
('otoyol/köprü','(d) şirket','araç geçiş garantisi → talep riski kamuda; Avrasya 2023Q4 sonrası garanti üstü','', '','VERİ Sayıştay KGM/ İKİNCİL'),
('otoyol/köprü','(e) döviz','Osmangazi 35 $/araç, ABD TÜFE endeksli (2025: 55 $), 40 bin araç/gün','', '','İKİNCİL (sözleşme aktarımı)'),
('havalimanları','(a) bütçe','DHMİ YİD garanti ödemesi 2018–2025',1.475,'mlr $','İKİNCİL (önerge, "iddia")'),
('havalimanları','(a) kamu GELİRİ','İHD bedeli toplamı (KDV dahil)',83.47,'mlr $','VERİ SBB (kamuya ödenen kira; net ters yönde)'),
('havalimanları','(b) kullanıcı','yolcu servis/dış hat ücretleri','', '','ÖLÇÜLMEDİ'),
('havalimanları','(e) döviz','yolcu garantisi ve İHD bedeli euro bazlı','', '','DOĞRULANMADI'),
('enerji özelleştirmesi','(a) kamu GELİRİ','üretim+dağıtım satış bedeli 2008–2025',28.3,'mlr $','İKİNCİL (ÖİB aktarımı)'),
('enerji özelleştirmesi','(b) kullanıcı','tarife artışı/kayıp-kaçak bedeli','', '','ÖLÇÜLMEDİ (EPDK tarife serisi çekilmedi)'),
('enerji özelleştirmesi','(c) çalışan','istihdam değişimi','', '','ÖLÇÜLMEDİ'),
('enerji özelleştirmesi','(d) şirket','KÖİ enerji İHD bedeli',23.99,'mlr $','VERİ SBB'),
('limanlar','(a) kamu GELİRİ','TDİ+TCDD liman satış/İHD 1997–2025',3.5,'mlr $','İKİNCİL'),
('limanlar','(b) kullanıcı','liman tarifeleri','', '','ÖLÇÜLMEDİ'),
]
csv.writer(open('maliyet_kim.csv','w')).writerows([['kalem','tasiyici','aciklama','tutar','birim','etiket']]+R)
S=[('Sağlık Bak.','KÖİ şehir hastanelerinde görevli şirkete verilen garanti tutarları nazım hesaplarda/dipnotta muhasebeleştirilmedi','VERİ Sayıştay (DW aktarımı)'),
('Sağlık Bak.','KÖİ projelerine dair kısa/uzun vadeli mali yükümlülükler Mali Borçlar hesap gruplarına kaydedilmedi','VERİ Sayıştay rapor metni'),
('Sağlık Bak.','Kira ödemeleri hatalı muhasebeleştirildi; 630 Giderler hesabı aracı hesap olarak kullanıldı','VERİ Sayıştay'),
('Sağlık Bak.','Ek-13 ekipmanlar (teslim edilen taşınırlar) kaydedilmedi','VERİ Sayıştay'),
('Sağlık Bak. 2025','17 hastanede mali kapatma/kesin hesap 2+ yıldır yok; eksik işler ve KDV istisnası kira indirimine yansıtılmadı; enerji giderleri düşülmedi','İKİNCİL (Memurlar.net, Sayıştay 2025 aktarımı)'),
('KGM','Talep garantileri "vazgeçilen gelir" olarak izlenmeli; yabancı para işlemler TCMB kuruyla değerlenmeli','VERİ Sayıştay KGM 2022 (arama özeti)'),
('Sağlık Bak. 2021','Dış proje kredisi kur değerlemesi yapılmadı','VERİ Sayıştay')]
csv.writer(open('sayistay_bulgu.csv','w')).writerows([['idare','bulgu','etiket']]+S)
a=111.1+85.1
print('2025 bütçe nakdi KÖİ:',a,'hastane payı',round(111.1/a*100,1),'KGM',round(85.1/a*100,1))
import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
K=['şehir hastaneleri','otoyol/köprü','havalimanları','enerji özelleştirmesi','limanlar'];T=['(a) bütçe','(b) kullanıcı','(c) çalışan','(d) şirket','(e) döviz']
st={'ölçüldü':'#2a7','ÖLÇÜLMEDİ':'#ccc','kamu geliri':'#58c','DOĞRULANMADI':'#fc6'}
fig,ax=plt.subplots(1,2,figsize=(14,4.5))
for i,k in enumerate(K):
 for j,t in enumerate(T):
  rr=[r for r in R if r[0]==k and r[1].startswith(t[:3])]
  c='#fff' if not rr else ('#ccc' if all('ÖLÇÜLMEDİ' in r[5] for r in rr) else '#58c' if any('GELİRİ' in r[1] for r in rr) else '#fc6' if all('DOĞRULANMADI' in r[5] for r in rr) else '#2a7')
  ax[0].add_patch(plt.Rectangle((j,len(K)-1-i),1,1,fc=c,ec='k'))
ax[0].set_xlim(0,5);ax[0].set_ylim(0,5);ax[0].set_xticks([x+.5 for x in range(5)]);ax[0].set_xticklabels(T,rotation=20);ax[0].set_yticks([y+.5 for y in range(5)]);ax[0].set_yticklabels(K[::-1]);ax[0].set_title('yeşil: tutar/hüküm var, gri: ölçülmedi, mavi: kamu geliri, sarı: doğrulanmadı')
ax[1].bar(['2025','2027 teklif'],[111.1,160.5],label='şehir hastanesi');ax[1].bar(['2025','2027 teklif'],[85.1,136.1],bottom=[111.1,160.5],label='otoyol/köprü garanti');ax[1].set_title('KÖİ bütçe nakdi, mlr TL (İKİNCİL)');ax[1].legend()
plt.tight_layout();plt.savefig('maliyet_kim.png',dpi=110)
