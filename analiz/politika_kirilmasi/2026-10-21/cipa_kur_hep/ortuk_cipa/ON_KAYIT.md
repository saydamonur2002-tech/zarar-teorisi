# ON_KAYIT — "O çıpa neydi?" (örtük çıpa), 2013-01..2016-10
Yazıldı 2026-10-21 ~13:30 TSİ, hesaptan önce. Veri: ../tr_aylik.csv, ../br_aylik.csv (EVDS3 anahtarsız web ön yüzü — BEYAN; BCB SGS/Olinda). EVDS_API_KEY okunmaz. Nedensellik yok; haber sayısı yok.
## A1 Sabit örtük düzey
b24, b12 ortalama, HAC %95 GA, std, min-max; ADF (H0 birim kök) ve KPSS (H0 düzey durağan).
AYAKTA: ADF p<0,05 VE KPSS p>0,05 VE std < geçmiş 12 ay enflasyon std'nin yarısı. YANLIŞ: ADF p>0,10 ve KPSS p<0,05.
## A2 TCMB Enflasyon Raporu tahmini
Her raporun (Oca/Nis/Tem/Eki) yıl sonu ve bir sonraki yıl sonu tahmini (birincil TCMB metni). Ölçü: |b12 − ilgili TCMB tahmini| vs |b12 − 5| ortalaması; olay penceresi: rapor ayı ile önceki ay arasında Δb12'nin, (yeni tahmin − eski tahmin) değişikliğiyle işaret uyumu.
AYAKTA: ortalama uzaklık tahmine <%5'e VE revizyon yönüyle işaret uyumu ≥%70. Birincil metin yoksa [DOĞRULANMADI].
## A3 Geçmiş enflasyon
b − π̄12 (son 12 ay yıllık TÜFE) ortalaması/GA; b'nin π̄'ye regresyonu eğimi (HAC). AYAKTA (yapışkan geçmişe bağlı): eğim GA 1'i içeriyor ve |ortalama fark|<0,5. YANLIŞ: eğim üst GA <0,5.
## A4 Belirsizlik bandı üst sınırı %7
Ortalama b24 GA'sı 7'yi içeriyor mu; ay payı b24∈[6,5;7,5]. AYAKTA: GA 7'yi içeriyor VE pay ≥%70.
## A5 Brezilya: aynı A1, A3, A4 (üst band 6,5) 12 ay Focus, aynı dönem ve 2005–2010.
## Kayma: b24 düzeyinin 12 aylık kayan ortalaması + ruptures/kayan ortalama; dönem ortalamaları 2013-01..2016-10, 2016-11..2018-07, 2018-08..2021-08, 2021-09..2023-06, 2023-07+.
## SAPMALAR (hesap sonrası)
- S1: A2 için 12 ay ilerisi tahmini, yıl sonu ve sonraki yıl sonu orta noktalarından doğrusal ara değerle (F12) kuruldu [HESAP/VEKİL]; b24 ise "sonraki yıl sonu" orta noktasıyla kıyaslandı. Rapor yayım günü yerine rapor ayı; olay penceresi Δb12 = b12(ay+1) − b12(ay−1).
- S2: 2015-II ve 2015-III'te değerler güncelleme cümlesinden alındı (er/*.txt); diğerleri "orta noktası" cümlesi. Kaynak: tcmb.gov.tr ER tam metin PDF'leri (birincil).
- S3: A5'te Brezilya için A2 (BCB Relatório) yapılmadı.
- S4: Δb12 işaret uyumu, dönemdeki yukarı eğilim nedeniyle pozitif yanlı olabilir; ek kontrol yapılmadı.
