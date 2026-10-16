# Faiz dışsallığı

Çekilme: 2026-10-16. Kurallar: `FAIZ_DISSALLIK_ONKAYIT.md`. Betik: `faiz_dissallik.py`. Sayılar: `faiz_dissallik_sonuc.json`.

Kurallar sonuçtan sonra değiştirilmedi. n < 36 olan dönemin katsayısı yazılmadı. Anlamlılık, aynı aydaki kısmi ilişkidir. TCMB’nin tepki verdiği iddiası değildir.

## 1. Üç cümle

Fonlama maliyeti dışsal kabul edilmez: 2018, 2021–22 ve 2023 kuklaları anlamlıdır ve 2011-02–2018-07 denkleminde enflasyon sapmasının katsayısı %5 eşiğini geçer. Gecelik faiz ile politika faizi dışsal kabul edilmez; geceliğin seri etiketi belirlenemiyor, politika faizinin EVDS serisi yoktur. En büyük belirsizlik 2018-08’den sonraki dört dönemin her birinde gözlem sayısının 36’nın altında kalmasıdır.

## 2. Katsayılar

Denklem: faiz_t = a + b1·sapma + b2·üretim açığı + b3·kur + b4·kredi büyümesi + b5·faiz_(t−1). OLS, Newey–West. Sapma = 12 aylık `TP.TUKFIY2025.GENEL` − 5. Hedef, 2026-10-16’da indirilen TCMB Inflation Targets sayfasında 2012–2028 için 5’tir. Üretim açığı, `TP.TSANAYMT2021.BCD` logaritmasının HP çevrimi, λ = 14400. Kur, `TP.DK.USD.A.YTL` için 100·Δlog. Kredi, `TP.KREDI.L001` 12 aylık yüzde değişimidir. Bu, toplam kredi hacmi arşividir.

Tam örneklem, fonlama `TP.APIFON4`, 2011-02…2025-01, n = 168, bant = 4, R² = 0,9877.

| Katsayı | Değer | t | %5 |
| --- | --- | --- | --- |
| b1 enflasyon sapması | −0,0163 | −0,94 | hayır |
| b2 üretim açığı | 0,0194 | 1,56 | hayır |
| b3 kur | −0,0278 | −1,53 | hayır |
| b4 kredi büyümesi | 0,0485 | 2,72 | evet |
| b5 gecikme | 1,0216 | 38,46 | evet |

Tam örneklem, gecelik `TP.PY.P06.ON`, 2007-01…2025-01, n = 217, bant = 4, R² = 0,9836.

| Katsayı | Değer | t | %5 |
| --- | --- | --- | --- |
| b1 enflasyon sapması | −0,0038 | −0,25 | hayır |
| b2 üretim açığı | 0,0151 | 1,00 | hayır |
| b3 kur | −0,0072 | −0,45 | hayır |
| b4 kredi büyümesi | 0,0336 | 2,45 | evet |
| b5 gecikme | 1,0106 | 50,89 | evet |

Dönem 1, fonlama, 2011-02…2018-07, n = 90, bant = 3, R² = 0,9529. Etiket: içsel. Eşiği geçen terim b1’dir. b4’ün t değeri 1,88’dir.

| Katsayı | Değer | t | %5 |
| --- | --- | --- | --- |
| b1 enflasyon sapması | 0,1742 | 3,59 | evet |
| b2 üretim açığı | −0,0136 | −0,42 | hayır |
| b3 kur | 0,0146 | 0,82 | hayır |
| b4 kredi büyümesi | 0,0208 | 1,88 | hayır |
| b5 gecikme | 0,9533 | 30,91 | evet |

Dönem 1, gecelik, 2007-01…2018-07, n = 139, bant = 4, R² = 0,9530. Etiket: dışsal. b1, b3 ve b4 eşiğin altında.

| Katsayı | Değer | t | %5 |
| --- | --- | --- | --- |
| b1 enflasyon sapması | 0,1423 | 1,20 | hayır |
| b2 üretim açığı | 0,0334 | 1,17 | hayır |
| b3 kur | 0,0084 | 0,61 | hayır |
| b4 kredi büyümesi | 0,0015 | 0,13 | hayır |
| b5 gecikme | 0,9442 | 31,57 | evet |

Dönem 2–5 için katsayı yok. R²’nin büyük kısmı gecikmededir.

## 3. Kırılma ve dönem n

Kuklalar tam örneklem denklemine eklendi. |t| > 1,96 ise kırılma vardır.

| Kukla | Pencere | Fonlama t | Gecelik t |
| --- | --- | --- | --- |
| d2018 | 2018-08…2018-12 | 4,49 | 4,49 |
| d2020 | 2020-03…2020-06 | 0,63 | 0,71 |
| d2122 | 2021-09…2022-12 | −2,01 | −2,17 |
| d2023 | 2023-06…örnek sonu | 3,03 | 3,27 |

İki seride de d2018, d2122 ve d2023 anlamlıdır. d2020 değildir. Kırılma vardır. Seri etiketi tam örneklemden verilmedi.

| Dönem | Sınır | Fonlama n | Fonlama etiket | Gecelik n | Gecelik etiket |
| --- | --- | --- | --- | --- | --- |
| 1 | …2018-07 | 90 | içsel | 139 | dışsal |
| 2 | 2018-08…2020-02 | 19 | belirlenemiyor | 19 | belirlenemiyor |
| 3 | 2020-03…2021-08 | 18 | belirlenemiyor | 18 | belirlenemiyor |
| 4 | 2021-09…2023-05 | 21 | belirlenemiyor | 21 | belirlenemiyor |
| 5 | 2023-06…2025-01 | 20 | belirlenemiyor | 20 | belirlenemiyor |

Dönem 5, kredi arşivi 2025-01’de bittiği için orada durur. AOFM ve gecelik 2026-10’a kadar gelir.

Tanım takvimi: bir haftalık repo serisi yoktur. AOFM’nin hangi kanalı ortaladığının gün gün listesi bu turda doğrulanmadı. Gecelik, `TP.PY.P06.ON` piyasa ağırlıklı ortalamasıdır. `TP.PY.P01.ON` ve `TP.PY.P02.ON` kotasyonları regresyona girmedi. Kırılma tarihleri yukarıdaki dört penceredir.

## 4. Dışsallık kararı

| Tanım | Seri | Karar | Dayanak |
| --- | --- | --- | --- |
| Politika faizi | yok | belirlenemiyor | EVDS’de bir haftalık repo ihale faizi yok. Elle kodlanmadı |
| Fonlama maliyeti | `TP.APIFON4` | içsel | Kırılma var. Dönem 1’de b1 anlamlı, n = 90 |
| Gecelik | `TP.PY.P06.ON` | belirlenemiyor | Kırılma var. Dönem 1 dışsal, n = 139. Sonraki dört dönem n < 36 |

Tam örneklemde iki seride de b4 anlamlıdır. Kırılma kuralı bu satırı seri etiketi yapmaz. Fonlamada tam örneklemin anlamlı terimi b4, dönem 1’in anlamlı terimi b1’dir.

## 5. Uygulanmayan öneri

Dışsal kabul edilmeyen ve belirlenemeyen dönemler için aday, PPK karar metninden elle kodlanmış anlatısal şoktur. Faiz değişiminin, anketin toplantı öncesi politika faizi beklentisinden (`TP.PKAUO.S04` ailesi) farkı ikinci adaydır. İkisi de bu turda kurulmadı. Kurulursa ayrı bir ön kayıt, yön, pencere ve anlamlılık eşiği ister.

## 6. Veri

Ortak örnek, fonlamada 2011-02…2025-01, n = 168. Gecelikte 2007-01…2025-01, n = 217. Bağlayan uç, kredi arşivinin 2025-01’de bitmesidir.

| Seri | Kod | İlk | Son | n |
| --- | --- | --- | --- | --- |
| Fonlama | `TP.APIFON4` | 2011-01 | 2026-10 | 190 |
| Gecelik | `TP.PY.P06.ON` | 2006-01 | 2026-10 | 250 |
| TÜFE | `TP.TUKFIY2025.GENEL` | 2006-01 | 2026-09 | 249 |
| Çekirdek B, arşiv, denklemde yok | `TP.FE.OKTG03` | 2006-01 | 2025-12 | 240 |
| Çekirdek C, arşiv, denklemde yok | `TP.FE.OKTG04` | 2006-01 | 2025-12 | 240 |
| Sanayi üretimi, arındırılmış | `TP.TSANAYMT2021.BCD` | 2006-01 | 2026-08 | 248 |
| USD alış | `TP.DK.USD.A.YTL` | 2006-01 | 2026-10 | 250 |
| Toplam kredi, arşiv | `TP.KREDI.L001` | 2006-01 | 2025-01 | 229 |
| 12 ay TÜFE beklentisi | `TP.PKAUO.S01.E.U` | 2013-01 | 2026-10 | 166 |

Ön kayıttaki sanayi başlangıcı 2010-01 yazıyordu. O tarama 2010’da açılmıştı. Bu çekimde aynı kod 2006-01’de başlar. Kod değişmedi.

Reel faiz = nominal − `TP.PKAUO.S01.E.U`. Beklenti aralığı 2013-01…2026-10 içinde boş ay sayısı 0’dır. Doldurma yapılmadı. Fonlama reel serisi n = 166, 2013-01…2026-10. Gecelik reel serisi aynı ay sayısı. Reel faiz tepki fonksiyonuna konmadı.

Eksikler: politika faizi serisi; 2018 sonrası dönemlerin gözlem eşiği; kredi arşivinin 2025-02’den sonrası; AOFM kanal takvimi; çekirdek B ve C’nin denklemde olmayışı. Çekirdek, ön kayıttaki denklemin değişkeni değildir.

## 7. Eleştiriler

Anket aylık çekimde deliksizdir. Yine de 12 ay sonrası yıllık enflasyon beklentisidir. Aylık fonlama oranından çıkarılınca iki ayrı ufuk birbirine yapışır. Seri 2013-01’de başlar. Fonlama denklemi 2011-02’de başlar. Reel serinin örtüşmediği 2011–2012 ayları tepki fonksiyonunda durur, çünkü reel faiz o fonksiyona konmadı. Toplantı günündeki bilgi ile ay ortalaması aynı nesne değildir.

Fonksiyon doğrusaldır. Kuklalar yalnız sabiti kaydırır. Eğimin dönemler arasında değişip değişmediği sınanmadı. Gecikme katsayısı 0,94 ile 1,02 arasındadır. R² 0,95–0,99 bandındadır ve büyük kısmı bu gecikmedir. Küçük bir kısmi t değeri, seriyi şok yapmaya yeten bir ölçüt olarak zayıftır. Tam örneklemde eşiği kredi geçer. 2018 öncesinde fonlamada eşiği enflasyon sapması geçer. Aynı doğrusal katsayı iki pencerede aynı terim değildir.

Resmi hedef yüzde 5’te durur. Gerçekleşen enflasyon bu hedefin çok uzağındadır. Bankanın o ay fiilen baktığı patika tablodaki 5 değilse, b1 yanlış sapmadır. ±2 belirsizlik bandı ve açık mektup bu denklemde yoktur. OLS eşanlıdır: enflasyon, kur ve kredi ile faiz aynı ayda belirlenir. Anlamlı b1, bir tepki fonksiyonunun teşhisi değildir. Döviz müdahalesi ve makroihtiyati araçlar denklemde yoktur. Onların izi b3 ve b4’e kalabilir.
