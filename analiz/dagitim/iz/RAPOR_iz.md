# RAPOR_iz — firma ücret kazancının izi + emekli/asgari ücret/göç (2015-25, %GSYH, 2014 düzeyine göre fark, kümülatif)
Ön kayıt: ON_KAYIT_iz.md (17:23 TSİ). Sapma: SAPMA_iz.md. Kod iz.py; seriler_iz.csv, tablo_iz.csv, ozet.json, iz.png.
## +10,03 nereye
| Kullanım | Kümülatif fark | Etiket |
|---|---|---|
| Yurt dışına DY geliri (kâr payı+yeniden yatırılan kazanç+DY faizi) | 1,85 | VERİ/VEKİL |
| Yurt dışına portföy geliri (hisse kâr payı+tahvil faizi, kamu dahil) | 2,02 | VERİ/VEKİL |
| Yurt dışına faiz, firmalar (diğer sektör UV + tüm KV) | 1,55 | VERİ/VEKİL |
| **Yurt dışı toplam** | **5,42** | HESAP |
| Vergi (gelir+kâr, bireysel dahil) | 3,37 | VEKİL |
| Kalan: yurtiçi banka faizi, yurtiçi temettü, yatırım, ölçülmeyen | 1,24 | HESAP |
Zamanlama uyuşmuyor: ücret kazancı 2020-23'te 21,6 puan, aynı yıllarda yurt dışı çıkış farkı 1,8; yıllık korelasyon −0,12. 2024-25'te ücret payı 2014'ün üstünde. Kümülatif eşleşme büyük ölçüde aritmetik [aday zayıf].
## Kriterler
K1 yurt dışı ≥5: 5,42 → TUTTU (sınırda; portföy satırı kamu tahvil faizini içeriyor, çıkarılırsa büyük olasılıkla <5).
K2 artık farkı: net birincil gelir çıkışı fazlası 4,17 / 3,85 = 1,08 → TUTTU [aday]; ama yıllık iz tutmuyor ve artık değerleme/stok kavramı, gelir akımı farklı kavram.
K3: yeni hesap yok (pasta/: makine 14,6→11 VEKİL, nedensel değil).
K4 emekli: OECD SOCX yaşlılık+dul nakit %GSYH 7,08 (2014) → 6,08 (2021): uç nokta −1,0 → TUTTU; ama 2015-20 hep 2014 üstünde, kümülatif fark +0,63 (daha fazla harcama). Uç noktaya bağlı, kırılgan. Reel ortalama aylık ÖLÇÜLMEDİ. SGK 2024 ödeme ≈ GSYH'nin %6,1'i [İKİNCİL].
K5 asgari ücret sıkışması: OECD asgari/ortalama 39,3 (2014) → 26,9 (2025); asgari/medyan 69 → 47 → TUTMADI (tersine açılma). Uyarı: OECD 2023-25 ortalama ücretleri tahmin içerebilir [DOĞRULANMADI]. Kayıt dışı istihdam (ILO) 36,3 → 26,6.
K6 göç: ÖLÇÜLEMEDİ. İkincil: 2024'te 151 bin vatandaş göç etti; lisans mezunu beyin göçü oranı %2 (2023, 2024) [İKİNCİL]; beşeri sermaye kaybı hesaplanmadı (savunulabilir değil).
## Güncel zarar havuzu sıralaması
1 Yurt dışına gelir çıkışı fazlası 4,2-5,4 (VERİ, artık farkını kümülatif kapatıyor, zamanlama uymuyor) · 2 Eğitim 2,6 (zarar/) · 3 Emekli: uç noktada −1,0 puan/yıl, kümülatif yok · 4 Asgari ücret sıkışması: yok · 5 Göç: ölçülemedi.
Kaynak: TCMB ödemeler dengesi Tablo 4 (eksik/ham/bop.txt), World Bank WDI API, AMECO (borc/), OECD SDMX (MIN2AVE, SOCX), ILO SDMX (EMP_NIFL). EVDS/EVDS3 bu turda kullanılmadı. Repoya yazılmadı. Nedensellik iddiası yok.
