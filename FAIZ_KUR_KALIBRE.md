# Faiz → kur kalibrasyonu

Soru: politika faizi (AOFM) sonraki çeyreğin dolar kurunu nasıl kaydırır?

Denklem: g = α + β · AOFM gecikmesi. g, çeyrek ortalaması USD/TRY'nin log farkı, yüzde puan.

## Katsayı

- Ana pencere 2021-Q1 → 2024-Q4, n=16. α **13.41**, β **-0.187** (se 0.066). R² 0.087.
- Bir puan AOFM, sonraki çeyreğin değer kaybını **0.19 puan** azaltır.
- Uzun pencere 2018-Q1 → 2024-Q4, n=28. β **-0.182** (se 0.059). İki pencerede eğim aynıdır.
- Reel faiz belirtimi (AOFM − yıllık TÜFE, gecikmeli) 2018-Q1 → 2024-Q4: β -0.027 (se 0.045), R² 0.005. İleri hesaba girmez.

## Sınav, 2025-Q1 → 2026-Q2

- Katsayı 2024-Q4 kurundan yürütülünce 2026-Q2 **47.06** çıkar. Ölçülen 45.37. Sapma **+3.7%**. 2026 ilk yarıda tahmin, ölçülen değer kaybının üstündedir.

| Çeyrek | Ölçülen g | Tahmin g |
| --- | ---: | ---: |
| 2025-Q1 | 4.80 | 4.05 |
| 2025-Q2 | 6.70 | 4.94 |
| 2025-Q3 | 5.05 | 4.53 |
| 2025-Q4 | 3.57 | 5.30 |
| 2026-Q1 | 3.32 | 6.02 |
| 2026-Q2 | 3.99 | 6.26 |

## İleri faiz yolları

- Son faiz: 2026-Q4 ve sonrası **37.00**. Eylül 2026 tam ayı ve 1–14 Ekim bu düzeydedir. Çeyrek kapanmadı; düzey varsayımdır.
- Anket: yıl sonu hedefleri `bes_yil_senaryo.csv` içinden okunur. 2026-Q4 anket yılı, sonrası yıl sonuna eşit adım. Son anket yılından sonra faiz sabit kalır.
- 2026-Q3 faizi iki yolda da ölçülmüş çeyrek ortalamasıdır. Kur çapası 2026-Q3 ölçülmüş çeyrek ortalamasıdır. İlk tahmin 2026-Q4.

Beş adım bu faizi üretmez. `bes_yil_senaryo` faiz hücresi `modellenmedi` kalır: o hücre beş adımın kendi düğmesidir.

## Ne denmez

- R² yüksek bir kur denklemi denmez. Faiz, çeyrek hareketinin küçük bir parçasıdır.
- Reel faiz kuru kalibre etti denmez. O belirtimin R²'si sıfıra yakındır.
- Beş adım faizi indirdi ya da kuru durdurdu denmez. Girdi AOFM yoludur.
- İç borç kuponu bu kanalla değişir denmez. r_ic 2025 kimliğinde durur. Kuran dış faiz bacağı değişir.
