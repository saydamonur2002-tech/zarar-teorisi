# Sapma kaydı

Ön kayıt `ON_KAYIT.md`. Koşu: `python3 zararin_muhasebesi/test_sfc_muhasebe.py` geçti. `python3 zararin_muhasebesi/build_page.py` geçti.

## Sayısal kriter

S0–S7 ve Tek Sistem paketi (kötümser / olası / iyimser, baz ve dış şok) `once_ozet.json` ile mutlak fark `< 1e-6`. **SAPMA yok.**

Zombi kapalı yönü tuttu (**aday**, model içi karşı-olgu): S4z reel GSYH endeksi 100,7 > S4 69,6. Tanımanın üretim avantajı 25,3 puandan 5,7 puana indi. Veri karşı-olgusu yok; bu bir nedensel tahmin değildir.

Açılış: finansal satır toplamı `2e-15` tn TL. Kesim net serveti − `pK` = `3e-14`. Banka net serveti = `BANKA_OZKAYNAK_TN` (4,65). Koşu hatalarının en büyüğü: gizli denklem `1,0e-12`, stok–akım `1,0e-12`, bilanço `1,1e-11` tn TL. Eşik `1e-8`. **SAPMA yok.**

Ön kayıttaki sermaye satırı cümlesi koşudan önce düzeltildi (sabit sermaye `pK`'ya toplanır). Sonuç görüldükten sonra eşik değiştirilmedi.

## Önce / sonra, 2029Q4

Önce = zipteki model. Sonra = bu klasör. S0–S7 sütunları aynı olduğu için tek sayı yazıldı. Etiket: **aday**.

| Senaryo | Enflasyon % | Net rezerv, mlr $ | Net rezerv 2028Q4 | Net rezerv 2027Q4 | Kamu borcu / GSYH % | Reel GSYH (2026Q3=100) | En düşük yıllık büyüme, puan |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| S0 Baz | 24,00 | −1,7 | 18,8 | 30,6 | 22,3 | 99,2 | −2,7 |
| S2 Reel değerlenme | 37,93 | −15,3 | 22,7 | 42,2 | 22,8 | 97,5 | −3,1 |
| S1 Dış şok | 1,94 | 67,6 | 38,9 | 3,5 | 32,2 | 88,4 | −13,2 |
| S4 Erteleme | −3,52 | 72,7 | 39,2 | 3,5 | 48,7 | 69,6 | −19,8 |
| S4z Zombi kapalı | 4,95 | 69,3 | 38,5 | 3,5 | 24,5 | 100,7 | −12,5 |
| S5 Tanıma | 4,96 | 64,0 | 39,7 | 3,5 | 28,3 | 101,3 | −9,8 |
| S5z Zombi kapalı | 6,83 | 69,3 | 38,8 | 3,5 | 24,1 | 103,2 | −7,6 |
| S3 Yeldan | 3,86 | 44,9 | 21,3 | 7,4 | 23,7 | 93,9 | −8,7 |
| S6 Sınır | 18,19 | −1,9 | 8,4 | 8,2 | 27,2 | 92,8 | −6,9 |
| S7 Sınır sert | 19,85 | 1,0 | 8,3 | 3,1 | 30,6 | 90,0 | −9,3 |

S4z ve S5z önce yoktu. Diğer satırlarda önce = sonra.

## Tek Sistem, baz arka plan

| Paket | Enflasyon 2029 % | Reel GSYH | Kamu borcu / GSYH % | Net rezerv 2028Q4 | USD/TL 2029 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Paketsiz | 24,00 | 99,2 | 22,3 | 18,8 | 102,34 |
| Kötümser | 25,46 | 93,1 | 24,2 | 21,1 | 102,97 |
| Olası | 23,98 | 98,8 | 22,5 | 28,8 | 97,80 |
| İyimser | 18,47 | 102,7 | 21,7 | 41,7 | 89,42 |

Bu dört satır da önce ile aynı (`once_ozet.json`). Dış şok arka planı da toleransın içinde kaldı. Dış şok paketsiz: enflasyon 1,94, kamu borcu %32,2, net rezerv 2029 67,6, USD/TL 110,15. Kötümser −2,57 / %40,9 / 75,7 / 108,08. Olası −0,93 / %37,8 / 74,9 / 106,10. İyimser 2,09 / %33,3 / 69,9 / 102,65.
