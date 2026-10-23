# Sapma kaydı

Ön kayıt `ON_KAYIT.md`. Koşu: `python3 zararin_muhasebesi/test_sfc_muhasebe.py` geçti. `python3 zararin_muhasebesi/build_page.py` geçti.

Haftalık logun son kaydı `kod_surumu.git = a3fdf4bccdef9f2f9ca4c807e8872b266d381739`, `kirli = true`. Bu, koşu anındaki HEAD'dir; entegrasyon commit'i ondan sonradır. Model dosyası `sfc_sha256 = 77950381a702f00331e2cd0b60a5074f98829b83055277bd51b69bfc067b04cf` ile kilitlidir.

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

## Ek — birincil veri güncellemesi

Ön kayıtın ek bölümü koşudan önce yazıldı. `once_ozet.json` bu koşunun referansı değildir. Eski = güncellemeden hemen önceki entegre koşu. Yeni = birincil gözlemle güncellenmiş girdi. Patika farkı girdi etkisidir; kimlik sapması değildir. Haftalık log, koşu anındaki HEAD'i yazar; bu commit ondan sonradır.

Muhasebe tuttu. Gizli denklem `1,0e-12`, bilanço `1,1e-11` tn TL. Test, tasarruf–yatırım eşiği `< 1e-8` ile geçti. S4z reel GSYH endeksi 100,3 > S4 68,9. Tanımanın üretim avantajı 26,1 puandan 6,6 puana indi. Model içi karşı-olgu; veri karşı-olgusu yok.

### Girdi, eski → yeni

| Kalem | Eski | Yeni | Etiket | Kaynak |
| --- | ---: | ---: | --- | --- |
| USD/TRY | 49,54 | 49,5389 | kanıt | TCMB ForexBuying, 22.10.2026, bülten 2026/200 |
| Politika faizi | 0,36 | 0,36 | kanıt | TCMB duyuru 2026-45, bir hafta vadeli repo |
| Brüt rezerv, mlr $ | 169,1 | 169,096 | kanıt | TCMB URDL I.A, 16.10.2026, 169.096 milyon $ |
| KV dış borç, kalan vade, mlr $ | 243,3 | 243,276 | kanıt | TCMB Tablo 5 toplam, Ağustos 2026 |
| Reel efektif kur | 105,45 | 105,45 | kanıt | TCMB TÜFE bazlı REK, Eylül 2026, 2025=100 |
| Yabancı hisse, mlr $ | 33,98 | 33,9811 | kanıt | TCMB Tablo 1, `TP.MKNETHAR.M1`, 16.10.2026 |
| Banka özkaynağı, tn TL | 4,65 | 4,565252392 | kanıt | EVDS `TP.TOP.V28`, 2026-07, 4.565.252.392 bin TL |
| Swap hariç net rezerv | 39,34 | 39,34 | [DOĞRULANMADI] | URDL'de başlık yok; bileşenler `veriler.json` |
| Emek payı | 0,381 | 0,381 | [DOĞRULANMADI] | TÜİK bülten sayfası sayı döndürmedi |
| Büyüme | 0,023 | 0,023 | [DOĞRULANMADI] | Aynı |
| Yabancı takas payı | 0,344 | 0,344 | [DOĞRULANMADI] | Borsa İstanbul tablosu okunmadı |
| BIST 100 | 11220,37 | 11220,37 | [DOĞRULANMADI] | Aynı. Açılış durumuna girmez |

Swap hariç net rezerv bileşenleri, 16.10.2026, milyon ABD doları: resmi rezerv 169.096; döviz varlıkları 54.492; altın 106.949; IMF 153; SDR 7.502; II.1 −38.592; II.2 forward −16.482; II.3 +4.312; III.1 şarta bağlı −68.703. Başlık bu satırlardan türetilmedi.

Patikayı oynatan girdi banka özkaynağıdır. Diğer kanıt satırları eski yuvarlağın içindedir.

### 2029Q4, eski → yeni

Enflasyon %, net rezerv mlr $, kamu borcu / GSYH %, reel GSYH endeksi (2026Q3=100). Etiket: **aday**.

| Senaryo | Enflasyon | Net rezerv | Kamu borcu / GSYH | Reel GSYH |
| --- | --- | --- | --- | --- |
| S0 | 24,00 → 24,00 | −1,7 → −1,7 | 22,3 → 22,2 | 99,2 → 99,2 |
| S4 | −3,52 → −3,92 | 72,7 → 73,7 | 48,7 → 49,7 | 69,6 → 68,9 |
| S4z | 4,95 → 4,48 | 69,3 → 68,8 | 24,5 → 25,1 | 100,7 → 100,3 |
| S5 | 4,96 → 4,83 | 64,0 → 63,7 | 28,3 → 28,4 | 101,3 → 101,2 |
| S5z | 6,83 → 6,69 | 69,3 → 68,9 | 24,1 → 24,3 | 103,2 → 103,1 |

Tek Sistem, baz. Sütunlar: enflasyon / reel GSYH / kamu borcu % / net rezerv 2028Q4 / USD/TL.

| Paket | Eski | Yeni |
| --- | --- | --- |
| Paketsiz | 24,00 / 99,2 / 22,3 / 18,8 / 102,34 | 24,00 / 99,2 / 22,2 / 18,9 / 102,32 |
| Kötümser | 25,46 / 93,1 / 24,2 / 21,1 / 102,97 | 25,28 / 91,5 / 24,8 / 21,2 / 103,01 |
| Olası | 23,98 / 98,8 / 22,5 / 28,8 / 97,80 | 23,88 / 97,3 / 23,0 / 28,9 / 97,82 |
| İyimser | 18,47 / 102,7 / 21,7 / 41,7 / 89,42 | 18,46 / 102,7 / 21,7 / 41,7 / 89,40 |

Tek Sistem, dış şok. Sütunlar: enflasyon / reel GSYH / kamu borcu % / net rezerv 2029 / USD/TL.

| Paket | Eski | Yeni |
| --- | --- | --- |
| Paketsiz | 1,94 / 88,4 / 32,2 / 67,6 / 110,15 | 1,52 / 87,9 / 32,8 / 67,1 / 109,74 |
| Kötümser | −2,57 / 79,5 / 40,9 / 75,7 / 108,08 | −3,20 / 78,4 / 42,1 / 77,6 / 107,56 |
| Olası | −0,93 / 83,4 / 37,8 / 74,9 / 106,10 | −1,40 / 82,4 / 38,9 / 76,2 / 105,71 |
| İyimser | 2,09 / 89,9 / 33,3 / 69,9 / 102,65 | 1,75 / 89,1 / 34,2 / 70,3 / 102,38 |

### S4 enflasyonu neden eksi

S4, dış şokun üzerine düşük tanımayı (φ = 0,2) bindirir. Gizli takip 2029'da GSYH'nin %3,7'sine çıkar; aynı şokta erteleme yokken (S1) %1,4'tür. Yatırım denklemi `γ_z = 0,8` ile bu oranı yatırımın içinden düşer. Reel GSYH endeksi 100'den 68,9'a iner. Zombi terimi kapatılınca (S4z) endeks 100,3 ve 2029 enflasyonu +%4,5 kalır. S1 enflasyonu +%1,5'tir.

Enflasyon denklemi `π = π^e + λ_f(ω − ω_f) + β_e(e − e^e) + β_y · açık`, `β_y = 0,20`. `π^e` OVP çıpasına çekilir; çıpa 2029'da %9'dur. Çöken üretim büyük eksi açık bırakır ve bu terim 2029 enflasyonunu −%3,9'a indirir. Önceki koşuda −%3,5 idi; özkaynak 4,65'ten 4,565'e inince çöküş biraz derinleşti. Bu, modelin kendi kapanışıdır (**aday**). Türkiye için nedensel bir tahmin değildir.
