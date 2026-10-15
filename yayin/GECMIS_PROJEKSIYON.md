# Salt geçmiş projeksiyonu

**Etiket:** `yalniz_gecmis_ileri_uzatma`. Girdi yalnız gozlem/evds_odeme_dengesi_aylik.csv (EVDS, aylık, mn USD).
Kullanılmayan: senaryo parametreleri, olasılık, katman çarpanı, λ/κ, faz takvimi, kalibrasyon ağırlıkları, kapı iskeleti.

## Gözlenen yıllar

| Yıl | r (YG gideri / ihracat) | Net YG gideri (mn $) |
| ---: | ---: | ---: |
| 2015 | 0.0765 | 9,276 |
| 2016 | 0.0778 | 8,501 |
| 2017 | 0.0822 | 10,403 |
| 2018 | 0.0854 | 10,778 |
| 2019 | 0.0874 | 11,479 |
| 2020 | 0.0727 | 8,316 |
| 2021 | 0.0686 | 11,094 |
| 2022 | 0.0555 | 8,728 |
| 2023 | 0.0749 | 11,240 |
| 2024 | 0.1029 | 17,456 |
| 2025 | 0.1204 | 21,845 |

Son 12 ay (2025-09..2026-08): r = **0.1191**, net = **23,445** mn $.

## Merkez sızıntı oranı (yatırım geliri gideri / mal ihracatı)

| Yöntem | 2026 | 2028 | 2031 | 2036 |
| --- | ---: | ---: | ---: | ---: |
| duz | 0.1191 | 0.1191 | 0.1191 | 0.1191 |
| trend5 | 0.1369 [0.0624; 0.3006] | 0.1939 [0.0683; 0.5507] | 0.3269 [0.0732; 1.4590] | 0.7805 [0.0776; 7.8510] |
| trendT | 0.0899 [0.0517; 0.1563] | 0.0933 [0.0512; 0.1700] | 0.0985 [0.0496; 0.1958] | 0.1079 [0.0457; 0.2545] |

## Net yatırım geliri gideri (mn USD)

| Yöntem | 2026 | 2028 | 2031 | 2036 |
| --- | ---: | ---: | ---: | ---: |
| duz | 23,445 | 23,445 | 23,445 | 23,445 |
| trend5 | 24,574 [9,099; 66,366] | 37,016 [9,901; 138,390] | 68,432 [10,338; 452,969] | 190,563 [10,312; 3,521,610] |
| trendT | 16,361 [8,807; 30,395] | 18,561 [9,472; 36,368] | 22,426 [10,385; 48,427] | 30,739 [11,751; 80,407] |

## Geriye test (2022'ye kadar fit, 2023–2025 tahmin)

| Seri | Yöntem | Ort. mutlak hata % | 2023 | 2024 | 2025 |
| --- | --- | ---: | ---: | ---: | ---: |
| r | duz | 41.9 | -25.8% | -46.0% | -53.9% |
| r | trend5 | 49.8 | -30.0% | -54.4% | -65.1% |
| r | trendT | 36.0 | -15.6% | -40.9% | -51.4% |
| net | duz | 44.1 | -22.3% | -50.0% | -60.0% |
| net | trend5 | 46.1 | -22.5% | -52.3% | -63.6% |
| net | trendT | 36.4 | -11.9% | -43.0% | -54.3% |

## Ne denmez

- Bu bir tahmin değil, geçmişin devamıdır. Rejim değişimi (2023'ten sonra r'nin ×1,6 artışı) geçmişten öngörülemez; geriye test bunu gösterir (üç yöntem de 2023–2025'te %36–50 ort. hata, hepsi eksik tahmin).
- Yöntem seçilmedi. Geriye test 3 gözlemlik: istatistiksel güç düşük; yalnız yönü gösterir. Hangisinin 'doğru' olduğu veriyle ayırt edilemiyor.
