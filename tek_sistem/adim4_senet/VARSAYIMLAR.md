# Adım 4 senet ve paylaşım — varsayımlar (2026-10-21)

Duyarlılık: Y = kararı değiştirebilir, O = sayıları belirgin değiştirir ama kararı değiştirmez, D = düşük.

| Kod | Açıklama | Değer/aralık | Dayanak | Duyarlılık | Nasıl ölçülür |
|---|---|---|---|---|---|
| V1 | Adres stoktan senede kayma oranı | %2 / 5 / 10 (19.361 mlr TL) | VARSAYIM (stoklar VERİ: TEK_SISTEM_KOPRU) | O | KKM giriş hızı, TÜFE'ye endeksli DİBS ihale talebi (HMB) |
| V2 | Hedef tutunca ek prim | %0,5 / 1 / 2 | VARSAYIM | O (prim yükü 1,9–38,7) | Tasarım parametresi; ihale talebiyle kalibre |
| V3 | Senetin atalet etkisi (ρ_son) | 0,59 / 0,55 / 0,45 → 2031 %12,9 / 11,7 / 9,4 | VARSAYIM (denklem HESAP) | Y | Endeksleme sözleşmelerinin hedefe geçiş oranı; ücret/kira endeks verisi |
| V4 | Enflasyon risk primi düşüşü | 0 / 0,2 / 0,5 puan | VARSAYIM — ölçülemedi (FRED blok, OECD'de TR uzun getiri yok) | Y (r=0'da tüm modeller eksi) | 10y DİBS getirisi − PKA 12 ay beklenti − reel faiz vekili; CDS; TCMB/BIS |
| V5 | NPL ~ enflasyon katsayısı (işaret) | −0,068 (2006–24) / +0,119 (2006–21) puan/puan | HESAP (yıllık WB NPL, n=18) | Y (banka netinin işaretini belirler) | Aylık BDDK NPL + reel faiz kontrolü, 2006+ |
| V6 | Mevduat kaymasında banka fonlama maliyet farkı | 0–3 puan | VARSAYIM | O–Y (C modelinde destek 3,9–58,1 mlr) | Mevduat vs repo/TCMB fonlama faizi farkı (TCMB, BDDK) |
| V7 | Hazine yeniden fiyatlama | yıl1 %66, sonrası tam (5 yıl ort. 0,93) | %66 VERİ (HMB Ağu-2026), sonrası VARSAYIM | D | HMB itfa takvimi |
| V8 | Banka payının kredi faizine yansıması | %0 / 50 / 100 (≤4 bp) | VARSAYIM | D | BDDK kredi faizi – fonlama marjı izlemesi |
| V9 | Firma katılım oranı | %10 / 30 / 60 | VARSAYIM | Y (%10'da katılan firma eksi) | E-fatura kayıtlı firmaların pilot katılımı (GİB) |
| V10 | Firma kazancının dağılımı (bedava binici) | Kazanç kredi payına göre tüm firmalara yayılır | VARSAYIM | Y | Katılımcıların ticari kredi payı (BDDK/KKB) |
| V11 | Paylaşım oranları | 1/3, 20-40-40, 50-25-25, 40-30-30, 50-50 | VARSAYIM — 40-30-30 hesaba dayanmaz | O | Katılım kısıtlarından türetilmeli |
| V12 | Bağımsız TÜFE eşiği | e-fatura fiyat endeksi − TÜFE ≤1 puan | VARSAYIM (tasarım) | O | E-fatura fiyat endeksi kurulumu |
| V13 | İhraç tavanı | 1.936 mlr TL (adres stokun %10'u, iç borcun ≤%20'si) | HESAP (V1'den) | O | Tasarım parametresi |
| V14 | BDDK mevduat ve NPL | 32.365 / 915 mlr TL, %3,09 (2 Eki 2026) | İKİNCİL (birincil sekme JS) | D | BDDK haftalık/aylık bülten birincil |
| V15 | Reel kazanç tanımı (Fisher) | Nominal faiz düşüşü reel kazanç değil | VARSAYIM (teori) | Y | — |
| V16 | Firma reel kazancı = TL ticari kredi × r | 11.261 mlr TL | VERİ (BDDK 2 Eki) + VARSAYIM | O | — |
| V17 | Bütçe kuralı | faiz dışı denge ≥0 | VARSAYIM (tasarım) | O | MYP/bütçe gerçekleşmeleri |
| V18 | Tarihsel benzerler (TR DİBS, Şili UF, İsrail, Brezilya URV, Pacto, 1985) | yorum | İKİNCİL/DOĞRULANMADI | O | Birincil seriler |
| V19 | B modeli banka payı | NPL kazancının %30'u | VARSAYIM | D | — |

En duyarlı üç: V4 risk primi, V5 NPL işareti, V9/V10 firma katılımı ve bedava binici.
